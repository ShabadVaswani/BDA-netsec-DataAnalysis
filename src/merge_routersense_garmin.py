import pandas as pd
import os

# Define file paths
garmin_weather_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_complete.csv'
routersense_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\processed\netsecfulldata\routersense_minute_processed.csv'
output_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_complete.csv'

print("Loading Garmin health and weather data...")
garmin_df = pd.read_csv(garmin_weather_file)
print(f"Loaded {len(garmin_df)} rows from Garmin health weather file")

print("\nLoading RouterSense network data...")
routersense_df = pd.read_csv(routersense_file)
print(f"Loaded {len(routersense_df)} rows from RouterSense file")

# Convert datetime columns to datetime type for proper merging
garmin_df['datetime'] = pd.to_datetime(garmin_df['datetime'])
routersense_df['datetime'] = pd.to_datetime(routersense_df['datetime'])

print("\nMerging datasets on datetime (left join to keep only Garmin timestamps)...")
# Left join to keep only rows that exist in garmin_df
merged_df = pd.merge(
    garmin_df,
    routersense_df[['datetime', 'total_data_bytes', 'total_upload_bytes', 'total_download_bytes', 'phone_active', 'remote_hostname']],
    on='datetime',
    how='left'
)

# Fill NaN values with 0 for numeric columns and empty string for remote_hostname
merged_df['total_data_bytes'] = merged_df['total_data_bytes'].fillna(0).astype(int)
merged_df['total_upload_bytes'] = merged_df['total_upload_bytes'].fillna(0).astype(int)
merged_df['total_download_bytes'] = merged_df['total_download_bytes'].fillna(0).astype(int)
merged_df['phone_active'] = merged_df['phone_active'].fillna(0).astype(int)
merged_df['remote_hostname'] = merged_df['remote_hostname'].fillna('')

print(f"\nMerged dataset has {len(merged_df)} rows")
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
