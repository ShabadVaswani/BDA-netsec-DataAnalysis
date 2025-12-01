const { chromium } = require('playwright');

async function testBinarySearch() {
    console.log('=== Testing Binary Search ===\n');

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

        // Test seeking to Nov 18, hours 0 and 12
        const targets = [
            { date: '2025-11-18', hour: 0 },
            { date: '2025-11-18', hour: 12 }
        ];

        for (const target of targets) {
            console.log(`\nSeeking to ${target.date} ${target.hour.toString().padStart(2, '0')}:00...`);

            const targetDateTime = new Date(`${target.date}T${target.hour.toString().padStart(2, '0')}:00:00`);
            const targetTime = targetDateTime.getTime();

            let attempts = 0;
            while (attempts < 15) {
                const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();
                const valueText = await slider.getAttribute('aria-valuetext');
                const [datePart, timePart] = valueText.split(' ');
                const currentDateTime = new Date(`${datePart}T${timePart}:00`);
                const currentTime = currentDateTime.getTime();
                const diff = targetTime - currentTime;
                const diffHours = diff / (1000 * 60 * 60);

                console.log(`  Attempt ${attempts + 1}: ${valueText}, diff: ${diffHours.toFixed(1)}h`);

                if (Math.abs(diffHours) < 0.5) {
                    console.log(`  ✓ Found!`);
                    break;
                }

                let dragAmount;
                if (Math.abs(diffHours) > 240) {
                    dragAmount = diffHours > 0 ? 0.2 : -0.2;
                } else if (Math.abs(diffHours) > 48) {
                    dragAmount = diffHours > 0 ? 0.1 : -0.1;
                } else if (Math.abs(diffHours) > 12) {
                    dragAmount = diffHours > 0 ? 0.05 : -0.05;
                } else {
                    dragAmount = diffHours > 0 ? 0.02 : -0.02;
                }

                const thumbBox = await slider.boundingBox();
                const trackBox = await page.evaluate(() => {
                    const thumb = document.querySelector('[role="slider"][aria-label="Select hour"]');
                    const track = thumb.parentElement;
                    const box = track.getBoundingClientRect();
                    return { x: box.x, y: box.y, width: box.width, height: box.height };
                });

                const startX = thumbBox.x + (thumbBox.width / 2);
                const startY = thumbBox.y + (thumbBox.height / 2);
                const endX = startX + (trackBox.width * dragAmount);
                const endY = trackBox.y + (trackBox.height / 2);

                await page.mouse.move(startX, startY);
                await page.mouse.down();
                await page.waitForTimeout(100);
                await page.mouse.move(endX, endY, { steps: 10 });
                await page.waitForTimeout(100);
                await page.mouse.up();
                await page.waitForTimeout(1000);

                attempts++;
            }
        }

        console.log('\nBrowser stays open for 15 seconds...');
        await page.waitForTimeout(15000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

testBinarySearch().catch(console.error);
