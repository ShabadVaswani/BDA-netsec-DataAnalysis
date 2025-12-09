const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

// Find and parse all METRICS.fit files
const garminDir = './data/garmin/2025-11-18';
const files = fs.readdirSync(garminDir);
const metricsFiles = files.filter(f => f.includes('METRICS.fit'));

console.log(`Found ${metricsFiles.length} METRICS.fit files\n`);

metricsFiles.forEach((filename, index) => {
    const filePath = path.join(garminDir, filename);
    const parser = new FitParser();
    const fitFile = fs.readFileSync(filePath);

    console.log(`\n${'='.repeat(70)}`);
    console.log(`FILE ${index + 1}: ${filename}`);
    console.log('='.repeat(70));

    parser.parse(fitFile, (error, data) => {
        if (error) {
            console.error('Parse error:', error);
            return;
        }

        // List all record types
        const recordTypes = Object.keys(data).filter(k => Array.isArray(data[k]) && data[k].length > 0);
        console.log(`\nRecord types: ${recordTypes.join(', ')}`);

        // Show monitoring_info if it exists
        if (data.monitoring_info && data.monitoring_info.length > 0) {
            console.log('\n--- MONITORING_INFO ---');
            data.monitoring_info.forEach(record => {
                console.log(JSON.stringify(record, null, 2));
            });
        }

        // Show monitoring if it exists
        if (data.monitoring && data.monitoring.length > 0) {
            console.log('\n--- MONITORING (first 3 records) ---');
            data.monitoring.slice(0, 3).forEach(record => {
                console.log(JSON.stringify(record, null, 2));
            });
            console.log(`\n... (${data.monitoring.length} total monitoring records)`);
        }

        // Show any other record types
        recordTypes.forEach(type => {
            if (type !== 'monitoring_info' && type !== 'monitoring' && type !== 'file_id') {
                console.log(`\n--- ${type.toUpperCase()} ---`);
                console.log(JSON.stringify(data[type][0], null, 2));
            }
        });
    });
});
