const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Find Stress and Body Battery Data
 * Investigates all FIT files to locate stress and body battery fields
 */

const garminDir = path.join(__dirname, '..', 'data', 'garmin', '2025-11-18 (1)');

console.log('=== Finding Stress and Body Battery Data ===\n');

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

let stressFound = false;
let bodyBatteryFound = false;
let stressFieldName = null;
let bodyBatteryFieldName = null;
let sampleStressRecord = null;
let sampleBodyBatteryRecord = null;

let filesChecked = 0;

wellnessFiles.forEach((filename) => {
    const filePath = path.join(garminDir, filename);
    const fileBuffer = fs.readFileSync(filePath);

    fitParser.parse(fileBuffer, (error, data) => {
        if (error) {
            filesChecked++;
            return;
        }

        // Check all possible data arrays
        const sectionsToCheck = ['monitors', 'monitoring', 'stress', 'records', 'sessions'];

        sectionsToCheck.forEach(section => {
            if (data[section] && Array.isArray(data[section]) && data[section].length > 0) {
                data[section].forEach(record => {
                    const fields = Object.keys(record);

                    // Look for stress-related fields
                    fields.forEach(field => {
                        const fieldLower = field.toLowerCase();
                        const value = record[field];

                        // Check for stress
                        if (fieldLower.includes('stress') && value !== null && value !== undefined) {
                            if (!stressFound) {
                                stressFound = true;
                                stressFieldName = field;
                                sampleStressRecord = {
                                    file: filename,
                                    section: section,
                                    field: field,
                                    value: value,
                                    timestamp: record.timestamp || record.stress_level_time,
                                    fullRecord: record
                                };
                            }
                        }

                        // Check for body battery
                        if ((fieldLower.includes('body') && fieldLower.includes('battery')) ||
                            fieldLower.includes('bodybattery') ||
                            fieldLower.includes('body_battery')) {
                            if (value !== null && value !== undefined) {
                                if (!bodyBatteryFound) {
                                    bodyBatteryFound = true;
                                    bodyBatteryFieldName = field;
                                    sampleBodyBatteryRecord = {
                                        file: filename,
                                        section: section,
                                        field: field,
                                        value: value,
                                        timestamp: record.timestamp,
                                        fullRecord: record
                                    };
                                }
                            }
                        }
                    });
                });
            }
        });

        filesChecked++;

        if (filesChecked === wellnessFiles.length) {
            reportFindings();
        }
    });
});

function reportFindings() {
    console.log('='.repeat(70));
    console.log('INVESTIGATION RESULTS');
    console.log('='.repeat(70));

    // STRESS DATA
    console.log('\n🔍 STRESS DATA:');
    if (stressFound) {
        console.log('  ✅ FOUND!');
        console.log(`  📍 Location: ${sampleStressRecord.section} array`);
        console.log(`  🏷️  Field Name: "${stressFieldName}"`);
        console.log(`  📊 Sample Value: ${sampleStressRecord.value}`);
        console.log(`  📅 Timestamp: ${sampleStressRecord.timestamp}`);
        console.log(`  📁 Found in: ${sampleStressRecord.file}`);
        console.log('\n  Full Sample Record:');
        console.log('  ' + JSON.stringify(sampleStressRecord.fullRecord, null, 2).split('\n').join('\n  '));
    } else {
        console.log('  ❌ NOT FOUND');
        console.log('  → No fields containing "stress" with non-null values');
    }

    // BODY BATTERY DATA
    console.log('\n🔍 BODY BATTERY DATA:');
    if (bodyBatteryFound) {
        console.log('  ✅ FOUND!');
        console.log(`  📍 Location: ${sampleBodyBatteryRecord.section} array`);
        console.log(`  🏷️  Field Name: "${bodyBatteryFieldName}"`);
        console.log(`  📊 Sample Value: ${sampleBodyBatteryRecord.value}`);
        console.log(`  📅 Timestamp: ${sampleBodyBatteryRecord.timestamp}`);
        console.log(`  📁 Found in: ${sampleBodyBatteryRecord.file}`);
        console.log('\n  Full Sample Record:');
        console.log('  ' + JSON.stringify(sampleBodyBatteryRecord.fullRecord, null, 2).split('\n').join('\n  '));
    } else {
        console.log('  ❌ NOT FOUND');
        console.log('  → No fields containing "body" and "battery" with non-null values');
    }

    // SUMMARY
    console.log('\n' + '='.repeat(70));
    console.log('SUMMARY');
    console.log('='.repeat(70));

    if (stressFound && bodyBatteryFound) {
        console.log('\n✅ SUCCESS: Both stress and body battery data found!');
        console.log('\n📝 To use in parser, update field names:');
        console.log(`  - Stress: record.${stressFieldName}`);
        console.log(`  - Body Battery: record.${bodyBatteryFieldName}`);
        console.log(`  - Data location: data.${sampleStressRecord.section}`);
    } else if (stressFound) {
        console.log('\n⚠️  PARTIAL: Only stress data found');
        console.log(`  - Use: record.${stressFieldName}`);
    } else if (bodyBatteryFound) {
        console.log('\n⚠️  PARTIAL: Only body battery data found');
        console.log(`  - Use: record.${bodyBatteryFieldName}`);
    } else {
        console.log('\n❌ FAILURE: Neither stress nor body battery data found');
        console.log('\n🔍 Possible reasons:');
        console.log('  1. Data might be in a different section');
        console.log('  2. Field names might be different');
        console.log('  3. Data might not be recorded by your device');
    }

    // Save detailed report
    const report = {
        stress: stressFound ? {
            found: true,
            field_name: stressFieldName,
            section: sampleStressRecord.section,
            sample_value: sampleStressRecord.value,
            sample_timestamp: sampleStressRecord.timestamp,
            sample_file: sampleStressRecord.file,
            full_record: sampleStressRecord.fullRecord
        } : { found: false },
        body_battery: bodyBatteryFound ? {
            found: true,
            field_name: bodyBatteryFieldName,
            section: sampleBodyBatteryRecord.section,
            sample_value: sampleBodyBatteryRecord.value,
            sample_timestamp: sampleBodyBatteryRecord.timestamp,
            sample_file: sampleBodyBatteryRecord.file,
            full_record: sampleBodyBatteryRecord.fullRecord
        } : { found: false }
    };

    const outputPath = path.join(__dirname, '..', 'output', 'garmin_parsed', 'stress_battery_report.json');
    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Detailed report saved to: ${outputPath}`);

    console.log('\n' + '='.repeat(70));
}
