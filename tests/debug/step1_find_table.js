const { chromium } = require('playwright');

/**
 * Step 1: Navigate to website and find the table
 */
async function findTable() {
    console.log('=== Step 1: Find Table ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({
        viewport: null
    });

    const page = await context.newPage();

    try {
        console.log('1. Navigating to dashboard...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        console.log('   ✓ Page loaded\n');

        await page.waitForTimeout(3000);

        console.log('2. Looking for Phone tab...');
        const phoneTab = page.locator('button[role="tab"]:has-text("Phone")');
        const tabCount = await phoneTab.count();
        console.log(`   Found ${tabCount} Phone tab(s)`);

        if (tabCount > 0) {
            console.log('   Clicking Phone tab...');
            await phoneTab.first().click();
            console.log('   ✓ Clicked\n');
            await page.waitForTimeout(2000);
        }

        console.log('3. Scrolling down to reveal table...');
        await page.evaluate(() => window.scrollBy(0, 800));
        await page.waitForTimeout(1000);
        console.log('   ✓ Scrolled\n');

        console.log('4. Looking for table...');
        const table = page.locator('table[role="grid"]');
        const tableCount = await table.count();
        console.log(`   Found ${tableCount} table(s)`);

        if (tableCount > 0) {
            const isVisible = await table.first().isVisible();
            console.log(`   Table visible: ${isVisible}`);

            if (isVisible) {
                console.log('   ✓ SUCCESS: Table found and visible!\n');
            }
        }

        console.log('Browser will stay open for 30 seconds for you to inspect...');
        await page.waitForTimeout(30000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

findTable().catch(console.error);
