#!/usr/bin/env python3
import csv
import pika
import time
from pathlib import Path
from datetime import datetime, timezone
from pyais.stream import IterMessages

# ==========================================================
# CONFIG
# ==========================================================
INPUT_QUEUE = "ais_nmea_queue"
OUTPUT_QUEUE = "cleaned_ais_queue"
OUT = Path("outputs")
REM_OUT = Path("rem")
OUT.mkdir(exist_ok=True)
REM_OUT.mkdir(exist_ok=True)

# Raw CSV for reference
RAW_CSV = "input/AIS_Klaipeda_From20250908_To20251008 2.csv"

# ==========================================================
# MESSAGE CATEGORY MAPPING
# ==========================================================
MESSAGE_MAP = {
    1: "dynamic_position",
    2: "dynamic_position",
    3: "dynamic_position",
    18: "static_position",
    19: "static_position",
    5: "voyage_info",
    24: "voyage_info",
    4: "base_station",
    21: "navigation_aid",
    7: "safety_messages",
    10: "safety_messages",
    12: "safety_messages",
    13: "safety_messages",
    14: "safety_messages",
    15: "safety_messages"
}

# ==========================================================
# SCHEMAS
# ==========================================================
SCHEMAS = {
    "dynamic_position": [
        "msg_type","repeat","mmsi","status","turn","speed","accuracy",
        "lon","lat","course","heading","second","maneuver","raim","radio","timestamp"
    ],
    "static_position": [
        "msg_type","repeat","mmsi","speed","accuracy","lon","lat",
        "course","heading","second","cs","display","dsc","band",
        "msg22","assigned","raim","radio","timestamp"
    ],
    "voyage_info": [
        "msg_type","repeat","mmsi","partno","shipname","timestamp"
    ],
    "base_station": [
        "msg_type","repeat","mmsi","year","month","day",
        "hour","minute","second","accuracy","lon","lat","epfd","raim","radio","timestamp"
    ],
    "navigation_aid": [
        "msg_type","repeat","mmsi","aid_type","name",
        "accuracy","lon","lat","timestamp"
    ],
    "safety_messages": [
        "msg_type","repeat","mmsi","timestamp"
    ],
    "binary_misc": [
        "msg_type","repeat","mmsi","timestamp"
    ]
}

# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================
def valid_mmsi(mmsi):
    try:
        return int(mmsi) > 0
    except Exception:
        return False

def valid_lat(lat):
    try:
        return -90 <= float(lat) <= 90
    except Exception:
        return False

def valid_lon(lon):
    try:
        return -180 <= float(lon) <= 180
    except Exception:
        return False

def valid_sog(sog):
    try:
        return float(sog) >= 0
    except Exception:
        return False

def clean_row(category, row):
    """Return True if row is valid, False otherwise"""
    if category not in ("base_station","binary_misc"):
        if not valid_mmsi(row.get("mmsi")):
            return False
    if category in ("dynamic_position","static_position","navigation_aid"):
        if not valid_lat(row.get("lat")) or not valid_lon(row.get("lon")):
            return False
    if category in ("dynamic_position","static_position"):
        if not valid_sog(row.get("speed")):
            return False
    return True

def filter_row(category, row):
    return {k: row.get(k) for k in SCHEMAS[category]}

def generate_rem_event(category, row):
    """Generate REM event only for dynamic, static, safety messages"""
    if category not in ["dynamic_position","static_position","safety_messages"]:
        return None
    return {
        "event_type": category,
        "mmsi": row.get("mmsi"),
        "lat": row.get("lat"),
        "lon": row.get("lon"),
        "sog": row.get("speed", 0),
        "cog": row.get("course", 0),
        "heading": row.get("heading", 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ==========================================================
# WRITERS
# ==========================================================
writers = {}
files = {}
rem_writer = None
rem_file = None

def get_writer(category):
    if category not in writers:
        f = open(OUT / f"{category}.csv", "w", newline="", encoding="utf-8")
        w = csv.DictWriter(f, fieldnames=SCHEMAS[category], extrasaction="ignore")
        w.writeheader()
        writers[category] = w
        files[category] = f
    return writers[category]

def get_rem_writer():
    global rem_writer, rem_file
    if not rem_writer:
        rem_file = open(REM_OUT / "rem_events.csv", "w", newline="", encoding="utf-8")
        rem_writer = csv.DictWriter(rem_file, fieldnames=[
            "event_type","mmsi","lat","lon","sog","cog","heading","timestamp"
        ])
        rem_writer.writeheader()
    return rem_writer

# ==========================================================
# RABBITMQ SETUP
# ==========================================================
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue=INPUT_QUEUE, durable=True)
channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

print("📡 Connected to RabbitMQ, waiting for AIS messages...")

# ==========================================================
# PROCESS MESSAGES
# ==========================================================
try:
    for method_frame, properties, body in channel.consume(INPUT_QUEUE, inactivity_timeout=1):
        if body is None:
            continue

        # Decode messages from NMEA bytes
        try:
            for msg in IterMessages(body):
                decoded = msg.decode().asdict()
                decoded["timestamp"] = datetime.now(timezone.utc).isoformat()

                msg_type = decoded.get("msg_type")
                category = MESSAGE_MAP.get(msg_type, "binary_misc")

                if not clean_row(category, decoded):
                    continue

                # Write CSV
                writer = get_writer(category)
                writer.writerow(filter_row(category, decoded))

                # REM events
                rem = generate_rem_event(category, decoded)
                if rem:
                    get_rem_writer().writerow(rem)

                # Send cleaned message to output queue
                channel.basic_publish(
                    exchange="",
                    routing_key=OUTPUT_QUEUE,
                    body=str(decoded).encode(),
                    properties=pika.BasicProperties(delivery_mode=2)
                )

        except Exception as e:
            print("❌ Decode error:", e)
            print("Raw NMEA:", body)

except KeyboardInterrupt:
    print("\n🛑 Stopping pipeline...")

finally:
    # Flush CSVs
    for f in files.values():
        f.close()
    if rem_file:
        rem_file.close()
    channel.close()
    connection.close()
    print("✅ CSV + REM flushed successfully")
