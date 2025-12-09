import pandas as pd
import numpy as np

# File paths
INPUT_FILE = 'data/processed/garminfulldata/health data- without  network data - garmin_minute_health_activity.csv.csv'
OUTPUT_FILE = 'output/garmin_health_filled.csv'

def fill_missing_values(df, column):
    """
    Fill missing values with average of nearest upper and lower values.
    If only one side is available, use that value.
    """
    # Create a copy of the column
    filled = df[column].copy()
    
    # Use interpolate with 'linear' method for middle values
    # This automatically averages between nearest neighbors
    filled = filled.interpolate(method='linear', limit_direction='both')
    
    # Forward fill for any remaining NaN at the start
    filled = filled.fillna(method='ffill')
    
    # Backward fill for any remaining NaN at the end
    filled = filled.fillna(method='bfill')
    
    return filled

def process_garmin_data():
    print(f"📂 Loading Garmin health data from {INPUT_FILE}...")
    
    # Load data
    df = pd.read_csv(INPUT_FILE)
    
    print(f"  Loaded {len(df):,} rows")
    print(f"  Columns: {list(df.columns)}")
    
    # Identify numeric columns that may have missing values
    # Exclude time-related columns
    time_columns = ['datetime', 'date', 'time', 'hour', 'minute', 'day_of_week']
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Columns to fill
    columns_to_fill = [col for col in numeric_columns if col not in time_columns]
    
    print(f"\n🔄 Filling missing values in {len(columns_to_fill)} columns...")
    
    # Track missing values before and after
    missing_before = {}
    missing_after = {}
    
    for col in columns_to_fill:
        missing_before[col] = df[col].isna().sum()
        if missing_before[col] > 0:
            print(f"  {col}: {missing_before[col]:,} missing values")
            df[col] = fill_missing_values(df, col)
            missing_after[col] = df[col].isna().sum()
    
    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Processing Complete!")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  Total rows: {len(df):,}")
    
    # Summary
    print(f"\n📊 Missing Values Summary:")
    total_filled = 0
    for col in columns_to_fill:
        if missing_before.get(col, 0) > 0:
            filled = missing_before[col] - missing_after.get(col, 0)
            total_filled += filled
            print(f"  {col}:")
            print(f"    Before: {missing_before[col]:,} missing")
            print(f"    After: {missing_after.get(col, 0):,} missing")
            print(f"    Filled: {filled:,} values")
    
    print(f"\n  Total values filled: {total_filled:,}")
    
    # Show sample
    print(f"\n📋 Sample data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    return df

if __name__ == "__main__":
    process_garmin_data()
