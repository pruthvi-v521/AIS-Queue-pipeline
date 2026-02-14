import pika
import json
import csv
import os
from datetime import datetime, timezone
from pyais import decode
import re


# CONFIGURATION (ONLY THESE 3 QUEUES WILL EXIST)


INPUT_QUEUE = "ais_nmea_queue"
ANALYSIS_QUEUE = "analysis_queue"
VISUALIZATION_QUEUE = "visualization_queue"

OUTPUT_DIR = "output_csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# RABBITMQ CONNECTION

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)

channel = connection.channel()

# declare ONLY these queues
channel.queue_declare(queue=INPUT_QUEUE, durable=True)
channel.queue_declare(queue=ANALYSIS_QUEUE, durable=True)
channel.queue_declare(queue=VISUALIZATION_QUEUE, durable=True)

print("Connected to RabbitMQ")
print("Receiving from:", INPUT_QUEUE)
print("Sending to:", ANALYSIS_QUEUE, "and", VISUALIZATION_QUEUE)



# CSV HANDLING


csv_files = {}
csv_writers = {}

def get_csv_writer(msg_type, fieldnames):

    filename = f"{OUTPUT_DIR}/msg_type_{msg_type}.csv"

    if msg_type not in csv_files:

        file_exists = os.path.exists(filename)

        f = open(filename, "a", newline="", encoding="utf-8")

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        if not file_exists:
            writer.writeheader()

        csv_files[msg_type] = f
        csv_writers[msg_type] = writer

    return csv_writers[msg_type]



# CHECKSUM VALIDATION

def valid_nmea_checksum(nmea):

    try:

        match = re.match(r'!(.*)\*(\w\w)', nmea)

        if not match:
            return False

        data, checksum = match.groups()

        calc = 0
        for char in data:
            calc ^= ord(char)

        return calc == int(checksum, 16)

    except:
        return False



# EXTRACT TAGBLOCK (timestamp and source)


def extract_tagblock(raw_line):

    source = None
    timestamp = None
    clean_nmea = raw_line

    if raw_line.startswith("\\"):

        try:

            parts = raw_line.split("\\")

            tagblock = parts[1]
            clean_nmea = parts[2]

            fields = tagblock.split(",")

            for field in fields:

                if field.startswith("s:"):
                    source = field.split(":", 1)[1]

                elif field.startswith("c:"):

                    ts = field.split(":", 1)[1]
                    ts = ts.split("*")[0]

                    timestamp = datetime.fromtimestamp(
                        int(ts),
                        timezone.utc
                    ).isoformat()

        except Exception as e:
            print("Tagblock parse error:", e)

    return timestamp, source, clean_nmea



# MAKE JSON SAFE


def make_json_safe(data):

    if isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}

    elif isinstance(data, list):
        return [make_json_safe(v) for v in data]

    elif isinstance(data, bytes):
        return data.decode("utf-8", errors="ignore")

    else:
        return data



# FRAGMENT BUFFER


fragment_buffer = {}


# PROCESS MESSAGE


def process_message(raw_line):

    timestamp, source, nmea = extract_tagblock(raw_line)

    if not nmea.startswith("!AIVDM"):
        return

    if not valid_nmea_checksum(nmea):

        print("\nINVALID CHECKSUM — DISCARDED")
        print(nmea)
        return

    parts = nmea.split(",")

    total_fragments = int(parts[1])
    fragment_number = int(parts[2])
    fragment_id = parts[3] if parts[3] else "no_id"

    key = fragment_id

    
    # MULTI-FRAGMENT HANDLING
    

    if total_fragments > 1:

        print("\nFragment received")
        print("Fragment ID:", key)
        print("Fragment:", fragment_number, "/", total_fragments)
        print("Raw fragment:", nmea)

        if key not in fragment_buffer:
            fragment_buffer[key] = {}

        fragment_buffer[key][fragment_number] = nmea

        if len(fragment_buffer[key]) < total_fragments:
            print("Waiting for remaining fragments...")
            return

        ordered_fragments = [
            fragment_buffer[key][i]
            for i in range(1, total_fragments + 1)
        ]

        print("\nALL FRAGMENTS RECEIVED — COMBINING NOW")
        for frag in ordered_fragments:
            print("Fragment:", frag)

        del fragment_buffer[key]

        try:

            decoded = decode(*ordered_fragments).asdict()

            print("\nCOMBINED MESSAGE SUCCESSFULLY")

        except Exception as e:

            print("DECODE FAILED:", e)
            return

    else:

        try:

            decoded = decode(nmea).asdict()

        except Exception as e:

            print("DECODE FAILED:", e)
            return


    
    # ADD TIMESTAMP AND SOURCE
    

    decoded["timestamp"] = timestamp
    decoded["source"] = source

    safe_decoded = make_json_safe(decoded)

    msg_type = safe_decoded.get("msg_type", "unknown")

    
    # PRINT FINAL MESSAGE
    

    print("\nFINAL DECODED MESSAGE")
    print(json.dumps(safe_decoded, indent=2))

    
    # WRITE CSV
    
    writer = get_csv_writer(msg_type, safe_decoded.keys())
    writer.writerow(safe_decoded)

    
    # SEND TO ANALYSIS QUEUE
    
    json_msg = json.dumps(safe_decoded)

    channel.basic_publish(
        exchange="",
        routing_key=ANALYSIS_QUEUE,
        body=json_msg,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    
    # SEND TO VISUALIZATION QUEUE
    

    channel.basic_publish(
        exchange="",
        routing_key=VISUALIZATION_QUEUE,
        body=json_msg,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print("\nSENT TO QUEUES SUCCESSFULLY")
    print("Analysis Queue:", ANALYSIS_QUEUE)
    print("Visualization Queue:", VISUALIZATION_QUEUE)



# CALLBACK


def callback(ch, method, properties, body):

    try:

        raw_line = body.decode("utf-8").strip()

        process_message(raw_line)

    except Exception as e:

        print("Processing Error:", e)

    ch.basic_ack(delivery_tag=method.delivery_tag)



# START CONSUMING

channel.basic_consume(
    queue=INPUT_QUEUE,
    on_message_callback=callback
)

print("\nWAITING FOR AIS DATA...\n")

try:

    channel.start_consuming()

except KeyboardInterrupt:

    print("\nSTOPPING PIPELINE")

finally:

    for f in csv_files.values():
        f.close()

    if channel.is_open:
        channel.close()

    if connection.is_open:
        connection.close()

    print("PIPELINE CLOSED")
