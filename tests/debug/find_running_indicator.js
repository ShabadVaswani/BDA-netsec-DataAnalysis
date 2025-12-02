const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Capture page HTML and find "running" indicator
 */
async function captureAndAnalyze() {
    console.log('=== Capturing Page for "Running" Indicator Analysis ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();

    try {
        console.log('Navigating...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);

        console.log('Clicking Phone tab...');
        await page.locator('button[role="tab"]:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);

        console.log('Scrolling...');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);

        // Capture initial state
        console.log('\n1. Capturing BEFORE slider change...');
        const htmlBefore = await page.content();
        fs.writeFileSync('page_before_change.html', htmlBefore);
        console.log('   Saved to: page_before_change.html');

        // Change slider
        console.log('\n2. Changing slider...');
        const slider = page.locator('input[type="range"][role="slider"]').first();
        const targetDateTime = new Date('2025-11-18T12:00:00');
        const timestampMicroseconds = Math.floor(targetDateTime.getTime() / 1000) * 1000000;

        await slider.fill(timestampMicroseconds.toString());
        await slider.evaluate((el, value) => {
            el.value = value.toString();
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }, timestampMicroseconds);

        console.log('   Slider changed!');
        console.log('   Waiting 500ms...');
        await page.waitForTimeout(500);

        // Capture during loading
        console.log('\n3. Capturing DURING loading (500ms after change)...');
        const htmlDuring = await page.content();
        fs.writeFileSync('page_during_loading.html', htmlDuring);
        console.log('   Saved to: page_during_loading.html');

        // Wait more
        console.log('\n4. Waiting 5 more seconds...');
        await page.waitForTimeout(5000);

        // Capture after loading
        console.log('\n5. Capturing AFTER loading...');
        const htmlAfter = await page.content();
        fs.writeFileSync('page_after_loading.html', htmlAfter);
        console.log('   Saved to: page_after_loading.html');

        // Search for "running" in all three
        console.log('\n6. Searching for "running" text...\n');

        const searchInHtml = (html, label) => {
            const lowerHtml = html.toLowerCase();
            const index = lowerHtml.indexOf('running');
            if (index !== -1) {
                const start = Math.max(0, index - 100);
                const end = Math.min(html.length, index + 100);
                const snippet = html.substring(start, end);
                console.log(`${label}:`);
                console.log(`   Found at position ${index}`);
                console.log(`   Context: ...${snippet}...`);
                console.log('');
            } else {
                console.log(`${label}: NOT FOUND`);
            }
        };

        searchInHtml(htmlBefore, 'BEFORE');
        searchInHtml(htmlDuring, 'DURING');
        searchInHtml(htmlAfter, 'AFTER');

        console.log('\n✓ Analysis complete!');
        console.log('Check the HTML files to find the running indicator.');
        console.log('\nBrowser stays open for 10 seconds...');
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

captureAndAnalyze().catch(console.error);
