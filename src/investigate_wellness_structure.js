const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Investigate WELLNESS files to find where health data is stored
 */

const garminDir = './data/garmin/2025-11-18';

console.log('=== Investigating WELLNESS File Structure ===\n');

const fitParser = new FitParser({
    force: true,
    speedUnit: 'km/h',
    lengthUnit: 'km',
    temperatureUnit: 'celsius',
    elapsedRecordField: true,
    mode: 'both'
});

const files = fs.readdirSync(garminDir);
const wellnessFiles = files.filter(f => f.includes('WELLNESS'));

console.log(`Checking ${wellnessFiles.length} WELLNESS files...\n`);

// Take first file as sample
const sampleFile = wellnessFiles[0];
const filePath = path.join(garminDir, sampleFile);
const fileBuffer = fs.readFileSync(filePath);

fitParser.parse(fileBuffer, (error, data) => {
    if (error) {
        console.error('Parse error:', error);
        return;
    }

    console.log(`File: ${sampleFile}\n`);
    console.log('='.repeat(70));
    console.log('AVAILABLE DATA SECTIONS');
    console.log('='.repeat(70));

    // List all sections with their record counts
    Object.keys(data).forEach(key => {
        if (Array.isArray(data[key])) {
            const count = data[key].length;
            if (count > 0) {
                console.log(`✓ ${key}: ${count} records`);
            }
        }
    });

    console.log('\n' + '='.repeat(70));
    console.log('DETAILED INSPECTION');
    console.log('='.repeat(70));

    // Check specific sections that might contain health data
    const sectionsToInspect = [
        'monitoring', 'monitors', 'monitoring_info', 'monitoring_hr_data',
        'stress', 'stress_level', 'stress_level_values',
        'records', 'sessions', 'monitoring_b2b'
    ];

    sectionsToInspect.forEach(section => {
        if (data[section] && Array.isArray(data[section]) && data[section].length > 0) {
            console.log(`\n--- ${section.toUpperCase()} (${data[section].length} records) ---`);

            // Show first record
            console.log('\nFirst record:');
            console.log(JSON.stringify(data[section][0], null, 2));

            // Show all unique fields
            const allFields = new Set();
            data[section].forEach(record => {
                Object.keys(record).forEach(field => allFields.add(field));
            });
            console.log('\nAll available fields:');
            console.log(Array.from(allFields).sort().join(', '));

            // Check for specific health metrics
            const hasHeartRate = data[section].some(r => r.heart_rate !== undefined && r.heart_rate !== null);
            const hasStress = data[section].some(r => {
                const keys = Object.keys(r);
                return keys.some(k => k.toLowerCase().includes('stress') && r[k] !== null && r[k] !== undefined);
            });
            const hasBodyBattery = data[section].some(r => {
                const keys = Object.keys(r);
                return keys.some(k => k.toLowerCase().includes('body') && k.toLowerCase().includes('battery') && r[k] !== null && r[k] !== undefined);
            });

            console.log('\nHealth metrics found:');
            console.log(`  Heart Rate: ${hasHeartRate ? '✓' : '✗'}`);
            console.log(`  Stress: ${hasStress ? '✓' : '✗'}`);
            console.log(`  Body Battery: ${hasBodyBattery ? '✓' : '✗'}`);
        }
    });

    console.log('\n' + '='.repeat(70));
});
