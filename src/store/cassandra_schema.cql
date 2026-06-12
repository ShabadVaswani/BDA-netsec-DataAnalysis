CREATE KEYSPACE IF NOT EXISTS bda_streaming
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS bda_streaming.minute_features_v1 (
    device_id text,
    day_bucket date,
    minute_ts timestamp,
    heart_rate double,
    stress_level double,
    body_battery double,
    respiration_rate double,
    steps_per_minute double,
    calories_per_minute double,
    temperature_celsius double,
    humidity_percent double,
    precipitation_mm double,
    rain_mm double,
    snowfall_cm double,
    cloud_cover_percent double,
    wind_speed_kmh double,
    wind_direction_degrees double,
    surface_pressure_hpa double,
    row_count int,
    file_path text,
    stress_rolling_mean_30 double,
    stress_volatility_30 double,
    stress_band text,
    PRIMARY KEY ((device_id, day_bucket), minute_ts)
) WITH CLUSTERING ORDER BY (minute_ts ASC);

CREATE TABLE IF NOT EXISTS bda_streaming.weather_hourly_v1 (
    location_id text,
    day_bucket date,
    hour_ts timestamp,
    temperature_celsius double,
    humidity_percent double,
    precipitation_mm double,
    rain_mm double,
    snowfall_cm double,
    cloud_cover_percent double,
    wind_speed_kmh double,
    wind_direction_degrees double,
    surface_pressure_hpa double,
    PRIMARY KEY ((location_id, day_bucket), hour_ts)
) WITH CLUSTERING ORDER BY (hour_ts ASC);

CREATE TABLE IF NOT EXISTS bda_streaming.garmin_minute_v1 (
    device_id text,
    day_bucket date,
    minute_ts timestamp,
    heart_rate double,
    stress_level double,
    body_battery double,
    respiration_rate double,
    steps_per_minute double,
    calories_per_minute double,
    PRIMARY KEY ((device_id, day_bucket), minute_ts)
) WITH CLUSTERING ORDER BY (minute_ts ASC);

CREATE TABLE IF NOT EXISTS bda_streaming.routersense_hourly_v1 (
    device_id text,
    day_bucket date,
    hour_ts timestamp,
    row_count int,
    file_path text,
    hash text,
    PRIMARY KEY ((device_id, day_bucket), hour_ts)
) WITH CLUSTERING ORDER BY (hour_ts ASC);
