#!/usr/bin/env python3

import csv
import pika
import json
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
        "hour","minute","second","accuracy","lon","lat",
        "epfd","raim","radio",
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
# VALIDATION
# ==========================================================
def valid_mmsi(mmsi):
    try:
        return int(mmsi) > 0
    except:
        return False

def valid_lat(lat):
    try:
        return -90 <= float(lat) <= 90
    except:
        return False

def valid_lon(lon):
    try:
        return -180 <= float(lon) <= 180
    except:
        return False

def valid_sog(sog):
    try:
        return float(sog) >= 0
    except:
        return False

def clean_row(category, row):
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

# ==========================================================
# TAG BLOCK EXTRACTION
# ==========================================================
def extract_tagblock(raw_line):
    timestamp = None
    source = None

    if raw_line.startswith("\\"):
        parts = raw_line.split("\\!", 1)
        tag = parts[0]
        clean_nmea = "!" + parts[1] if len(parts) > 1 else raw_line

        for field in tag.split(","):
            if field.startswith("c:"):
                try:
                    unix_part = field.split(":",1)[1]
                    unix_part = unix_part.split("*")[0]
                    timestamp = datetime.fromtimestamp(
                        int(unix_part),
                        tz=timezone.utc
                    ).isoformat()
                except:
                    pass
            if field.startswith("s:"):
                source = field.split(":",1)[1]

        return timestamp, source, clean_nmea

    return None, None, raw_line

# ==========================================================
# REM EVENT
# ==========================================================
def generate_rem_event(category, row):
    if category not in ["dynamic_position","static_position","safety_messages"]:
        return None

    return {
        "event_type": category,
        "mmsi": row.get("mmsi"),
        "lat": row.get("lat"),
        "lon": row.get("lon"),
        "sog": row.get("speed",0),
        "cog": row.get("course",0),
        "heading": row.get("heading",0),
        "timestamp": row.get("timestamp"),
        "source": row.get("source")
    }

# ==========================================================
# FILE WRITERS
# ==========================================================
writers = {}
files = {}
rem_writer = None
rem_file = None

def get_writer(category):
    if category not in writers:
        f = open(OUT / f"{category}.csv","w",newline="",encoding="utf-8")
        w = csv.DictWriter(f,fieldnames=SCHEMAS[category])
        w.writeheader()
        writers[category] = w
        files[category] = f
    return writers[category]

def get_rem_writer():
    global rem_writer, rem_file
    if not rem_writer:
        rem_file = open(REM_OUT / "rem_events.csv","w",newline="",encoding="utf-8")
        rem_writer = csv.DictWriter(rem_file, fieldnames=[
            "event_type","mmsi","lat","lon","sog","cog","heading",
            "timestamp","source"
        ])
        rem_writer.writeheader()
    return rem_writer

# ==========================================================
# RABBITMQ
# ==========================================================
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue=INPUT_QUEUE, durable=True)
channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

print("📡 Connected to RabbitMQ, waiting for AIS messages...")

# ==========================================================
# MAIN LOOP
# ==========================================================
try:
    for method_frame, properties, body in channel.consume(INPUT_QUEUE, inactivity_timeout=1):

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
                category = MESSAGE_MAP.get(msg_type,"binary_misc")

                if not clean_row(category, decoded):
                    continue

                # Save CSV
                get_writer(category).writerow(
                    filter_row(category, decoded)
                )

                # Save REM
                rem = generate_rem_event(category, decoded)
                if rem:
                    get_rem_writer().writerow(rem)

                # SEND CLEANED JSON TO QUEUE
                json_message = json.dumps(decoded)

                channel.basic_publish(
                    exchange="",
                    routing_key=OUTPUT_QUEUE,
                    body=json_message.encode("utf-8"),
                    properties=pika.BasicProperties(delivery_mode=2)
                )

                print("➡ Sent CLEANED JSON:", json_message[:120])

        except Exception as e:
            print("Decode error:", e)

        channel.basic_ack(method_frame.delivery_tag)

except KeyboardInterrupt:
    print("\nStopping pipeline...")

finally:
    for f in files.values():
        f.close()
    if rem_file:
        rem_file.close()
    try:
        channel.close()
    except:
        pass
    connection.close()
    print("CSV + REM flushed successfully")
