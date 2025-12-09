import pandas as pd
import numpy as np

# Load the data
input_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_inner.csv'
output_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_inner_features.csv'

print("Loading data...")
df = pd.read_csv(input_file)
print(f"Loaded {len(df)} rows")

# Convert datetime to proper datetime type
df['datetime'] = pd.to_datetime(df['datetime'])

# Sort by datetime to ensure proper order
df = df.sort_values('datetime').reset_index(drop=True)

print("\nCalculating derived features...")

# 1. stress_rolling_mean_30: Rolling mean of stress_level over last 30 minutes
print("  - Calculating stress_rolling_mean_30...")
df['stress_rolling_mean_30'] = df['stress_level'].rolling(window=30, min_periods=1).mean()

# 2. stress_volatility_30: Standard deviation of stress_level over last 30 minutes
print("  - Calculating stress_volatility_30...")
df['stress_volatility_30'] = df['stress_level'].rolling(window=30, min_periods=1).std()

# 3. battery_drain_rate_1hr: How fast body_battery is changing over last hour (60 minutes)
print("  - Calculating battery_drain_rate_1hr...")
# Calculate the difference in body_battery over the last 60 minutes
# Positive value = draining, Negative value = charging
df['battery_drain_rate_1hr'] = df['body_battery'].diff(periods=60) * -1  # Multiply by -1 so positive = drain

# 4. screen_streak_minutes: Consecutive minutes where phone_active = 1
print("  - Calculating screen_streak_minutes...")
# Create a grouping variable that changes when phone_active changes
df['phone_active_group'] = (df['phone_active'] != df['phone_active'].shift()).cumsum()

# For each group where phone_active = 1, calculate the cumulative count
df['screen_streak_minutes'] = 0
active_mask = df['phone_active'] == 1
df.loc[active_mask, 'screen_streak_minutes'] = df[active_mask].groupby('phone_active_group').cumcount() + 1

# Drop the temporary grouping column
df = df.drop('phone_active_group', axis=1)

print("\nFeature calculation complete!")
print("\nNew columns added:")
print("  - stress_rolling_mean_30: Rolling mean of stress over 30 minutes")
print("  - stress_volatility_30: Standard deviation of stress over 30 minutes")
print("  - battery_drain_rate_1hr: Body battery drain rate over 1 hour (positive = draining)")
print("  - screen_streak_minutes: Consecutive minutes of phone activity")

# Display sample statistics
print("\n" + "="*60)
print("Sample Statistics:")
print("="*60)
print(f"\nstress_rolling_mean_30:")
print(f"  Mean: {df['stress_rolling_mean_30'].mean():.2f}")
print(f"  Min: {df['stress_rolling_mean_30'].min():.2f}")
print(f"  Max: {df['stress_rolling_mean_30'].max():.2f}")

print(f"\nstress_volatility_30:")
print(f"  Mean: {df['stress_volatility_30'].mean():.2f}")
print(f"  Min: {df['stress_volatility_30'].min():.2f}")
print(f"  Max: {df['stress_volatility_30'].max():.2f}")

print(f"\nbattery_drain_rate_1hr:")
print(f"  Mean: {df['battery_drain_rate_1hr'].mean():.2f}")
print(f"  Min: {df['battery_drain_rate_1hr'].min():.2f}")
print(f"  Max: {df['battery_drain_rate_1hr'].max():.2f}")

print(f"\nscreen_streak_minutes:")
print(f"  Mean: {df['screen_streak_minutes'].mean():.2f}")
print(f"  Min: {df['screen_streak_minutes'].min():.0f}")
print(f"  Max: {df['screen_streak_minutes'].max():.0f}")

# Show a few example rows
print("\n" + "="*60)
print("Sample rows with new features:")
print("="*60)
sample_cols = ['datetime', 'stress_level', 'stress_rolling_mean_30', 'stress_volatility_30', 
               'body_battery', 'battery_drain_rate_1hr', 'phone_active', 'screen_streak_minutes']
print(df[sample_cols].head(100).to_string(index=False))

# Save to new file
print(f"\nSaving to {output_file}...")
df.to_csv(output_file, index=False)
print("Done!")
print(f"\nOutput file: {output_file}")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
