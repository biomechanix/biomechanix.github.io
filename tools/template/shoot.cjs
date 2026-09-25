// Full-page screenshots at exact viewport widths (helper for side_by_side.py).
// Input: JSON array of {url, width, out}. Uses Playwright Chromium, or the
// installed Google Chrome if Playwright's Chromium isn't downloaded.
// playwright-core is resolved from $PLAYWRIGHT_CORE, node_modules, or the
// sibling mm-frontend checkout.
const path = require('path');
function loadPlaywright() {
  for (const t of [process.env.PLAYWRIGHT_CORE, 'playwright-core',
    path.resolve(__dirname, '../../../mm-frontend/node_modules/playwright-core')].filter(Boolean)) {
    try { return require(t); } catch (_) {}
  }
  console.error('playwright-core not found; set PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core');
  process.exit(2);
}
const pw = loadPlaywright();
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  let browser;
  try { browser = await pw.chromium.launch(); } catch (_) { browser = await pw.chromium.launch({ channel: 'chrome' }); }
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.width, height: 900 }, deviceScaleFactor: 1 });
    await page.goto(j.url, { waitUntil: 'networkidle', timeout: 45000 });
    // load lazy images and let entrance animations settle
    await page.evaluate(async () => {
      document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; });
      for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(800);
    await page.screenshot({ path: j.out, fullPage: true });
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
