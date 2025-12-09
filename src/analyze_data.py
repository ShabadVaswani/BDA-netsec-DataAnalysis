"""
RouterSense and Garmin Data Analysis
Comprehensive analysis of phone network activity and health metrics
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 8)

class DataAnalyzer:
    def __init__(self, routersense_path, garmin_dir):
        """
        Initialize the analyzer with data paths
        
        Args:
            routersense_path: Path to phone_overall_activities.csv
            garmin_dir: Directory containing Garmin FIT files
        """
        self.routersense_path = Path(routersense_path)
        self.garmin_dir = Path(garmin_dir)
        self.output_dir = Path('output/analysis_results')
        self.viz_dir = Path('output/visualizations')
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir.mkdir(parents=True, exist_ok=True)
        
        self.routersense_df = None
        self.garmin_df = None
        self.combined_df = None
        
    def load_routersense_data(self):
        """Load and preprocess RouterSense data"""
        print("Loading RouterSense data...")
        
        # Load CSV
        df = pd.read_csv(self.routersense_path)
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Parse metadata JSON
        def parse_metadata(meta_str):
            try:
                meta = json.loads(meta_str)
                return meta.get('registered_domain', ''), meta.get('entity_name', '')
            except:
                return '', ''
        
        df[['domain', 'company']] = df['metadata_json'].apply(
            lambda x: pd.Series(parse_metadata(x))
        )
        
        # Calculate total bandwidth
        df['total_bytes'] = df['upload_byte_count'] + df['download_byte_count']
        df['total_packets'] = df['upload_packet_count'] + df['download_packet_count']
        
        print(f"✓ Loaded {len(df):,} network activity records")
        print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")
        print(f"  Unique domains: {df['domain'].nunique()}")
        print(f"  Unique companies: {df['company'].nunique()}")
        
        self.routersense_df = df
        return df
    
    def aggregate_routersense_hourly(self):
        """Aggregate RouterSense data to hourly metrics"""
        print("\nAggregating RouterSense data to hourly...")
        
        df = self.routersense_df
        
        # Aggregate by hour
        hourly = df.groupby(df['datetime'].dt.floor('H')).agg({
            'upload_byte_count': 'sum',
            'download_byte_count': 'sum',
            'total_bytes': 'sum',
            'upload_packet_count': 'sum',
            'download_packet_count': 'sum',
            'total_packets': 'sum',
            'remote_hostname': 'count'  # Number of connections
        }).reset_index()
        
        hourly.columns = ['datetime', 'upload_bytes', 'download_bytes', 'total_bytes',
                         'upload_packets', 'download_packets', 'total_packets', 
                         'connection_count']
        
        # Convert bytes to MB for readability
        hourly['upload_mb'] = hourly['upload_bytes'] / 1e6
        hourly['download_mb'] = hourly['download_bytes'] / 1e6
        hourly['total_mb'] = hourly['total_bytes'] / 1e6
        
        print(f"✓ Aggregated to {len(hourly)} hourly records")
        
        return hourly
    
    def load_garmin_data(self):
        """Load and parse Garmin FIT files"""
        print("\nLoading Garmin data...")
        
        # Check if parsed data already exists
        parsed_dir = Path('output/garmin_parsed')
        
        if not parsed_dir.exists() or not list(parsed_dir.glob('*.json')):
            print("⚠ No parsed Garmin data found in output/garmin_parsed/")
            print("  Please run: node src/parse_garmin_fit.js")
            return None
        
        # Load all parsed JSON files
        all_data = []
        
        for json_file in parsed_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Extract records based on file type
                if 'wellness' in json_file.name.lower():
                    records = data.get('records', [])
                elif 'monitoring' in json_file.name.lower():
                    records = data.get('monitoring_records', [])
                else:
                    records = data.get('records', [])
                
                all_data.extend(records)
            except Exception as e:
                print(f"  Warning: Could not load {json_file.name}: {e}")
        
        if not all_data:
            print("⚠ No Garmin records found")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'])
        
        print(f"✓ Loaded {len(df):,} Garmin records")
        print(f"  Columns: {', '.join(df.columns)}")
        
        self.garmin_df = df
        return df
    
    def aggregate_garmin_hourly(self):
        """Aggregate Garmin data to hourly averages"""
        print("\nAggregating Garmin data to hourly...")
        
        df = self.garmin_df
        
        if df is None or len(df) == 0:
            print("⚠ No Garmin data to aggregate")
            return None
        
        # Define aggregation based on available columns
        agg_dict = {}
        
        if 'heart_rate' in df.columns:
            agg_dict['heart_rate'] = 'mean'
        if 'stress_level' in df.columns:
            agg_dict['stress_level'] = 'mean'
        if 'body_battery' in df.columns:
            agg_dict['body_battery'] = 'mean'
        if 'steps' in df.columns:
            agg_dict['steps'] = 'sum'
        if 'calories' in df.columns:
            agg_dict['calories'] = 'sum'
        if 'distance' in df.columns:
            agg_dict['distance'] = 'sum'
        
        if not agg_dict:
            print("⚠ No recognized health metrics found")
            return None
        
        # Aggregate by hour
        hourly = df.groupby(df['datetime'].dt.floor('H')).agg(agg_dict).reset_index()
        
        print(f"✓ Aggregated to {len(hourly)} hourly records")
        print(f"  Metrics: {', '.join(agg_dict.keys())}")
        
        return hourly
    
    def merge_datasets(self, routersense_hourly, garmin_hourly):
        """Merge RouterSense and Garmin data on datetime"""
        print("\nMerging datasets...")
        
        if garmin_hourly is None:
            print("⚠ Cannot merge: No Garmin data available")
            print("  Proceeding with RouterSense data only")
            self.combined_df = routersense_hourly
            return routersense_hourly
        
        # Merge on datetime
        combined = pd.merge(
            routersense_hourly, 
            garmin_hourly, 
            on='datetime', 
            how='inner'
        )
        
        # Add time features
        combined['hour'] = combined['datetime'].dt.hour
        combined['day_of_week'] = combined['datetime'].dt.dayofweek
        combined['is_weekend'] = combined['day_of_week'].isin([5, 6])
        combined['date'] = combined['datetime'].dt.date
        
        print(f"✓ Merged dataset: {len(combined)} records")
        print(f"  Date range: {combined['datetime'].min()} to {combined['datetime'].max()}")
        
        # Save combined dataset
        output_path = self.output_dir / 'combined_hourly.csv'
        combined.to_csv(output_path, index=False)
        print(f"✓ Saved to: {output_path}")
        
        self.combined_df = combined
        return combined
    
    def generate_summary_stats(self):
        """Generate summary statistics"""
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        
        if self.combined_df is None:
            print("⚠ No combined data available")
            return
        
        df = self.combined_df
        
        print("\nNetwork Usage:")
        print(f"  Total data: {df['total_mb'].sum():.2f} MB")
        print(f"  Avg per hour: {df['total_mb'].mean():.2f} MB")
        print(f"  Peak hour: {df['total_mb'].max():.2f} MB")
        print(f"  Avg connections/hour: {df['connection_count'].mean():.0f}")
        
        if 'stress_level' in df.columns:
            print("\nHealth Metrics:")
            print(f"  Avg stress: {df['stress_level'].mean():.1f}")
            print(f"  Max stress: {df['stress_level'].max():.1f}")
            
        if 'heart_rate' in df.columns:
            print(f"  Avg heart rate: {df['heart_rate'].mean():.1f} BPM")
            print(f"  Max heart rate: {df['heart_rate'].max():.1f} BPM")
        
        if 'body_battery' in df.columns:
            print(f"  Avg body battery: {df['body_battery'].mean():.1f}")
        
        # Save summary
        summary_path = self.output_dir / 'summary_statistics.txt'
        with open(summary_path, 'w') as f:
            f.write(df.describe().to_string())
        print(f"\n✓ Detailed stats saved to: {summary_path}")
    
    def analyze_top_domains(self):
        """Analyze top domains by bandwidth"""
        print("\nAnalyzing top domains...")
        
        df = self.routersense_df
        
        # Top domains by total bandwidth
        top_domains = df.groupby('domain').agg({
            'total_bytes': 'sum',
            'upload_byte_count': 'sum',
            'download_byte_count': 'sum',
            'remote_hostname': 'count'
        }).sort_values('total_bytes', ascending=False).head(20)
        
        top_domains['total_mb'] = top_domains['total_bytes'] / 1e6
        top_domains['upload_mb'] = top_domains['upload_byte_count'] / 1e6
        top_domains['download_mb'] = top_domains['download_byte_count'] / 1e6
        top_domains.columns = ['total_bytes', 'upload_bytes', 'download_bytes', 
                               'connections', 'total_mb', 'upload_mb', 'download_mb']
        
        print("\nTop 10 Domains by Bandwidth:")
        print(top_domains[['total_mb', 'connections']].head(10))
        
        # Save
        output_path = self.output_dir / 'top_domains.csv'
        top_domains.to_csv(output_path)
        print(f"✓ Saved to: {output_path}")
        
        return top_domains
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline"""
        print("\n" + "="*70)
        print("STARTING FULL ANALYSIS")
        print("="*70)
        
        # Load data
        self.load_routersense_data()
        routersense_hourly = self.aggregate_routersense_hourly()
        
        garmin_df = self.load_garmin_data()
        garmin_hourly = self.aggregate_garmin_hourly() if garmin_df is not None else None
        
        # Merge
        self.merge_datasets(routersense_hourly, garmin_hourly)
        
        # Analysis
        self.generate_summary_stats()
        self.analyze_top_domains()
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"\nResults saved to: {self.output_dir}")
        
        return self.combined_df


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = DataAnalyzer(
        routersense_path='data/phone_overall_activities.csv',
        garmin_dir='data/garmin'
    )
    
    # Run analysis
    combined_df = analyzer.run_full_analysis()
    
    print("\n✓ Analysis complete! Check output/analysis_results/ for results")
