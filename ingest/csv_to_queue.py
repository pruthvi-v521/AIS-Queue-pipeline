import csv
import pika
import time

CSV_FILE = "input/AIS_Klaipeda_From20250908_To20251008.csv"
QUEUE_NAME = "ais_nmea_queue"

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="rabbitmq", port=5672, virtual_host="/", credentials=pika.PlainCredentials("ais", "aispass"))
)
channel = connection.channel()

# Declare a durable queue
channel.queue_declare(queue=QUEUE_NAME, durable=True)

print("CSV Reader started...")

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue

        nmea = row[0]  # assuming NMEA sentence is in the first column

        # Publish to RabbitMQ
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=nmea.encode(),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )

        print("➡ Sent:", nmea[:80])  # print first 80 characters
        time.sleep(0.05)  # simulate real-time streaming

# Close connection
connection.close()
print("CSV streaming finished")
