import pandas as pd

# File paths
HEALTH_FILE = 'output/garmin_health_filled.csv'
STEPS_FILE = 'data/garmin/step data extracted/garmin_step_data_processed.csv'
SLEEP_FILE = 'data/garmin/sleep data extracted/garmin_sleep_data_processed.csv'
OUTPUT_FILE = 'output/garmin_health_complete.csv'

def merge_daily_data():
    print("📂 Loading data files...")
    
    # Load minute-level health data
    health_df = pd.read_csv(HEALTH_FILE)
    health_df['datetime'] = pd.to_datetime(health_df['datetime'])
    health_df['date'] = health_df['datetime'].dt.date
    print(f"  Health data: {len(health_df):,} rows")
    
    # Load daily step data
    steps_df = pd.read_csv(STEPS_FILE)
    steps_df['date'] = pd.to_datetime(steps_df['date']).dt.date
    print(f"  Step data: {len(steps_df)} days")
    
    # Load daily sleep data
    sleep_df = pd.read_csv(SLEEP_FILE)
    sleep_df['date'] = pd.to_datetime(sleep_df['date']).dt.date
    print(f"  Sleep data: {len(sleep_df)} days")
    
    print("\n🔄 Merging daily data into minute-level records...")
    
    # Merge steps (left join to keep all health records)
    health_df = health_df.merge(
        steps_df[['date', 'total_steps']], 
        on='date', 
        how='left'
    )
    
    # Merge sleep (left join to keep all health records)
    health_df = health_df.merge(
        sleep_df[['date', 'sleep_duration_hours']], 
        on='date', 
        how='left'
    )
    
    # Drop the temporary date column (keep original date column from health data)
    # Reorder columns to put new data at the end
    cols = [col for col in health_df.columns if col not in ['total_steps', 'sleep_duration_hours']]
    cols.extend(['total_steps', 'sleep_duration_hours'])
    health_df = health_df[cols]
    
    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    health_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Merge Complete!")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  Total rows: {len(health_df):,}")
    print(f"  Columns: {list(health_df.columns)}")
    
    # Check coverage
    print(f"\n📊 Data Coverage:")
    print(f"  Minutes with step data: {health_df['total_steps'].notna().sum():,} ({health_df['total_steps'].notna().sum()/len(health_df)*100:.1f}%)")
    print(f"  Minutes with sleep data: {health_df['sleep_duration_hours'].notna().sum():,} ({health_df['sleep_duration_hours'].notna().sum()/len(health_df)*100:.1f}%)")
    
    # Show sample
    print(f"\n📋 Sample data (first 10 rows):")
    sample_cols = ['datetime', 'heart_rate', 'stress_level', 'body_battery', 'total_steps', 'sleep_duration_hours']
    print(health_df[sample_cols].head(10).to_string(index=False))
    
    return health_df

if __name__ == "__main__":
    merge_daily_data()
