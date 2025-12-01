const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

/**
 * Step 3: Complete download workflow
 * 1. Navigate and click Phone tab
 * 2. Scroll to table
 * 3. Hover over table to reveal download button
 * 4. Click download button
 */
async function completeDownload() {
    console.log('=== Complete Download Workflow ===\n');

    const downloadDir = path.join(__dirname, 'downloads');
    if (!fs.existsSync(downloadDir)) {
        fs.mkdirSync(downloadDir, { recursive: true });
    }

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({
        viewport: null,
        acceptDownloads: true,
        downloadsPath: downloadDir
    });

    const page = await context.newPage();

    // Track downloads
    page.on('download', async download => {
        console.log('\n🎉 DOWNLOAD DETECTED!');
        console.log(`File: ${download.suggestedFilename()}`);
        const downloadPath = await download.path();
        console.log(`Saved: ${downloadPath}\n`);
    });

    try {
        // Step 1: Navigate
        console.log('1. Navigating...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);
        console.log('   ✓ Loaded\n');

        // Step 2: Click Phone tab
        console.log('2. Clicking Phone tab...');
        await page.locator('button[role="tab"]:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);
        console.log('   ✓ Clicked\n');

        // Step 3: Scroll to table area
        console.log('3. Scrolling to table...');
        await page.evaluate(() => window.scrollTo(0, 600));
        await page.waitForTimeout(1500);
        console.log('   ✓ Scrolled\n');

        // Step 4: Find and hover over table
        console.log('4. Finding table...');
        const table = page.locator('table[role="grid"]').first();

        // Wait for table to be attached and visible
        await table.waitFor({ state: 'attached', timeout: 5000 });
        console.log('   Table found');

        // Scroll table into view
        await table.scrollIntoViewIfNeeded();
        await page.waitForTimeout(1000);

        // Hover over table
        console.log('   Hovering over table...');
        await table.hover({ force: true });
        await page.waitForTimeout(2000); // Wait for download button to appear
        console.log('   ✓ Hovered\n');

        // Step 5: Find and click download button
        console.log('5. Looking for download button...');
        const downloadButton = page.locator('button[aria-label="Download as CSV"]').first();

        if (await downloadButton.count() > 0) {
            console.log('   Button found');

            // Make sure it's visible
            if (await downloadButton.isVisible()) {
                console.log('   Clicking...');
                await downloadButton.click();
                console.log('   ✓ Clicked!\n');

                console.log('Waiting 15 seconds for download...');
                console.log('(If popup appears, please select save location)\n');
                await page.waitForTimeout(15000);
            } else {
                console.log('   Button not visible');
            }
        } else {
            console.log('   Button not found');
        }

        console.log('Browser will close in 5 seconds...');
        await page.waitForTimeout(5000);

    } catch (error) {
        console.error('Error:', error.message);
        await page.screenshot({ path: path.join(downloadDir, 'error.png'), fullPage: true });
    } finally {
        await browser.close();
    }
}

completeDownload().catch(console.error);
