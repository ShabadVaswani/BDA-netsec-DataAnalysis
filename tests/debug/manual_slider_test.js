const { chromium } = require('playwright');

/**
 * Manual test: Open page and let user manually move slider to see if data changes
 */
async function manualSliderTest() {
    console.log('=== Manual Slider Test ===\n');
    console.log('This script will:');
    console.log('1. Open the dashboard');
    console.log('2. Let YOU manually move the slider');
    console.log('3. Capture the table data before and after\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();

    try {
        console.log('Opening dashboard...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);

        console.log('Clicking Phone tab...');
        await page.locator('button[role="tab"]:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);

        console.log('Scrolling to table...');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);

        // Capture initial data
        console.log('\n1. Capturing INITIAL table data...');
        const initialData = await page.evaluate(() => {
            const table = document.querySelector('table[role="grid"]');
            if (!table) return null;

            const rows = [];
            const bodyRows = table.querySelectorAll('tbody tr');
            bodyRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                const rowText = Array.from(cells).map(c => c.textContent.trim()).join(' | ');
                rows.push(rowText);
            });

            return rows;
        });

        console.log('Initial data (first 5 rows):');
        initialData.slice(0, 5).forEach((row, idx) => {
            console.log(`  ${idx + 1}. ${row}`);
        });

        console.log('\n\n*** NOW: Please manually move the slider to a DIFFERENT time ***');
        console.log('*** Wait for "RUNNING..." to appear and disappear ***');
        console.log('*** Then press ENTER in this terminal ***\n');

        // Wait for user input
        await new Promise(resolve => {
            process.stdin.once('data', () => resolve());
        });

        // Capture data after manual change
        console.log('\n2. Capturing AFTER table data...');
        const afterData = await page.evaluate(() => {
            const table = document.querySelector('table[role="grid"]');
            if (!table) return null;

            const rows = [];
            const bodyRows = table.querySelectorAll('tbody tr');
            bodyRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                const rowText = Array.from(cells).map(c => c.textContent.trim()).join(' | ');
                rows.push(rowText);
            });

            return rows;
        });

        console.log('After data (first 5 rows):');
        afterData.slice(0, 5).forEach((row, idx) => {
            console.log(`  ${idx + 1}. ${row}`);
        });

        // Compare
        console.log('\n3. Comparison:');
        const same = JSON.stringify(initialData) === JSON.stringify(afterData);
        if (same) {
            console.log('   ❌ DATA IS THE SAME - Slider not working or no historical data!');
        } else {
            console.log('   ✅ DATA CHANGED - Slider works!');
            console.log('\n   Differences:');
            for (let i = 0; i < Math.min(initialData.length, afterData.length); i++) {
                if (initialData[i] !== afterData[i]) {
                    console.log(`   Row ${i + 1}:`);
                    console.log(`     Before: ${initialData[i]}`);
                    console.log(`     After:  ${afterData[i]}`);
                }
            }
        }

        console.log('\n\nBrowser will stay open. Close it when done.');
        await page.waitForTimeout(300000); // 5 minutes

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

manualSliderTest().catch(console.error);
