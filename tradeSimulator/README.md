# Trade Simulator

The Trade Simulator sub-project simulates real-time trade data flow, allowing you to either insert trades directly into a database (such as SingleStore) or send them to Kafka. This is useful for performance testing, load generation, or general integration testing of downstream systems.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Running the Simulator](#running-the-simulator)
- [Modes of Operation](#modes-of-operation)
- [Logging](#logging)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

This sub-project reads trade data from a CSV file (or downloads it from SingleStore if not found), samples trades at a specified rate, and sends them to either a database or Kafka. This simulates a real-time trades environment, helping you test and evaluate how downstream systems handle incoming trade data.

## Features

- **Dynamic Configuration:** Use environment variables to configure database, Kafka, throughput, and more.
- **Throughput Control:** A rate limiter ensures trades are sent at a controlled rate.
- **Database Insertion:** Insert trades directly into SingleStore (or other supported SQL databases) in batches.
- **Kafka Production:** Send trades as JSON messages to a Kafka topic for stream processing.
- **Logging & Retry:** Comprehensive logging and retry mechanisms ensure resilience and observability.

## Project Structure

```
tradeSimulator/
├─ __init__.py
├─ config.py
├─ db_handler.py
├─ kafka_producer.py
├─ logger_config.py
├─ producer.py
├─ simulator.py
├─ utils.py
├─ tests/
│  ├─ __init__.py
│  ├─ test_config.py
│  ├─ test_db_handler.py
│  ├─ test_kafka_producer.py
│  ├─ test_logger_config.py
│  ├─ test_producer.py
│  ├─ test_simulator.py
│  └─ test_utils.py
└─ requirements.txt
```

**Key Files:**
- **config.py:** Configuration from environment variables.
- **db_handler.py:** Handles batch insertion into SingleStore.
- **kafka_producer.py:** Kafka producer client implementation.
- **producer.py:** Provides interfaces to Routes between DB and Kafka producers.
- **simulator.py:** Main entry point that loads data, simulates trades, and sends them out.
- **utils.py:** Utility classes/functions for data loading, rate limiting, etc.

## Prerequisites

- **Python 3.9+** (Recommended)
- **pip** for installing dependencies
- **SingleStore or Another Database** (if using "db" mode)
- **Kafka Broker** (if using "kafka" mode)
- **.env file** with the necessary environment variables.

## Configuration

Set environment variables in a `.env` file in `tradeSimulator/`. Key variables include:

- **Log Level:** `LOG_LEVEL=INFO`
- **Database URL:** `SINGLESTORE_DB_URL=mysql://user:password@host/db`
- **Kafka Broker & Topic:** `KAFKA_BROKER=localhost:9092`, `KAFKA_TOPIC=trades`
- **Throughput:** `THROUGHPUT=1000` (trades per second)
- **Mode:** `MODE=db` or `MODE=kafka`
- **Batch Size:** `BATCH_SIZE=1000`
- **Local CSV Path:** `LOCAL_CSV_PATH=./trades_data.csv`

Example `.env`:
```env
LOG_LEVEL=INFO
SINGLESTORE_DB_URL=mysql://user:password@host:3306/mydatabase
THROUGHPUT=500
MODE=db
BATCH_SIZE=1000
NUM_THREADS=8
LOCAL_CSV_PATH=./trades_data.csv
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=trades
```

## Running the Simulator

1. **Install Dependencies:**
   ```bash
   cd tradeSimulator
   pip install -r requirements.txt
   ```

2. **Check Configuration:**
   Ensure `.env` is properly set. Make sure SingleStore (or your chosen DB) and/or Kafka are running and accessible.

3. **Run the Simulator:**
   ```bash
   python simulator.py
   ```

   The simulator will start sending trades at the configured throughput. If `MODE=db`, trades are inserted into the database. If `MODE=kafka`, trades are published to Kafka.

## Modes of Operation

- **DB Mode:**  
  Set `MODE=db` to insert trades directly into the `live_trades` table in SingleStore.
  
- **Kafka Mode:**  
  Set `MODE=kafka` to send trades to the configured Kafka topic.

## Logging

Logs are printed to `stdout` by default. The log level can be set via `LOG_LEVEL` in `.env`. For debugging, use `DEBUG`. For production, `INFO` or `WARN` is recommended.

## Testing

Run tests with:
```bash
pytest --maxfail=1 --disable-warnings -v
```

Before running tests, ensure you have a test environment configured or mock the necessary services.

## Troubleshooting

- **NaN in 'conditions' Column:**  
  The simulator replaces `NaN` values in `conditions` with empty strings. If issues persist, inspect your data and configuration.

- **Database Connectivity Issues:**  
  Check `SINGLESTORE_DB_URL` and ensure the database is reachable. Verify credentials.

- **Kafka Connectivity Issues:**  
  Ensure your Kafka broker is running and `KAFKA_BROKER` is correct.

- **Performance Adjustments:**  
  Tweak `THROUGHPUT`, `BATCH_SIZE`, or `NUM_THREADS` to optimize performance.
