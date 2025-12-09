import pandas as pd
import numpy as np

# File paths
input_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_inner_features.csv'
output_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_inner_features_cleaned.csv'

print("Loading dataset...")
df = pd.read_csv(input_file)
print(f"Loaded {len(df)} rows with {len(df.columns)} columns")

# Identify rolling window columns (the ones we added)
rolling_columns = [
    'stress_rolling_mean_30',
    'stress_volatility_30', 
    'battery_drain_rate_1hr',
    'screen_streak_minutes'
]

print("\n" + "="*60)
print("BEFORE BACKFILL - NaN Count:")
print("="*60)
for col in rolling_columns:
    nan_count = df[col].isna().sum()
    print(f"{col}: {nan_count} NaN values")

print(f"\nTotal NaN values across all rolling columns: {df[rolling_columns].isna().sum().sum()}")

# Apply backward fill (bfill) to rolling columns
print("\n" + "="*60)
print("Applying Backward Fill (bfill)...")
print("="*60)

for col in rolling_columns:
    # Backward fill - propagate first valid value backward
    df[col] = df[col].bfill()
    
    # For any remaining NaNs (edge cases), fill with 0
    df[col] = df[col].fillna(0)
    
    print(f"✓ Backfilled {col}")

print("\n" + "="*60)
print("AFTER BACKFILL - NaN Count:")
print("="*60)
for col in rolling_columns:
    nan_count = df[col].isna().sum()
    print(f"{col}: {nan_count} NaN values")

total_nans = df[rolling_columns].isna().sum().sum()
print(f"\nTotal NaN values across all rolling columns: {total_nans}")

# Verification check
if total_nans == 0:
    print("\n✅ SUCCESS: All NaN values have been filled!")
else:
    print(f"\n⚠️  WARNING: {total_nans} NaN values still remain")

# Show sample of first few rows to verify backfill worked
print("\n" + "="*60)
print("Sample of first 10 rows (rolling columns only):")
print("="*60)
print(df[['datetime'] + rolling_columns].head(10).to_string(index=False))

# Save cleaned dataset
print(f"\nSaving cleaned dataset to: {output_file}")
df.to_csv(output_file, index=False)
print("✅ File saved successfully!")

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print(f"Input file:  {input_file}")
print(f"Output file: {output_file}")
print(f"Total rows:  {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"NaN values remaining: {total_nans}")
print("="*60)
