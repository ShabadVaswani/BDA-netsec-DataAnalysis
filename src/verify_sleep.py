import pandas as pd

df = pd.read_csv('data/garmin/sleep data extracted/garmin_sleep_data_processed.csv')

print("✅ Sleep data processed successfully")
print(f"  File: garmin_sleep_data_processed.csv")
print(f"  Total rows: {len(df)}")

print(f"\nColumns: {list(df.columns)}")

print(f"\nSleep Statistics:")
print(f"  Average: {df['sleep_duration_hours'].mean():.2f} hours")
print(f"  Min: {df['sleep_duration_hours'].min():.2f} hours")
print(f"  Max: {df['sleep_duration_hours'].max():.2f} hours")

print(f"\nFirst 5 rows:")
print(df.head().to_string(index=False))

print(f"\nLast 5 rows:")
print(df.tail().to_string(index=False))
