import pandas as pd

df = pd.read_csv('output/garmin_health_complete.csv')

print("🔍 Checking for steps and sleep data presence...\n")

# Check total_steps column
print("=" * 60)
print("STEPS DATA (total_steps column)")
print("=" * 60)

if 'total_steps' in df.columns:
    total_rows = len(df)
    non_null_steps = df['total_steps'].notna().sum()
    null_steps = df['total_steps'].isna().sum()
    
    print(f"✓ Column exists")
    print(f"  Total rows: {total_rows:,}")
    print(f"  Rows with step data: {non_null_steps:,} ({non_null_steps/total_rows*100:.1f}%)")
    print(f"  Rows without step data: {null_steps:,} ({null_steps/total_rows*100:.1f}%)")
    
    if non_null_steps > 0:
        print(f"\n  Step data statistics:")
        print(f"    Min: {df['total_steps'].min():.0f}")
        print(f"    Max: {df['total_steps'].max():.0f}")
        print(f"    Average: {df['total_steps'].mean():.0f}")
        
        print(f"\n  Sample rows with step data:")
        sample = df[df['total_steps'].notna()][['datetime', 'date', 'total_steps']].head(5)
        print(sample.to_string(index=False))
    else:
        print("\n  ❌ No step data found!")
else:
    print("❌ Column 'total_steps' not found!")

# Check sleep_duration_hours column
print("\n" + "=" * 60)
print("SLEEP DATA (sleep_duration_hours column)")
print("=" * 60)

if 'sleep_duration_hours' in df.columns:
    total_rows = len(df)
    non_null_sleep = df['sleep_duration_hours'].notna().sum()
    null_sleep = df['sleep_duration_hours'].isna().sum()
    
    print(f"✓ Column exists")
    print(f"  Total rows: {total_rows:,}")
    print(f"  Rows with sleep data: {non_null_sleep:,} ({non_null_sleep/total_rows*100:.1f}%)")
    print(f"  Rows without sleep data: {null_sleep:,} ({null_sleep/total_rows*100:.1f}%)")
    
    if non_null_sleep > 0:
        print(f"\n  Sleep data statistics:")
        print(f"    Min: {df['sleep_duration_hours'].min():.2f} hours")
        print(f"    Max: {df['sleep_duration_hours'].max():.2f} hours")
        print(f"    Average: {df['sleep_duration_hours'].mean():.2f} hours")
        
        print(f"\n  Sample rows with sleep data:")
        sample = df[df['sleep_duration_hours'].notna()][['datetime', 'date', 'sleep_duration_hours']].head(5)
        print(sample.to_string(index=False))
    else:
        print("\n  ❌ No sleep data found!")
else:
    print("❌ Column 'sleep_duration_hours' not found!")

# Check unique dates with data
print("\n" + "=" * 60)
print("DATE COVERAGE")
print("=" * 60)

df['date'] = pd.to_datetime(df['date'])
unique_dates = df['date'].dt.date.unique()
print(f"Total unique dates in file: {len(unique_dates)}")

if 'total_steps' in df.columns:
    dates_with_steps = df[df['total_steps'].notna()]['date'].dt.date.unique()
    print(f"Dates with step data: {len(dates_with_steps)}")

if 'sleep_duration_hours' in df.columns:
    dates_with_sleep = df[df['sleep_duration_hours'].notna()]['date'].dt.date.unique()
    print(f"Dates with sleep data: {len(dates_with_sleep)}")
