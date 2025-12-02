# Garmin Band Data Structure Report

## 📊 Overview

**Data Source:** Garmin Fitness Band (Product 3869, Serial: 3517294351)  
**Date:** November 18, 2025  
**Total Files:** 38 FIT files  
**Software Version:** 11.03

---

## 🗂️ File Types & Structure

### 1. WELLNESS Files (20 files)
**Primary data container** - Contains minute-by-minute health and activity data

#### Key Data Sections:

**A. Monitors (Minute-by-Minute Data)**
- **Timestamp** - Exact time of measurement
- **Heart Rate** - BPM (beats per minute)
- **Activity Type Intensity** - Activity level indicator
- **Distance** - Distance traveled
- **Cycles** - Step count
- **Active Time** - Time spent active
- **Active Calories** - Calories burned
- **Duration** - Activity duration

**Example Record:**
```json
{
  "timestamp": "2025-11-18T05:02:00.000Z",
  "heart_rate": 89,
  "current_activity_type_intensity": 104
}
```

**B. Stress Data (Minute-by-Minute)**
- **Stress Level Value** - Stress score (0-100)
- **Body Battery** - Energy level (0-100)
- **Stress Level Time** - Timestamp

**Example Record:**
```json
{
  "stress_level_time": "2025-11-18T05:01:00.000Z",
  "stress_level_value": 34,
  "body_battery": 18
}
```

**C. Events**
- Activity markers and transitions
- Timestamps for significant events

**D. Device Info**
- Device serial number
- Manufacturer (Garmin)
- Software version
- Product ID

**E. Monitor Info**
- Resting metabolic rate (2202 in sample)
- Activity type (e.g., "walking")
- Conversion factors for distance/calories

---

### 2. SLEEP_DATA Files (16 files)
**Sleep tracking data** - Contains sleep stages and quality metrics

**Note:** The sample file analyzed was empty (no sleep records), but structure includes:
- Sleep stages (light, deep, REM, awake)
- Sleep start/end times
- Sleep quality metrics
- Heart rate during sleep
- Movement data

---

### 3. METRICS Files (2 files)
**Health metrics snapshots** - Periodic health measurements

**Contains:**
- Device information
- Timestamp of measurement
- Likely includes: VO2 max, fitness age, recovery time (not in sample)

---

## 📈 Data Granularity

| Data Type | Frequency | Example Fields |
|-----------|-----------|----------------|
| **Heart Rate** | Every 1 minute | BPM value |
| **Stress Level** | Every 1 minute | 0-100 score, body battery |
| **Activity** | Variable | Steps, distance, calories, intensity |
| **Sleep** | Per sleep session | Stages, duration, quality |
| **Metrics** | Periodic | Health snapshots |

---

## 🔑 Key Data Fields for Analysis

### Available Metrics:

#### Continuous (Minute-by-Minute):
1. **Heart Rate** - `heart_rate` (BPM)
2. **Stress Level** - `stress_level_value` (0-100)
3. **Body Battery** - `body_battery` (0-100, energy level)
4. **Activity Intensity** - `current_activity_type_intensity`
5. **Timestamp** - Exact time of measurement

#### Activity Metrics:
1. **Steps** - `cycles`
2. **Distance** - `distance`
3. **Active Time** - `active_time`
4. **Calories** - `active_calories`
5. **Activity Type** - `activity_type` (walking, running, etc.)

#### Physiological:
1. **Resting Metabolic Rate** - `resting_metabolic_rate`
2. **Heart Rate Variability** - `hrv` (if available)

---

## 📊 Data Comparison: Garmin vs RouterSense

| Aspect | Garmin Data | RouterSense Data |
|--------|-------------|------------------|
| **Granularity** | 1-minute intervals | Hourly summaries |
| **Data Type** | Physiological (HR, stress) | Network activity |
| **File Format** | Binary (.fit) | Text (CSV) |
| **Records/Day** | ~1,440 (24h × 60min) | ~288 (24h × 12 rows/hour) |
| **File Count** | 38 files | 24 files |
| **Timestamp** | Minute precision | Hour precision |

---

## 💡 Analysis Opportunities

### Potential Correlations to Explore:

1. **Network Usage vs Stress**
   - High network activity → Increased stress?
   - Social media domains → Stress patterns?

2. **Network Usage vs Heart Rate**
   - Video streaming → Sedentary behavior?
   - Gaming → Elevated heart rate?

3. **Time-Based Patterns**
   - Late-night phone usage → Poor sleep quality?
   - Morning network activity → Body battery levels?

4. **Activity vs Network**
   - Active periods → Reduced network usage?
   - Sedentary periods → Increased browsing?

5. **Domain-Specific Impacts**
   - Work domains (email, productivity) → Stress levels?
   - Entertainment domains → Relaxation indicators?

---

## 🎯 Recommended Next Steps

### 1. Data Preparation
- ✅ Parse all FIT files to CSV/JSON
- ✅ Align timestamps (both to minute/hour)
- ✅ Create unified dataset

### 2. Data Organization
```
dataset_for_analysis/
├── garmin_data/
│   ├── 2025-11-18/
│   │   ├── heart_rate.csv
│   │   ├── stress.csv
│   │   ├── activity.csv
│   │   └── sleep.csv
└── routersense_data/
    └── 2025-11-18/
        ├── hour_00.csv
        ...
```

### 3. Analysis Pipeline
1. **Aggregate Garmin data** to hourly averages
2. **Merge with RouterSense** data by timestamp
3. **Calculate correlations** between metrics
4. **Visualize patterns** (time series, heatmaps)
5. **Statistical analysis** (regression, clustering)

---

## 📝 Sample Data Preview

### WELLNESS Data (Minute-by-Minute):
```
Timestamp,Heart_Rate,Stress_Level,Body_Battery,Activity_Intensity
2025-11-18T05:01:00Z,89,34,18,104
2025-11-18T05:02:00Z,99,61,18,102
2025-11-18T05:03:00Z,93,65534,18,104
```

### RouterSense Data (Hourly):
```
Time,Domain,Company,Download (kB),Upload (kB)
14:58,google.com,Google,0.321,0.142
14:58,veggly.net,,6214.028,55.361
```

---

## 🚀 Best Path Forward

### Option A: Hourly Aggregation (Recommended)
- Aggregate Garmin data to hourly averages
- Match RouterSense hourly files
- Easier correlation analysis
- Less data complexity

### Option B: Minute-Level Detail
- Keep Garmin at minute level
- Expand RouterSense to show activity within each hour
- More granular insights
- Higher complexity

### Option C: Hybrid Approach
- Hourly for initial exploration
- Drill down to minute-level for interesting patterns
- Best of both worlds

**Recommendation:** Start with **Option A** for quick insights, then move to **Option C** for deeper analysis.

---

## 📦 Files Generated

- `garmin_parsed/WELLNESS_parsed.json` - Full WELLNESS data structure
- `garmin_parsed/SLEEP_DATA_parsed.json` - Sleep data structure
- `garmin_parsed/METRICS_parsed.json` - Metrics data structure

**Next:** Convert all 38 FIT files to CSV for easy analysis!
