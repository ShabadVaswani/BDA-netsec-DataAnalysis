const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Intercept network requests to find how data is loaded
 */
async function interceptNetworkRequests() {
    console.log('=== Network Request Interceptor ===\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300,
        args: ['--start-maximized']
    });

    const context = await browser.newContext({
        viewport: null
    });

    const page = await context.newPage();

    const apiRequests = [];
    const dataResponses = [];

    // Listen to all requests
    page.on('request', request => {
        const url = request.url();
        const method = request.method();

        // Log API-like requests
        if (url.includes('api') || url.includes('data') || url.includes('.json') || url.includes('.csv')) {
            console.log(`📤 REQUEST: ${method} ${url}`);
            apiRequests.push({ method, url, timestamp: new Date().toISOString() });
        }
    });

    // Listen to all responses
    page.on('response', async response => {
        const url = response.url();
        const status = response.status();
        const contentType = response.headers()['content-type'] || '';

        // Log interesting responses
        if (contentType.includes('json') || contentType.includes('csv') || url.includes('data')) {
            console.log(`📥 RESPONSE: ${status} ${url}`);
            console.log(`   Content-Type: ${contentType}`);

            try {
                // Try to get response body for JSON
                if (contentType.includes('json')) {
                    const body = await response.json();
                    console.log(`   Data preview: ${JSON.stringify(body).substring(0, 200)}...`);

                    dataResponses.push({
                        url,
                        status,
                        contentType,
                        data: body,
                        timestamp: new Date().toISOString()
                    });
                }
                // For CSV
                else if (contentType.includes('csv') || contentType.includes('text')) {
                    const text = await response.text();
                    console.log(`   Data preview: ${text.substring(0, 200)}...`);

                    dataResponses.push({
                        url,
                        status,
                        contentType,
                        data: text,
                        timestamp: new Date().toISOString()
                    });
                }
            } catch (e) {
                console.log(`   (Could not read body: ${e.message})`);
            }

            console.log('');
        }
    });

    try {
        console.log('Navigating to dashboard...\n');
        await page.goto('https://dashboard.routersense.ai/view_device?pid=3fdb2c571ad727deaaa2a97b4fcf6b22', {
            waitUntil: 'networkidle',
            timeout: 60000
        });

        console.log('\nPage loaded. Waiting for data to load...\n');
        await page.waitForTimeout(5000);

        console.log('Clicking Phone tab...\n');
        const phoneTab = page.locator('button[role="tab"]:has-text("Phone")');
        if (await phoneTab.count() > 0) {
            await phoneTab.first().click();
            await page.waitForTimeout(3000);
        }

        console.log('Scrolling down...\n');
        await page.evaluate(() => window.scrollTo(0, 800));
        await page.waitForTimeout(3000);

        console.log('\n=== SUMMARY ===');
        console.log(`Total API requests captured: ${apiRequests.length}`);
        console.log(`Total data responses captured: ${dataResponses.length}\n`);

        // Save captured data
        const outputDir = path.join(__dirname, 'network_analysis');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        fs.writeFileSync(
            path.join(outputDir, 'api_requests.json'),
            JSON.stringify(apiRequests, null, 2)
        );

        fs.writeFileSync(
            path.join(outputDir, 'data_responses.json'),
            JSON.stringify(dataResponses, null, 2)
        );

        console.log('Saved network data to network_analysis/ folder');
        console.log('\nBrowser will stay open for 20 seconds...');
        await page.waitForTimeout(20000);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
}

interceptNetworkRequests().catch(console.error);
