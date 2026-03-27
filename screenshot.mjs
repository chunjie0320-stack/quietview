import puppeteer from 'puppeteer';
const browser = await puppeteer.launch({
  headless: true,
  executablePath: '/usr/bin/chromium-browser',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
});
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.goto('http://localhost:18234/quietview-demo.html', { waitUntil: 'networkidle0', timeout: 15000 });
await page.screenshot({ path: '/root/.openclaw/workspace/qv_final.png', fullPage: false });
await browser.close();
console.log('done');
