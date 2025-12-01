const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Extract table data directly from the DOM (no download button needed!)
 */
async function extractTableData() {
    console.log('=== Extract Table Data from DOM ===\n');

    const downloadDir = path.join(__dirname, 'downloads');
    if (!fs.existsSync(downloadDir)) {
        fs.mkdirSync(downloadDir, { recursive: true });
    }

    const TARGET_DATE = '2025-11-18';

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
        console.log('1. Navigating...');
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

        console.log('3. Scrolling to table...');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);
        console.log('   ✓ Scrolled\n');

        console.log('4. Extracting table data...');

        // Extract table data from DOM
        const tableData = await page.evaluate(() => {
            const table = document.querySelector('table[role="grid"]');
            if (!table) return null;

            const rows = [];
            const headerCells = table.querySelectorAll('thead th');
            const headers = Array.from(headerCells).map(th => th.textContent.trim());

            const bodyRows = table.querySelectorAll('tbody tr');
            bodyRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                const rowData = {};
                cells.forEach((cell, index) => {
                    rowData[headers[index]] = cell.textContent.trim();
                });
                rows.push(rowData);
            });

            return { headers, rows };
        });

        if (tableData && tableData.rows.length > 0) {
            console.log(`   ✓ Extracted ${tableData.rows.length} rows`);
            console.log(`   Headers: ${tableData.headers.join(', ')}\n`);

            // Convert to CSV
            const csvLines = [];
            csvLines.push(tableData.headers.join(','));

            tableData.rows.forEach(row => {
                const values = tableData.headers.map(header => {
                    const value = row[header] || '';
                    // Escape commas and quotes
                    if (value.includes(',') || value.includes('"')) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                });
                csvLines.push(values.join(','));
            });

            const csv = csvLines.join('\n');

            // Save to file
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `routersense_data_${timestamp}.csv`;
            const filepath = path.join(downloadDir, filename);

            fs.writeFileSync(filepath, csv);
            console.log(`✅ SUCCESS! Saved to: ${filename}\n`);
            console.log('Preview of first few rows:');
            console.log(csvLines.slice(0, 5).join('\n'));
        } else {
            console.log('   ✗ No table data found');
        }

        console.log('\nBrowser will close in 5 seconds...');
        await page.waitForTimeout(5000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

extractTableData().catch(console.error);
