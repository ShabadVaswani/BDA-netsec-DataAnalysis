# Kafka + Spark + Cassandra Streaming Stack

This guide adds a non-destructive local streaming layer on top of the existing CSV pipeline.

## Non-Destructive Rule

- Existing data and outputs remain untouched.
- New streaming outputs are additive and written under `output/streaming/`.
- Existing scripts and CSV paths remain valid fallback behavior.

## Services

The stack is defined in `docker-compose.yml`:

- Kafka (KRaft mode): `localhost:9092`
- Cassandra: `localhost:9042`
- Spark Master UI: `http://localhost:8080`
- Spark Worker UI: `http://localhost:8081`

## First-Time Setup

1. Install dependencies:
   - `npm install`
   - `pip install -r requirements.txt`

2. Copy config:
   - `copy config.example.json config.json` (Windows PowerShell)
   - Update device IDs/paths as needed.

3. Start services:
   - `npm run stack:up`

4. Initialize Cassandra schema:
   - `python src/store/init_cassandra.py`

## Streaming Flow

1. Produce events from existing ingestion scripts:
   - RouterSense: `npm run stream:routersense -- 2025-11-18 2025-11-18`
   - Garmin: `npm run stream:garmin`
   - Weather: `npm run stream:weather`

2. Run Spark fusion job:
   - `python src/spark/stream_fusion.py`
   - In containerized tools profile:
     - `docker compose --profile tools run --rm spark-submit python src/spark/stream_fusion.py --master spark://spark-master:7077`

3. Export fused rows from Cassandra (optional, additive CSV):
   - `python src/store/export_cassandra.py --output output/streaming/exports/minute_features_v1.csv`

## Cassandra-Backed Consumers (Fallback Preserved)

These scripts can export from Cassandra first when `BDA_USE_CASSANDRA=1`, then continue with CSV processing:

- `src/run_analysis.py`
- `AEON wellness index/5_aeon_wellness_dashboard.py`
- `LSTM model/create_lstm_sequences.py`
- `EXO-model/bio_exclusive_vae.py`

Example (PowerShell):

```powershell
$env:BDA_USE_CASSANDRA="1"
python src/run_analysis.py
```

## Smoke Test Checklist

1. `docker compose config` succeeds.
2. `python -m compileall src`
3. `python src/store/init_cassandra.py`
4. Publish a small weather batch and verify no file deletions occurred in `data/` or `output/`.
5. Run export command and verify `output/streaming/exports/minute_features_v1.csv` exists.

## Shutdown

- `npm run stack:down`
