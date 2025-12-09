import pandas as pd
import os

# Define file paths
garmin_weather_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_complete.csv'
routersense_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\routersense_minute_processed.csv'
output_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_inner.csv'

print("Loading Garmin health and weather data...")
garmin_df = pd.read_csv(garmin_weather_file)
print(f"Loaded {len(garmin_df)} rows from Garmin health weather file")

print("\nLoading RouterSense network data...")
routersense_df = pd.read_csv(routersense_file)
print(f"Loaded {len(routersense_df)} rows from RouterSense file")

# Convert datetime columns to datetime type for proper merging
garmin_df['datetime'] = pd.to_datetime(garmin_df['datetime'])
routersense_df['datetime'] = pd.to_datetime(routersense_df['datetime'])

print("\nMerging datasets on datetime (inner join - only keeping matching timestamps)...")
# Inner join to keep only rows that exist in BOTH datasets
merged_df = pd.merge(
    garmin_df,
    routersense_df[['datetime', 'total_data_bytes', 'total_upload_bytes', 'total_download_bytes', 'phone_active', 'remote_hostname']],
    on='datetime',
    how='inner'
)

print(f"\nMerged dataset has {len(merged_df)} rows")
print(f"Removed {len(garmin_df) - len(merged_df)} rows that were not in RouterSense data")
print(f"Columns: {', '.join(merged_df.columns)}")

# Save to output file
print(f"\nSaving merged data to {output_file}...")
merged_df.to_csv(output_file, index=False)
print("Done!")

# Display summary statistics
print("\n=== Summary Statistics ===")
print(f"Date range: {merged_df['date'].min()} to {merged_df['date'].max()}")
print(f"Total minutes with network data: {(merged_df['total_data_bytes'] > 0).sum()}")
print(f"Total minutes with phone active: {(merged_df['phone_active'] == 1).sum()}")
print(f"\nFirst few rows:")
print(merged_df.head())
