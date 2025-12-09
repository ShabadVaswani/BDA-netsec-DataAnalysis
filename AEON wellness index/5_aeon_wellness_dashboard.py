"""
AEON Wellness Index Dashboard
==============================
This script creates a comprehensive wellness dashboard with 4 pillars:
- BIO (40%): Biological/Physical Health
- SLEEP (30%): Sleep Quality
- ENV (20%): Environmental Factors
- COG (10%): Cognitive/Digital Wellness

Author: AEON Wellness Analytics
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("=" * 70)
print("AEON WELLNESS INDEX DASHBOARD")
print("=" * 70)
print("\n[1/5] Loading data...")

# Load normalized CSV data
df = pd.read_csv('health_net_features_2_normalize.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

# Load bio stability scores
bio_scores = np.load('../EXO-model/bio_stability_scores.npy')

# Align lengths - trim the start of CSV to match bio_scores length
trim_amount = len(df) - len(bio_scores)
df_aligned = df.iloc[trim_amount:].reset_index(drop=True)

# Verify alignment
assert len(df_aligned) == len(bio_scores), f"Length mismatch: {len(df_aligned)} vs {len(bio_scores)}"
print(f"  Trimmed {trim_amount} records from start of CSV")
print(f"✓ Data loaded: {len(df_aligned)} records aligned")
print(f"  Date range: {df_aligned['datetime'].min()} to {df_aligned['datetime'].max()}")

# ============================================================================
# 2. DEFINE WELLNESS PILLARS (0-100 SCALE)
# ============================================================================
print("\n[2/5] Calculating wellness pillars...")

def z_to_score(z_score, invert=False):
    """
    Convert Z-Score to 0-100 scale.
    
    Args:
        z_score: Standardized Z-score
        invert: If True, higher Z-score = lower wellness (for "bad" metrics)
    
    Returns:
        Score clipped between 0 and 100
    """
    if invert:
        # For "bad" things like stress: higher Z = lower score
        score = 50 - (z_score * 10)
    else:
        # For "good" things like battery: higher Z = higher score
        score = 50 + (z_score * 10)
    
    return np.clip(score, 0, 100)

# Create a copy for calculations
wellness_df = df_aligned.copy()

# --- BIO PILLAR (40%): Biological/Physical Health ---
# Components: Inverted Stress, Inverted HR, Body Battery, Bio Stability Score
wellness_df['stress_score'] = z_to_score(wellness_df['stress_level'], invert=True)
wellness_df['hr_score'] = z_to_score(wellness_df['heart_rate'], invert=True)
wellness_df['battery_score'] = z_to_score(wellness_df['body_battery'], invert=False)

# Convert bio_stability_scores (reconstruction error) to 0-100 scale
# Lower reconstruction error = better stability = higher score
bio_stability_z = (bio_scores - bio_scores.mean()) / bio_scores.std()
wellness_df['bio_stability_score'] = z_to_score(bio_stability_z, invert=True)

wellness_df['BIO_Score'] = (
    wellness_df['stress_score'] + 
    wellness_df['hr_score'] + 
    wellness_df['battery_score'] + 
    wellness_df['bio_stability_score']
) / 4

# --- SLEEP PILLAR (30%): Sleep Quality ---
wellness_df['SLEEP_Score'] = z_to_score(wellness_df['sleep_duration_of_day'], invert=False)

# --- ENV PILLAR (20%): Environmental Factors ---
wellness_df['rain_score'] = z_to_score(wellness_df['rain_mm'], invert=True)
wellness_df['wind_score'] = z_to_score(wellness_df['wind_speed_kmh'], invert=True)

# Temperature deviation (distance from comfortable 20°C)
temp_deviation = np.abs(wellness_df['temperature_celsius'])
temp_deviation_z = (temp_deviation - temp_deviation.mean()) / temp_deviation.std()
wellness_df['temp_score'] = z_to_score(temp_deviation_z, invert=True)

wellness_df['ENV_Score'] = (
    wellness_df['rain_score'] + 
    wellness_df['wind_score'] + 
    wellness_df['temp_score']
) / 3

# --- COG PILLAR (10%): Cognitive/Digital Wellness ---
wellness_df['screen_score'] = z_to_score(wellness_df['screen_streak_minutes'], invert=True)
wellness_df['phone_score'] = z_to_score(wellness_df['phone_active'], invert=True)

wellness_df['COG_Score'] = (
    wellness_df['screen_score'] + 
    wellness_df['phone_score']
) / 2

print("✓ Wellness pillars calculated:")
print(f"  BIO Score:   {wellness_df['BIO_Score'].mean():.1f} ± {wellness_df['BIO_Score'].std():.1f}")
print(f"  SLEEP Score: {wellness_df['SLEEP_Score'].mean():.1f} ± {wellness_df['SLEEP_Score'].std():.1f}")
print(f"  ENV Score:   {wellness_df['ENV_Score'].mean():.1f} ± {wellness_df['ENV_Score'].std():.1f}")
print(f"  COG Score:   {wellness_df['COG_Score'].mean():.1f} ± {wellness_df['COG_Score'].std():.1f}")

# ============================================================================
# 3. CALCULATE TOTAL AEON INDEX
# ============================================================================
print("\n[3/5] Computing AEON Wellness Index...")

# Weighted sum of 4 pillars
wellness_df['AEON_Index'] = (
    wellness_df['BIO_Score'] * 0.40 +
    wellness_df['SLEEP_Score'] * 0.30 +
    wellness_df['ENV_Score'] * 0.20 +
    wellness_df['COG_Score'] * 0.10
)

# Add 7-day rolling average for trend analysis
wellness_df['AEON_7Day_Avg'] = wellness_df['AEON_Index'].rolling(
    window=7*24*60,  # 7 days in minutes
    min_periods=1
).mean()

print(f"✓ AEON Index computed:")
print(f"  Overall Mean: {wellness_df['AEON_Index'].mean():.2f}")
print(f"  Overall Std:  {wellness_df['AEON_Index'].std():.2f}")
print(f"  Range: [{wellness_df['AEON_Index'].min():.2f}, {wellness_df['AEON_Index'].max():.2f}]")

# ============================================================================
# 4. VISUALIZE THE DASHBOARD
# ============================================================================
print("\n[4/5] Creating visualizations...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# --- PLOT 1: AEON Index Over Time ---
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(wellness_df['datetime'], wellness_df['AEON_Index'], 
         alpha=0.3, color='steelblue', linewidth=0.5, label='AEON Index')
ax1.plot(wellness_df['datetime'], wellness_df['AEON_7Day_Avg'], 
         color='darkblue', linewidth=2, label='7-Day Rolling Average')
ax1.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Baseline (50)')
ax1.fill_between(wellness_df['datetime'], 0, wellness_df['AEON_Index'], 
                  alpha=0.1, color='steelblue')
ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
ax1.set_ylabel('AEON Wellness Index (0-100)', fontsize=12, fontweight='bold')
ax1.set_title('AEON Wellness Index Over Time', fontsize=16, fontweight='bold', pad=20)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 100)

# --- PLOT 2: Radar Chart (Spider Plot) ---
ax2 = fig.add_subplot(gs[1, 0], projection='polar')

# Calculate average scores for each pillar
pillar_means = {
    'BIO\n(40%)': wellness_df['BIO_Score'].mean(),
    'SLEEP\n(30%)': wellness_df['SLEEP_Score'].mean(),
    'ENV\n(20%)': wellness_df['ENV_Score'].mean(),
    'COG\n(10%)': wellness_df['COG_Score'].mean()
}

categories = list(pillar_means.keys())
values = list(pillar_means.values())
values += values[:1]  # Complete the circle

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

ax2.plot(angles, values, 'o-', linewidth=2, color='darkgreen', label='Average')
ax2.fill(angles, values, alpha=0.25, color='green')
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, fontsize=10, fontweight='bold')
ax2.set_ylim(0, 100)
ax2.set_yticks([25, 50, 75, 100])
ax2.set_yticklabels(['25', '50', '75', '100'], fontsize=8)
ax2.set_title('Wellness Pillar Balance', fontsize=14, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3)

# --- PLOT 3: Heatmap (Day of Week vs Hour of Day) ---
ax3 = fig.add_subplot(gs[1, 1:])

# Extract hour and day of week (use unique names to avoid conflicts)
wellness_df['hour_of_day'] = wellness_df['datetime'].dt.hour
wellness_df['day_name'] = wellness_df['datetime'].dt.day_name()

# Create heatmap data using groupby
heatmap_data = wellness_df.groupby(['day_name', 'hour_of_day'])['AEON_Index'].mean().unstack()

# Reorder days
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])

sns.heatmap(heatmap_data, cmap='RdYlGn', center=50, vmin=0, vmax=100,
            cbar_kws={'label': 'AEON Index'}, ax=ax3, linewidths=0.5)
ax3.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax3.set_ylabel('Day of Week', fontsize=12, fontweight='bold')
ax3.set_title('AEON Score Heatmap: Day vs Hour', fontsize=14, fontweight='bold', pad=20)

# --- PLOT 4: Individual Pillar Trends ---
ax4 = fig.add_subplot(gs[2, :])

# Resample to daily for cleaner visualization
daily_df = wellness_df.set_index('datetime').resample('D').mean(numeric_only=True)

ax4.plot(daily_df.index, daily_df['BIO_Score'], label='BIO (40%)', linewidth=2, alpha=0.8)
ax4.plot(daily_df.index, daily_df['SLEEP_Score'], label='SLEEP (30%)', linewidth=2, alpha=0.8)
ax4.plot(daily_df.index, daily_df['ENV_Score'], label='ENV (20%)', linewidth=2, alpha=0.8)
ax4.plot(daily_df.index, daily_df['COG_Score'], label='COG (10%)', linewidth=2, alpha=0.8)
ax4.axhline(y=50, color='gray', linestyle='--', alpha=0.5)

ax4.set_xlabel('Date', fontsize=12, fontweight='bold')
ax4.set_ylabel('Pillar Score (0-100)', fontsize=12, fontweight='bold')
ax4.set_title('Individual Wellness Pillar Trends (Daily Average)', fontsize=14, fontweight='bold', pad=20)
ax4.legend(loc='upper left', fontsize=10, ncol=4)
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 100)

plt.suptitle('AEON WELLNESS INDEX DASHBOARD', 
             fontsize=20, fontweight='bold', y=0.98)

plt.savefig('aeon_wellness_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Dashboard saved: aeon_wellness_dashboard.png")

# ============================================================================
# 5. PRINT SUMMARY
# ============================================================================
print("\n[5/5] Generating summary report...")
print("\n" + "=" * 70)
print("AEON WELLNESS INDEX SUMMARY REPORT")
print("=" * 70)

# Find best and worst days
daily_aeon = wellness_df.groupby(wellness_df['datetime'].dt.date)['AEON_Index'].mean()

best_day = daily_aeon.idxmax()
best_score = daily_aeon.max()

worst_day = daily_aeon.idxmin()
worst_score = daily_aeon.min()

print(f"\n📊 OVERALL STATISTICS:")
print(f"   Total Records:     {len(wellness_df):,}")
print(f"   Date Range:        {wellness_df['datetime'].min().date()} to {wellness_df['datetime'].max().date()}")
print(f"   Average AEON:      {wellness_df['AEON_Index'].mean():.2f} / 100")
print(f"   Std Deviation:     {wellness_df['AEON_Index'].std():.2f}")

print(f"\n🏆 BEST DAY:")
print(f"   Date:              {best_day}")
print(f"   AEON Score:        {best_score:.2f} / 100")
best_day_data = wellness_df[wellness_df['datetime'].dt.date == best_day]
print(f"   BIO Score:         {best_day_data['BIO_Score'].mean():.2f}")
print(f"   SLEEP Score:       {best_day_data['SLEEP_Score'].mean():.2f}")
print(f"   ENV Score:         {best_day_data['ENV_Score'].mean():.2f}")
print(f"   COG Score:         {best_day_data['COG_Score'].mean():.2f}")

print(f"\n⚠️  WORST DAY:")
print(f"   Date:              {worst_day}")
print(f"   AEON Score:        {worst_score:.2f} / 100")
worst_day_data = wellness_df[wellness_df['datetime'].dt.date == worst_day]
print(f"   BIO Score:         {worst_day_data['BIO_Score'].mean():.2f}")
print(f"   SLEEP Score:       {worst_day_data['SLEEP_Score'].mean():.2f}")
print(f"   ENV Score:         {worst_day_data['ENV_Score'].mean():.2f}")
print(f"   COG Score:         {worst_day_data['COG_Score'].mean():.2f}")

print(f"\n💡 PILLAR AVERAGES:")
print(f"   BIO (40%):         {wellness_df['BIO_Score'].mean():.2f} / 100")
print(f"   SLEEP (30%):       {wellness_df['SLEEP_Score'].mean():.2f} / 100")
print(f"   ENV (20%):         {wellness_df['ENV_Score'].mean():.2f} / 100")
print(f"   COG (10%):         {wellness_df['COG_Score'].mean():.2f} / 100")

print("\n" + "=" * 70)
print("✓ AEON Wellness Dashboard Complete!")
print("=" * 70)

# Save the wellness dataframe for further analysis
wellness_df.to_csv('aeon_wellness_scores.csv', index=False)
print("\n📁 Wellness scores saved to: aeon_wellness_scores.csv")

plt.show()
