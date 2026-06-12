import argparse
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

from streaming.config import load_config


def build_session(app_name: str, master: str, cassandra_host: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master(master)
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
            "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1",
        )
        .config("spark.cassandra.connection.host", cassandra_host)
        .getOrCreate()
    )


def main():
    parser = argparse.ArgumentParser(description="Spark streaming fusion job")
    parser.add_argument("--master", default=None)
    args = parser.parse_args()

    cfg = load_config()
    spark_cfg = cfg.get("spark", {})
    cass_cfg = cfg.get("cassandra", {})
    kafka_cfg = cfg.get("kafka", {})
    topics = kafka_cfg.get("topics", {})
    kafka_brokers = ",".join(kafka_cfg.get("brokers", ["localhost:9092"]))

    cassandra_hosts = cass_cfg.get("contactPoints", ["localhost"])

    spark = build_session(
        app_name=spark_cfg.get("appName", "BDAStreamingFusion"),
        master=args.master or spark_cfg.get("master", "local[*]"),
        cassandra_host=cassandra_hosts[0],
    )

    routersense_schema = StructType(
        [
            StructField("source", StringType(), True),
            StructField("date", StringType(), True),
            StructField("hour", IntegerType(), True),
            StructField("hour_str", StringType(), True),
            StructField("file_path", StringType(), True),
            StructField("row_count", IntegerType(), True),
            StructField("hash", StringType(), True),
            StructField("captured_at", StringType(), True),
        ]
    )
    garmin_schema = StructType(
        [
            StructField("source", StringType(), True),
            StructField("datetime", StringType(), True),
            StructField("heart_rate", DoubleType(), True),
            StructField("stress_level", DoubleType(), True),
            StructField("body_battery", DoubleType(), True),
            StructField("respiration_rate", DoubleType(), True),
            StructField("steps_per_minute", DoubleType(), True),
            StructField("calories_per_minute", DoubleType(), True),
            StructField("captured_at", StringType(), True),
        ]
    )
    weather_schema = StructType(
        [
            StructField("source", StringType(), True),
            StructField("datetime", StringType(), True),
            StructField("temperature_celsius", DoubleType(), True),
            StructField("humidity_percent", DoubleType(), True),
            StructField("precipitation_mm", DoubleType(), True),
            StructField("rain_mm", DoubleType(), True),
            StructField("snowfall_cm", DoubleType(), True),
            StructField("cloud_cover_percent", DoubleType(), True),
            StructField("wind_speed_kmh", DoubleType(), True),
            StructField("wind_direction_degrees", DoubleType(), True),
            StructField("surface_pressure_hpa", DoubleType(), True),
            StructField("captured_at", StringType(), True),
        ]
    )

    if not topics.get("routersenseRaw") or not topics.get("garminRaw") or not topics.get("weatherRaw"):
        raise ValueError("Kafka topic names are missing in config.json/config.example.json")

    routersense_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_brokers)
        .option("subscribe", topics["routersenseRaw"])
        .option("startingOffsets", "latest")
        .load()
        .selectExpr("CAST(value AS STRING) AS json")
    )
    routersense_df = (
        routersense_df.select(F.from_json("json", routersense_schema).alias("r"))
        .select("r.*")
        .withColumn("minute_ts", F.to_timestamp(F.concat_ws(" ", F.col("date"), F.concat(F.col("hour_str"), F.lit(":00:00")))))
    )

    garmin_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_brokers)
        .option("subscribe", topics["garminRaw"])
        .option("startingOffsets", "latest")
        .load()
        .selectExpr("CAST(value AS STRING) AS json")
    )
    garmin_df = (
        garmin_df.select(F.from_json("json", garmin_schema).alias("g"))
        .select("g.*")
        .withColumn("minute_ts", F.to_timestamp("datetime"))
    )

    weather_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_brokers)
        .option("subscribe", topics["weatherRaw"])
        .option("startingOffsets", "latest")
        .load()
        .selectExpr("CAST(value AS STRING) AS json")
    )
    weather_df = (
        weather_df.select(F.from_json("json", weather_schema).alias("w"))
        .select("w.*")
        .withColumn("minute_ts", F.to_timestamp("datetime"))
    )

    joined = (
        garmin_df.withWatermark("minute_ts", "2 hours")
        .join(
            weather_df.withWatermark("minute_ts", "2 hours"),
            on=["minute_ts"],
            how="left",
        )
        .join(
            routersense_df.withWatermark("minute_ts", "2 hours"),
            on=["minute_ts"],
            how="left",
        )
        .withColumn("device_id", F.lit("default_device"))
        .withColumn("day_bucket", F.to_date("minute_ts"))
        .withColumn("stress_rolling_mean_30", F.col("stress_level"))
        .withColumn("stress_volatility_30", F.lit(None).cast(DoubleType()))
        .withColumn(
            "stress_band",
            F.when(F.col("stress_level") >= 75, F.lit("high"))
            .when(F.col("stress_level") >= 40, F.lit("medium"))
            .otherwise(F.lit("low")),
        )
    )

    checkpoint_root = Path(spark_cfg.get("checkpointRoot", "output/streaming/checkpoints"))
    output_root = Path(cfg.get("paths", {}).get("streamingDir", "output/streaming"))

    csv_query = (
        joined.writeStream.outputMode("append")
        .format("csv")
        .option("path", str(output_root / "fused_minute"))
        .option("header", "true")
        .option("checkpointLocation", str(checkpoint_root / "csv"))
        .trigger(processingTime="30 seconds")
        .start()
    )

    cassandra_query = (
        joined.writeStream.outputMode("append")
        .format("org.apache.spark.sql.cassandra")
        .option("keyspace", cass_cfg.get("keyspace", "bda_streaming"))
        .option("table", cass_cfg.get("tables", {}).get("minuteFeatures", "minute_features_v1"))
        .option("checkpointLocation", str(checkpoint_root / "cassandra"))
        .trigger(processingTime="30 seconds")
        .start()
    )

    csv_query.awaitTermination()
    cassandra_query.awaitTermination()


if __name__ == "__main__":
    main()
