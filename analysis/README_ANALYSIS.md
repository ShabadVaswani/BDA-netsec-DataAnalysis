# Garmin + RouterSense Analysis Notebook

**File:** `analysis/garmin_routersense_analysis.ipynb`

## 📊 What This Notebook Does

This notebook performs a complete analysis of your Garmin health data combined with RouterSense network activity data for **November 18, 2025**.

### Data Flow:

```
1. Load Garmin Data
   ├── Minute-level health (heart rate, stress, body battery)
   └── Hourly activity (steps, calories, intensity)
   
2. Load RouterSense Data
   └── Network activity (MB, connections, apps)
   
3. Filter for Nov 18, 2025
   └── Isolate single day (temporary, will expand later)
   
4. Aggregate to Hourly
   ├── Garmin: Average health metrics per hour
   └── RouterSense: Sum network activity per hour
   
5. Merge Datasets
   └── Join on datetime (hourly)
   
6. Analyze
   ├── Correlation matrix
   ├── Scatter plots
   ├── Time series
   └── Summary statistics
```

---

## 🚀 How to Run

### Option 1: VS Code
1. Open `analysis/garmin_routersense_analysis.ipynb` in VS Code
2. Select Python kernel
3. Run all cells (Ctrl+Shift+P → "Run All")

### Option 2: Jupyter Lab
```bash
cd analysis
jupyter lab garmin_routersense_analysis.ipynb
```

### Option 3: Jupyter Notebook
```bash
cd analysis
jupyter notebook garmin_routersense_analysis.ipynb
```

---

## 📈 What You'll Get

### 1. **Data Quality Report**
- Record counts
- Coverage percentages
- Missing value analysis

### 2. **Hourly Patterns**
- Network usage by hour
- Heart rate by hour
- Stress level by hour
- Body battery by hour

### 3. **Correlation Analysis**
- Correlation matrix heatmap
- Key correlations identified
- Statistical relationships

### 4. **Visualizations**
- Scatter plots (network vs health)
- Time series comparison
- Normalized trends

### 5. **Summary Statistics**
- Total network usage
- Average health metrics
- Peak hours identified
- Activity totals

### 6. **Combined Dataset**
- Saved to: `output/analysis_results/combined_garmin_routersense_nov18.csv`
- Ready for further analysis

---

## 📊 Expected Insights

The notebook will help you discover:

1. **Does network usage correlate with stress?**
   - Positive correlation = more usage → more stress
   - Negative correlation = more usage → less stress

2. **Does phone usage affect heart rate?**
   - Identify apps/times that spike HR

3. **Does phone usage drain body battery?**
   - Energy depletion patterns

4. **Activity vs phone usage patterns**
   - Are you more active when using phone less?

---

## 🔧 Requirements

Make sure you have these installed:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

Or use the project requirements:
```bash
pip install -r requirements.txt
```

---

## 📁 Data Files Used

### Input:
- `output/garmin_parsed/garmin_minute_health.csv` (3,179 records)
- `output/garmin_parsed/garmin_hourly_activity.csv` (25 records)
- `data/phone_overall_activities.csv` (RouterSense data)

### Output:
- `output/analysis_results/combined_garmin_routersense_nov18.csv`

---

## ⚠️ Current Limitations

1. **Single Day:** Only Nov 18, 2025 data
   - Need more Garmin data for better analysis
   - Will expand date range when available

2. **Sparse Data:** Health metrics not recorded every minute
   - Heart rate: 36.8% coverage
   - Stress: 44.3% coverage
   - Body battery: 45.2% coverage
   - This is normal for fitness trackers

3. **Hourly Aggregation:** Loses minute-level detail
   - Necessary for alignment
   - Can drill down to minutes later

---

## 🎯 Next Steps After Running

1. **Review correlations** - Which are strongest?
2. **Identify patterns** - What times show interesting relationships?
3. **Add more data** - Get more days of Garmin data
4. **Deep dive** - Analyze specific apps/domains
5. **Sleep analysis** - Process sleep data (Table 3)

---

## 💡 Tips

- **Run cells in order** - Each cell depends on previous ones
- **Check for errors** - If a cell fails, check data paths
- **Modify as needed** - Feel free to add your own analysis
- **Save often** - Save notebook after making changes

---

## 🐛 Troubleshooting

**Error: File not found**
- Check that Garmin data is parsed: `npm run parse`
- Verify files exist in `output/garmin_parsed/`

**Error: No data for Nov 18**
- Check RouterSense data date range
- Verify Garmin data is from Nov 18, 2025

**Error: Missing library**
- Install requirements: `pip install -r requirements.txt`

---

## 📝 Notebook Structure

1. **Setup** - Import libraries
2. **Load Garmin** - Health + activity data
3. **Aggregate Garmin** - To hourly
4. **Load RouterSense** - Network data
5. **Filter Date** - Nov 18 only
6. **Aggregate RouterSense** - To hourly
7. **Merge** - Combine datasets
8. **EDA** - Exploratory analysis
9. **Correlations** - Statistical relationships
10. **Visualizations** - Plots and charts
11. **Time Series** - Temporal patterns
12. **Summary** - Key statistics
13. **Save** - Export combined data
14. **Insights** - Conclusions

---

## ✅ Success Criteria

After running, you should have:
- [x] Combined dataset with ~25 hourly records
- [x] Correlation matrix showing relationships
- [x] Multiple visualizations
- [x] Summary statistics
- [x] Saved CSV file for further analysis

---

**Ready to discover how your phone usage affects your health!** 🚀
