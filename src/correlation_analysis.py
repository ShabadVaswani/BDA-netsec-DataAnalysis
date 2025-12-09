"""
Correlation Analysis and Visualization
Analyze correlations between network usage and health metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CorrelationAnalyzer:
    def __init__(self, combined_data_path='output/analysis_results/combined_hourly.csv'):
        """Initialize with combined dataset"""
        self.data_path = Path(combined_data_path)
        self.viz_dir = Path('output/visualizations')
        self.viz_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = None
        
    def load_data(self):
        """Load combined dataset"""
        print("Loading combined dataset...")
        self.df = pd.read_csv(self.data_path)
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        print(f"✓ Loaded {len(self.df)} records")
        return self.df
    
    def calculate_correlations(self):
        """Calculate correlation matrix"""
        print("\nCalculating correlations...")
        
        # Select numeric columns for correlation
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # Focus on key metrics
        key_metrics = []
        for col in ['total_mb', 'connection_count', 'stress_level', 
                    'heart_rate', 'body_battery', 'steps']:
            if col in numeric_cols:
                key_metrics.append(col)
        
        if len(key_metrics) < 2:
            print("⚠ Not enough metrics for correlation analysis")
            return None
        
        # Calculate correlation matrix
        corr_matrix = self.df[key_metrics].corr()
        
        print("\nCorrelation Matrix:")
        print(corr_matrix)
        
        # Save
        output_path = Path('output/analysis_results/correlation_matrix.csv')
        corr_matrix.to_csv(output_path)
        print(f"✓ Saved to: {output_path}")
        
        return corr_matrix
    
    def plot_correlation_heatmap(self, corr_matrix):
        """Create correlation heatmap"""
        print("\nCreating correlation heatmap...")
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   fmt='.2f', square=True, linewidths=1,
                   cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix: Network Usage vs Health Metrics', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        output_path = self.viz_dir / 'correlation_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to: {output_path}")
        plt.close()
    
    def plot_time_series(self):
        """Create time series plots"""
        print("\nCreating time series plots...")
        
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        
        # Network usage
        axes[0].plot(self.df['datetime'], self.df['total_mb'], 
                    color='#2E86AB', linewidth=1.5)
        axes[0].set_title('Network Usage Over Time', fontweight='bold')
        axes[0].set_ylabel('Total MB')
        axes[0].grid(True, alpha=0.3)
        
        # Stress level
        if 'stress_level' in self.df.columns:
            axes[1].plot(self.df['datetime'], self.df['stress_level'], 
                        color='#A23B72', linewidth=1.5)
            axes[1].set_title('Stress Level Over Time', fontweight='bold')
            axes[1].set_ylabel('Stress (0-100)')
            axes[1].grid(True, alpha=0.3)
        
        # Heart rate
        if 'heart_rate' in self.df.columns:
            axes[2].plot(self.df['datetime'], self.df['heart_rate'], 
                        color='#F18F01', linewidth=1.5)
            axes[2].set_title('Heart Rate Over Time', fontweight='bold')
            axes[2].set_ylabel('BPM')
            axes[2].grid(True, alpha=0.3)
        
        # Body battery
        if 'body_battery' in self.df.columns:
            axes[3].plot(self.df['datetime'], self.df['body_battery'], 
                        color='#06A77D', linewidth=1.5)
            axes[3].set_title('Body Battery Over Time', fontweight='bold')
            axes[3].set_ylabel('Energy (0-100)')
            axes[3].set_xlabel('Date')
            axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.viz_dir / 'time_series_plots.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to: {output_path}")
        plt.close()
    
    def plot_scatter_correlations(self):
        """Create scatter plots for key correlations"""
        print("\nCreating scatter plots...")
        
        # Check which metrics are available
        has_stress = 'stress_level' in self.df.columns
        has_hr = 'heart_rate' in self.df.columns
        has_battery = 'body_battery' in self.df.columns
        
        num_plots = sum([has_stress, has_hr, has_battery])
        
        if num_plots == 0:
            print("⚠ No health metrics available for scatter plots")
            return
        
        fig, axes = plt.subplots(1, num_plots, figsize=(6*num_plots, 5))
        if num_plots == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # Network usage vs Stress
        if has_stress:
            axes[plot_idx].scatter(self.df['total_mb'], self.df['stress_level'], 
                                  alpha=0.5, color='#A23B72')
            axes[plot_idx].set_xlabel('Network Usage (MB)')
            axes[plot_idx].set_ylabel('Stress Level')
            axes[plot_idx].set_title('Network Usage vs Stress')
            axes[plot_idx].grid(True, alpha=0.3)
            
            # Add trend line
            z = np.polyfit(self.df['total_mb'].dropna(), 
                          self.df['stress_level'].dropna(), 1)
            p = np.poly1d(z)
            axes[plot_idx].plot(self.df['total_mb'], p(self.df['total_mb']), 
                               "r--", alpha=0.8, linewidth=2)
            plot_idx += 1
        
        # Network usage vs Heart Rate
        if has_hr:
            axes[plot_idx].scatter(self.df['total_mb'], self.df['heart_rate'], 
                                  alpha=0.5, color='#F18F01')
            axes[plot_idx].set_xlabel('Network Usage (MB)')
            axes[plot_idx].set_ylabel('Heart Rate (BPM)')
            axes[plot_idx].set_title('Network Usage vs Heart Rate')
            axes[plot_idx].grid(True, alpha=0.3)
            
            z = np.polyfit(self.df['total_mb'].dropna(), 
                          self.df['heart_rate'].dropna(), 1)
            p = np.poly1d(z)
            axes[plot_idx].plot(self.df['total_mb'], p(self.df['total_mb']), 
                               "r--", alpha=0.8, linewidth=2)
            plot_idx += 1
        
        # Network usage vs Body Battery
        if has_battery:
            axes[plot_idx].scatter(self.df['total_mb'], self.df['body_battery'], 
                                  alpha=0.5, color='#06A77D')
            axes[plot_idx].set_xlabel('Network Usage (MB)')
            axes[plot_idx].set_ylabel('Body Battery')
            axes[plot_idx].set_title('Network Usage vs Body Battery')
            axes[plot_idx].grid(True, alpha=0.3)
            
            z = np.polyfit(self.df['total_mb'].dropna(), 
                          self.df['body_battery'].dropna(), 1)
            p = np.poly1d(z)
            axes[plot_idx].plot(self.df['total_mb'], p(self.df['total_mb']), 
                               "r--", alpha=0.8, linewidth=2)
        
        plt.tight_layout()
        output_path = self.viz_dir / 'scatter_correlations.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to: {output_path}")
        plt.close()
    
    def plot_hourly_patterns(self):
        """Analyze patterns by hour of day"""
        print("\nAnalyzing hourly patterns...")
        
        hourly_avg = self.df.groupby('hour').agg({
            'total_mb': 'mean',
            'connection_count': 'mean'
        })
        
        # Add health metrics if available
        if 'stress_level' in self.df.columns:
            hourly_avg['stress_level'] = self.df.groupby('hour')['stress_level'].mean()
        if 'heart_rate' in self.df.columns:
            hourly_avg['heart_rate'] = self.df.groupby('hour')['heart_rate'].mean()
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Network usage by hour
        axes[0].bar(hourly_avg.index, hourly_avg['total_mb'], 
                   color='#2E86AB', alpha=0.7)
        axes[0].set_title('Average Network Usage by Hour of Day', fontweight='bold')
        axes[0].set_xlabel('Hour of Day')
        axes[0].set_ylabel('Average MB')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Stress by hour (if available)
        if 'stress_level' in hourly_avg.columns:
            axes[1].bar(hourly_avg.index, hourly_avg['stress_level'], 
                       color='#A23B72', alpha=0.7)
            axes[1].set_title('Average Stress Level by Hour of Day', fontweight='bold')
            axes[1].set_xlabel('Hour of Day')
            axes[1].set_ylabel('Average Stress')
            axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.viz_dir / 'hourly_patterns.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to: {output_path}")
        plt.close()
    
    def run_full_analysis(self):
        """Run complete correlation analysis"""
        print("\n" + "="*70)
        print("CORRELATION ANALYSIS")
        print("="*70)
        
        self.load_data()
        corr_matrix = self.calculate_correlations()
        
        if corr_matrix is not None:
            self.plot_correlation_heatmap(corr_matrix)
        
        self.plot_time_series()
        self.plot_scatter_correlations()
        self.plot_hourly_patterns()
        
        print("\n" + "="*70)
        print("VISUALIZATION COMPLETE")
        print("="*70)
        print(f"\nVisualizations saved to: {self.viz_dir}")


if __name__ == "__main__":
    analyzer = CorrelationAnalyzer()
    analyzer.run_full_analysis()
    
    print("\n✓ Correlation analysis complete!")
    print("  Check output/visualizations/ for charts")
