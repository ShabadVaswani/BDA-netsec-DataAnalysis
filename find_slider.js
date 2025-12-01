const { chromium } = require('playwright');

/**
 * Find the slider element and show all possible selectors
 */
async function findSlider() {
    console.log('=== Finding Slider Element ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();

    try {
        console.log('1. Loading page...');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);
        console.log('   ✓ Loaded\n');

        console.log('2. Clicking Phone tab...');
        await page.locator('button[role="tab"]:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);
        console.log('   ✓ Clicked\n');

        console.log('3. Scrolling...');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);
        console.log('   ✓ Scrolled\n');

        console.log('4. Searching for ALL slider elements...\n');

        // Try multiple selectors
        const selectors = [
            'input[type="range"]',
            'input[role="slider"]',
            'input[type="range"][role="slider"]',
            '[role="slider"]',
            'input.slider',
            'input[class*="slider"]',
            'input[class*="Slider"]',
            '[data-testid*="slider"]',
            '[data-testid*="Slider"]'
        ];

        for (const selector of selectors) {
            const count = await page.locator(selector).count();
            console.log(`Selector: ${selector}`);
            console.log(`  Found: ${count} element(s)`);

            if (count > 0) {
                // Get details of first match
                const details = await page.locator(selector).first().evaluate(el => ({
                    tag: el.tagName,
                    type: el.type,
                    role: el.getAttribute('role'),
                    class: el.className,
                    id: el.id,
                    name: el.name,
                    value: el.value,
                    min: el.min,
                    max: el.max,
                    step: el.step
                }));

                console.log(`  Details:`, JSON.stringify(details, null, 2));
            }
            console.log('');
        }

        // Also search in the entire DOM
        console.log('5. Analyzing ALL input elements on page...\n');
        const allInputs = await page.evaluate(() => {
            const inputs = document.querySelectorAll('input');
            return Array.from(inputs).map(input => ({
                type: input.type,
                role: input.getAttribute('role'),
                class: input.className,
                id: input.id,
                value: input.value?.substring(0, 50),
                visible: input.offsetParent !== null
            }));
        });

        console.log(`Total input elements: ${allInputs.length}\n`);
        allInputs.forEach((input, idx) => {
            console.log(`Input ${idx + 1}:`);
            console.log(`  Type: ${input.type}`);
            console.log(`  Role: ${input.role || 'none'}`);
            console.log(`  Class: ${input.class || 'none'}`);
            console.log(`  ID: ${input.id || 'none'}`);
            console.log(`  Value: ${input.value || 'none'}`);
            console.log(`  Visible: ${input.visible}`);
            console.log('');
        });

        console.log('\nBrowser will stay open for 30 seconds for manual inspection...');
        console.log('Look for the slider element in the browser!');
        await page.waitForTimeout(30000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

findSlider().catch(console.error);
