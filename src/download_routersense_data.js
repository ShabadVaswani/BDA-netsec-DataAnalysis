const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Load configuration
let config;
try {
    const configPath = path.join(__dirname, '..', 'config.json');
    if (!fs.existsSync(configPath)) {
        console.error('Error: config.json not found!');
        console.error('Please copy config.example.json to config.json and fill in your device ID.');
        process.exit(1);
    }
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
} catch (error) {
    console.error('Error loading config.json:', error.message);
    process.exit(1);
}

// Parse arguments
const args = process.argv.slice(2);
let START_DATE = config.download.defaultStartDate;
let END_DATE = config.download.defaultEndDate;

if (args.length === 1) {
    START_DATE = args[0];
    END_DATE = args[0];
} else if (args.length >= 2) {
    START_DATE = args[0];
    END_DATE = args[1];
}

function getDateRange(startDate, endDate) {
    const dates = [];
    const start = new Date(startDate);
    const end = new Date(endDate);

    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        dates.push(d.toISOString().split('T')[0]);
    }

    return dates;
}

async function getSliderDateTime(page) {
    const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();
    const valueText = await slider.getAttribute('aria-valuetext');
    const [datePart, timePart] = valueText.split(' ');
    return new Date(`${datePart}T${timePart}:00`);
}

async function dragSlider(page, deltaPosition) {
    const slider = page.locator('[role="slider"][aria-label="Select hour"]').first();
    const thumbBox = await slider.boundingBox();
    const trackBox = await page.evaluate(() => {
        const thumb = document.querySelector('[role="slider"][aria-label="Select hour"]');
        const track = thumb.parentElement;
        const box = track.getBoundingClientRect();
        return { x: box.x, y: box.y, width: box.width, height: box.height };
    });

    const startX = thumbBox.x + (thumbBox.width / 2);
    const startY = thumbBox.y + (thumbBox.height / 2);
    const endX = startX + (trackBox.width * deltaPosition);
    const endY = trackBox.y + (trackBox.height / 2);

    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.waitForTimeout(50);
    await page.mouse.move(endX, endY, { steps: 5 });
    await page.waitForTimeout(50);
    await page.mouse.up();
    await page.waitForTimeout(800);
}

async function seekToDateTime(page, targetDate, targetHour) {
    const targetDateTime = new Date(`${targetDate}T${targetHour.toString().padStart(2, '0')}:00:00`);
    const targetTime = targetDateTime.getTime();

    console.log(`  Seeking to ${targetDate} ${targetHour.toString().padStart(2, '0')}:00...`);

    let attempts = 0;
    const maxAttempts = 20;
    let lastDiff = Infinity;
    let stuckCount = 0;

    while (attempts < maxAttempts) {
        const currentDateTime = await getSliderDateTime(page);
        const currentTime = currentDateTime.getTime();
        const diff = targetTime - currentTime;
        const diffHours = diff / (1000 * 60 * 60);

        console.log(`    [${attempts + 1}] ${currentDateTime.toISOString().substring(0, 16).replace('T', ' ')} (${diffHours > 0 ? '+' : ''}${diffHours.toFixed(1)}h)`);

        if (Math.abs(diffHours) < 0.5) {
            console.log(`    ✓ Target reached!`);
            return true;
        }

        if (Math.abs(diffHours - lastDiff) < 0.1) {
            stuckCount++;
            if (stuckCount > 3) {
                console.log(`    ⚠ Stuck, accepting current position`);
                return true;
            }
        } else {
            stuckCount = 0;
        }
        lastDiff = diffHours;

        let dragAmount;
        const absDiff = Math.abs(diffHours);

        if (absDiff > 480) {
            dragAmount = diffHours > 0 ? 0.15 : -0.15;
        } else if (absDiff > 240) {
            dragAmount = diffHours > 0 ? 0.08 : -0.08;
        } else if (absDiff > 120) {
            dragAmount = diffHours > 0 ? 0.04 : -0.04;
        } else if (absDiff > 48) {
            dragAmount = diffHours > 0 ? 0.02 : -0.02;
        } else if (absDiff > 12) {
            dragAmount = diffHours > 0 ? 0.01 : -0.01;
        } else if (absDiff > 3) {
            dragAmount = diffHours > 0 ? 0.005 : -0.005;
        } else {
            dragAmount = diffHours > 0 ? 0.002 : -0.002;
        }

        await dragSlider(page, dragAmount);
        attempts++;
    }

    console.log(`    ⚠ Max attempts reached`);
    return false;
}

async function waitForDataToLoad(page) {
    try {
        await page.waitForTimeout(2000);
        try {
            await page.waitForSelector('text=RUNNING', { state: 'hidden', timeout: 15000 });
        } catch {
            await page.waitForTimeout(8000);
        }
        await page.waitForTimeout(2000);
    } catch {
        await page.waitForTimeout(10000);
    }
}

async function downloadDateRange() {
    const dates = getDateRange(START_DATE, END_DATE);

    console.log('\n=== RouterSense Downloader (ISO Timestamps) ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 50,
        args: ['--start-maximized']
    });

    const page = await browser.newPage({ viewport: null });

    let totalDownloaded = 0;
    let totalSkipped = 0;
    let totalUpdated = 0;

    try {
        console.log('Loading...');
        const routersenseUrl = `${config.routersense.baseUrl}?pid=${config.routersense.deviceId}`;
        await page.goto(routersenseUrl, {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        await page.waitForTimeout(3000);

        await page.locator('button:has-text("Phone")').first().click();
        await page.waitForTimeout(2000);

        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(1500);
        console.log('✓ Ready\n');

        for (let dateIndex = 0; dateIndex < dates.length; dateIndex++) {
            const targetDate = dates[dateIndex];
            const baseDir = path.join(__dirname, '..', config.download.outputDir);
            const dateDir = path.join(baseDir, targetDate);

            if (!fs.existsSync(dateDir)) {
                fs.mkdirSync(dateDir, { recursive: true });
            }

            console.log(`\nDate ${dateIndex + 1}/${dates.length}: ${targetDate}\n`);

            let downloaded = 0;
            let skipped = 0;
            let updated = 0;

            for (let hour = 0; hour < 24; hour++) {
                const hourStr = hour.toString().padStart(2, '0');

                console.log(`[${hour + 1}/24] ${targetDate} ${hourStr}:00`);

                try {
                    await seekToDateTime(page, targetDate, hour);
                    await waitForDataToLoad(page);

                    const actualDateTime = await getSliderDateTime(page);
                    console.log(`    Final: ${actualDateTime.toISOString().substring(0, 16).replace('T', ' ')}`);

                    // Extract data with ISO timestamp conversion
                    const tableData = await page.evaluate((targetDate) => {
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
                                const header = headers[index];
                                const value = cell.textContent.trim();

                                // Convert Time field to ISO timestamp
                                if (header === 'Time' && value) {
                                    const [hours, minutes] = value.split(':');
                                    if (hours && minutes) {
                                        const isoTimestamp = `${targetDate}T${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}:00.000Z`;
                                        rowData[header] = isoTimestamp;
                                    } else {
                                        rowData[header] = value;
                                    }
                                } else {
                                    rowData[header] = value;
                                }
                            });
                            rows.push(rowData);
                        });

                        return { headers, rows };
                    }, targetDate);

                    if (tableData && tableData.rows.length > 0) {
                        const csvLines = [];
                        csvLines.push(tableData.headers.join(','));

                        tableData.rows.forEach(row => {
                            const values = tableData.headers.map(header => {
                                const value = row[header] || '';
                                if (value.includes(',') || value.includes('"')) {
                                    return `"${value.replace(/"/g, '""')}"`;
                                }
                                return value;
                            });
                            csvLines.push(values.join(','));
                        });

                        const newCsv = csvLines.join('\n');
                        const newHash = crypto.createHash('md5').update(newCsv).digest('hex');

                        const filename = `hour_${hourStr}.csv`;
                        const filepath = path.join(dateDir, filename);

                        if (fs.existsSync(filepath)) {
                            const existingCsv = fs.readFileSync(filepath, 'utf8');
                            const existingHash = crypto.createHash('md5').update(existingCsv).digest('hex');

                            if (newHash === existingHash) {
                                skipped++;
                                console.log('    ⏭️  Skipped');
                            } else {
                                fs.writeFileSync(filepath, newCsv);
                                updated++;
                                console.log('    🔄 Updated');
                            }
                        } else {
                            fs.writeFileSync(filepath, newCsv);
                            downloaded++;
                            console.log('    ✅ Downloaded');
                        }
                    }

                } catch (error) {
                    console.error(`    ✗ ${error.message}`);
                }
            }

            console.log(`\nSummary: 📥 ${downloaded} | 🔄 ${updated} | ⏭️ ${skipped}`);

            totalDownloaded += downloaded;
            totalSkipped += skipped;
            totalUpdated += updated;
        }

        console.log(`\n=== Final: 📥 ${totalDownloaded} | 🔄 ${totalUpdated} | ⏭️ ${totalSkipped} ===`);

    } catch (error) {
        console.error(`\n✗ Fatal: ${error.message}`);
    } finally {
        console.log('\nClosing...');
        await page.waitForTimeout(5000);
        await browser.close();
    }
}

downloadDateRange().catch(console.error);
