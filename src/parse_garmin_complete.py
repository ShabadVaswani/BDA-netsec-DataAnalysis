import fitdecode
import pandas as pd
import os
import glob
from datetime import datetime, timedelta
import pytz

# Configuration
DATA_DIR = 'data/garmin'
OUTPUT_DIR = 'output/garmin_parsed'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'garmin_minute_health_activity.csv')
EST = pytz.timezone('US/Eastern')

def parse_wellness_file(file_path):
    """Parse a single WELLNESS.fit file and return lists of records."""
    respiration_data = []
    stress_data = []
    monitoring_data = []
    
    try:
        with fitdecode.FitReader(file_path) as fit:
            for frame in fit:
                if isinstance(frame, fitdecode.FitDataMessage):
                    # 1. Respiration Rate
                    if frame.name == 'respiration_rate':
                        record = {}
                        if frame.has_field('timestamp'):
                            record['timestamp'] = frame.get_value('timestamp')
                        if frame.has_field('respiration_rate'):
                            record['respiration_rate'] = frame.get_value('respiration_rate')
                        
                        if 'timestamp' in record and 'respiration_rate' in record:
                            respiration_data.append(record)

                    # 2. Stress Level & Body Battery
                    elif frame.name == 'stress_level':
                        record = {}
                        # Stress messages sometimes use stress_level_time instead of timestamp
                        if frame.has_field('stress_level_time'):
                            record['timestamp'] = frame.get_value('stress_level_time')
                        elif frame.has_field('timestamp'):
                            record['timestamp'] = frame.get_value('timestamp')
                            
                        if frame.has_field('stress_level_value'):
                            val = frame.get_value('stress_level_value')
                            # Filter invalid stress values
                            if val is not None and val <= 100:
                                record['stress_level'] = val
                            else:
                                record['stress_level'] = None
                                
                        if frame.has_field('body_battery'):
                            record['body_battery'] = frame.get_value('body_battery')
                            
                        if 'timestamp' in record:
                            stress_data.append(record)

                    # 3. Monitoring (Heart Rate, Steps, etc.)
                    elif frame.name == 'monitoring':
                        record = {}
                        if frame.has_field('timestamp'):
                            record['timestamp'] = frame.get_value('timestamp')
                            
                        if frame.has_field('heart_rate'):
                            record['heart_rate'] = frame.get_value('heart_rate')
                        
                        if frame.has_field('cycles'): # Steps are often 'cycles'
                            record['steps_cumulative'] = frame.get_value('cycles')
                        elif frame.has_field('steps'):
                            record['steps_cumulative'] = frame.get_value('steps')
                            
                        if frame.has_field('active_calories'):
                            record['calories_cumulative'] = frame.get_value('active_calories')
                            
                        if frame.has_field('distance'):
                            record['distance_meters_cumulative'] = frame.get_value('distance')
                            
                        if 'timestamp' in record:
                            monitoring_data.append(record)
                            
    except Exception as e:
        print(f"⚠️ Error parsing {file_path}: {e}")
        
    return respiration_data, stress_data, monitoring_data

def process_all_files():
    print(f"🚀 Starting Garmin Health Parsing (Python/fitdecode)")
    print(f"📂 Data Directory: {DATA_DIR}")
    
    # Find all WELLNESS.fit files
    fit_files = glob.glob(os.path.join(DATA_DIR, '**', '*WELLNESS.fit'), recursive=True)
    print(f"📄 Found {len(fit_files)} WELLNESS.fit files")
    
    all_respiration = []
    all_stress = []
    all_monitoring = []
    
    for i, file_path in enumerate(fit_files):
        if (i+1) % 10 == 0:
            print(f"   Processing file {i+1}/{len(fit_files)}...")
            
        resp, stress, monit = parse_wellness_file(file_path)
        all_respiration.extend(resp)
        all_stress.extend(stress)
        all_monitoring.extend(monit)
        
    print(f"\n📊 Extracted Records:")
    print(f"   - Respiration: {len(all_respiration)}")
    print(f"   - Stress: {len(all_stress)}")
    print(f"   - Monitoring: {len(all_monitoring)}")
    
    # Create DataFrames
    print("\n🔄 Merging and processing data...")
    
    df_resp = pd.DataFrame(all_respiration)
    if not df_resp.empty:
        df_resp = df_resp.drop_duplicates(subset='timestamp', keep='first')
        df_resp.set_index('timestamp', inplace=True)
        
    df_stress = pd.DataFrame(all_stress)
    if not df_stress.empty:
        df_stress = df_stress.drop_duplicates(subset='timestamp', keep='first')
        df_stress.set_index('timestamp', inplace=True)
        
    df_monit = pd.DataFrame(all_monitoring)
    if not df_monit.empty:
        df_monit = df_monit.drop_duplicates(subset='timestamp', keep='first')
        df_monit.set_index('timestamp', inplace=True)
        
    # Merge all dataframes on timestamp (outer join to keep all data)
    # Start with monitoring as base, join others
    combined = pd.DataFrame()
    
    dfs_to_merge = []
    if not df_monit.empty: dfs_to_merge.append(df_monit)
    if not df_stress.empty: dfs_to_merge.append(df_stress)
    if not df_resp.empty: dfs_to_merge.append(df_resp)
    
    if not dfs_to_merge:
        print("❌ No data extracted!")
        return
        
    combined = dfs_to_merge[0]
    for df in dfs_to_merge[1:]:
        combined = combined.join(df, how='outer', lsuffix='_dup')
        
    # Cleanup duplicate columns if any
    combined = combined.loc[:, ~combined.columns.str.endswith('_dup')]
    
    # Reset index to make timestamp a column
    combined.reset_index(inplace=True)
    
    # Convert to EST
    print("🕒 Converting timestamps to EST...")
    combined['datetime'] = pd.to_datetime(combined['timestamp'], utc=True).dt.tz_convert(EST)
    
    # Add time features
    combined['date'] = combined['datetime'].dt.date
    combined['time'] = combined['datetime'].dt.time
    combined['hour'] = combined['datetime'].dt.hour
    combined['minute'] = combined['datetime'].dt.minute
    combined['day_of_week'] = combined['datetime'].dt.day_name()
    
    # Calculate Deltas for cumulative metrics
    print("➗ Calculating per-minute deltas...")
    combined.sort_values('datetime', inplace=True)
    
    # Calculate deltas per day to avoid jumps between days
    combined['steps_per_minute'] = combined.groupby('date')['steps_cumulative'].diff().fillna(0)
    combined['calories_per_minute'] = combined.groupby('date')['calories_cumulative'].diff().fillna(0)
    
    # Clean up negative deltas (resets or errors)
    combined.loc[combined['steps_per_minute'] < 0, 'steps_per_minute'] = 0
    combined.loc[combined['calories_per_minute'] < 0, 'calories_per_minute'] = 0
    
    # Reorder columns
    cols = ['datetime', 'date', 'time', 'hour', 'minute', 'day_of_week', 
            'heart_rate', 'stress_level', 'body_battery', 'respiration_rate',
            'steps_cumulative', 'calories_cumulative', 'distance_meters_cumulative',
            'steps_per_minute', 'calories_per_minute']
            
    # Keep only columns that exist
    final_cols = [c for c in cols if c in combined.columns]
    combined = combined[final_cols]
    
    # Save
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Saved consolidated data to: {OUTPUT_FILE}")
    print(f"   Total Rows: {len(combined)}")
    print(f"   Columns: {', '.join(combined.columns)}")

if __name__ == "__main__":
    process_all_files()
