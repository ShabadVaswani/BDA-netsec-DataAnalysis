import pandas as pd

# Load the file
df = pd.read_csv('output/garmin_health_complete.csv')

print("🔄 Converting total_steps to integer...")

# Convert total_steps to integer (Int64 allows NaN values)
df['total_steps'] = df['total_steps'].astype('Int64')

# Save back
df.to_csv('output/garmin_health_complete.csv', index=False)

print("✅ Conversion complete!")

print(f"\nData types:")
print(f"  total_steps: {df['total_steps'].dtype}")
print(f"  sleep_duration_hours: {df['sleep_duration_hours'].dtype}")

print(f"\nSample data:")
print(df[['datetime', 'total_steps', 'sleep_duration_hours']].head(10).to_string(index=False))

# Verify no decimals in steps
print(f"\nVerification:")
print(f"  All step values are integers: {df['total_steps'].dropna().apply(lambda x: x == int(x)).all()}")
