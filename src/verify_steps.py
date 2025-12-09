import pandas as pd

df = pd.read_csv('data/garmin/step data extracted/garmin_step_data_processed.csv')

print("✅ Step data processed successfully")
print(f"  File: garmin_step_data_processed.csv")
print(f"  Total rows: {len(df)}")

print(f"\nColumns: {list(df.columns)}")

print(f"\n📊 Step Statistics:")
print(f"  Average steps: {df['total_steps'].mean():.0f}")
print(f"  Minimum steps: {df['total_steps'].min()}")
print(f"  Maximum steps: {df['total_steps'].max()}")
print(f"  Average goal: {df['step_goal'].mean():.0f}")
print(f"  Days meeting goal (≥100%): {(df['percent_of_goal'] >= 100).sum()} out of {len(df)}")

print(f"\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

print(f"\nLast 5 rows:")
print(df.tail(5).to_string(index=False))
