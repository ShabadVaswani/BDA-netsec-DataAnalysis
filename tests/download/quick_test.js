const { chromium } = require('playwright');

async function quickTest() {
    console.log('=== Quick Test: 2 Hours ===\n');

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

        await page.locator('button:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);

        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);

        const hours = [0, 12];

        for (const hour of hours) {
            console.log(`\nTesting hour ${hour}...`);

            const targetDateTime = new Date(`2025-11-18T${hour.toString().padStart(2, '0')}:00:00`);
            const timestampMicroseconds = Math.floor(targetDateTime.getTime() / 1000) * 1000000;

            // Find slider
            const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();
            const sliderBox = await slider.boundingBox();

            const minValue = parseInt(await slider.getAttribute('aria-valuemin'));
            const maxValue = parseInt(await slider.getAttribute('aria-valuemax'));

            const position = (timestampMicroseconds - minValue) / (maxValue - minValue);
            const targetX = sliderBox.x + (sliderBox.width * position);
            const targetY = sliderBox.y + (sliderBox.height / 2);

            console.log(`  Clicking at position ${position.toFixed(2)} (${targetX.toFixed(0)}, ${targetY.toFixed(0)})`);
            await page.mouse.click(targetX, targetY);

            console.log('  Waiting 12 seconds...');
            await page.waitForTimeout(12000);

            const firstRow = await page.evaluate(() => {
                const table = document.querySelector('table[role="grid"]');
                if (!table) return 'NO TABLE';
                const firstRow = table.querySelector('tbody tr');
                if (!firstRow) return 'NO ROWS';
                const cells = firstRow.querySelectorAll('td');
                return Array.from(cells).map(c => c.textContent.trim()).join(' | ');
            });

            console.log(`  First row: ${firstRow}`);
        }

        console.log('\nBrowser stays open for 10 seconds...');
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

quickTest().catch(console.error);
