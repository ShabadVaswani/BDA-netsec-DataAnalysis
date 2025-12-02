const { chromium } = require('playwright');

async function findSliderTrack() {
    console.log('=== Finding Slider Track ===\n');

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

        console.log('Analyzing slider structure...\n');

        // Find the slider container
        const sliderInfo = await page.evaluate(() => {
            // Find the slider element
            const sliderThumb = document.querySelector('[role="slider"][aria-label="Select hour"]');
            if (!sliderThumb) return { found: false };

            // Get parent elements to find the track
            const parent1 = sliderThumb.parentElement;
            const parent2 = parent1?.parentElement;
            const parent3 = parent2?.parentElement;

            return {
                found: true,
                thumb: {
                    class: sliderThumb.className,
                    box: sliderThumb.getBoundingClientRect()
                },
                parent1: {
                    tag: parent1?.tagName,
                    class: parent1?.className,
                    box: parent1?.getBoundingClientRect()
                },
                parent2: {
                    tag: parent2?.tagName,
                    class: parent2?.className,
                    box: parent2?.getBoundingClientRect()
                },
                parent3: {
                    tag: parent3?.tagName,
                    class: parent3?.className,
                    box: parent3?.getBoundingClientRect()
                }
            };
        });

        if (sliderInfo.found) {
            console.log('Slider Thumb:');
            console.log(`  Width: ${sliderInfo.thumb.box.width}px`);
            console.log(`  Position: (${sliderInfo.thumb.box.x}, ${sliderInfo.thumb.box.y})`);

            console.log('\nParent 1 (likely the track):');
            console.log(`  Tag: ${sliderInfo.parent1.tag}`);
            console.log(`  Width: ${sliderInfo.parent1.box.width}px`);
            console.log(`  Position: (${sliderInfo.parent1.box.x}, ${sliderInfo.parent1.box.y})`);

            console.log('\nParent 2:');
            console.log(`  Tag: ${sliderInfo.parent2.tag}`);
            console.log(`  Width: ${sliderInfo.parent2.box.width}px`);

            console.log('\nParent 3:');
            console.log(`  Tag: ${sliderInfo.parent3.tag}`);
            console.log(`  Width: ${sliderInfo.parent3.box.width}px`);

            // Test clicking on the track (parent1)
            console.log('\n\nTesting clicks on the track (parent1)...');

            const trackX = sliderInfo.parent1.box.x;
            const trackWidth = sliderInfo.parent1.box.width;
            const trackY = sliderInfo.parent1.box.y + (sliderInfo.parent1.box.height / 2);

            const positions = [0.1, 0.5, 0.9];

            for (const pos of positions) {
                const clickX = trackX + (trackWidth * pos);
                console.log(`\nClicking at ${(pos * 100).toFixed(0)}% (x=${clickX.toFixed(0)})`);

                await page.mouse.click(clickX, trackY);
                await page.waitForTimeout(2000);

                const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();
                const newText = await slider.getAttribute('aria-valuetext');
                console.log(`  Result: ${newText}`);
            }
        }

        console.log('\n\nBrowser stays open for 20 seconds...');
        await page.waitForTimeout(20000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

findSliderTrack().catch(console.error);
