"""
Master Analysis Script
Run complete RouterSense + Garmin analysis pipeline
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from analyze_data import DataAnalyzer
from correlation_analysis import CorrelationAnalyzer

def main():
    print("\n" + "="*70)
    print("ROUTERSENSE + GARMIN FULL ANALYSIS")
    print("="*70)
    
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
