FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy everything
COPY . .

# Fix shell script line endings
RUN dos2unix wait-for-rabbitmq.sh || true
RUN chmod +x wait-for-rabbitmq.sh

# Install Python deps (ALL services share same env)
RUN pip install --no-cache-dir -r requirements.txt
