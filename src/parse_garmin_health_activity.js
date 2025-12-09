const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Parse all Garmin WELLNESS.fit files and create a consolidated minute-level dataset
 * Output: garmin_minute_health_activity.csv
 */

console.log('🏃 Starting Garmin Health & Activity Data Parsing...\n');

// Configuration
const GARMIN_DATA_DIR = './data/garmin';
const OUTPUT_FILE = './output/garmin_parsed/garmin_minute_health_activity.csv';
const STRESS_THRESHOLD = 100; // Filter out stress values > 100

// Ensure output directory exists
const outputDir = path.dirname(OUTPUT_FILE);
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

// Storage for all parsed data
const allMinuteData = [];
let totalFilesProcessed = 0;
let totalRecordsExtracted = 0;

/**
 * Convert UTC timestamp to EST
 */
function convertToEST(utcDate) {
    const estOffset = -5 * 60; // EST is UTC-5
    const estDate = new Date(utcDate.getTime() + estOffset * 60 * 1000);
    return estDate;
}

/**
 * Format datetime for CSV
 */
function formatDateTime(date) {
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const day = String(date.getUTCDate()).padStart(2, '0');
    const hour = String(date.getUTCHours()).padStart(2, '0');
    const minute = String(date.getUTCMinutes()).padStart(2, '0');
    const second = String(date.getUTCSeconds()).padStart(2, '0');

    return {
        datetime: `${year}-${month}-${day} ${hour}:${minute}:${second}`,
        date: `${year}-${month}-${day}`,
        time: `${hour}:${minute}:${second}`,
        hour: parseInt(hour),
        minute: parseInt(minute)
    };
}

/**
 * Get day of week from date
 */
function getDayOfWeek(date) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getUTCDay()];
}

/**
 * Parse a single WELLNESS.fit file
 */
function parseWellnessFile(filePath) {
    return new Promise((resolve, reject) => {
        const parser = new FitParser();
        const fitFile = fs.readFileSync(filePath);

        parser.parse(fitFile, (error, data) => {
            if (error) {
                reject(error);
                return;
            }

            const records = [];
            const dataByTimestamp = {};

            // Extract from 'monitors' section (contains heart rate, steps, calories, etc.)
            if (data.monitors && data.monitors.length > 0) {
                data.monitors.forEach(record => {
                    if (!record.timestamp) return;

                    const utcDate = new Date(record.timestamp);
                    const estDate = convertToEST(utcDate);
                    const dateTime = formatDateTime(estDate);
                    const key = dateTime.datetime;

                    if (!dataByTimestamp[key]) {
                        dataByTimestamp[key] = {
                            ...dateTime,
                            day_of_week: getDayOfWeek(estDate),
                            heart_rate: null,
                            stress_level: null,
                            body_battery: null,
                            respiration_rate: null,
                            steps_cumulative: null,
                            calories_cumulative: null,
                            distance_meters_cumulative: null
                        };
                    }

                    // Extract metrics from monitors
                    if (record.heart_rate !== undefined && record.heart_rate !== null) {
                        dataByTimestamp[key].heart_rate = record.heart_rate;
                    }
                    if (record.steps !== undefined && record.steps !== null) {
                        dataByTimestamp[key].steps_cumulative = record.steps;
                    }
                    if (record.calories !== undefined && record.calories !== null) {
                        dataByTimestamp[key].calories_cumulative = record.calories;
                    }
                    if (record.distance !== undefined && record.distance !== null) {
                        dataByTimestamp[key].distance_meters_cumulative = record.distance;
                    }
                    if (record.respiration_rate !== undefined && record.respiration_rate !== null) {
                        dataByTimestamp[key].respiration_rate = record.respiration_rate;
                    }
                });
            }

            // Extract from 'stress' section (contains stress level and body battery)
            if (data.stress && data.stress.length > 0) {
                data.stress.forEach(record => {
                    if (!record.stress_level_time && !record.timestamp) return;

                    const timestamp = record.stress_level_time || record.timestamp;
                    const utcDate = new Date(timestamp);
                    const estDate = convertToEST(utcDate);
                    const dateTime = formatDateTime(estDate);
                    const key = dateTime.datetime;

                    if (!dataByTimestamp[key]) {
                        dataByTimestamp[key] = {
                            ...dateTime,
                            day_of_week: getDayOfWeek(estDate),
                            heart_rate: null,
                            stress_level: null,
                            body_battery: null,
                            respiration_rate: null,
                            steps_cumulative: null,
                            calories_cumulative: null,
                            distance_meters_cumulative: null
                        };
                    }

                    // Extract stress level
                    if (record.stress_level_value !== undefined && record.stress_level_value !== null) {
                        let stressLevel = record.stress_level_value;
                        // Filter stress values > 100
                        if (stressLevel > STRESS_THRESHOLD) {
                            stressLevel = null;
                        }
                        dataByTimestamp[key].stress_level = stressLevel;
                    }

                    // Extract body battery
                    if (record.body_battery !== undefined && record.body_battery !== null) {
                        dataByTimestamp[key].body_battery = record.body_battery;
                    }
                });
            }

            // Convert to array
            Object.values(dataByTimestamp).forEach(record => records.push(record));

            resolve(records);
        });
    });
}

/**
 * Process all date folders
 */
async function processAllDates() {
    const dateFolders = fs.readdirSync(GARMIN_DATA_DIR)
        .filter(name => {
            const fullPath = path.join(GARMIN_DATA_DIR, name);
            return fs.statSync(fullPath).isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(name);
        })
        .sort();

    console.log(`📅 Found ${dateFolders.length} date folders to process\n`);

    for (const dateFolder of dateFolders) {
        const datePath = path.join(GARMIN_DATA_DIR, dateFolder);
        const files = fs.readdirSync(datePath);
        const wellnessFiles = files.filter(f => f.includes('WELLNESS.fit'));

        console.log(`Processing ${dateFolder}: ${wellnessFiles.length} WELLNESS files`);

        for (const wellnessFile of wellnessFiles) {
            const filePath = path.join(datePath, wellnessFile);

            try {
                const records = await parseWellnessFile(filePath);
                allMinuteData.push(...records);
                totalFilesProcessed++;
                totalRecordsExtracted += records.length;
            } catch (error) {
                console.error(`  ❌ Error parsing ${wellnessFile}:`, error.message);
            }
        }
    }
}

/**
 * Consolidate duplicate timestamps (take first non-null value)
 */
function consolidateData() {
    console.log('\n📊 Consolidating duplicate timestamps...');

    const consolidated = {};

    allMinuteData.forEach(record => {
        const key = record.datetime;

        if (!consolidated[key]) {
            consolidated[key] = { ...record };
        } else {
            // Merge: take first non-null value for each field
            Object.keys(record).forEach(field => {
                if (consolidated[key][field] === null && record[field] !== null) {
                    consolidated[key][field] = record[field];
                }
            });
        }
    });

    return Object.values(consolidated).sort((a, b) =>
        a.datetime.localeCompare(b.datetime)
    );
}

/**
 * Calculate per-minute deltas for cumulative metrics
 */
function calculateDeltas(data) {
    console.log('🔢 Calculating per-minute deltas...');

    for (let i = 0; i < data.length; i++) {
        if (i === 0) {
            data[i].steps_per_minute = null;
            data[i].calories_per_minute = null;
        } else {
            // Only calculate delta if same date (don't cross midnight)
            if (data[i].date === data[i - 1].date) {
                const stepsDelta = (data[i].steps_cumulative !== null && data[i - 1].steps_cumulative !== null)
                    ? data[i].steps_cumulative - data[i - 1].steps_cumulative
                    : null;

                const caloriesDelta = (data[i].calories_cumulative !== null && data[i - 1].calories_cumulative !== null)
                    ? data[i].calories_cumulative - data[i - 1].calories_cumulative
                    : null;

                data[i].steps_per_minute = stepsDelta;
                data[i].calories_per_minute = caloriesDelta;
            } else {
                // New day, reset deltas
                data[i].steps_per_minute = null;
                data[i].calories_per_minute = null;
            }
        }
    }

    return data;
}

/**
 * Write data to CSV
 */
function writeCSV(data) {
    console.log(`\n💾 Writing to ${OUTPUT_FILE}...`);

    const headers = [
        'datetime',
        'date',
        'time',
        'hour',
        'minute',
        'day_of_week',
        'heart_rate',
        'stress_level',
        'body_battery',
        'respiration_rate',
        'steps_cumulative',
        'calories_cumulative',
        'distance_meters_cumulative',
        'steps_per_minute',
        'calories_per_minute'
    ];

    let csv = headers.join(',') + '\n';

    data.forEach(record => {
        const row = headers.map(header => {
            const value = record[header];
            return value !== null && value !== undefined ? value : '';
        });
        csv += row.join(',') + '\n';
    });

    fs.writeFileSync(OUTPUT_FILE, csv);
}

/**
 * Print summary statistics
 */
function printSummary(data) {
    console.log('\n' + '='.repeat(60));
    console.log('✅ PARSING COMPLETE');
    console.log('='.repeat(60));
    console.log(`📁 Files processed: ${totalFilesProcessed}`);
    console.log(`📊 Total records extracted: ${totalRecordsExtracted}`);
    console.log(`🔄 Consolidated records: ${data.length}`);

    const dateRange = {
        start: data[0]?.date,
        end: data[data.length - 1]?.date
    };
    console.log(`📅 Date range: ${dateRange.start} to ${dateRange.end}`);

    // Calculate coverage
    const coverage = {
        heart_rate: data.filter(r => r.heart_rate !== null).length,
        stress_level: data.filter(r => r.stress_level !== null).length,
        body_battery: data.filter(r => r.body_battery !== null).length,
        steps: data.filter(r => r.steps_cumulative !== null).length
    };

    console.log('\n📈 Data Coverage:');
    console.log(`   Heart Rate: ${(coverage.heart_rate / data.length * 100).toFixed(1)}%`);
    console.log(`   Stress Level: ${(coverage.stress_level / data.length * 100).toFixed(1)}%`);
    console.log(`   Body Battery: ${(coverage.body_battery / data.length * 100).toFixed(1)}%`);
    console.log(`   Steps: ${(coverage.steps / data.length * 100).toFixed(1)}%`);

    console.log(`\n💾 Output file: ${OUTPUT_FILE}`);
    console.log('='.repeat(60));
}

/**
 * Main execution
 */
async function main() {
    try {
        await processAllDates();
        const consolidated = consolidateData();
        const withDeltas = calculateDeltas(consolidated);
        writeCSV(withDeltas);
        printSummary(withDeltas);
    } catch (error) {
        console.error('\n❌ Fatal error:', error);
        process.exit(1);
    }
}

// Run
main();
