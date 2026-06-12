import argparse

from store.cassandra_client import export_minute_features_csv


def main():
    parser = argparse.ArgumentParser(description="Export Cassandra minute features to CSV")
    parser.add_argument("--output", default="output/streaming/exports/minute_features_v1.csv")
    parser.add_argument("--limit", type=int, default=50000)
    parser.add_argument("--device-id", default=None)
    args = parser.parse_args()

    output_path = export_minute_features_csv(
        output_path=args.output,
        limit=args.limit,
        device_id=args.device_id,
    )
    print(f"Exported Cassandra minute features to: {output_path}")


if __name__ == "__main__":
    main()
