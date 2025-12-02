const { chromium } = require('playwright');

async function testSliderDrag() {
    console.log('=== Testing Slider Drag ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500,
        args: ['--start-maximized']
    });

    const page = await browser.newPage({ viewport: null });

    try {
        console.log('Loading page...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);

        console.log('Clicking Phone tab...');
        await page.locator('button:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);

        console.log('Scrolling...');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);

        console.log('\nFinding slider...');
        const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();

        // Get initial value
        const initialValue = await slider.getAttribute('aria-valuenow');
        const initialText = await slider.getAttribute('aria-valuetext');
        console.log(`Initial value: ${initialValue}`);
        console.log(`Initial text: ${initialText}`);

        // Get slider position
        const sliderBox = await slider.boundingBox();
        console.log(`Slider position: x=${sliderBox.x}, y=${sliderBox.y}, width=${sliderBox.width}`);

        // Test 3 different positions
        const positions = [0.2, 0.5, 0.8]; // 20%, 50%, 80% along the slider

        for (const pos of positions) {
            console.log(`\n--- Testing position ${(pos * 100).toFixed(0)}% ---`);

            const targetX = sliderBox.x + (sliderBox.width * pos);
            const targetY = sliderBox.y + (sliderBox.height / 2);

            console.log(`Clicking at (${targetX.toFixed(0)}, ${targetY.toFixed(0)})`);
            await page.mouse.click(targetX, targetY);
            await page.waitForTimeout(2000);

            // Read new value
            const newValue = await slider.getAttribute('aria-valuenow');
            const newText = await slider.getAttribute('aria-valuetext');
            console.log(`New value: ${newValue}`);
            console.log(`New text: ${newText}`);

            // Check if it changed
            if (newValue !== initialValue) {
                console.log('✅ Value changed!');
            } else {
                console.log('❌ Value did NOT change');
            }

            await page.waitForTimeout(1000);
        }

        console.log('\n\nNow testing drag...');

        // Try dragging from left to right
        const startX = sliderBox.x + 50;
        const endX = sliderBox.x + sliderBox.width - 50;
        const y = sliderBox.y + (sliderBox.height / 2);

        console.log(`Dragging from ${startX.toFixed(0)} to ${endX.toFixed(0)}`);

        await page.mouse.move(startX, y);
        await page.mouse.down();
        await page.mouse.move(endX, y, { steps: 20 });
        await page.mouse.up();
        await page.waitForTimeout(2000);

        const finalValue = await slider.getAttribute('aria-valuenow');
        const finalText = await slider.getAttribute('aria-valuetext');
        console.log(`After drag value: ${finalValue}`);
        console.log(`After drag text: ${finalText}`);

        console.log('\n\nBrowser will stay open for 30 seconds...');
        console.log('You can manually drag the slider to see it work!');
        await page.waitForTimeout(30000);

    } catch (error) {
        console.error('Error:', error.message);
        console.error(error.stack);
    } finally {
        await browser.close();
    }
}

testSliderDrag().catch(console.error);
