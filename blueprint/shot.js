// 사용: node blueprint/shot.js <html> <png> [width] [height]  — 미리보기 스크린샷 (보고서 빌드에는 쓰지 않는다)
const { chromium } = require('playwright');
(async () => {
  const [html, png, w, h] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: process.env.SE_CHROMIUM || '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: +(w || 1400), height: +(h || 1000) } });
  await p.goto('file://' + require('path').resolve(html));
  await p.screenshot({ path: png, fullPage: true });
  await b.close();
})();
