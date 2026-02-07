#!/usr/bin/env python3
import csv
import pika
from pathlib import Path
from datetime import datetime, timezone
from pyais.stream import IterMessages

# ==========================================================
# CONFIG
# ==========================================================
INPUT_QUEUE = "ais_nmea_queue"
OUTPUT_QUEUE = "cleaned_ais_queue"

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

# ==========================================================
# MESSAGE CATEGORY MAP
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
        "lon","lat","course","heading","second","maneuver","raim","radio",
        "timestamp","source"
    ],
    "static_position": [
        "msg_type","repeat","mmsi","speed","accuracy","lon","lat",
        "course","heading","second","cs","display","dsc","band",
        "msg22","assigned","raim","radio",
        "timestamp","source"
    ],
    "voyage_info": [
        "msg_type","repeat","mmsi","partno","shipname",
        "timestamp","source"
    ],
    "base_station": [
        "msg_type","repeat","mmsi","year","month","day",
        "hour","minute","second","accuracy","lon","lat","epfd","raim","radio",
        "timestamp","source"
    ],
    "navigation_aid": [
        "msg_type","repeat","mmsi","aid_type","name",
        "accuracy","lon","lat",
        "timestamp","source"
    ],
    "safety_messages": [
        "msg_type","repeat","mmsi",
        "timestamp","source"
    ],
    "binary_misc": [
        "msg_type","repeat","mmsi",
        "timestamp","source"
    ]
}

# ==========================================================
# TAG BLOCK PARSER (CHECKSUM SAFE)
# ==========================================================
def extract_tagblock(line: str):
    timestamp = None
    source = None

    if "\\!" in line:
        tag_part, nmea_part = line.split("\\!", 1)
        tag_part = tag_part.strip("\\ ")

        for field in tag_part.split(","):
            if field.startswith("c:"):
                raw_ts = field.split(":", 1)[1]
                raw_ts = raw_ts.split("*", 1)[0]  # ⭐ FIX
                timestamp = datetime.fromtimestamp(
                    int(raw_ts), tz=timezone.utc
                ).isoformat()

            elif field.startswith("s:"):
                source = field.split(":", 1)[1]

        return timestamp, source, "!" + nmea_part

    return None, None, line.strip()

# ==========================================================
# BASIC CLEANING
# ==========================================================
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

def clean_row(category, row):
    if category in ("dynamic_position","static_position","navigation_aid"):
        return valid_lat(row.get("lat")) and valid_lon(row.get("lon"))
    return True

# ==========================================================
# CSV WRITERS
# ==========================================================
writers = {}
files = {}

def get_writer(category):
    if category not in writers:
        f = open(OUT / f"{category}.csv", "w", newline="", encoding="utf-8")
        w = csv.DictWriter(f, fieldnames=SCHEMAS[category])
        w.writeheader()
        writers[category] = w
        files[category] = f
    return writers[category]

# ==========================================================
# RABBITMQ SETUP
# ==========================================================
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue=INPUT_QUEUE, durable=True)
channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

print("📡 Connected to RabbitMQ, waiting for AIS messages...")

# ==========================================================
# MAIN LOOP
# ==========================================================
try:
    for method, props, body in channel.consume(INPUT_QUEUE, inactivity_timeout=1):
        if body is None:
            continue

        raw_line = body.decode(errors="ignore").strip()
        ts, src, clean_nmea = extract_tagblock(raw_line)

        try:
            for msg in IterMessages(clean_nmea.encode()):
                decoded = msg.decode().asdict()
                decoded["timestamp"] = ts
                decoded["source"] = src

                msg_type = decoded.get("msg_type")
                category = MESSAGE_MAP.get(msg_type, "binary_misc")

                if not clean_row(category, decoded):
                    continue

                get_writer(category).writerow(
                    {k: decoded.get(k) for k in SCHEMAS[category]}
                )

                channel.basic_publish(
                    exchange="",
                    routing_key=OUTPUT_QUEUE,
                    body=str(decoded).encode(),
                    properties=pika.BasicProperties(delivery_mode=2)
                )

        except Exception as e:
            print("Decode error:", e)
            print("Raw:", raw_line)

except KeyboardInterrupt:
    print("\nStopping pipeline...")

finally:
    for f in files.values():
        f.close()
    channel.close()
    connection.close()
    print("CSV flushed successfully")
