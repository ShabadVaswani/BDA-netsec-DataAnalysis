const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Comprehensive Garmin Data Parser
 * Outputs:
 *   1. Minute-level health data (HR, stress, body battery)
 *   2. Hourly activity data (steps, calories, activity)
 *   3. Sleep data (separate, for later)
 */

const garminDir = path.join(__dirname, '..', 'data', 'garmin', '2025-11-18 (1)');
const outputDir = path.join(__dirname, '..', 'output', 'garmin_parsed');

// Create output directory
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

console.log('=== Comprehensive Garmin Data Parser ===\n');

const fitParser = new FitParser({
    force: true,
    speedUnit: 'km/h',
    lengthUnit: 'km',
    temperatureUnit: 'celsius',
    elapsedRecordField: true,
    mode: 'both'
});

// Get all files
const files = fs.readdirSync(garminDir);
const wellnessFiles = files.filter(f => f.includes('WELLNESS'));
const sleepFiles = files.filter(f => f.includes('SLEEP_DATA'));
const metricsFiles = files.filter(f => f.includes('METRICS'));

console.log(`Found ${wellnessFiles.length} WELLNESS files`);
console.log(`Found ${sleepFiles.length} SLEEP_DATA files`);
console.log(`Found ${metricsFiles.length} METRICS files\n`);

// Data collectors
let allMinuteHealth = [];
let allActivityData = [];
let allSleepData = [];

let filesProcessed = 0;
const totalFiles = wellnessFiles.length + sleepFiles.length + metricsFiles.length;

// Process WELLNESS files
wellnessFiles.forEach((filename) => {
    const filePath = path.join(garminDir, filename);
    const fileBuffer = fs.readFileSync(filePath);

    fitParser.parse(fileBuffer, (error, data) => {
        if (error) {
            console.error(`✗ Error parsing ${filename}:`, error);
            filesProcessed++;
            return;
        }

        console.log(`✓ Parsed ${filename}`);

        // Extract minute-level health data from monitors (heart rate)
        if (data.monitors && data.monitors.length > 0) {
            data.monitors.forEach(record => {
                allMinuteHealth.push({
                    datetime: record.timestamp,
                    heart_rate: record.heart_rate || null,
                    stress_level: null,  // Will be filled from stress array
                    body_battery: null   // Will be filled from stress array
                });

                // Also collect for hourly aggregation
                allActivityData.push({
                    datetime: record.timestamp,
                    steps: record.cycles || 0,
                    calories: record.active_calories || 0,
                    active_minutes: record.active_time || 0,
                    activity_intensity: record.current_activity_type_intensity || null
                });
            });
        }

        // Extract stress and body battery from stress array
        if (data.stress && data.stress.length > 0) {
            data.stress.forEach(record => {
                allMinuteHealth.push({
                    datetime: record.stress_level_time,
                    heart_rate: null,  // Not in stress array
                    stress_level: record.stress_level_value || null,
                    body_battery: record.body_battery || null
                });
            });
        }

        filesProcessed++;
        if (filesProcessed === totalFiles) {
            processData();
        }
    });
});

// Process SLEEP files (for later use)
sleepFiles.forEach((filename) => {
    const filePath = path.join(garminDir, filename);
    const fileBuffer = fs.readFileSync(filePath);

    fitParser.parse(fileBuffer, (error, data) => {
        if (error) {
            console.error(`✗ Error parsing ${filename}:`, error);
            filesProcessed++;
            return;
        }

        console.log(`✓ Parsed ${filename} (sleep data collected for later)`);

        // Store raw sleep data for later processing
        if (data.sleep_levels || data.monitoring || data.sessions) {
            allSleepData.push({
                filename: filename,
                data: data
            });
        }

        filesProcessed++;
        if (filesProcessed === totalFiles) {
            processData();
        }
    });
});

// Process METRICS files
metricsFiles.forEach((filename) => {
    const filePath = path.join(garminDir, filename);
    const fileBuffer = fs.readFileSync(filePath);

    fitParser.parse(fileBuffer, (error, data) => {
        if (error) {
            console.error(`✗ Error parsing ${filename}:`, error);
            filesProcessed++;
            return;
        }

        console.log(`✓ Parsed ${filename}`);

        // Extract any additional metrics
        if (data.records && data.records.length > 0) {
            data.records.forEach(record => {
                if (record.heart_rate) {
                    allMinuteHealth.push({
                        datetime: record.timestamp,
                        heart_rate: record.heart_rate,
                        stress_level: null,
                        body_battery: null
                    });
                }
            });
        }

        filesProcessed++;
        if (filesProcessed === totalFiles) {
            processData();
        }
    });
});

function processData() {
    console.log('\n' + '='.repeat(70));
    console.log('PROCESSING DATA');
    console.log('='.repeat(70));

    // Filter out records with invalid timestamps
    allMinuteHealth = allMinuteHealth.filter(r => r.datetime);
    allActivityData = allActivityData.filter(r => r.datetime);

    // Sort by datetime
    allMinuteHealth.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
    allActivityData.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));

    console.log(`\n📊 Data Collected:`);
    console.log(`  - Minute health records: ${allMinuteHealth.length}`);
    console.log(`  - Activity records: ${allActivityData.length}`);
    console.log(`  - Sleep files: ${allSleepData.length}`);

    // TABLE 1: Minute-level health data
    console.log(`\n📝 Creating Table 1: garmin_minute_health.csv`);
    createMinuteHealthCSV();

    // TABLE 2: Hourly activity data
    console.log(`📝 Creating Table 2: garmin_hourly_activity.csv`);
    createHourlyActivityCSV();

    // TABLE 3: Sleep data (save raw for later processing)
    console.log(`📝 Saving sleep data for Table 3 (to be processed later)`);
    saveSleepData();

    // Create summary
    createSummary();

    console.log('\n' + '='.repeat(70));
    console.log('✓ PARSING COMPLETE');
    console.log('='.repeat(70));
    console.log(`\n📁 Output directory: ${outputDir}`);
    console.log(`\n✓ Table 1: garmin_minute_health.csv (${allMinuteHealth.length} records)`);
    console.log(`✓ Table 2: garmin_hourly_activity.csv`);
    console.log(`✓ Sleep data saved for later processing`);
}

function createMinuteHealthCSV() {
    const csvLines = [];
    csvLines.push('datetime,heart_rate,stress_level,body_battery');

    allMinuteHealth.forEach(record => {
        csvLines.push([
            new Date(record.datetime).toISOString(),  // Convert to ISO format
            record.heart_rate !== null ? record.heart_rate : '',
            record.stress_level !== null ? record.stress_level : '',
            record.body_battery !== null ? record.body_battery : ''
        ].join(','));
    });

    const outputPath = path.join(outputDir, 'garmin_minute_health.csv');
    fs.writeFileSync(outputPath, csvLines.join('\n'));

    console.log(`  ✓ Saved ${allMinuteHealth.length} minute-level records`);

    // Also save as JSON for easier Python loading
    const jsonPath = path.join(outputDir, 'garmin_minute_health.json');
    fs.writeFileSync(jsonPath, JSON.stringify(allMinuteHealth, null, 2));
    console.log(`  ✓ Also saved as JSON`);
}

function createHourlyActivityCSV() {
    // Aggregate to hourly
    const hourlyMap = {};

    allActivityData.forEach(record => {
        const hour = new Date(record.datetime);
        hour.setMinutes(0, 0, 0);
        const hourKey = hour.toISOString();

        if (!hourlyMap[hourKey]) {
            hourlyMap[hourKey] = {
                datetime: hourKey,
                steps: 0,
                calories: 0,
                active_minutes: 0,
                activity_intensity_values: []
            };
        }

        hourlyMap[hourKey].steps += record.steps;
        hourlyMap[hourKey].calories += record.calories;
        hourlyMap[hourKey].active_minutes += record.active_minutes;

        if (record.activity_intensity !== null) {
            hourlyMap[hourKey].activity_intensity_values.push(record.activity_intensity);
        }
    });

    // Calculate averages and create CSV
    const hourlyRecords = Object.values(hourlyMap).map(hour => ({
        datetime: hour.datetime,
        steps: hour.steps,
        calories: Math.round(hour.calories),
        active_minutes: Math.round(hour.active_minutes),
        activity_intensity_avg: hour.activity_intensity_values.length > 0
            ? Math.round(hour.activity_intensity_values.reduce((a, b) => a + b, 0) / hour.activity_intensity_values.length)
            : null
    }));

    hourlyRecords.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));

    const csvLines = [];
    csvLines.push('datetime,steps,calories,active_minutes,activity_intensity_avg');

    hourlyRecords.forEach(record => {
        csvLines.push([
            new Date(record.datetime).toISOString(),  // Convert to ISO format
            record.steps,
            record.calories,
            record.active_minutes,
            record.activity_intensity_avg !== null ? record.activity_intensity_avg : ''
        ].join(','));
    });

    const outputPath = path.join(outputDir, 'garmin_hourly_activity.csv');
    fs.writeFileSync(outputPath, csvLines.join('\n'));

    console.log(`  ✓ Saved ${hourlyRecords.length} hourly activity records`);

    // Also save as JSON
    const jsonPath = path.join(outputDir, 'garmin_hourly_activity.json');
    fs.writeFileSync(jsonPath, JSON.stringify(hourlyRecords, null, 2));
    console.log(`  ✓ Also saved as JSON`);
}

function saveSleepData() {
    const outputPath = path.join(outputDir, 'garmin_sleep_raw.json');
    fs.writeFileSync(outputPath, JSON.stringify(allSleepData, null, 2));
    console.log(`  ✓ Saved ${allSleepData.length} sleep files for later processing`);
}

function createSummary() {
    const summary = {
        parsing_date: new Date().toISOString(),
        files_processed: {
            wellness: wellnessFiles.length,
            sleep: sleepFiles.length,
            metrics: metricsFiles.length,
            total: totalFiles
        },
        records_created: {
            minute_health: allMinuteHealth.length,
            hourly_activity: Object.keys(allActivityData.reduce((acc, r) => {
                const hour = new Date(r.datetime);
                hour.setMinutes(0, 0, 0);
                acc[hour.toISOString()] = true;
                return acc;
            }, {})).length,
            sleep_files: allSleepData.length
        },
        time_range: {
            start: allMinuteHealth[0]?.datetime,
            end: allMinuteHealth[allMinuteHealth.length - 1]?.datetime
        },
        data_quality: {
            heart_rate_coverage: allMinuteHealth.filter(r => r.heart_rate !== null).length / allMinuteHealth.length,
            stress_coverage: allMinuteHealth.filter(r => r.stress_level !== null).length / allMinuteHealth.length,
            body_battery_coverage: allMinuteHealth.filter(r => r.body_battery !== null).length / allMinuteHealth.length
        }
    };

    const outputPath = path.join(outputDir, 'parsing_summary.json');
    fs.writeFileSync(outputPath, JSON.stringify(summary, null, 2));

    console.log(`\n📊 Data Quality:`);
    console.log(`  - Heart Rate coverage: ${(summary.data_quality.heart_rate_coverage * 100).toFixed(1)}%`);
    console.log(`  - Stress coverage: ${(summary.data_quality.stress_coverage * 100).toFixed(1)}%`);
    console.log(`  - Body Battery coverage: ${(summary.data_quality.body_battery_coverage * 100).toFixed(1)}%`);
}
