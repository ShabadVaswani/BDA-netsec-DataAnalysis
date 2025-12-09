import pandas as pd
from datetime import datetime
import re

# File paths
INPUT_FILE = 'data/garmin/step data extracted/garmin step data - Sheet1.csv'
OUTPUT_FILE = 'data/garmin/step data extracted/garmin_step_data_processed.csv'

def parse_step_data():
    print(f"📂 Loading step data from {INPUT_FILE}...")
    
    # Load data
    df = pd.read_csv(INPUT_FILE)
    
    print(f"  Loaded {len(df)} rows")
    print(f"  Original columns: {list(df.columns)}")
    
    print("\n🔄 Processing dates and calculating total steps...")
    
    def convert_date(date_str):
        """Convert 'Nov 5' format to '2025-11-05' format"""
        date_obj = datetime.strptime(date_str + ' 2025', '%b %d %Y')
        return date_obj.strftime('%Y-%m-%d')
    
    def calculate_total_steps(percent_str):
        """
        Extract percentage and goal from string like '142% of 8,680'
        and calculate total steps
        """
        # Use regex to extract percentage and goal
        match = re.match(r'(\d+)% of ([\d,]+)', percent_str)
        if match:
            percentage = int(match.group(1))
            goal = int(match.group(2).replace(',', ''))
            
            # Calculate total steps
            total_steps = int((percentage / 100) * goal)
            return total_steps, goal, percentage
        return None, None, None
    
    # Process each row
    df['date'] = df['date'].apply(convert_date)
    
    # Extract steps, goal, and percentage
    step_data = df['percent of goal'].apply(calculate_total_steps)
    df['total_steps'] = step_data.apply(lambda x: x[0])
    df['step_goal'] = step_data.apply(lambda x: x[1])
    df['percent_of_goal'] = step_data.apply(lambda x: x[2])
    
    # Reorder columns
    df = df[['date', 'total_steps', 'step_goal', 'percent_of_goal']]
    
    # Sort by date
    df = df.sort_values('date')
    
    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Processing Complete!")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  Total rows: {len(df)}")
    
    # Show statistics
    print(f"\n📊 Step Statistics:")
    print(f"  Average steps: {df['total_steps'].mean():.0f}")
    print(f"  Minimum steps: {df['total_steps'].min()}")
    print(f"  Maximum steps: {df['total_steps'].max()}")
    print(f"  Average goal: {df['step_goal'].mean():.0f}")
    print(f"  Days meeting goal: {(df['percent_of_goal'] >= 100).sum()} out of {len(df)}")
    
    # Show sample
    print(f"\n📋 Sample data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    return df

if __name__ == "__main__":
    parse_step_data()
