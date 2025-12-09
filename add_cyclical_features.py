import pandas as pd
import numpy as np

# 1. Load the Data
print("Loading data...")
df = pd.read_csv(r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\cleaned\health_net_features.csv')

print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# 2. Minute Encoding (period = 60)
print("\nCreating minute cyclical features...")
df['minute_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
df['minute_cos'] = np.cos(2 * np.pi * df['minute'] / 60)

# 3. Hour Encoding (period = 24)
print("Creating hour cyclical features...")
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# 4. Day Encoding
print("Creating day of week cyclical features...")
# Map day names to integers (Monday=0, Sunday=6)
day_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

df['day_numeric'] = df['day_of_week'].map(day_mapping)

# Create cyclical features (period = 7)
df['day_sin'] = np.sin(2 * np.pi * df['day_numeric'] / 7)
df['day_cos'] = np.cos(2 * np.pi * df['day_numeric'] / 7)

# 5. Weekend Flag
print("Creating weekend flag...")
df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)

# 6. Save the result
output_file = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\cleaned\health_net_features_1.csv'
print(f"\nSaving to {output_file}...")
df.to_csv(output_file, index=False)

print(f"\nFinal shape: {df.shape}")
print(f"\nNew columns added:")
print("  - minute_sin, minute_cos")
print("  - hour_sin, hour_cos")
print("  - day_numeric, day_sin, day_cos")
print("  - is_weekend")

# Display sample of the new features
print("\nSample of cyclical features:")
print(df[['hour', 'minute', 'day_of_week', 'hour_sin', 'hour_cos', 
         'minute_sin', 'minute_cos', 'day_sin', 'day_cos', 'is_weekend']].head(10))

print("\n✓ Processing complete!")
