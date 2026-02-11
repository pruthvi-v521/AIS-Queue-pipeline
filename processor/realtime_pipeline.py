#!/usr/bin/env python3

import csv
import os
import time
import pika
import json
from pathlib import Path
from datetime import datetime, timezone
from pyais.stream import IterMessages

# ==========================================================
# ENV CONFIG
# ==========================================================
RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_USER = os.getenv("RABBIT_USER", "ais")
RABBIT_PASS = os.getenv("RABBIT_PASS", "aispass")
STATION_ID = os.getenv("STATION_ID", "KLAIPEDA_01")

INPUT_QUEUE = "ais_nmea_queue"
OUTPUT_QUEUE = "cleaned_ais_queue"

OUT = Path("outputs")
REM_OUT = Path("rem")

OUT.mkdir(exist_ok=True)
REM_OUT.mkdir(exist_ok=True)

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
# SCHEMAS (+ station_id kept)
# ==========================================================
SCHEMAS = {
    "dynamic_position": ["msg_type","repeat","mmsi","status","turn","speed","accuracy",
                         "lon","lat","course","heading","second","maneuver","raim","radio",
                         "timestamp","source","station_id"],

    "static_position": ["msg_type","repeat","mmsi","speed","accuracy","lon","lat",
                        "course","heading","second","cs","display","dsc","band",
                        "msg22","assigned","raim","radio",
                        "timestamp","source","station_id"],

    "voyage_info": ["msg_type","repeat","mmsi","partno","shipname",
                    "timestamp","source","station_id"],

    "base_station": ["msg_type","repeat","mmsi","year","month","day",
                     "hour","minute","second","accuracy","lon","lat",
                     "epfd","raim","radio","timestamp","source","station_id"],

    "navigation_aid": ["msg_type","repeat","mmsi","aid_type","name",
                       "accuracy","lon","lat","timestamp","source","station_id"],

    "safety_messages": ["msg_type","repeat","mmsi","timestamp","source","station_id"],
    "binary_misc": ["msg_type","repeat","mmsi","timestamp","source","station_id"]
}

# ==========================================================
# VALIDATION
# ==========================================================
def valid_mmsi(m): 
    try: return int(m) > 0
    except: return False

def valid_lat(v): 
    try: return -90 <= float(v) <= 90
    except: return False

def valid_lon(v): 
    try: return -180 <= float(v) <= 180
    except: return False

def valid_sog(v): 
    try: return float(v) >= 0
    except: return False

def clean_row(category, row):
    if category not in ("base_station","binary_misc"):
        if not valid_mmsi(row.get("mmsi")): return False

    if category in ("dynamic_position","static_position","navigation_aid"):
        if not valid_lat(row.get("lat")) or not valid_lon(row.get("lon")): return False

    if category in ("dynamic_position","static_position"):
        if not valid_sog(row.get("speed")): return False

    return True

def filter_row(category, row):
    return {k: row.get(k) for k in SCHEMAS[category]}

# ==========================================================
# TAG BLOCK PARSER
# ==========================================================
def extract_tagblock(line):
    timestamp, source = None, None

    if "\\!" in line:
        tag, nmea = line.split("\\!",1)

        for f in tag.split(","):
            if f.startswith("c:"):
                ts = f.split(":",1)[1].split("*")[0]
                timestamp = datetime.fromtimestamp(int(ts),tz=timezone.utc).isoformat()
            if f.startswith("s:"):
                source = f.split(":",1)[1]

        return timestamp, source, "!" + nmea

    return None, None, line.strip()

# ==========================================================
# REM EVENT GENERATOR
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
writers, files = {}, {}
rem_writer, rem_file = None, None

def get_writer(cat):
    if cat not in writers:
        f = open(OUT/f"{cat}.csv","w",newline="",encoding="utf-8")
        w = csv.DictWriter(f,fieldnames=SCHEMAS[cat])
        w.writeheader()
        writers[cat]=w; files[cat]=f
    return writers[cat]

def get_rem_writer():
    global rem_writer, rem_file
    if not rem_writer:
        rem_file=open(REM_OUT/"rem_events.csv","w",newline="",encoding="utf-8")
        rem_writer=csv.DictWriter(rem_file,
            fieldnames=["event_type","mmsi","lat","lon","sog","cog","heading","timestamp","source"])
        rem_writer.writeheader()
    return rem_writer

# ==========================================================
# SAFE CONNECT (retry)
# ==========================================================
def connect():
    creds = pika.PlainCredentials(RABBIT_USER,RABBIT_PASS)

    for i in range(15):
        try:
            conn=pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST,credentials=creds))
            print("Connected to RabbitMQ")
            return conn
        except pika.exceptions.AMQPConnectionError:
            print("Retrying RabbitMQ...")
            time.sleep(2)

    raise RuntimeError("RabbitMQ unavailable")

# ==========================================================
# MAIN
# ==========================================================
connection = connect()
channel = connection.channel()

channel.queue_declare(queue=INPUT_QUEUE, durable=True)
channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

count = 0
print("Waiting for AIS messages...")

try:
    for method, props, body in channel.consume(INPUT_QUEUE, inactivity_timeout=1):

        if body is None:
            continue

        raw = body.decode(errors="ignore").strip()
        ts, src, clean = extract_tagblock(raw)

        for msg in IterMessages(clean.encode()):
            decoded = msg.decode().asdict()

            # enrichment
            decoded["timestamp"] = ts
            decoded["source"] = src
            decoded["station_id"] = STATION_ID

            category = MESSAGE_MAP.get(decoded.get("msg_type"),"binary_misc")

            if not clean_row(category, decoded):
                continue

            # CSV
            get_writer(category).writerow(filter_row(category, decoded))

            # REM
            rem = generate_rem_event(category, decoded)
            if rem:
                get_rem_writer().writerow(rem)

            # JSON publish
            channel.basic_publish(
                exchange="",
                routing_key=OUTPUT_QUEUE,
                body=json.dumps(decoded, default=str).encode(),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            count += 1
            if count % 100 == 0:
                print(f"Processed {count} messages")

        channel.basic_ack(method.delivery_tag)

finally:
    for f in files.values(): f.close()
    if rem_file: rem_file.close()
    channel.close()
    connection.close()
