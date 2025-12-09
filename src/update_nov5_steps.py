import pandas as pd

# Load the file
df = pd.read_csv('output/garmin_health_complete.csv')

# Convert date column to datetime for comparison
df['date'] = pd.to_datetime(df['date'])

# Update total_steps for November 5, 2025
target_date = pd.to_datetime('2025-11-05').date()
mask = df['date'].dt.date == target_date

# Count how many rows will be updated
rows_to_update = mask.sum()

print(f"🔄 Updating steps for November 5, 2025...")
print(f"  Rows to update: {rows_to_update:,}")

# Update the steps
df.loc[mask, 'total_steps'] = 8625

# Save back
df.to_csv('output/garmin_health_complete.csv', index=False)

print(f"\n✅ Update complete!")
print(f"  All {rows_to_update:,} minutes on 2025-11-05 now have total_steps = 8,625")

# Verify
verification = df[mask][['datetime', 'date', 'total_steps']].head(5)
print(f"\nVerification (first 5 rows from Nov 5):")
print(verification.to_string(index=False))
