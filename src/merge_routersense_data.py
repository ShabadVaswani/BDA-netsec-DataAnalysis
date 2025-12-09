import pandas as pd
from datetime import datetime

# Read the input files
print("Reading garmin_health_weather_complete.csv...")
garmin_weather_df = pd.read_csv('c:/Users/shaba/Documents/Collage/BDA-netsec-DataAnalysis/output/garmin_health_weather_complete.csv')

print("Reading routersense_minute_processed.csv...")
routersense_df = pd.read_csv('c:/Users/shaba/Documents/Collage/BDA-netsec-DataAnalysis/data/processed/netsecfulldata/routersense_minute_processed.csv')

# Convert datetime columns to datetime objects
garmin_weather_df['datetime'] = pd.to_datetime(garmin_weather_df['datetime'])
routersense_df['datetime'] = pd.to_datetime(routersense_df['datetime'])

# Select only the RouterSense columns we need
routersense_columns = ['datetime', 'total_data_bytes', 'total_upload_bytes', 'total_download_bytes', 'phone_active', 'remote_hostname']
routersense_subset = routersense_df[routersense_columns]

# Merge the dataframes - left join to keep only Garmin dates/times
print("Merging data...")
merged_df = garmin_weather_df.merge(routersense_subset, on='datetime', how='left')

# Save the result
output_path = 'c:/Users/shaba/Documents/Collage/BDA-netsec-DataAnalysis/output/garmin_health_weather_network_complete.csv'
print(f"Saving to {output_path}...")
merged_df.to_csv(output_path, index=False)

print(f"Done! Created file with {len(merged_df)} rows")
print(f"Columns: {', '.join(merged_df.columns)}")

# Show a sample of the data
print("\nSample of merged data:")
print(merged_df.head(10))

# Show statistics about the merge
print(f"\nMerge statistics:")
print(f"Total rows: {len(merged_df)}")
print(f"Rows with network data: {merged_df['total_data_bytes'].notna().sum()}")
print(f"Rows without network data: {merged_df['total_data_bytes'].isna().sum()}")
