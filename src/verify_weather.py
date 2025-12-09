import pandas as pd

df = pd.read_csv('output/weather_data_hourly.csv')

print("✅ Weather data file created successfully!")
print(f"  File: output/weather_data_hourly.csv")
print(f"  Total hours: {len(df):,}")
print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
print(f"\nColumns:")
for col in df.columns:
    print(f"  - {col}")

print(f"\nSample data (first 5 rows):")
print(df.head()[['datetime', 'temperature_celsius', 'humidity_percent', 'precipitation_mm', 'wind_speed_kmh']].to_string(index=False))

print(f"\nData summary:")
print(f"  Temperature range: {df['temperature_celsius'].min():.1f}°C to {df['temperature_celsius'].max():.1f}°C")
print(f"  Humidity range: {df['humidity_percent'].min():.0f}% to {df['humidity_percent'].max():.0f}%")
print(f"  Total precipitation: {df['precipitation_mm'].sum():.1f} mm")
