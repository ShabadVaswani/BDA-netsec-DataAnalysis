# RouterSense Data Downloader

Automated Playwright script to download hourly network activity data from RouterSense dashboard with smart duplicate detection and beautiful console output.

## Features

- ✅ **Date Range Support** - Download single date or multiple dates
- ✅ **Smart Duplicate Detection** - MD5 hashing to skip identical data
- ✅ **Organized Structure** - Files organized by date in folders
- ✅ **Dynamic Progress** - Real-time progress bars and colored output
- ✅ **Efficient** - Only updates changed data, skips duplicates
- ✅ **24 Hours** - Downloads all 24 hourly CSV files per date

## Quick Start

### 1. Installation

```bash
# Install dependencies
npm install

# Install Chromium browser for Playwright
npx playwright install chromium
```

### 2. Run the Downloader

```bash
# Download default date (2025-11-18)
node download_routersense_data.js

# Download specific date
node download_routersense_data.js 2025-11-20

# Download date range
node download_routersense_data.js 2025-11-18 2025-11-20
```

## How to Use

### Basic Usage

**Download a single date:**
```bash
node download_routersense_data.js 2025-11-18
```

This will:
1. Open a browser window (you'll see it working)
2. Navigate to the RouterSense dashboard
3. Download data for all 24 hours of November 18, 2025
4. Save files to `dataset_for_analysis/routersense_data/2025-11-18/`
5. Show a progress bar and summary

### Download Multiple Dates

**Download a date range:**
```bash
node download_routersense_data.js 2025-11-18 2025-11-24
```

This downloads data for:
- November 18, 2025
- November 19, 2025
- November 20, 2025
- ... through November 24, 2025

Each date gets its own folder with 24 hourly CSV files.

### Real-World Examples

**Download a week of data:**
```bash
node download_routersense_data.js 2025-11-01 2025-11-07
```

**Download a month:**
```bash
node download_routersense_data.js 2025-11-01 2025-11-30
```

**Update existing data:**
```bash
# Run the same command again - it will only update changed files!
node download_routersense_data.js 2025-11-18
```

## Output Structure

Files are organized by date:

```
dataset_for_analysis/
└── routersense_data/
    ├── 2025-11-18/
    │   ├── hour_00.csv  (midnight - 1 AM)
    │   ├── hour_01.csv  (1 AM - 2 AM)
    │   ├── hour_02.csv  (2 AM - 3 AM)
    │   ...
    │   └── hour_23.csv  (11 PM - midnight)
    ├── 2025-11-19/
    │   ├── hour_00.csv
    │   ...
    └── 2025-11-20/
        ├── hour_00.csv
        ...
```

## CSV File Format

Each CSV file contains:

| Column | Description |
|--------|-------------|
| **Time** | Timestamp of network activity |
| **Domain** | Website domain (e.g., google.com) |
| **Company** | Company name (e.g., Google) |
| **Download (kB)** | Download data in kilobytes |
| **Upload (kB)** | Upload data in kilobytes |

**Example:**
```csv
Time,Domain,Company,Download (kB),Upload (kB)
14:58,google.com,Google,0.321,0.142
14:58,veggly.net,,6214.028,55.361
14:57,gstatic.com,Google,0.177,0.104
```

## Understanding the Output

When you run the script, you'll see:

### 1. Header Section
```
======================================================================
RouterSense Smart Downloader
======================================================================

ℹ Date Range: 2025-11-18 to 2025-11-18
ℹ Total Dates: 1
ℹ Output: dataset_for_analysis/routersense_data/
```

### 2. Initialization
```
▶ Initializing Browser
  Navigating to dashboard...
✓ Page loaded
✓ Phone tab selected
✓ Ready to download
```

### 3. Progress Bar (updates in real-time)
```
[██████████████████████████████] 100% (24/24) 2025-11-18 23:00
```

### 4. Summary for Each Date
```
Summary for 2025-11-18:
  📥 New downloads: 5      (new files created)
  🔄 Updated files: 3      (files with changed data)
  ⏭️  Skipped (identical): 16  (no changes, skipped)
  📁 C:\...\dataset_for_analysis\routersense_data\2025-11-18
```

### 5. Final Summary
```
======================================================================
Final Summary
======================================================================
Dates processed: 1
📥 Total new downloads: 5
🔄 Total updated: 3
⏭️  Total skipped: 16
📁 Location: dataset_for_analysis/routersense_data/
```

## Smart Features Explained

### Duplicate Detection
- Uses **MD5 hashing** to compare file content
- **Skips** downloading if data is identical to existing file
- **Updates** only if data has changed
- Saves time and bandwidth!

### What happens when you re-run?
1. **Identical data** → Skipped (no download)
2. **Changed data** → Updated (overwrites old file)
3. **New hour** → Downloaded (creates new file)

### Example Scenario
```bash
# First run - downloads all 24 hours
node download_routersense_data.js 2025-11-18
# Output: 📥 New downloads: 24

# Second run - data hasn't changed
node download_routersense_data.js 2025-11-18
# Output: ⏭️ Skipped (identical): 24

# Third run - some data updated
node download_routersense_data.js 2025-11-18
# Output: 🔄 Updated files: 3, ⏭️ Skipped: 21
```

## Troubleshooting

### Browser doesn't open
- Make sure Chromium is installed: `npx playwright install chromium`

### No data downloaded
- Check that the date exists on the RouterSense dashboard
- The dashboard might not have data for future dates

### Script runs but files are empty
- Wait for the script to complete (don't close the browser)
- Check the console output for errors

### Want to see what's happening?
- The browser runs in **non-headless mode** (visible)
- You can watch it navigate and download data
- Progress bar shows real-time status

## Tips & Best Practices

1. **Start small** - Test with a single date first
2. **Check the data** - Verify one CSV file before downloading large ranges
3. **Re-run safely** - The script won't re-download identical data
4. **Server friendly** - Built-in 500ms delay between requests
5. **Organize by date** - Each date gets its own folder automatically

## Advanced Usage

### Change the default date
Edit the script and change:
```javascript
let START_DATE = '2025-11-18';  // Change this
```

### Adjust delays
If the script is too fast/slow, edit:
```javascript
await page.waitForTimeout(3500);  // Time to wait for data load
await page.waitForTimeout(500);   // Delay between hours
```

## Need Help?

- Check the console output for detailed error messages
- Look at the debug screenshots in the `downloads/` folder (if any)
- Verify the date format is `YYYY-MM-DD`
- Make sure you have internet connection

---

**Created with ❤️ using Playwright automation**
