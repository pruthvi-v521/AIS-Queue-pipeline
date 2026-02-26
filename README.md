# AIS Pipeline – Setup and Run Guide

## Overview

This project implements a real-time AIS (Automatic Identification System) data processing pipeline.

The system:

* Reads AIS CSV files
* Publishes messages to RabbitMQ
* Processes and enriches AIS data
* Stores cleaned results for downstream analysis
* Runs fully containerized using Docker Compose

No manual Python installation is required.

---

# Prerequisites

Install:

## 1. Docker Desktop

Mac / Windows: Docker Desktop
Linux: Docker Engine + Docker Compose

Verify:

docker --version
docker compose version

---

# Project Structure

Your project should look like this:

```

AIS-Queue-pipeline/
│
├── docker-compose.yml
├── Dockerfile
├── wait-for-rabbitmq.sh
├── requirements.txt
│
├── input/                ← REQUIRED (place CSV here)
├── outputs/              ← auto-created
│
├── ingest/
│   └── csv_to_queue.py
│
├── processor/
│   ├── realtime_pipeline.py
│   └── healthcheck.py
│
├── rem/
└── README.md

```
---

# IMPORTANT – Input Data Requirement

Before running the pipeline, you MUST place your AIS CSV file inside the `input/` folder.

Example:
```
input/
└── AIS_Klaipeda_From20250908_To20250909.csv
```

The ingest service automatically reads files from this folder and publishes them to RabbitMQ.

If this folder is empty:

* No messages will be produced
* Processor will appear idle
* No outputs will be generated

---

# First-Time Setup

## Step 1 — Clone repository
```
git clone <your-repo-url>
cd AIS-Queue-pipeline
```

---

## Step 2 — Add your CSV file

Create input folder if it doesn't exist:

mkdir input

Copy your AIS CSV:

cp your_file.csv input/

---

## Step 3 — Build containers
```
docker compose build
```
---

## Step 4 — Start the pipeline
```
docker compose up
```
Run in background:
```
docker compose up -d
```
---

# What Starts Automatically

When Docker starts, these services run:

| Service          | Purpose                             |
| ---------------- | ----------------------------------- |
| rabbitmq         | Message broker (durable queue)      |
| ingest           | Reads CSV → publishes messages      |
| processor        | Decodes + enriches + writes CSV     |
| anomaly-detector | Dummy service for modular extension |

---

# Monitoring

## View logs

Processor:
```
docker compose logs -f processor
```
RabbitMQ:
```
docker compose logs -f rabbitmq
```
---

# RabbitMQ Dashboard

Open:
```
http://localhost:15672
```
Credentials:
```
Username: ais
Password: aispass
```
You can:

* Inspect queues
* See message counts
* Monitor consumers

---

# Outputs

Processed results are written to:

outputs/

Example files:

* dynamic_position.csv
* voyage_info.csv
* navigation_aid.csv

---

# Health Checks

Check service status:
```
docker compose ps
```
Healthy services show:
```
healthy
```
---

# Metrics

Processor logs progress:

Processed 100 messages
Processed 200 messages

This confirms the pipeline is running correctly.

---

# Stop / Restart

Stop:
```
docker compose down
```
Remove volumes:
```
docker compose down -v
```
Restart:
```
docker compose up -d
```
---

# Adding New Services

The architecture is modular.

To add new components (analysis, collision detection, etc.), add a new service in docker-compose.yml:

my-service:
build: .
command: python analysis/service.py
depends_on:
- rabbitmq

Services can consume from the cleaned AIS queue.

---

# Troubleshooting

## Nothing happens

Check:

* CSV exists inside input/
* ingest logs show publishing
* processor logs show processing

## RabbitMQ issues

docker compose down -v
docker compose up --build

## No output files

Ensure messages are being processed in logs.

---

# Quick Start

mkdir input
copy your CSV into input/

docker compose build
docker compose up

Open:
```
http://localhost:15672
```
Pipeline should now be running.
