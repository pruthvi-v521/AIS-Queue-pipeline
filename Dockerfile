FROM python:3.11-slim

WORKDIR /app

# Install netcat inside the container
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "processor/realtime_pipeline.py"]
