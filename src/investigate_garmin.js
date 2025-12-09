const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Investigate Garmin FIT file structure
 * Analyze all WELLNESS files to understand unknown fields
 */

const garminDir = path.join(__dirname, '..', 'data', 'garmin', '2025-11-18 (1)');

console.log('=== Garmin FIT Data Investigation ===\n');

const fitParser = new FitParser({
    force: true,
    speedUnit: 'km/h',
    lengthUnit: 'km',
    temperatureUnit: 'celsius',
    elapsedRecordField: true,
    mode: 'both'
});

// Get all WELLNESS files
const files = fs.readdirSync(garminDir);
const wellnessFiles = files.filter(f => f.includes('WELLNESS'));

console.log(`Found ${wellnessFiles.length} WELLNESS files\n`);

// Collect all data
let allMonitors = [];
let allStress = [];
let allFieldNames = new Set();

wellnessFiles.forEach((filename, idx) => {
    const filePath = path.join(garminDir, filename);
    const fileBuffer = fs.readFileSync(filePath);

    fitParser.parse(fileBuffer, (error, data) => {
        if (error) {
            console.error(`Error parsing ${filename}:`, error);
            return;
        }

        // Collect monitors data
        if (data.monitors && data.monitors.length > 0) {
            allMonitors = allMonitors.concat(data.monitors);

            // Collect all field names
            data.monitors.forEach(record => {
                Object.keys(record).forEach(key => allFieldNames.add(key));
            });
        }

        // Collect stress data
        if (data.stress && data.stress.length > 0) {
            allStress = allStress.concat(data.stress);
        }

        // After processing all files
        if (idx === wellnessFiles.length - 1) {
            setTimeout(() => analyzeData(), 100);
        }
    });
});

function analyzeData() {
    console.log('='.repeat(70));
    console.log('DATA ANALYSIS RESULTS');
    console.log('='.repeat(70));

    console.log(`\n📊 Total Records Collected:`);
    console.log(`  - Monitor records: ${allMonitors.length}`);
    console.log(`  - Stress records: ${allStress.length}`);

    // Analyze monitor fields
    console.log(`\n🔍 All Fields Found in Monitors:`);
    const sortedFields = Array.from(allFieldNames).sort();
    sortedFields.forEach(field => console.log(`  - ${field}`));

    // Analyze field values
    console.log(`\n📈 Field Value Analysis:`);

    sortedFields.forEach(field => {
        const values = allMonitors
            .map(r => r[field])
            .filter(v => v !== null && v !== undefined);

        if (values.length === 0) return;

        const uniqueValues = [...new Set(values)];
        const numericValues = values.filter(v => typeof v === 'number');

        console.log(`\n  ${field}:`);
        console.log(`    - Total values: ${values.length}`);
        console.log(`    - Unique values: ${uniqueValues.length}`);

        if (numericValues.length > 0) {
            const min = Math.min(...numericValues);
            const max = Math.max(...numericValues);
            const avg = numericValues.reduce((a, b) => a + b, 0) / numericValues.length;

            console.log(`    - Type: numeric`);
            console.log(`    - Range: ${min} to ${max}`);
            console.log(`    - Average: ${avg.toFixed(2)}`);

            // Show distribution for small unique sets
            if (uniqueValues.length <= 20) {
                const distribution = {};
                values.forEach(v => {
                    distribution[v] = (distribution[v] || 0) + 1;
                });
                console.log(`    - Distribution:`, distribution);
            }
        } else {
            console.log(`    - Type: ${typeof values[0]}`);
            if (uniqueValues.length <= 10) {
                console.log(`    - Unique values:`, uniqueValues);
            }
        }
    });

    // Sample records
    console.log(`\n📝 Sample Monitor Records (first 5):`);
    console.log('='.repeat(70));
    allMonitors.slice(0, 5).forEach((record, idx) => {
        console.log(`\nRecord ${idx + 1}:`);
        console.log(JSON.stringify(record, null, 2));
    });

    // Sample stress records
    if (allStress.length > 0) {
        console.log(`\n📝 Sample Stress Records (first 3):`);
        console.log('='.repeat(70));
        allStress.slice(0, 3).forEach((record, idx) => {
            console.log(`\nRecord ${idx + 1}:`);
            console.log(JSON.stringify(record, null, 2));
        });
    }

    // Time range analysis
    const timestamps = allMonitors
        .map(r => r.timestamp)
        .filter(t => t)
        .sort();

    if (timestamps.length > 0) {
        console.log(`\n⏰ Time Range:`);
        console.log(`  - First record: ${timestamps[0]}`);
        console.log(`  - Last record: ${timestamps[timestamps.length - 1]}`);
        console.log(`  - Duration: ${timestamps.length} records`);
    }

    // Check for heart rate
    console.log(`\n❤️  Heart Rate Check:`);
    const hrFields = sortedFields.filter(f =>
        f.toLowerCase().includes('heart') ||
        f.toLowerCase().includes('hr') ||
        f.toLowerCase().includes('bpm')
    );

    if (hrFields.length > 0) {
        console.log(`  ✓ Found heart rate fields: ${hrFields.join(', ')}`);
    } else {
        console.log(`  ✗ No obvious heart rate fields found`);
        console.log(`  → Check METRICS files for heart rate data`);
    }

    // Save analysis results
    const results = {
        summary: {
            total_monitors: allMonitors.length,
            total_stress: allStress.length,
            fields: sortedFields,
            time_range: {
                start: timestamps[0],
                end: timestamps[timestamps.length - 1]
            }
        },
        sample_monitors: allMonitors.slice(0, 10),
        sample_stress: allStress.slice(0, 10)
    };

    const outputPath = path.join(__dirname, '..', 'output', 'garmin_parsed', 'investigation_results.json');
    fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
    console.log(`\n✓ Full results saved to: ${outputPath}`);

    console.log('\n' + '='.repeat(70));
    console.log('INVESTIGATION COMPLETE');
    console.log('='.repeat(70));
}
