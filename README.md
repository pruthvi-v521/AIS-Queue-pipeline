# AIS Real-Time Processing Pipeline

## Overview

This project implements a **real-time AIS (Automatic Identification System) data processing pipeline**. The pipeline ingests AIS CSV data, decodes and enriches messages, and makes the processed data available for downstream analysis and visualization.

The system is fully containerized, supports modular microservices, and includes basic operational monitoring.

---

## Current Status

### Core Pipeline (Completed)
- **System Containerization & Orchestration**
  - All major components (ingest, processor, RabbitMQ) are containerized with Docker.
  - Docker Compose defines service dependencies, networking, and persistent storage for RabbitMQ.
  - Environment variables are configurable for development and deployment.

- **Stream Robustness & Fault Tolerance**
  - Durable RabbitMQ queues ensure messages are not lost.
  - Restart policies (`always` / `on-failure`) are applied to all services.
  - Temporary RabbitMQ downtime is handled using retry/wait scripts.

- **Metadata Enrichment & Pipeline Support**
  - AIS messages are enriched with `station_id` and `timestamp`.
  - Modular architecture is ready for future services (e.g., anomaly detection).

- **Monitoring & Health Metrics Logging**
  - Healthchecks implemented for RabbitMQ and processor containers.
  - Processor logs message counters every 100 messages to track throughput.

---

## Pipeline Flow Diagram

CSV Reader
   ↓
NMEA Message Ingestion
   ↓
[Deployment: Containerized Ingest Service] ✅
   ↓
RabbitMQ Queue (Durable, Persistent) ✅
   ↓
[Deployment: Queue Configuration, Fault Tolerance, Monitoring] ✅
   ↓
Realtime Processing Server ✅
   ↓
Decoding (pyais) ✅
   ↓
Splitting by msg_type ✅
   ↓
Normalization (REM Events) ✅
   ↓
[Deployment: Metadata Enrichment
 Station ID, Timestamps, Processing Stage] ✅
   ↓
Memory Cache ⚪
   ↓
Correlation Engine ⚪
   ↓
Cleaning / Filtering ✅
   ↓
[Deployment: Optional Quality Control Services
 Trajectory Prediction / Anomaly Detection (Infrastructure Support)] ✅
   ↓
Storage (PostgreSQL DB) ⚪
   ↓
[Deployment: Persistent Volumes, Backup, Environment Management] ✅
   ↓
Analysis Layer ⚪
   ↓
API Layer ⚪
   ↓
Frontend Visualization ⚪

# AIS Pipeline – Setup and Run Guide

This document explains how to set up and run the complete AIS real-time processing pipeline locally using Docker.

The system is fully containerized, so no manual Python installation or dependency setup is required.

---

# Prerequisites

Install the following:

## 1. Docker Desktop

* Mac / Windows: Docker Desktop
* Linux: Docker Engine + Docker Compose

Verify installation:

```bash
docker --version
docker compose version
```

---

# Project Structure (Expected)

```
AIS-Queue-pipeline/
│
├── docker-compose.yml
├── Dockerfile
├── wait-for-rabbitmq.sh
│
├── ingest/
│   └── csv_to_queue.py
│
├── processor/
│   ├── realtime_pipeline.py
│   └── healthcheck.py
│
├── outputs/          # auto-created (CSV outputs)
├── rem/              # metadata files (optional)
```

---

# First-Time Setup

## Step 1 — Clone repository

```bash
git clone <your-repo-url>
cd AIS-Queue-pipeline
```

---

## Step 2 — Build containers

Build images for ingest and processor:

```bash
docker compose build
```

---

## Step 3 — Start the pipeline

```bash
docker compose up
```

Run in background:

```bash
docker compose up -d
```

---

# What Starts Automatically

When Docker Compose starts, the following services run:

| Service          | Purpose                                     |
| ---------------- | ------------------------------------------- |
| rabbitmq         | Message broker with durable queues          |
| ingest           | Reads CSV and pushes AIS NMEA to queue      |
| processor        | Decodes, cleans, enriches, writes CSV       |
| anomaly-detector | Dummy optional module for future extensions |

---

# Monitoring

## View logs

Processor logs:

```bash
docker compose logs -f processor
```

RabbitMQ logs:

```bash
docker compose logs -f rabbitmq
```

---

## RabbitMQ Dashboard

Open in browser:

```
http://localhost:15672
```

Login credentials:

```
Username: ais
Password: aispass
```

From the dashboard you can:

* Inspect queues
* Monitor message counts
* Check consumers

---

# Output Files

Processed CSV files are written to:

```
./outputs/
```

Examples:

```
dynamic_position.csv
voyage_info.csv
navigation_aid.csv
```

---

# Restart and Stop

Stop services:

```bash
docker compose down
```

Stop and remove volumes:

```bash
docker compose down -v
```

Restart:

```bash
docker compose up -d
```

---

# Healthchecks

Check container health:

```bash
docker compose ps
```

Healthy services will display:

```
healthy
```

---

# Metrics

Processor logs throughput information:

```
Processed 100 messages
Processed 200 messages
```

This confirms:

* Messages are flowing
* Queue is working
* Processor is active

---

# Adding New Services (Optional)

To add new modules such as collision detection or analytics, add a new service in `docker-compose.yml`:

```yaml
my-service:
  build: .
  command: python analysis/service.py
  depends_on:
    - rabbitmq
```

Services can consume messages from:

```
cleaned_ais_queue
```

---

# Troubleshooting

## RabbitMQ not starting

```bash
docker compose down -v
docker compose up --build
```

## Processor stuck waiting

Check:

```bash
docker compose logs rabbitmq
```

## No CSV output

Ensure:

* ingest is publishing messages
* processor logs show message counts

---

# Quick Start

```bash
docker compose build
docker compose up
```

Then open:

```
http://localhost:15672
```

The pipeline should now be running.


