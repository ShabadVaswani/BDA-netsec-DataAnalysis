import pandas as pd
import os

FILE_1 = 'output/garmin_parsed/garmin_minute_health.csv'
FILE_2 = 'output/garmin_parsed/garmin_minute_health_activity.csv'
OUTPUT_FILE = 'output/garmin_parsed/garmin_minute_health_joined.csv'

def join_files():
    print("🔄 Joining Garmin CSV files...")
    
    if not os.path.exists(FILE_1) or not os.path.exists(FILE_2):
        print("❌ One or both input files missing.")
        return

    # Load files
    print(f"   Loading {FILE_1}...")
    df1 = pd.read_csv(FILE_1)
    df1['datetime'] = pd.to_datetime(df1['datetime'], utc=True)
    
    print(f"   Loading {FILE_2}...")
    df2 = pd.read_csv(FILE_2)
    df2['datetime'] = pd.to_datetime(df2['datetime'], utc=True)
    
    # Merge
    print("   Merging on datetime (outer join)...")
    # Suffixes: _old (from file 1), _new (from file 2)
    merged = pd.merge(df1, df2, on='datetime', how='outer', suffixes=('_old', '_new'))
    
    # Coalesce columns
    # Find all columns that have suffixes
    cols = [c.replace('_new', '') for c in merged.columns if c.endswith('_new')]
    
    print(f"   Coalescing {len(cols)} overlapping columns...")
    for col in cols:
        old_col = f"{col}_old"
        new_col = f"{col}_new"
        
        # Create combined column: prefer new, fallback to old
        merged[col] = merged[new_col].combine_first(merged[old_col])
        
        # Drop suffix columns
        merged.drop(columns=[old_col, new_col], inplace=True)
        
    # Sort by datetime
    merged.sort_values('datetime', inplace=True)
    
    # Save
    print(f"💾 Saving to {OUTPUT_FILE}...")
    merged.to_csv(OUTPUT_FILE, index=False)
    
    print("\n✅ Join Complete!")
    print(f"   Total Rows: {len(merged)}")
    print(f"   Columns: {', '.join(merged.columns)}")

if __name__ == "__main__":
    join_files()
