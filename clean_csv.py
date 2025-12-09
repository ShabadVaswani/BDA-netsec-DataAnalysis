import pandas as pd
import os

# Read the original CSV
input_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\output\garmin_health_weather_network_inner_features_cleaned.csv'
df = pd.read_csv(input_file)

# Remove specified columns
columns_to_remove = ['steps_of_day', 'remote_hostname']
df_cleaned = df.drop(columns=columns_to_remove)

# Create a new folder for cleaned data if it doesn't exist
output_folder = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\cleaned'
os.makedirs(output_folder, exist_ok=True)

# Save with a shorter name
output_file = os.path.join(output_folder, 'health_net_features.csv')
df_cleaned.to_csv(output_file, index=False)

print(f"Original shape: {df.shape}")
print(f"New shape: {df_cleaned.shape}")
print(f"Removed columns: {columns_to_remove}")
print(f"\nFile saved to: {output_file}")
print(f"Columns in new file: {list(df_cleaned.columns)}")
