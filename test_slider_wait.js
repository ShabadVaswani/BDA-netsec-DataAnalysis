const { chromium } = require('playwright');

/**
 * Test slider with better selector and longer wait
 */
async function testSliderWithWait() {
    console.log('=== Testing Slider with Long Wait ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();

    try {
        console.log('Loading...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(5000);

        console.log('Clicking Phone tab...');
        const phoneTab = await page.locator('button:has-text("Phone")').first();
        await phoneTab.click();
        await page.waitForTimeout(3000);

        console.log('Scrolling...');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(2000);

        console.log('\nLooking for slider...');

        // Try to find slider by looking for input type=range
        const slider = await page.locator('input[type="range"]').first();
        const sliderExists = await slider.count() > 0;

        console.log(`Slider found: ${sliderExists}`);

        if (sliderExists) {
            // Get current value
            const currentValue = await slider.inputValue();
            console.log(`Current value: ${currentValue}`);

            // Test changing to hour 0 (midnight)
            console.log('\nChanging to hour 0 (2025-11-18 00:00)...');
            const targetDateTime = new Date('2025-11-18T00:00:00');
            const timestampMicroseconds = Math.floor(targetDateTime.getTime() / 1000) * 1000000;

            console.log(`Target timestamp: ${timestampMicroseconds}`);

            await slider.fill(timestampMicroseconds.toString());
            console.log('Slider filled');

            await page.waitForTimeout(1000);

            // Trigger events
            await slider.evaluate((el, value) => {
                el.value = value.toString();
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }, timestampMicroseconds);

            console.log('Events dispatched');
            console.log('\nWaiting 15 seconds for data to load...');
            await page.waitForTimeout(15000);

            // Check table data
            const tableData = await page.evaluate(() => {
                const table = document.querySelector('table[role="grid"]');
                if (!table) return { found: false };

                const rows = [];
                const bodyRows = table.querySelectorAll('tbody tr');
                bodyRows.forEach((row, idx) => {
                    if (idx < 3) { // First 3 rows
                        const cells = row.querySelectorAll('td');
                        const rowText = Array.from(cells).map(c => c.textContent.trim()).join(' | ');
                        rows.push(rowText);
                    }
                });

                return { found: true, rows };
            });

            if (tableData.found) {
                console.log('\nTable data (first 3 rows):');
                tableData.rows.forEach((row, idx) => {
                    console.log(`  ${idx + 1}. ${row}`);
                });
            } else {
                console.log('\n❌ Table not found!');
            }

            console.log('\n\nNow try hour 12 (noon)...');
            const targetDateTime2 = new Date('2025-11-18T12:00:00');
            const timestampMicroseconds2 = Math.floor(targetDateTime2.getTime() / 1000) * 1000000;

            await slider.fill(timestampMicroseconds2.toString());
            await page.waitForTimeout(1000);
            await slider.evaluate((el, value) => {
                el.value = value.toString();
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }, timestampMicroseconds2);

            console.log('Waiting 15 seconds...');
            await page.waitForTimeout(15000);

            const tableData2 = await page.evaluate(() => {
                const table = document.querySelector('table[role="grid"]');
                if (!table) return { found: false };

                const rows = [];
                const bodyRows = table.querySelectorAll('tbody tr');
                bodyRows.forEach((row, idx) => {
                    if (idx < 3) {
                        const cells = row.querySelectorAll('td');
                        const rowText = Array.from(cells).map(c => c.textContent.trim()).join(' | ');
                        rows.push(rowText);
                    }
                });

                return { found: true, rows };
            });

            if (tableData2.found) {
                console.log('\nTable data (first 3 rows):');
                tableData2.rows.forEach((row, idx) => {
                    console.log(`  ${idx + 1}. ${row}`);
                });

                // Compare
                const same = JSON.stringify(tableData.rows) === JSON.stringify(tableData2.rows);
                console.log(`\n${same ? '❌ DATA IS SAME' : '✅ DATA IS DIFFERENT'}`);
            }
        }

        console.log('\nBrowser stays open for 20 seconds...');
        await page.waitForTimeout(20000);

    } catch (error) {
        console.error('\n❌ Error:', error.message);
        console.error(error.stack);
    } finally {
        await browser.close();
    }
}

testSliderWithWait().catch(console.error);
