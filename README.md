# AIS Pipeline – Setup and Run Guide

## Overview

This project implements a real-time AIS (Automatic Identification System) data 
processing pipeline.

The system:

* Reads AIS CSV files
* Publishes messages to RabbitMQ
* Processes and enriches AIS data
* Stores cleaned results for downstream analysis
* Creates a PostgreSQL database
* Exposes the database using API
* Captures everything on the frontend
* Runs fully containerized using Docker Compose

No manual Python installation is required.

---

# Prerequisites

Install:

## 1. Docker Desktop

Mac / Windows: Docker Desktop
Linux: Docker Engine + Docker Compose

Verify:
```
docker --version
docker compose version
```

## 2. Python (3.11 recommended)

Mac (using Homebrew):
```
brew install python@3.11
```
Windows: Download from https://www.python.org/downloads/

Verify:
```
python --version
```

---

# First-Time Setup

## Step 1 — Clone repository
```
git clone <your-repo-url>
cd AIS-Queue-pipeline
```

---

## Step 2 — Create and activate Python virtual environment

Mac / Linux:
```
python3 -m venv venv
source venv/bin/activate
```

Windows:
```
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt confirming 
the environment is active.

---

## Step 3 — Install Python dependencies
```
pip install -r requirements.txt
```

---

## Step 4 — Add your CSV file

Create input folder if it doesn't exist:
```
mkdir input
```

Copy your AIS CSV:
```
cp your_file.csv input/
```

Example:
```
input/
└── AIS_Klaipeda_From20250908_To20250909.csv
```

The ingest service automatically reads files from this folder and publishes 
them to RabbitMQ.

If this folder is empty:

* No messages will be produced
* Processor will appear idle
* No outputs will be generated

---

# Project Structure

Your project should look like this:
```
AIS-Q-Pipeline
├── api/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── monitoring.py
│   │   │   ├── positions.py
│   │   │   └── vessels.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── __pycache__/
│
├── frontend/
│   ├── streamlit_app.py
│   ├── api_client.py
│   └── __pycache__/
│
├── ingest/
│   └── csv_to_queue.py
│
├── processor/
│   └── (processing scripts)
│
├── input/
│   └── (raw input files)
│
├── outputs/
│   └── (generated outputs)
│
├── rem/
│   └── (misc or archived files)
│
├── docker-compose.yml
├── Dockerfile
├── environment.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

# IMPORTANT – Input Data Requirement

Before running the pipeline, you MUST place your AIS CSV file inside 
the `input/` folder.

Example:
```
input/
└── AIS_Klaipeda_From20250908_To20250909.csv
```

---

On Terminal 1:

## Step 5 — Build containers
```
docker compose build
```

---

## Step 6 — Start the pipeline
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

On Terminal 2:

1. Run the PostgreSQL database
2. Run the API with commands:
```
cd api
uvicorn app.main:app --reload
```

---

On Terminal 3:

Run the frontend with commands:
```
cd frontend
streamlit run streamlit_app.py
```

---

# Outputs

Processed results are written to:
```
outputs/
```

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
```
Processed 100 messages
Processed 200 messages
```

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

To add new components (analysis, collision detection, etc.), add a new 
service in docker-compose.yml:
```
my-service:
  build: .
  command: python analysis/service.py
  depends_on:
    - rabbitmq
```

Services can consume from the cleaned AIS queue.

---

# Troubleshooting

## Virtual environment not activated

If you see `ModuleNotFoundError` when running the API or frontend locally, 
make sure your virtual environment is active:

Mac / Linux:
```
source venv/bin/activate
```

Windows:
```
venv\Scripts\activate
```

Then reinstall dependencies:
```
pip install -r requirements.txt
```

## Nothing happens

Check:

* CSV exists inside input/
* ingest logs show publishing
* processor logs show processing

## RabbitMQ issues
```
docker compose down -v
docker compose up --build
```

## No output files

Ensure messages are being processed in logs.

---

# Quick Start
```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

mkdir input
cp your_file.csv input/

docker compose build
docker compose up
```

Open:
```
http://localhost:15672
```

Pipeline should now be running.
