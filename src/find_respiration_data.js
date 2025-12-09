const FitParser = require('fit-file-parser').default;
const fs = require('fs');

/**
 * Deep investigation of FIT file structure to find respiration data
 */

const testFile = './data/garmin/2025-11-18/383443983790_WELLNESS.fit';

console.log('🔍 Deep Investigation of FIT File Structure\n');
console.log(`File: ${testFile}\n`);

const parser = new FitParser({
    force: true,
    speedUnit: 'km/h',
    lengthUnit: 'km',
    temperatureUnit: 'celsius',
    elapsedRecordField: true,
    mode: 'both'
});

const fitFile = fs.readFileSync(testFile);

parser.parse(fitFile, (error, data) => {
    if (error) {
        console.error('Parse error:', error);
        return;
    }

    console.log('='.repeat(70));
    console.log('ALL RECORD TYPES IN FILE');
    console.log('='.repeat(70));

    // List ALL record types
    const allTypes = Object.keys(data).filter(key => {
        return Array.isArray(data[key]) && data[key].length > 0;
    });

    allTypes.forEach(type => {
        console.log(`\n${type}: ${data[type].length} records`);
    });

    console.log('\n' + '='.repeat(70));
    console.log('SEARCHING FOR RESPIRATION DATA');
    console.log('='.repeat(70));

    // Search for respiration in all record types
    let respirationFound = false;

    allTypes.forEach(type => {
        const records = data[type];

        // Check if any record has respiration-related fields
        records.forEach((record, idx) => {
            Object.keys(record).forEach(field => {
                if (field.toLowerCase().includes('respir')) {
                    if (!respirationFound) {
                        console.log(`\n✓ FOUND RESPIRATION DATA!`);
                        console.log(`  Location: data.${type}[${idx}]`);
                        console.log(`  Field: ${field}`);
                        console.log(`  Value: ${record[field]}`);
                        console.log(`\n  Full record:`);
                        console.log(JSON.stringify(record, null, 2));
                        respirationFound = true;
                    }
                }
            });
        });
    });

    if (!respirationFound) {
        console.log('\n❌ No respiration fields found in standard field names');
        console.log('\nChecking for unnamed/generic fields that might contain respiration...\n');

        // Check each record type for patterns
        allTypes.forEach(type => {
            console.log(`\n--- ${type.toUpperCase()} ---`);
            if (data[type].length > 0) {
                console.log('First record:');
                console.log(JSON.stringify(data[type][0], null, 2));

                console.log('\nAll unique fields:');
                const allFields = new Set();
                data[type].forEach(r => Object.keys(r).forEach(k => allFields.add(k)));
                console.log(Array.from(allFields).sort().join(', '));
            }
        });
    }

    console.log('\n' + '='.repeat(70));
});
