const { chromium } = require('playwright');

/**
 * Enhanced UI Inspector - specifically looking for date selection controls
 */
async function inspectDateControls() {
    const browser = await chromium.launch({
        headless: false,
        slowMo: 300
    });

    const page = await browser.newPage();

    try {
        console.log('Opening RouterSense dashboard...\n');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });

        await page.waitForTimeout(3000);

        console.log('=== DATE SELECTION CONTROLS ANALYSIS ===\n');

        // 1. Check for ALL input elements
        console.log('1. ALL INPUT ELEMENTS:');
        const inputs = await page.locator('input').all();
        console.log(`   Found ${inputs.length} input element(s)\n`);
        for (let i = 0; i < inputs.length; i++) {
            const input = inputs[i];
            const type = await input.getAttribute('type');
            const id = await input.getAttribute('id');
            const className = await input.getAttribute('class');
            const placeholder = await input.getAttribute('placeholder');
            const value = await input.getAttribute('value');
            const name = await input.getAttribute('name');

            console.log(`   Input ${i}:`);
            console.log(`      type="${type}"`);
            console.log(`      id="${id}"`);
            console.log(`      name="${name}"`);
            console.log(`      class="${className}"`);
            console.log(`      placeholder="${placeholder}"`);
            console.log(`      value="${value}"`);
            console.log('');
        }

        // 2. Check for date-related text
        console.log('\n2. ELEMENTS WITH DATE-RELATED TEXT:');
        const dateElements = await page.locator('*:has-text("Select"), *:has-text("Date"), *:has-text("2025"), *:has-text("November"), *:has-text("Nov")').all();
        console.log(`   Found ${Math.min(dateElements.length, 10)} date-related elements (showing first 10)\n`);
        for (let i = 0; i < Math.min(dateElements.length, 10); i++) {
            const el = dateElements[i];
            const tagName = await el.evaluate(e => e.tagName);
            const text = await el.textContent();
            const className = await el.getAttribute('class');
            console.log(`   Element ${i}: <${tagName}> class="${className}"`);
            console.log(`      text="${text?.trim().substring(0, 100)}"`);
            console.log('');
        }

        // 3. Look for calendar/date picker components
        console.log('\n3. CALENDAR/DATE PICKER COMPONENTS:');
        const calendarSelectors = [
            '[class*="calendar"]',
            '[class*="datepicker"]',
            '[class*="date-picker"]',
            '[id*="calendar"]',
            '[id*="datepicker"]',
            '[role="dialog"]',
            '[class*="picker"]'
        ];

        for (const selector of calendarSelectors) {
            const count = await page.locator(selector).count();
            if (count > 0) {
                console.log(`   Found ${count} element(s) with selector: ${selector}`);
            }
        }

        // 4. Check the visible text on the page for date info
        console.log('\n4. CURRENT DATE DISPLAY:');
        const bodyText = await page.locator('body').textContent();
        const dateMatches = bodyText?.match(/\d{4}-\d{2}-\d{2}/g);
        if (dateMatches) {
            console.log(`   Found date patterns: ${[...new Set(dateMatches)].join(', ')}`);
        }

        // 5. Try to find the "Select hour" element and its siblings
        console.log('\n5. "SELECT HOUR" AREA STRUCTURE:');
        const selectHourElement = page.locator('text="Select hour"').first();
        if (await selectHourElement.count() > 0) {
            console.log('   Found "Select hour" element');

            // Get parent container
            const parent = selectHourElement.locator('xpath=..');
            const parentHTML = await parent.evaluate(el => {
                return el.outerHTML.substring(0, 500);
            });
            console.log('   Parent HTML (first 500 chars):');
            console.log(parentHTML);
        }

        // 6. Interactive inspection
        console.log('\n\n=== INTERACTIVE MODE ===');
        console.log('The browser will stay open for 60 seconds.');
        console.log('Please manually interact with the date selector to see how it works.');
        console.log('Observe:');
        console.log('  - How do you change the date?');
        console.log('  - Is there a calendar popup?');
        console.log('  - Are there arrow buttons?');
        console.log('  - Is it part of the same slider as the hour?');
        console.log('\nWatching for 60 seconds...\n');

        await page.waitForTimeout(60000);

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await browser.close();
    }
}

inspectDateControls().catch(console.error);
