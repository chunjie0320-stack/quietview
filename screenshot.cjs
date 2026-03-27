const puppeteer = require('/usr/local/node/lib/node_modules/puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://localhost:18234/quietview-demo.html', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));
  // 点成长tab，展开喵子自言自语，看26日
  await page.evaluate(() => { document.querySelector('[data-tab="growth"]') && document.querySelector('[data-tab="growth"]').click(); });
  await new Promise(r => setTimeout(r, 800));
  await page.evaluate(() => {
    var items = document.querySelectorAll('.nav-l2');
    items.forEach(function(el){ if(el.textContent.indexOf('喵子自言自语') > -1) el.click(); });
  });
  await new Promise(r => setTimeout(r, 600));
  await page.evaluate(() => {
    var items = document.querySelectorAll('.nav-l3');
    items.forEach(function(el){ if(el.textContent.indexOf('03月26日') > -1) el.click(); });
  });
  await new Promise(r => setTimeout(r, 600));
  await page.screenshot({ path: '/root/.openclaw/workspace/qv_miao_date.png' });
  await browser.close();
  console.log('done');
})();
