# FROM python:3.11-slim

# WORKDIR /app

# # Install netcat inside the container
# RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["python", "processor/realtime_pipeline.py"]


FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  netcat-openbsd \
  dos2unix \
  && rm -rf /var/lib/apt/lists/*

# Copy project files into container
COPY . .

# Convert Windows line endings → Linux line endings (important for .sh files)
RUN dos2unix wait-for-rabbitmq.sh || true

# Make script executable
RUN chmod +x wait-for-rabbitmq.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command (can be overridden by docker-compose entrypoint)
CMD ["python"]

FROM python:3.11-slim

WORKDIR /app

# Install netcat inside the container
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "processor/realtime_pipeline.py"]
