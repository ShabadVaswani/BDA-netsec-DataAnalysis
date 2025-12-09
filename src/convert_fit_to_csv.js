const FitParser = require('fit-file-parser').default;
const fs = require('fs');
const path = require('path');

/**
 * Convert all FIT files to CSV format, preserving original structure
 * Creates separate CSV files for each FIT file and each record type within
 */

console.log('🔄 Converting FIT files to CSV...\n');

const GARMIN_DATA_DIR = './data/garmin';
const OUTPUT_DIR = './output/garmin_raw_csv';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const fitParser = new FitParser({
    force: true,
    speedUnit: 'km/h',
    lengthUnit: 'km',
    temperatureUnit: 'celsius',
    elapsedRecordField: true,
    mode: 'both'
});

let totalFilesProcessed = 0;
let totalCSVsCreated = 0;

/**
 * Convert a single FIT file to CSV(s)
 */
function convertFitToCSV(fitFilePath, outputBasePath) {
    return new Promise((resolve, reject) => {
        const fileBuffer = fs.readFileSync(fitFilePath);

        fitParser.parse(fileBuffer, (error, data) => {
            if (error) {
                reject(error);
                return;
            }

            const csvFiles = [];

            // Process each record type
            Object.keys(data).forEach(recordType => {
                if (Array.isArray(data[recordType]) && data[recordType].length > 0) {
                    const records = data[recordType];

                    // Get all unique fields across all records
                    const allFields = new Set();
                    records.forEach(record => {
                        Object.keys(record).forEach(field => allFields.add(field));
                    });

                    const fields = Array.from(allFields).sort();

                    // Create CSV content
                    let csv = fields.join(',') + '\n';

                    records.forEach(record => {
                        const row = fields.map(field => {
                            const value = record[field];

                            // Handle different data types
                            if (value === null || value === undefined) {
                                return '';
                            } else if (typeof value === 'string') {
                                // Escape commas and quotes in strings
                                return `"${value.replace(/"/g, '""')}"`;
                            } else if (value instanceof Date) {
                                return value.toISOString();
                            } else if (typeof value === 'object') {
                                return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
                            } else {
                                return value;
                            }
                        });
                        csv += row.join(',') + '\n';
                    });

                    // Write CSV file
                    const csvFileName = `${outputBasePath}_${recordType}.csv`;
                    fs.writeFileSync(csvFileName, csv);
                    csvFiles.push({
                        type: recordType,
                        file: csvFileName,
                        records: records.length
                    });
                    totalCSVsCreated++;
                }
            });

            resolve(csvFiles);
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

    console.log(`📅 Found ${dateFolders.length} date folders\n`);

    for (const dateFolder of dateFolders) {
        const datePath = path.join(GARMIN_DATA_DIR, dateFolder);
        const dateOutputDir = path.join(OUTPUT_DIR, dateFolder);

        // Create date-specific output directory
        if (!fs.existsSync(dateOutputDir)) {
            fs.mkdirSync(dateOutputDir, { recursive: true });
        }

        const files = fs.readdirSync(datePath);
        const fitFiles = files.filter(f => f.endsWith('.fit'));

        console.log(`Processing ${dateFolder}: ${fitFiles.length} FIT files`);

        for (const fitFile of fitFiles) {
            const fitFilePath = path.join(datePath, fitFile);
            const baseName = fitFile.replace('.fit', '');
            const outputBasePath = path.join(dateOutputDir, baseName);

            try {
                const csvFiles = await convertFitToCSV(fitFilePath, outputBasePath);
                console.log(`  ✓ ${fitFile}: ${csvFiles.length} record types`);
                totalFilesProcessed++;
            } catch (error) {
                console.error(`  ✗ ${fitFile}: ${error.message}`);
            }
        }
    }
}

/**
 * Main execution
 */
async function main() {
    try {
        await processAllDates();

        console.log('\n' + '='.repeat(60));
        console.log('✅ CONVERSION COMPLETE');
        console.log('='.repeat(60));
        console.log(`📁 FIT files processed: ${totalFilesProcessed}`);
        console.log(`📊 CSV files created: ${totalCSVsCreated}`);
        console.log(`💾 Output directory: ${OUTPUT_DIR}`);
        console.log('='.repeat(60));
    } catch (error) {
        console.error('\n❌ Fatal error:', error);
        process.exit(1);
    }
}

// Run
main();
