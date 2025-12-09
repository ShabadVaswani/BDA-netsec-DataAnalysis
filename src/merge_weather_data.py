import pandas as pd
from datetime import datetime

# Read the input files
print("Reading garmin_health_complete.csv...")
garmin_df = pd.read_csv('c:/Users/shaba/Documents/Collage/BDA-netsec-DataAnalysis/output/garmin_health_complete.csv')

print("Reading weather_data_filtered.csv...")
weather_df = pd.read_csv('c:/Users/shaba/Documents/Collage/BDA-netsec-DataAnalysis/output/weather_data_filtered.csv')

# Convert datetime columns to datetime objects
garmin_df['datetime'] = pd.to_datetime(garmin_df['datetime'])
weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])

# Create a date-hour key for merging
garmin_df['merge_key'] = garmin_df['datetime'].dt.floor('H')
weather_df['merge_key'] = weather_df['datetime']

# Select only the weather columns we need
weather_columns = ['merge_key', 'temperature_celsius', 'rain_mm', 'cloud_cover_percent', 'wind_speed_kmh']
weather_subset = weather_df[weather_columns]

# Merge the dataframes
print("Merging data...")
merged_df = garmin_df.merge(weather_subset, on='merge_key', how='left')

# Drop the merge_key column as it's no longer needed
merged_df = merged_df.drop('merge_key', axis=1)

# Save the result
output_path = 'c:/Users/shaba/Documents/Collage/BDA-netsec-DataAnalysis/output/garmin_health_weather_complete.csv'
print(f"Saving to {output_path}...")
merged_df.to_csv(output_path, index=False)

print(f"Done! Created file with {len(merged_df)} rows")
print(f"Columns: {', '.join(merged_df.columns)}")

# Show a sample of the data
print("\nSample of merged data:")
print(merged_df.head(10))
