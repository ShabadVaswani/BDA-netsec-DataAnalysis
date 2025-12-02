const { chromium } = require('playwright');
const path = require('path');

/**
 * Step 2 (Updated): Hover over table, then find and click download button
 */
async function clickDownloadButton() {
    console.log('=== Step 2: Hover Over Table and Click Download ===\n');

    const downloadDir = path.join(__dirname, 'downloads');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({
        viewport: null,
        acceptDownloads: true,
        downloadsPath: downloadDir
    });

    const page = await context.newPage();

    // Listen for downloads
    let downloadDetected = false;
    page.on('download', async download => {
        downloadDetected = true;
        console.log('\n   🎉 DOWNLOAD DETECTED!');
        console.log(`   File: ${download.suggestedFilename()}`);
        const downloadPath = await download.path();
        console.log(`   Saved to: ${downloadPath}\n`);
    });

    try {
        console.log('1. Navigating to dashboard...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        console.log('   ✓ Page loaded\n');
        await page.waitForTimeout(3000);

        console.log('2. Clicking Phone tab...');
        const phoneTab = page.locator('button[role="tab"]:has-text("Phone")');
        if (await phoneTab.count() > 0) {
            await phoneTab.first().click();
            console.log('   ✓ Clicked\n');
            await page.waitForTimeout(2000);
        }

        console.log('3. Scrolling down...');
        await page.evaluate(() => window.scrollBy(0, 800));
        await page.waitForTimeout(1000);
        console.log('   ✓ Scrolled\n');

        console.log('4. Hovering over table to reveal download button...');
        const table = page.locator('table[role="grid"]').first();
        const tableCount = await table.count();
        console.log(`   Found ${tableCount} table(s)`);

        if (tableCount > 0) {
            await table.hover();
            console.log('   ✓ Hovering over table');
            await page.waitForTimeout(1500); // Wait for buttons to appear
            console.log('   ✓ Waited for buttons to appear\n');
        }

        console.log('5. Looking for download button...');
        const downloadButton = page.locator('button[aria-label="Download as CSV"]');
        const buttonCount = await downloadButton.count();
        console.log(`   Found ${buttonCount} download button(s)`);

        if (buttonCount > 0) {
            const isVisible = await downloadButton.first().isVisible();
            console.log(`   Button visible: ${isVisible}`);

            if (isVisible) {
                console.log('   Clicking download button...');
                await downloadButton.first().click();
                console.log('   ✓ Clicked!');
                console.log('   Waiting 10 seconds for download popup/completion...');

                // Wait longer for download popup and manual selection
                await page.waitForTimeout(10000);

                if (downloadDetected) {
                    console.log('   ✓ SUCCESS: Download completed!\n');
                } else {
                    console.log('   ⚠ Download may require manual location selection\n');
                }
            }
        } else {
            console.log('   ✗ Download button not found after hovering');
        }

        console.log('Browser will stay open for 10 seconds...');
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

clickDownloadButton().catch(console.error);
