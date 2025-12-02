const { chromium } = require('playwright');

async function testProperDrag() {
    console.log('=== Testing Proper Slider Drag ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
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

        console.log('Finding slider...');
        const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();

        const initialText = await slider.getAttribute('aria-valuetext');
        console.log(`Initial: ${initialText}\n`);

        // Get the slider thumb position
        const thumbBox = await slider.boundingBox();
        console.log(`Thumb: x=${thumbBox.x.toFixed(0)}, y=${thumbBox.y.toFixed(0)}, width=${thumbBox.width}`);

        // Find the track (parent element)
        const trackBox = await page.evaluate(() => {
            const thumb = document.querySelector('[role="slider"][aria-label="Select hour"]');
            const track = thumb.parentElement;
            const box = track.getBoundingClientRect();
            return { x: box.x, y: box.y, width: box.width, height: box.height };
        });

        console.log(`Track: x=${trackBox.x.toFixed(0)}, y=${trackBox.y.toFixed(0)}, width=${trackBox.width.toFixed(0)}\n`);

        // Test dragging to different positions
        const targetPositions = [0.1, 0.5, 0.9]; // 10%, 50%, 90% along track

        for (const targetPos of targetPositions) {
            console.log(`--- Dragging to ${(targetPos * 100).toFixed(0)}% ---`);

            // Start position: center of thumb
            const startX = thumbBox.x + (thumbBox.width / 2);
            const startY = thumbBox.y + (thumbBox.height / 2);

            // End position: target position on track
            const endX = trackBox.x + (trackBox.width * targetPos);
            const endY = trackBox.y + (trackBox.height / 2);

            console.log(`Dragging from (${startX.toFixed(0)}, ${startY.toFixed(0)}) to (${endX.toFixed(0)}, ${endY.toFixed(0)})`);

            // Perform drag
            await page.mouse.move(startX, startY);
            await page.mouse.down();
            await page.waitForTimeout(100);
            await page.mouse.move(endX, endY, { steps: 10 });
            await page.waitForTimeout(100);
            await page.mouse.up();

            await page.waitForTimeout(2000);

            // Read new value
            const newText = await slider.getAttribute('aria-valuetext');
            console.log(`Result: ${newText}`);

            // Update thumb position for next drag
            const newThumbBox = await slider.boundingBox();
            thumbBox.x = newThumbBox.x;
            thumbBox.y = newThumbBox.y;

            await page.waitForTimeout(1000);
        }

        console.log('\n\nBrowser stays open for 20 seconds...');
        await page.waitForTimeout(20000);

    } catch (error) {
        console.error('Error:', error.message);
        console.error(error.stack);
    } finally {
        await browser.close();
    }
}

testProperDrag().catch(console.error);
