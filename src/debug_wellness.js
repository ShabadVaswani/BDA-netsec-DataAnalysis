const FitParser = require('fit-file-parser').default;
const fs = require('fs');

// Debug: Check what's actually in a WELLNESS file
const testFile = './data/garmin/2025-11-18/383443983790_WELLNESS.fit';

console.log(`Debugging file: ${testFile}\n`);

const parser = new FitParser();
const fitFile = fs.readFileSync(testFile);

parser.parse(fitFile, (error, data) => {
    if (error) {
        console.error('Parse error:', error);
        return;
    }

    console.log('=== Available record types ===');
    Object.keys(data).forEach(key => {
        if (Array.isArray(data[key]) && data[key].length > 0) {
            console.log(`${key}: ${data[key].length} records`);
        }
    });

    console.log('\n=== Sample monitoring record ===');
    if (data.monitoring && data.monitoring.length > 0) {
        console.log(JSON.stringify(data.monitoring[0], null, 2));
        console.log('\nAll fields in monitoring records:');
        const allFields = new Set();
        data.monitoring.forEach(r => Object.keys(r).forEach(k => allFields.add(k)));
        console.log(Array.from(allFields).sort().join(', '));
    } else {
        console.log('NO MONITORING DATA FOUND');
    }

    console.log('\n=== Checking other record types ===');
    ['records', 'monitoring_info', 'monitoring_hr_data', 'stress_level', 'monitoring_b2b'].forEach(type => {
        if (data[type] && data[type].length > 0) {
            console.log(`\n${type}:`);
            console.log(JSON.stringify(data[type][0], null, 2));
        }
    });
});
