# Lakekeeper Parallel Write Issue Demonstration

This project demonstrates a parallel write issue in Lakekeeper, where the API returns a 500 error instead of 409 when multiple threads attempt to write simultaneously to the same Iceberg table.

## Problem Demonstrated

When executed with multiple workers (`--workers > 1`), Lakekeeper may return HTTP 500 error instead of the expected 409 (Conflict) error for concurrent writes. This indicates a problem in handling parallel write conflicts.

## How to Reproduce

### Execution that works (1 worker)

```bash
lakekeeper-ingest sample_data.csv --workers 1
```

### Execution that demonstrates the problem (multiple workers)

```bash
lakekeeper-ingest sample_data.csv --workers 2
```

## Prerequisites

- Docker and Docker Compose
- Running Lakekeeper server (included in docker-compose.yml)

## Quick Start

### 1. Build and Start Services

```bash
docker compose up -d
```

This will start:

- Lakekeeper server
- PostgreSQL database
- MinIO object storage
- Ingestion container (ready for manual execution)

### 2. Access the Ingestion Container

```bash
docker compose exec lakekeeper-ingestion bash
```

### 3. Demonstrate the Problem

Inside the container, execute:

#### Test with 1 worker (should work)

```bash
lakekeeper-ingest sample_data.csv --workers 1
```

#### Test with multiple workers (may fail with 500 error)

```bash
lakekeeper-ingest sample_data.csv --workers 2
```

## Command Options

- `--workers`: Number of parallel workers (default: 2)
  - Use `1` for normal operation
  - Use `>1` to demonstrate the concurrency problem
- `--chunk-size`: Number of rows per chunk (default: 1000)

## Expected vs Actual Behavior

### Expected Behavior

- With 1 worker: Success
- With multiple workers: 409 (Conflict) error for concurrent writes

### Current Behavior (Bug)

- With 1 worker: Success
- With multiple workers: 500 (Internal Server Error)

## Data Generation

The project now generates sample data at runtime instead of using a static CSV file. The data includes:

- Unique IDs
- User names
- Random ages
- Salaries with normal distribution
- Departments
- Active/inactive status
- Creation timestamps

## Project Structure

```sh
├── src/
│   ├── main.py           # Main CLI
│   ├── ingestion.py      # Ingestion logic
│   └── data_generator.py # Sample data generation
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Dockerfile for the ingestion container
├── README.md             # This file
└── sample_data.csv       # Sample data
```

## Configuration

Available environment variables:

- `CATALOG_URL`: Lakekeeper catalog URL (default: http://localhost:8181/catalog)
- `WAREHOUSE`: Warehouse name (default: demo)
- `CATALOG_NAME`: Catalog name (default: my_catalog)
- `CATALOG_TOKEN`: Authentication token (default: dummy)
- `NAMESPACE`: Table namespace (default: default)
- `TABLE_NAME`: Table name (default: sample_table)
