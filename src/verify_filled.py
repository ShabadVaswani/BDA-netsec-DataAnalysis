import pandas as pd

df = pd.read_csv('output/garmin_health_filled.csv')

print("✅ Filled Garmin health data created")
print(f"  File: output/garmin_health_filled.csv")
print(f"  Total rows: {len(df):,}")
print(f"  Columns: {list(df.columns)}")

print(f"\nChecking for remaining missing values:")
has_missing = False
for col in df.columns:
    missing = df[col].isna().sum()
    if missing > 0:
        print(f"  {col}: {missing} missing")
        has_missing = True

if not has_missing:
    print("  ✓ No missing values found in any column!")

# Check numeric columns specifically
numeric_missing = df.select_dtypes(include=['number']).isna().sum().sum()
print(f"\nNumeric columns missing values: {numeric_missing}")

# Show sample of filled data
print(f"\nSample data (rows 5-10):")
print(df.iloc[5:10].to_string(index=False))
