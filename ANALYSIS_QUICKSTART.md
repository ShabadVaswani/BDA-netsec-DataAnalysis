# Quick Start: Full Data Analysis

## 📊 What This Does

Analyzes your RouterSense phone activity data and correlates it with Garmin health metrics to find:
- Which apps increase your stress
- How phone usage affects heart rate
- Impact on body battery/energy
- Peak usage times and patterns

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txtK
```

### Step 2: Parse Garmin Data (if not done already)
```bash
npm run parse
```

### Step 3: Run Full Analysis
```bash
npm run analyze
```

Or run directly:
```bash
python src/run_analysis.py
```

---

## 📁 What Gets Generated

### Data Files (`output/analysis_results/`)
- `combined_hourly.csv` - Merged RouterSense + Garmin data
- `correlation_matrix.csv` - Correlation coefficients
- `top_domains.csv` - Top apps by bandwidth
- `summary_statistics.txt` - Detailed stats

### Visualizations (`output/visualizations/`)
- `correlation_heatmap.png` - Correlation matrix heatmap
- `time_series_plots.png` - Network usage, stress, HR, body battery over time
- `scatter_correlations.png` - Network usage vs health metrics
- `hourly_patterns.png` - Usage patterns by hour of day

---

## 📊 Analysis Pipeline

The analysis runs in 2 phases:

### Phase 1: Data Loading & Merging
1. Loads RouterSense CSV (`phone_overall_activities.csv`)
2. Parses timestamps and metadata (domains, companies)
3. Aggregates to hourly metrics
4. Loads parsed Garmin data
5. Merges datasets on datetime
6. Generates summary statistics

### Phase 2: Correlation Analysis
1. Calculates correlation matrix
2. Creates correlation heatmap
3. Plots time series (usage, stress, HR, battery)
4. Creates scatter plots (usage vs health)
5. Analyzes hourly patterns

---

## 🔍 What You'll Learn

### Network Usage Patterns
- Total data usage over time
- Peak usage hours
- Most used apps/domains
- Bandwidth consumption trends

### Health Correlations
- **Stress vs Usage:** Does phone use increase stress?
- **Heart Rate vs Usage:** Impact on heart rate
- **Body Battery vs Usage:** Energy drain patterns
- **Time Patterns:** When usage affects health most

### Specific Insights
- Which apps correlate with highest stress
- Optimal phone usage times
- Weekend vs weekday differences
- High usage vs low usage health impact

---

## 📈 Sample Findings

After running the analysis, you might discover:

✅ **"YouTube usage between 10-11 PM correlates with 15% higher stress"**
✅ **"Social media apps drain body battery 2x faster than productivity apps"**
✅ **"Peak phone usage at 8 PM coincides with peak stress levels"**
✅ **"Low usage mornings (6-8 AM) show 20% better body battery recovery"**

---

## 🛠️ Troubleshooting

### "No Garmin data found"
- Make sure you've run `npm run parse` first
- Check that `data/garmin/` contains FIT files
- Parsed data should be in `output/garmin_parsed/`

### "Module not found"
- Run `pip install -r requirements.txt`
- Make sure Python 3.8+ is installed

### "No such file: phone_overall_activities.csv"
- Make sure the file is in `data/phone_overall_activities.csv`
- Check the file path in the script

---

## 🎯 Next Steps After Analysis

1. **Review visualizations** in `output/visualizations/`
2. **Check correlation matrix** - which metrics correlate strongest?
3. **Identify problem apps** - which domains increase stress?
4. **Adjust behavior** - limit high-stress apps during certain times
5. **Re-run analysis** after behavior changes to measure improvement

---

## 💡 Tips

- Run analysis weekly to track trends
- Compare weekday vs weekend patterns
- Look for specific app categories (social media, work, entertainment)
- Correlate with external factors (work stress, sleep quality)

---

**Ready to start?** Run:
```bash
npm run analyze
```

Results will be in `output/` directory! 🎉
