const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

/**
 * Analyze the RouterSense page structure after JavaScript loads
 * Save the rendered HTML and DOM structure for analysis
 */
async function analyzePage() {
    const outputDir = path.join(__dirname, 'analysis');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({
        viewport: null
    });

    const page = await context.newPage();

    try {
        console.log('Loading page...\n');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });

        await page.waitForTimeout(5000); // Extra time for Streamlit to render

        console.log('Page loaded. Analyzing structure...\n');

        // 1. Save full rendered HTML
        const html = await page.content();
        fs.writeFileSync(path.join(outputDir, 'rendered_page.html'), html);
        console.log('✓ Saved rendered HTML');

        // 2. Find and analyze the table
        console.log('\n=== TABLE ANALYSIS ===');
        const tables = await page.locator('table, [role="table"], .dataframe, [class*="table"]').all();
        console.log(`Found ${tables.length} table-like element(s)\n`);

        for (let i = 0; i < tables.length; i++) {
            const table = tables[i];
            const tagName = await table.evaluate(el => el.tagName);
            const className = await table.getAttribute('class');
            const id = await table.getAttribute('id');

            console.log(`Table ${i}:`);
            console.log(`  Tag: <${tagName}>`);
            console.log(`  ID: ${id}`);
            console.log(`  Class: ${className}`);

            // Get table HTML
            const tableHTML = await table.evaluate(el => el.outerHTML.substring(0, 2000));
            fs.writeFileSync(path.join(outputDir, `table_${i}.html`), tableHTML);
            console.log(`  ✓ Saved to table_${i}.html\n`);
        }

        // 3. Hover over table and find buttons
        console.log('=== HOVERING OVER TABLE ===');
        if (tables.length > 0) {
            const mainTable = tables[0];
            await mainTable.hover();
            await page.waitForTimeout(2000);
            console.log('Hovered over first table\n');

            // Take screenshot after hover
            await page.screenshot({
                path: path.join(outputDir, 'after_hover.png'),
                fullPage: true
            });
            console.log('✓ Screenshot saved\n');

            // Find all visible buttons after hover
            console.log('=== BUTTONS AFTER HOVER ===');
            const buttons = await page.locator('button:visible, a:visible, [role="button"]:visible').all();
            console.log(`Found ${buttons.length} visible clickable elements\n`);

            const buttonInfo = [];
            for (let i = 0; i < Math.min(buttons.length, 30); i++) {
                const btn = buttons[i];
                const text = await btn.textContent().catch(() => '');
                const ariaLabel = await btn.getAttribute('aria-label').catch(() => '');
                const title = await btn.getAttribute('title').catch(() => '');
                const className = await btn.getAttribute('class').catch(() => '');
                const tagName = await btn.evaluate(el => el.tagName).catch(() => '');
                const dataTestId = await btn.getAttribute('data-testid').catch(() => '');

                const info = {
                    index: i,
                    tag: tagName,
                    text: text?.trim(),
                    ariaLabel,
                    title,
                    className,
                    dataTestId
                };

                buttonInfo.push(info);

                if (text?.toLowerCase().includes('download') ||
                    ariaLabel?.toLowerCase().includes('download') ||
                    title?.toLowerCase().includes('download') ||
                    className?.toLowerCase().includes('download')) {
                    console.log(`*** DOWNLOAD BUTTON CANDIDATE #${i} ***`);
                    console.log(`  Tag: <${tagName}>`);
                    console.log(`  Text: "${text?.trim()}"`);
                    console.log(`  aria-label: "${ariaLabel}"`);
                    console.log(`  title: "${title}"`);
                    console.log(`  class: "${className}"`);
                    console.log(`  data-testid: "${dataTestId}"`);
                    console.log('');
                }
            }

            // Save button info to JSON
            fs.writeFileSync(
                path.join(outputDir, 'buttons.json'),
                JSON.stringify(buttonInfo, null, 2)
            );
            console.log('✓ Saved button info to buttons.json\n');
        }

        // 4. Analyze the slider
        console.log('=== SLIDER ANALYSIS ===');
        const sliders = await page.locator('input[type="range"]').all();
        console.log(`Found ${sliders.length} slider(s)\n`);

        for (let i = 0; i < sliders.length; i++) {
            const slider = sliders[i];
            const min = await slider.getAttribute('min');
            const max = await slider.getAttribute('max');
            const value = await slider.getAttribute('value');
            const step = await slider.getAttribute('step');
            const id = await slider.getAttribute('id');
            const className = await slider.getAttribute('class');

            console.log(`Slider ${i}:`);
            console.log(`  ID: ${id}`);
            console.log(`  Class: ${className}`);
            console.log(`  min: ${min}, max: ${max}, value: ${value}, step: ${step}`);
            console.log('');
        }

        console.log('\n=== ANALYSIS COMPLETE ===');
        console.log(`Results saved to: ${outputDir}`);
        console.log('\nBrowser will stay open for 30 seconds for manual inspection...');

        await page.waitForTimeout(30000);

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await browser.close();
    }
}

analyzePage().catch(console.error);
