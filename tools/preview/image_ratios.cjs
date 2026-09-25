// Measure how images actually render (width x height) in WebKit and Chromium,
// on desktop and iPhone viewports, and compare with each image's natural ratio.
// Use this when someone says images look "stretched" — Chrome alone is not
// proof, because Safari/WebKit lays out flex/grid images differently.
//
// Usage: node tools/preview/image_ratios.cjs URL [selector]
//   URL       live page (https://biomechanix.github.io/fitness) or preview
//   selector  default 'main img'
// Needs playwright-core plus browsers (`npx playwright install webkit chromium`).
// Resolves playwright-core from $PLAYWRIGHT_CORE, then normal require, then the
// sibling mm-frontend checkout, which already has it installed.
const path = require('path');
function loadPlaywright() {
  const tries = [process.env.PLAYWRIGHT_CORE, 'playwright-core',
    path.resolve(__dirname, '../../../mm-frontend/node_modules/playwright-core')].filter(Boolean);
  for (const t of tries) { try { return require(t); } catch (_) {} }
  console.error('playwright-core not found; set PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core');
  process.exit(2);
}
const pw = loadPlaywright();
(async () => {
  const url = process.argv[2], sel = process.argv[3] || 'main img';
  if (!url) { console.error('usage: node image_ratios.cjs URL [selector]'); process.exit(2); }
  let worst = 0;
  for (const engine of ['webkit', 'chromium']) {
    let browser;
    try { browser = await pw[engine].launch(); }
    catch (e) {
      // Fall back to the locally installed Google Chrome for the Chromium engine.
      try { if (engine !== 'chromium') throw e; browser = await pw.chromium.launch({ channel: 'chrome' }); }
      catch (_) { console.log(`${engine}: not installed (npx playwright install ${engine})`); continue; }
    }
    for (const [name, opts] of [['desktop', { viewport: { width: 1280, height: 900 } }], ['iphone', pw.devices['iPhone 13']]]) {
      const page = await (await browser.newContext(opts)).newPage();
      await page.goto(url, { waitUntil: 'networkidle' });
      // Lazy images off-screen haven't loaded yet (naturalWidth 0) — scroll them in.
      await page.$$eval(sel, imgs => imgs.forEach(i => { i.loading = 'eager'; i.scrollIntoView(); }));
      await page.waitForFunction(s => [...document.querySelectorAll(s)].every(i => i.complete), sel, { timeout: 15000 }).catch(() => {});
      const unloaded = await page.$$eval(sel, imgs => imgs.filter(i => !i.naturalWidth).map(i => i.getAttribute('src')));
      for (const u of unloaded) { console.log(`${engine.padEnd(8)} ${name.padEnd(7)} NOT LOADED ${u}`); worst = Math.max(worst, 1); }
      const rows = await page.$$eval(sel, imgs => imgs.filter(i => i.naturalWidth).map(i => {
        const cs = getComputedStyle(i);
        const bw = parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth);
        const bh = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth);
        const w = i.clientWidth, h = i.clientHeight;          // content box, excludes border
        return { src: i.getAttribute('src'), w, h, got: h / w, want: i.naturalHeight / i.naturalWidth, bw, bh };
      }));
      for (const r of rows) {
        const err = Math.abs(r.got / r.want - 1);
        worst = Math.max(worst, err);
        console.log(`${engine.padEnd(8)} ${name.padEnd(7)} ${err > 0.01 ? 'STRETCHED' : 'ok       '} ${r.src} ${r.w}x${r.h} ratio ${r.got.toFixed(3)} (natural ${r.want.toFixed(3)})`);
      }
      if (!rows.length) console.log(`${engine} ${name}: no images matched '${sel}'`);
    }
    await browser.close();
  }
  process.exit(worst > 0.01 ? 1 : 0);
})();
