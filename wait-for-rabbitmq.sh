#!/bin/sh
# wait-for-rabbitmq.sh
# Waits for RabbitMQ to become available before starting the main application

# Host and port, with defaults
RABBIT_HOST="${RABBITMQ_HOST:-rabbitmq}"
RABBIT_PORT="${RABBITMQ_PORT:-5672}"

# Maximum retries and sleep interval
MAX_RETRIES=60
SLEEP_TIME=2

echo "⏳ Waiting for RabbitMQ at $RABBIT_HOST:$RABBIT_PORT..."

retry_count=0
# Loop until RabbitMQ is reachable
while ! nc -z "$RABBIT_HOST" "$RABBIT_PORT"; do
    retry_count=$((retry_count + 1))
    
    # Exit if maximum retries exceeded
    if [ "$retry_count" -ge "$MAX_RETRIES" ]; then
        echo "❌ RabbitMQ did not become ready after $MAX_RETRIES attempts."
        exit 1
    fi

    echo "Waiting for RabbitMQ... ($retry_count/$MAX_RETRIES)"
    sleep "$SLEEP_TIME"
done

echo "✅ RabbitMQ is up!"

# Execute the main command passed to the container
exec "$@"
