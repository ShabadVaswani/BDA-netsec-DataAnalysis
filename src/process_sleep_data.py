import pandas as pd
from datetime import datetime, timedelta

# File path
INPUT_FILE = 'data/garmin/sleep data extracted/garmin sleep data  - Sheet1.csv'
OUTPUT_FILE = 'data/garmin/sleep data extracted/garmin_sleep_data_processed.csv'

def parse_sleep_data():
    print(f"📂 Loading sleep data from {INPUT_FILE}...")
    
    # Load data
    df = pd.read_csv(INPUT_FILE)
    
    print(f"  Loaded {len(df)} rows")
    print(f"  Original columns: {list(df.columns)}")
    
    # Convert date to proper format (assuming 2025 for recent dates, 2024 for older)
    print("\n🔄 Processing dates and times...")
    
    def convert_date(date_str):
        """Convert 'Nov 5' format to '2025-11-05' format"""
        # Parse the date string
        date_obj = datetime.strptime(date_str + ' 2025', '%b %d %Y')
        return date_obj.strftime('%Y-%m-%d')
    
    def calculate_duration(bedtime_str, waketime_str, date_str):
        """Calculate sleep duration in hours"""
        # Parse times
        bed_time = datetime.strptime(bedtime_str, '%H:%M')
        wake_time = datetime.strptime(waketime_str, '%H:%M')
        
        # If wake time is earlier than bed time, it means we crossed midnight
        if wake_time.time() < bed_time.time():
            # Add a day to wake time
            wake_time += timedelta(days=1)
        
        # Calculate duration
        duration = wake_time - bed_time
        duration_hours = duration.total_seconds() / 3600
        
        return round(duration_hours, 2)
    
    # Process each row
    df['date'] = df['date'].apply(convert_date)
    df['sleep_duration_hours'] = df.apply(
        lambda row: calculate_duration(row['bedtime'], row['waketime'], row['date']), 
        axis=1
    )
    
    # Reorder columns
    df = df[['date', 'bedtime', 'waketime', 'sleep_duration_hours']]
    
    # Sort by date
    df = df.sort_values('date')
    
    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Processing Complete!")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  Total rows: {len(df)}")
    
    # Show statistics
    print(f"\n📊 Sleep Statistics:")
    print(f"  Average sleep duration: {df['sleep_duration_hours'].mean():.2f} hours")
    print(f"  Minimum sleep: {df['sleep_duration_hours'].min():.2f} hours")
    print(f"  Maximum sleep: {df['sleep_duration_hours'].max():.2f} hours")
    
    # Show sample
    print(f"\n📋 Sample data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    return df

if __name__ == "__main__":
    parse_sleep_data()
