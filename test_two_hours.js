const { chromium } = require('playwright');
const fs = require('fs');

/**
 * Quick test: Download just 2 hours and compare the data
 */
async function testTwoHours() {
    console.log('=== Testing 2 Hours ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 200,
        args: ['--start-maximized']
    });

    const page = await browser.newPage({ viewport: null });

    try {
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);

        await page.locator('button[role="tab"]:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);

        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);

        const hours = [0, 12]; // Test midnight and noon
        const results = [];

        for (const hour of hours) {
            console.log(`\nTesting hour ${hour}:00...`);

            const hourStr = hour.toString().padStart(2, '0');
            const targetDateTime = new Date(`2025-11-18T${hourStr}:00:00`);
            const timestampMicroseconds = Math.floor(targetDateTime.getTime() / 1000) * 1000000;

            const slider = page.locator('input[type="range"][role="slider"]').first();
            await slider.fill(timestampMicroseconds.toString());
            await slider.evaluate((el, value) => {
                el.value = value.toString();
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }, timestampMicroseconds);

            console.log('  Waiting for data to load (10 seconds)...');
            await page.waitForTimeout(10000);

            const tableData = await page.evaluate(() => {
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

            results.push({ hour, data: tableData });

            console.log(`  Got ${tableData.length} rows`);
            console.log(`  First row: ${tableData[0]}`);
        }

        // Compare
        console.log('\n=== COMPARISON ===\n');
        console.log(`Hour 0 first row:  ${results[0].data[0]}`);
        console.log(`Hour 12 first row: ${results[1].data[0]}`);

        const same = JSON.stringify(results[0].data) === JSON.stringify(results[1].data);
        if (same) {
            console.log('\n❌ DATA IS IDENTICAL - Still not working!');
        } else {
            console.log('\n✅ DATA IS DIFFERENT - It works!');
        }

        console.log('\nBrowser stays open for 10 seconds...');
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

testTwoHours().catch(console.error);
