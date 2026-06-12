from store.cassandra_client import run_schema


def main():
    run_schema()
    print("Cassandra schema initialized.")


if __name__ == "__main__":
    main()
