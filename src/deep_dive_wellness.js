const FitParser = require('fit-file-parser').default;
const fs = require('fs');

const testFile = './data/garmin/2025-11-05/380127734123_WELLNESS.fit';
const parser = new FitParser({ force: true, mode: 'both' });
const fitFile = fs.readFileSync(testFile);

parser.parse(fitFile, (error, data) => {
    if (error) return console.error(error);

    console.log('=== CHECKING KEY VARIATIONS ===');

    function checkKeys(arrayName, array) {
        if (!array || array.length === 0) return;

        const keySets = new Set();
        const limit = Math.min(array.length, 50);

        for (let i = 0; i < limit; i++) {
            const keys = Object.keys(array[i]).sort().join(',');
            keySets.add(keys);
        }

        console.log(`\n[${arrayName}] Unique key sets in first ${limit} records:`);
        keySets.forEach(k => console.log(`- ${k}`));
    }

    checkKeys('stress', data.stress);
    checkKeys('monitors', data.monitors);
});
