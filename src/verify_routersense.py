import pandas as pd

df = pd.read_csv('output/routersense_minute_processed.csv')

print("✓ Updated file created: output/routersense_minute_processed.csv")
print(f"  Total rows: {len(df):,}")
print(f"  Columns: {list(df.columns)}")
print(f"  Minutes with phone_active=1: {df['phone_active'].sum():,}")

# Find minutes that meet core criteria
active_core = df[(df['total_upload_bytes'] > 10240) & (df['total_download_bytes'] > 10240000)]
print(f"\n  Core active minutes (upload>10KB AND download>10MB): {len(active_core)}")

if len(active_core) > 0:
    print("\nExample showing phone_active propagation:")
    idx = active_core.index[0]
    sample = df.iloc[max(0, idx-2):min(len(df), idx+3)]
    print(sample[['datetime', 'total_upload_bytes', 'total_download_bytes', 'phone_active', 'remote_hostname']].to_string(index=False))
else:
    print("\nNo minutes meet the core criteria (upload>10KB AND download>10MB)")
    print("Showing first few rows with any data:")
    print(df[df['total_data_bytes'] > 0].head(5)[['datetime', 'total_upload_bytes', 'total_download_bytes', 'phone_active', 'remote_hostname']].to_string(index=False))
