import pandas as pd

# Load the filled data
df = pd.read_csv('output/garmin_health_filled.csv')

print("🔄 Rounding health metrics to integers...")

# Columns that should be integers
cols_to_round = ['heart_rate', 'stress_level', 'body_battery']

for col in cols_to_round:
    if col in df.columns:
        # Round to nearest integer
        df[col] = df[col].round().astype('Int64')
        print(f"  ✓ Rounded {col}")

# Save back to the same file
df.to_csv('output/garmin_health_filled.csv', index=False)

print(f"\n✅ File updated: output/garmin_health_filled.csv")
print(f"\nSample data (showing integer values):")
print(df[['datetime', 'heart_rate', 'stress_level', 'body_battery']].head(10).to_string(index=False))

# Verify no decimals
print(f"\nVerification:")
for col in cols_to_round:
    if col in df.columns:
        print(f"  {col} data type: {df[col].dtype}")
