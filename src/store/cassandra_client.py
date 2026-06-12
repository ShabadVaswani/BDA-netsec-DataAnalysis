from pathlib import Path
from typing import Optional

import pandas as pd
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

from streaming.config import load_config


def get_session():
    config = load_config()
    cass_cfg = config.get("cassandra", {})
    hosts = cass_cfg.get("contactPoints", ["localhost"])
    port = cass_cfg.get("port", 9042)
    keyspace = cass_cfg.get("keyspace", "bda_streaming")
    cluster = Cluster(contact_points=hosts, port=port)
    session = cluster.connect()
    session.execute(f"CREATE KEYSPACE IF NOT EXISTS {keyspace} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}")
    session.set_keyspace(keyspace)
    session.row_factory = dict_factory
    return cluster, session, config


def run_schema():
    cluster, session, _ = get_session()
    try:
        schema_path = Path(__file__).with_name("cassandra_schema.cql")
        statements = schema_path.read_text(encoding="utf-8").split(";")
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                session.execute(stmt)
    finally:
        session.shutdown()
        cluster.shutdown()


def fetch_minute_features(limit: int = 50000, device_id: Optional[str] = None) -> pd.DataFrame:
    cluster, session, cfg = get_session()
    try:
        table = cfg.get("cassandra", {}).get("tables", {}).get("minuteFeatures", "minute_features_v1")
        if device_id:
            query = f"SELECT * FROM {table} WHERE device_id = %s ALLOW FILTERING LIMIT %s"
            rows = session.execute(query, [device_id, limit])
        else:
            query = f"SELECT * FROM {table} LIMIT {limit}"
            rows = session.execute(query)
        return pd.DataFrame(list(rows))
    finally:
        session.shutdown()
        cluster.shutdown()


def export_minute_features_csv(output_path: str, limit: int = 50000, device_id: Optional[str] = None) -> str:
    df = fetch_minute_features(limit=limit, device_id=device_id)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return str(out)
