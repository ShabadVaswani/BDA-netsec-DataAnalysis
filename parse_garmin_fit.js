const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Parse Garmin FIT files and display their structure
 */

const garminDir = path.join(__dirname, 'downloads', '2025-11-18 (1)');
const outputDir = path.join(__dirname, 'garmin_parsed');

// Create output directory
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

console.log('=== Garmin FIT File Parser ===\n');

// Get sample files of each type
const files = fs.readdirSync(garminDir);
const wellnessFile = files.find(f => f.includes('WELLNESS'));
const sleepFile = files.find(f => f.includes('SLEEP_DATA'));
const metricsFile = files.find(f => f.includes('METRICS'));

const sampleFiles = [
    { name: wellnessFile, type: 'WELLNESS' },
    { name: sleepFile, type: 'SLEEP_DATA' },
    { name: metricsFile, type: 'METRICS' }
];

const fitParser = new FitParser({
    force: true,
    speedUnit: 'km/h',
    lengthUnit: 'km',
    temperatureUnit: 'celsius',
    elapsedRecordField: true,
    mode: 'both'
});

sampleFiles.forEach(({ name, type }) => {
    if (!name) {
        console.log(`⚠ No ${type} file found\n`);
        return;
    }

    console.log(`\n${'='.repeat(70)}`);
    console.log(`Parsing: ${name}`);
    console.log(`Type: ${type}`);
    console.log('='.repeat(70));

    const filePath = path.join(garminDir, name);
    const fileBuffer = fs.readFileSync(filePath);

    fitParser.parse(fileBuffer, (error, data) => {
        if (error) {
            console.error(`✗ Error parsing ${name}:`, error);
            return;
        }

        console.log('\n📊 Data Structure:\n');

        // Show available data sections
        console.log('Available sections:');
        Object.keys(data).forEach(key => {
            if (Array.isArray(data[key])) {
                console.log(`  - ${key}: ${data[key].length} records`);
            } else if (typeof data[key] === 'object') {
                console.log(`  - ${key}: object`);
            } else {
                console.log(`  - ${key}: ${data[key]}`);
            }
        });

        // Show sample records from main data sections
        const recordSections = ['records', 'monitoring', 'sleep', 'sessions', 'laps', 'events'];

        recordSections.forEach(section => {
            if (data[section] && data[section].length > 0) {
                console.log(`\n📝 ${section.toUpperCase()} (showing first 3 records):`);
                console.log('-'.repeat(70));

                const samples = data[section].slice(0, 3);
                samples.forEach((record, idx) => {
                    console.log(`\nRecord ${idx + 1}:`);
                    console.log(JSON.stringify(record, null, 2));
                });

                // Show all available fields
                const allFields = new Set();
                data[section].forEach(record => {
                    Object.keys(record).forEach(field => allFields.add(field));
                });
                console.log(`\nAll available fields in ${section}:`);
                console.log(Array.from(allFields).sort().join(', '));
            }
        });

        // Save full parsed data to JSON
        const outputFile = path.join(outputDir, `${type}_parsed.json`);
        fs.writeFileSync(outputFile, JSON.stringify(data, null, 2));
        console.log(`\n✓ Full data saved to: ${outputFile}`);

        // Create CSV for main data section
        const mainSection = data.records || data.monitoring || data.sleep || [];
        if (mainSection.length > 0) {
            const csvFile = path.join(outputDir, `${type}_data.csv`);

            // Get all unique fields
            const fields = new Set();
            mainSection.forEach(record => {
                Object.keys(record).forEach(field => fields.add(field));
            });
            const fieldArray = Array.from(fields).sort();

            // Create CSV
            const csvLines = [];
            csvLines.push(fieldArray.join(','));

            mainSection.forEach(record => {
                const values = fieldArray.map(field => {
                    const value = record[field];
                    if (value === null || value === undefined) return '';
                    if (typeof value === 'object') return JSON.stringify(value);
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                });
                csvLines.push(values.join(','));
            });

            fs.writeFileSync(csvFile, csvLines.join('\n'));
            console.log(`✓ CSV saved to: ${csvFile}`);
            console.log(`  Records: ${mainSection.length}`);
            console.log(`  Fields: ${fieldArray.length}`);
        }
    });
});

console.log('\n' + '='.repeat(70));
console.log('✓ Parsing complete!');
console.log(`📁 Output directory: ${outputDir}`);
console.log('='.repeat(70));
