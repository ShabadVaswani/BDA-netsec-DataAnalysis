import pandas as pd
import pytz
import os

# Files
GARMIN_FILE = 'output/garmin_parsed/garmin_minute_health_joined.csv'
ROUTERSENSE_FILE = 'data/phone_overall_activities.csv'
OUTPUT_FILE = 'output/final_merged_dataset.csv'

# Timezone
EST = pytz.timezone('US/Eastern')

def merge_datasets():
    print("🚀 Starting Final Data Merge...")
    
    # 1. Load Garmin Data
    print(f"   Loading Garmin data: {GARMIN_FILE}")
    if not os.path.exists(GARMIN_FILE):
        print("❌ Garmin file not found!")
        return
        
    garmin_df = pd.read_csv(GARMIN_FILE)
    garmin_df['datetime'] = pd.to_datetime(garmin_df['datetime'], utc=True)
    print(f"   Garmin Rows: {len(garmin_df)}")
    
    # 2. Load RouterSense Data
    print(f"   Loading RouterSense data: {ROUTERSENSE_FILE}")
    if not os.path.exists(ROUTERSENSE_FILE):
        print("❌ RouterSense file not found!")
        return
        
    rs_df = pd.read_csv(ROUTERSENSE_FILE)
    
    # Convert Unix timestamp to datetime (UTC then EST)
    print("   Converting RouterSense timestamps...")
    rs_df['datetime'] = pd.to_datetime(rs_df['timestamp'], unit='s', utc=True).dt.tz_convert(EST)
    
    # Drop original timestamp column to avoid confusion, or keep it if needed
    # rs_df.drop(columns=['timestamp'], inplace=True)
    
    print(f"   RouterSense Rows: {len(rs_df)}")
    
    # 3. Merge
    print("   Merging datasets (Outer Join on datetime)...")
    # Ensure Garmin datetime is also EST for matching
    garmin_df['datetime'] = garmin_df['datetime'].dt.tz_convert(EST)
    
    merged = pd.merge(garmin_df, rs_df, on='datetime', how='outer', suffixes=('_garmin', '_rs'))
    
    # Sort
    merged.sort_values('datetime', inplace=True)
    
    # 4. Save
    print(f"💾 Saving to {OUTPUT_FILE}...")
    merged.to_csv(OUTPUT_FILE, index=False)
    
    print("\n✅ Merge Complete!")
    print(f"   Total Rows: {len(merged)}")
    print(f"   Columns: {', '.join(merged.columns)}")
    
    # Check for missing data alignment
    garmin_only = merged[merged['device_ip_address'].isna()]
    rs_only = merged[merged['heart_rate'].isna() & merged['device_ip_address'].notna()]
    
    print(f"\n📊 Alignment Stats:")
    print(f"   - Total Minutes: {len(merged)}")
    print(f"   - Garmin Only (No Network Data): {len(garmin_only)}")
    print(f"   - RouterSense Only (No Health Data): {len(rs_only)}")
    print(f"   - Overlapping Data: {len(merged) - len(garmin_only) - len(rs_only)}")

if __name__ == "__main__":
    merge_datasets()
