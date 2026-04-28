#!/usr/bin/env node
// Buddy 5状态截图 → 发给女王大人
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = '/tmp/buddy-shots';
fs.mkdirSync(OUT, { recursive: true });

const STATES = [
  { btn: 0, name: 'idle',     label: '😌 待机' },
  { btn: 1, name: 'happy',    label: '🎉 开心' },
  { btn: 2, name: 'confused', label: '🤔 困惑' },
  { btn: 3, name: 'sleeping', label: '😴 睡觉' },
  { btn: 4, name: 'peeking',  label: '👀 偷看' },
];

// ensure http server
const { execSync, spawn } = require('child_process');
try { execSync('curl -s http://localhost:9988/buddy-pixel-demo.html > /dev/null'); }
catch(e) {
  spawn('python3', ['-m', 'http.server', '9988'], {
    cwd: '/root/.openclaw/workspace', detached: true, stdio: 'ignore'
  }).unref();
  execSync('sleep 2');
}

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 800, height: 600 });
  await page.goto('http://localhost:9988/buddy-pixel-demo.html', { waitUntil: 'networkidle' });

  for (const s of STATES) {
    const btns = await page.locator('.btn').all();
    await btns[s.btn].click();
    await page.waitForTimeout(400);
    const file = path.join(OUT, `${s.name}.png`);
    await page.locator('#stage').screenshot({ path: file });
    console.log(`✓ ${s.label} → ${file}`);
  }

  await browser.close();
  console.log('done');
})();
