import pandas as pd

FILE = 'output/garmin_parsed/garmin_minute_health_activity.csv'

try:
    df = pd.read_csv(FILE)
    print(f"📊 Verifying: {FILE}")
    print(f"   Total Rows: {len(df)}")
    
    if 'respiration_rate' in df.columns:
        non_null = df['respiration_rate'].count()
        print(f"   Non-null Respiration Records: {non_null}")
        print(f"   Coverage: {(non_null / len(df) * 100):.1f}%")
        
        if non_null > 0:
            print("\n✅ SUCCESS: Respiration data found!")
            print(df[df['respiration_rate'].notna()][['datetime', 'respiration_rate']].head())
        else:
            print("\n❌ FAILURE: Respiration column exists but is empty.")
    else:
        print("\n❌ FAILURE: Respiration column missing.")
        
except Exception as e:
    print(f"❌ Error: {e}")
