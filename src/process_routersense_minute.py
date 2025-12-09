import pandas as pd
import pytz
from datetime import datetime, timedelta

# Configuration
INPUT_FILE = 'data/phone_overall_activities.csv'
OUTPUT_FILE = 'output/routersense_minute_processed.csv'
EST = pytz.timezone('US/Eastern')

def process_routersense_to_minute():
    print(f"📂 Loading RouterSense data from {INPUT_FILE}...")
    
    # Load data
    df = pd.read_csv(INPUT_FILE)
    
    # Convert Unix timestamp to datetime (EST)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).dt.tz_convert(EST).dt.tz_localize(None)
    
    # Floor to minute
    df['minute'] = df['datetime'].dt.floor('min')
    
    print(f"   Loaded {len(df):,} records")
    print(f"   Time range: {df['datetime'].min()} to {df['datetime'].max()}")
    
    # Aggregate by minute
    print("\n🔄 Aggregating to minute-level...")
    
    # Group by minute and aggregate
    minute_agg = df.groupby('minute').agg({
        'upload_byte_count': 'sum',
        'download_byte_count': 'sum',
        'remote_hostname': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]  # Most frequent hostname
    }).reset_index()
    
    # Calculate total data exchanged (in bytes)
    minute_agg['total_data_bytes'] = minute_agg['upload_byte_count'] + minute_agg['download_byte_count']
    
    # Determine if phone is active (upload > 10 KB AND download > 10,000 KB = 10 MB)
    # 10 KB = 10,240 bytes, 10 MB = 10,240,000 bytes
    minute_agg['phone_active_core'] = (
        (minute_agg['upload_byte_count'] > 10240) & 
        (minute_agg['download_byte_count'] > 10240000)
    ).astype(int)
    
    # Rename minute to datetime
    minute_agg.rename(columns={'minute': 'datetime'}, inplace=True)
    
    # Create a complete minute range from start to end
    print("\n📅 Creating complete minute range...")
    start_time = minute_agg['datetime'].min()
    end_time = minute_agg['datetime'].max()
    
    # Generate all minutes in range (timezone-naive)
    all_minutes = pd.date_range(start=start_time, end=end_time, freq='min')
    complete_df = pd.DataFrame({'datetime': all_minutes})
    
    # Merge with aggregated data (left join to keep all minutes)
    result = complete_df.merge(minute_agg, on='datetime', how='left')
    
    # Fill missing values
    result['upload_byte_count'] = result['upload_byte_count'].fillna(0).astype(int)
    result['download_byte_count'] = result['download_byte_count'].fillna(0).astype(int)
    result['total_data_bytes'] = result['total_data_bytes'].fillna(0).astype(int)
    result['phone_active_core'] = result['phone_active_core'].fillna(0).astype(int)
    result['remote_hostname'] = result['remote_hostname'].fillna('')
    
    # Expand phone_active to include minute before and after
    # Use rolling window to check if any of the 3 minutes (prev, current, next) are active
    result['phone_active'] = result['phone_active_core'].rolling(window=3, center=True, min_periods=1).max().astype(int)
    
    # Drop the temporary core column
    result.drop(columns=['phone_active_core'], inplace=True)
    
    # Add time components
    result['date'] = result['datetime'].dt.date
    result['time'] = result['datetime'].dt.time
    result['hour'] = result['datetime'].dt.hour
    result['minute'] = result['datetime'].dt.minute
    result['day_of_week'] = result['datetime'].dt.day_name()
    
    # Reorder columns
    result = result[[
        'datetime', 'date', 'time', 'hour', 'minute', 'day_of_week',
        'total_data_bytes', 'upload_byte_count', 'download_byte_count', 
        'phone_active', 'remote_hostname'
    ]]
    
    # Rename for clarity
    result.rename(columns={
        'upload_byte_count': 'total_upload_bytes',
        'download_byte_count': 'total_download_bytes'
    }, inplace=True)
    
    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    result.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Processing Complete!")
    print(f"   Total minutes: {len(result):,}")
    print(f"   Minutes with activity: {(result['total_data_bytes'] > 0).sum():,}")
    print(f"   Minutes with phone active: {result['phone_active'].sum():,}")
    print(f"   Date range: {result['date'].min()} to {result['date'].max()}")
    
    # Show sample
    print(f"\n📊 Sample rows:")
    print(result.head(10).to_string(index=False))

if __name__ == "__main__":
    process_routersense_to_minute()
