import pika, os, sys

try:
    creds = pika.PlainCredentials(
        os.getenv("RABBIT_USER"),
        os.getenv("RABBIT_PASS")
    )
    pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBIT_HOST"),
            credentials=creds
        )
    )
    sys.exit(0)
except:
    sys.exit(1)
