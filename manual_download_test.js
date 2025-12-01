const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

/**
 * Manual-assisted download test with fullscreen browser
 */
async function manualDownloadTest() {
    const downloadDir = path.join(__dirname, 'downloads');
    if (!fs.existsSync(downloadDir)) {
        fs.mkdirSync(downloadDir, { recursive: true });
    }

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
        args: ['--start-maximized'] // Start maximized
    });

    const context = await browser.newContext({
        acceptDownloads: true,
        viewport: null, // Use full screen
        screen: { width: 1920, height: 1080 }
    });

    const page = await context.newPage();

    // Listen for downloads
    page.on('download', async download => {
        console.log('\n🎉 DOWNLOAD DETECTED!');
        console.log(`   Suggested filename: ${download.suggestedFilename()}`);

        const filename = `test_download_${Date.now()}.csv`;
        const filepath = path.join(downloadDir, filename);
        await download.saveAs(filepath);
        console.log(`   ✓ Saved as: ${filename}\n`);
    });

    // Listen for console logs from the page
    page.on('console', msg => console.log('PAGE:', msg.text()));

    try {
        console.log('Opening RouterSense dashboard...\n');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });

        await page.waitForTimeout(3000);
        console.log('Page loaded!\n');

        // Maximize the window
        await page.evaluate(() => {
            window.moveTo(0, 0);
            window.resizeTo(screen.width, screen.height);
        });

        // Take screenshot
        await page.screenshot({ path: path.join(downloadDir, 'manual_test_fullscreen.png'), fullPage: true });

        // Try to find all clickable elements near the table
        console.log('=== Analyzing page for download buttons ===\n');

        const allButtons = await page.locator('button, a[download], [role="button"]').all();
        console.log(`Found ${allButtons.length} clickable elements\n`);

        // Print details of buttons that might be download-related
        for (let i = 0; i < Math.min(allButtons.length, 20); i++) {
            const btn = allButtons[i];
            const text = await btn.textContent().catch(() => '');
            const ariaLabel = await btn.getAttribute('aria-label').catch(() => '');
            const title = await btn.getAttribute('title').catch(() => '');
            const className = await btn.getAttribute('class').catch(() => '');

            if (text || ariaLabel || title || className?.includes('download')) {
                console.log(`Button ${i}:`);
                console.log(`  Text: "${text?.trim()}"`);
                console.log(`  aria-label: "${ariaLabel}"`);
                console.log(`  title: "${title}"`);
                console.log(`  class: "${className}"`);
                console.log('');
            }
        }

        console.log('\n=== MANUAL TEST MODE ===');
        console.log('\nPlease do the following:');
        console.log('1. Adjust the date/time slider to November 18, 2025, 00:00');
        console.log('2. Click the download button');
        console.log('3. Wait for the download to complete');
        console.log('\nThe script will automatically detect and save the download.');
        console.log('Browser will stay open for 3 minutes...\n');

        // Wait 3 minutes for manual interaction
        await page.waitForTimeout(180000);

        console.log('\n=== Test Complete ===');
        console.log('Check the downloads folder for the test file.');

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await browser.close();
    }
}

manualDownloadTest().catch(console.error);
