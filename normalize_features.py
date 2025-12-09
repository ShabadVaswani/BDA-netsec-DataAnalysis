import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

# 1. Load the Data
print("Loading data...")
df = pd.read_csv(r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\cleaned\health_net_features_1.csv')

print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# 2. Define Features
# Columns to exclude from scaling
exclude_columns = ['datetime', 'date', 'time', 'hour', 'minute', 'day_of_week', 'day_numeric']

# Features to scale (all numerical columns except excluded ones)
feature_columns = [
    'heart_rate', 'stress_level', 'body_battery', 'sleep_duration_of_day',
    'temperature_celsius', 'rain_mm', 'cloud_cover_percent', 'wind_speed_kmh',
    'total_data_bytes', 'total_upload_bytes', 'total_download_bytes', 'phone_active',
    'stress_rolling_mean_30', 'stress_volatility_30', 'battery_drain_rate_1hr',
    'screen_streak_minutes', 'minute_sin', 'minute_cos', 'hour_sin', 'hour_cos',
    'day_sin', 'day_cos', 'is_weekend'
]

print(f"\nFeatures to scale ({len(feature_columns)}): {feature_columns}")

# 3. Apply Scaling
print("\nApplying StandardScaler (Z-Score Normalization)...")
scaler = StandardScaler()

# Fit and transform the feature columns
scaled_features = scaler.fit_transform(df[feature_columns])

# Create a DataFrame with scaled features
scaled_df = pd.DataFrame(scaled_features, columns=feature_columns, index=df.index)

# 4. Save the Scaler
scaler_path = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\cleaned\health_net_features_2_scalar.pkl'
print(f"\nSaving scaler to: {scaler_path}")
joblib.dump(scaler, scaler_path)
print("✓ Scaler saved successfully!")

# 5. Save the Data
# Combine non-feature columns with scaled feature columns
final_df = pd.concat([df[exclude_columns], scaled_df], axis=1)

output_path = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\data\cleaned\health_net_features_2_normalize.csv'
print(f"\nSaving normalized data to: {output_path}")
final_df.to_csv(output_path, index=False)
print("✓ Normalized data saved successfully!")

# 6. Verify
print("\n" + "="*80)
print("VERIFICATION: First 5 rows of normalized features")
print("="*80)
print("\nOriginal values (before scaling):")
print(df[feature_columns].head())

print("\nNormalized values (after scaling - should be roughly between -2 and 2):")
print(scaled_df.head())

print("\n" + "="*80)
print("Statistics of normalized features:")
print("="*80)
print(scaled_df.describe())

print("\n✓ Processing complete!")
print(f"\nFiles created:")
print(f"  1. Scaler: {scaler_path}")
print(f"  2. Normalized data: {output_path}")
print(f"\nFinal shape: {final_df.shape}")
