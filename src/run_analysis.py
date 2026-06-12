"""
Master Analysis Script
Run complete RouterSense + Garmin analysis pipeline
"""

import sys
from pathlib import Path
import os
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from analyze_data import DataAnalyzer
from correlation_analysis import CorrelationAnalyzer
from store.cassandra_client import export_minute_features_csv

def main():
    print("\n" + "="*70)
    print("ROUTERSENSE + GARMIN FULL ANALYSIS")
    print("="*70)
    
    # Optional Cassandra export path for additive compatibility with existing analysis scripts.
    cassandra_enabled = os.getenv("BDA_USE_CASSANDRA", "0") == "1"
    if cassandra_enabled:
        export_path = "output/analysis_results/cassandra_minute_features.csv"
        try:
            exported = export_minute_features_csv(export_path, limit=200000)
            if Path(exported).exists():
                df = pd.read_csv(exported)
                print(f"  Cassandra export ready: {exported} ({len(df)} rows)")
        except Exception as exc:
            print(f"  ⚠ Cassandra export failed, continuing with CSV pipeline: {exc}")

    # Step 1: Load and merge data
    print("\n[1/2] Loading and merging data...")
    analyzer = DataAnalyzer(
        routersense_path='data/phone_overall_activities.csv',
        garmin_dir='data/garmin'
    )
    
    combined_df = analyzer.run_full_analysis()
    
    # Step 2: Correlation analysis and visualization
    print("\n[2/2] Running correlation analysis...")
    corr_analyzer = CorrelationAnalyzer()
    corr_analyzer.run_full_analysis()
    
    print("\n" + "="*70)
    print("COMPLETE ANALYSIS FINISHED")
    print("="*70)
    print("\n📊 Results:")
    print("  - Data: output/analysis_results/")
    print("  - Visualizations: output/visualizations/")
    print("\n✓ Analysis complete!")

if __name__ == "__main__":
    main()
