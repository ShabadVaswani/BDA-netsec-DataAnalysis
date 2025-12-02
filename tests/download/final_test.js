const { chromium } = require('playwright');

async function quickTest2Hours() {
    console.log('=== Quick Test: Hours 0 and 12 ===\n');

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
        const results = [];

        for (const hour of hours) {
            console.log(`\nHour ${hour}:00...`);

            const targetDateTime = new Date(`2025-11-18T${hour.toString().padStart(2, '0')}:00:00`);
            const timestampMicroseconds = Math.floor(targetDateTime.getTime() / 1000) * 1000000;

            // Drag slider
            const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();
            const minValue = parseInt(await slider.getAttribute('aria-valuemin'));
            const maxValue = parseInt(await slider.getAttribute('aria-valuemax'));
            const targetPosition = (timestampMicroseconds - minValue) / (maxValue - minValue);

            const thumbBox = await slider.boundingBox();
            const trackBox = await page.evaluate(() => {
                const thumb = document.querySelector('[role="slider"][aria-label="Select hour"]');
                const track = thumb.parentElement;
                const box = track.getBoundingClientRect();
                return { x: box.x, y: box.y, width: box.width, height: box.height };
            });

            const startX = thumbBox.x + (thumbBox.width / 2);
            const startY = thumbBox.y + (thumbBox.height / 2);
            const endX = trackBox.x + (trackBox.width * targetPosition);
            const endY = trackBox.y + (trackBox.height / 2);

            await page.mouse.move(startX, startY);
            await page.mouse.down();
            await page.waitForTimeout(100);
            await page.mouse.move(endX, endY, { steps: 10 });
            await page.waitForTimeout(100);
            await page.mouse.up();

            console.log('  Waiting 12 seconds...');
            await page.waitForTimeout(12000);

            const sliderValue = await slider.getAttribute('aria-valuetext');
            console.log(`  Slider shows: ${sliderValue}`);

            const firstRow = await page.evaluate(() => {
                const table = document.querySelector('table[role="grid"]');
                if (!table) return 'NO TABLE';
                const firstRow = table.querySelector('tbody tr');
                if (!firstRow) return 'NO ROWS';
                const cells = firstRow.querySelectorAll('td');
                return Array.from(cells).map(c => c.textContent.trim()).join(' | ');
            });

            console.log(`  First row: ${firstRow}`);
            results.push({ hour, data: firstRow });
        }

        console.log('\n=== COMPARISON ===');
        console.log(`Hour 0:  ${results[0].data}`);
        console.log(`Hour 12: ${results[1].data}`);
        console.log(results[0].data === results[1].data ? '❌ SAME DATA' : '✅ DIFFERENT DATA');

        console.log('\nBrowser stays open for 10 seconds...');
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

quickTest2Hours().catch(console.error);
