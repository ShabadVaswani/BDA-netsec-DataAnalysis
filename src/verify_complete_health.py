import pandas as pd

df = pd.read_csv('output/garmin_health_complete.csv')

print("✅ Complete health data file created")
print(f"  File: output/garmin_health_complete.csv")
print(f"  Total rows: {len(df):,}")

print(f"\nColumns ({len(df.columns)}):")
for col in df.columns:
    print(f"  - {col}")

print(f"\n📊 Data Coverage:")
print(f"  Minutes with step data: {df['total_steps'].notna().sum():,} ({df['total_steps'].notna().sum()/len(df)*100:.1f}%)")
print(f"  Minutes with sleep data: {df['sleep_duration_hours'].notna().sum():,} ({df['sleep_duration_hours'].notna().sum()/len(df)*100:.1f}%)")

print(f"\nSample data (showing new columns):")
sample_cols = ['datetime', 'date', 'heart_rate', 'stress_level', 'total_steps', 'sleep_duration_hours']
print(df[sample_cols].head(10).to_string(index=False))

# Check a specific day
print(f"\nExample: All minutes from 2025-11-05 have the same daily values:")
nov5 = df[df['date'] == '2025-11-05'][['datetime', 'total_steps', 'sleep_duration_hours']].head(5)
print(nov5.to_string(index=False))
