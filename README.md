# BDA Network Security Data Analysis

Analysis of network activity (RouterSense) and physiological data (Garmin) to understand correlations between digital behavior and health metrics.

## 🎯 Project Overview

This project analyzes the relationship between:
- **Network Activity** (RouterSense data): Websites visited, bandwidth usage, timing
- **Physiological Metrics** (Garmin data): Heart rate, stress levels, body battery, activity

**Goal:** Identify how phone/internet usage affects stress, heart rate, and overall wellbeing.

---

## 📋 Prerequisites

- Node.js (v14 or higher)
- npm

---

## 🚀 Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd BDA-netsec-DataAnalysis
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure your settings

Copy the example config file:
```bash
cp config.example.json config.json
```

Edit `config.json` and add your RouterSense device ID:
```json
{
  "routersense": {
    "baseUrl": "https://dashboard.routersense.ai/view_device",
    "deviceId": "YOUR_DEVICE_ID_HERE"
  }
}
```

**How to find your device ID:**
1. Go to your RouterSense dashboard
2. Look at the URL: `https://dashboard.routersense.ai/view_device?pid=XXXXX`
3. Copy the value after `pid=`

---

## 📥 Download RouterSense Data

### Using npm scripts (recommended)
```bash
npm run download 2025-11-18
```

### Or run directly
```bash
node src/download_routersense_data.js 2025-11-18
```

### Download date range
```bash
node src/download_routersense_data.js 2025-11-18 2025-11-20
```

**Output:** CSV files in `data/routersense/YYYY-MM-DD/`

Each hour gets its own file (`hour_00.csv` through `hour_23.csv`) with:
- Time (ISO timestamp)
- Domain
- Company
- Download (kB)
- Upload (kB)

---

## 🏃 Parse Garmin Data

Place your Garmin FIT files in the `data/garmin/` directory, then run:

```bash
npm run parse
```

Or run directly:
```bash
node src/parse_garmin_fit.js
```

**Output:** JSON files in `output/garmin_parsed/` directory

---

## 📊 Data Structure

### RouterSense Data
- **Granularity:** Hourly files with minute-level records
- **Format:** CSV with ISO timestamps
- **Fields:** Time, Domain, Company, Download, Upload

### Garmin Data
- **Granularity:** Minute-by-minute
- **Format:** Binary FIT files → JSON/CSV
- **Metrics:** Heart rate, stress, body battery, steps, calories

---

## 📁 Project Structure

```
BDA-netsec-DataAnalysis/
├── src/                        # Production code
│   ├── download_routersense_data.js
│   └── parse_garmin_fit.js
│
├── scripts/                    # Utility scripts
│   └── download_hours_8_23.js
│
├── tests/                      # Test files
│   ├── slider/                 # Slider tests
│   ├── download/               # Download tests
│   ├── debug/                  # Debug scripts
│   └── artifacts/              # Test outputs
│
├── docs/                       # Documentation
│   ├── COMPLETE_DATA_ANALYSIS_REPORT.md
│   ├── GARMIN_DATA_STRUCTURE.md
│   ├── README_downloader.md
│   └── GITHUB_SETUP.md
│
├── data/                       # Data (gitignored)
│   ├── routersense/            # RouterSense downloads
│   ├── garmin/                 # Garmin FIT files
│   └── processed/              # Processed data
│
├── output/                     # Generated outputs (gitignored)
│   ├── garmin_parsed/          # Parsed Garmin data
│   ├── network_analysis/       # Analysis results
│   └── reports/                # Reports
│
├── analysis/                   # Jupyter notebooks
│   └── analysis.ipynb
│
├── config.json                 # Your settings (gitignored)
├── config.example.json         # Template config
├── package.json                # Dependencies
├── .gitignore                  # Protected files
├── README.md                   # This file
└── LICENSE                     # MIT License
```

---

## 🛠️ Technical Details

### RouterSense Downloader
- Uses Playwright for browser automation
- Binary search algorithm for accurate time navigation
- Handles Streamlit custom slider component
- Waits for "RUNNING..." indicator before scraping
- MD5 hash comparison to avoid duplicate downloads

### Garmin Parser
- Uses `fit-file-parser` npm package
- Extracts: heart rate, stress, body battery, activity
- Outputs to JSON for inspection

---

## 📖 Documentation

All documentation is in the `docs/` directory:

- `docs/README_downloader.md` - Detailed downloader usage
- `docs/GARMIN_DATA_STRUCTURE.md` - Garmin data analysis
- `docs/COMPLETE_DATA_ANALYSIS_REPORT.md` - Analysis opportunities
- `docs/GITHUB_SETUP.md` - GitHub setup guide

---

## 🤝 Contributing

This is a personal data analysis project. If you want to use it:

1. Fork the repository
2. Create your own `config.json` with your device ID
3. Never commit your personal data
4. Share insights, not raw data!

---

## ⚠️ Disclaimer

This project is for personal data analysis and research purposes. Ensure you have permission to access and analyze any data you use. Be mindful of privacy when sharing results.

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- RouterSense for network monitoring
- Garmin for health tracking
- Playwright for browser automation
