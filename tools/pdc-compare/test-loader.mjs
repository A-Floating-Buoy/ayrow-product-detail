// pdc.js 제품 JS 불러오기 점검 — 스킨 파일을 가짜 주소(http://pdc.test)로 내주고 확인한다
//   실행: node test-loader.mjs
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const SKIN = path.resolve(import.meta.dirname, '../../../ayrow-cafe24-skin-2026');
const TYPES = { '.css': 'text/css', '.js': 'application/javascript', '.html': 'text/html' };
const DEMO_JS = "PDC.register('demo', function (root, PDC) { root.setAttribute('data-ok', String(PDC.qsa('[data-pdc-section]', root).length)); });";

function page(prefix) {
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="${prefix}/css/core/tokens.css">
<link rel="stylesheet" href="${prefix}/css/core/tokens-ayrow-v3.css">
<link rel="stylesheet" href="${prefix}/css/module/product/pdc.css">
</head><body>
<link rel="stylesheet" href="${prefix}/css/module/product/pdc-demo.css?ver=20261111000001">
<div class="pdc" data-pdc data-pdc-product="demo" data-pdc-ver="20261111000001">
  <section class="pdc__section pdc__section--contained" data-pdc-section="a" data-pdc-nav-title="A"><p>a</p></section>
  <section class="pdc__section pdc__section--band" data-pdc-section="b"><p>b</p></section>
  <section class="pdc__section" data-pdc-section="c"><ul><li>c</li></ul></section>
</div>
<script src="${prefix}/js/module/product/pdc.js"></script>
</body></html>`;
}

const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new' });
let failed = 0;

for (const prefix of ['', '/skin-skin10']) {
  const tab = await browser.newPage();
  await tab.setViewport({ width: 1280, height: 900 });
  const requests = [];
  await tab.setRequestInterception(true);
  tab.on('request', (req) => {
    const url = new URL(req.url());
    requests.push(url.pathname + url.search);
    if (url.pathname === '/test.html') return req.respond({ contentType: 'text/html', body: page(prefix) });
    if (url.pathname.endsWith('/pdc-demo.js')) return req.respond({ contentType: TYPES['.js'], body: DEMO_JS });
    if (url.pathname.endsWith('/pdc-demo.css')) return req.respond({ contentType: TYPES['.css'], body: '' });
    const file = path.join(SKIN, url.pathname.slice(prefix.length));
    if (fs.existsSync(file)) return req.respond({ contentType: TYPES[path.extname(file)] || 'text/plain', body: fs.readFileSync(file) });
    return req.respond({ status: 404, body: '' });
  });
  await tab.goto('http://pdc.test/test.html', { waitUntil: 'networkidle0' });
  const result = await tab.evaluate(() => {
    const root = document.querySelector('[data-pdc]');
    const pad = (key, side) => getComputedStyle(document.querySelector(`[data-pdc-section="${key}"]`))[`padding${side}`];
    return {
      ok: root.getAttribute('data-ok'),
      color: getComputedStyle(root).color,
      padA: [pad('a', 'Top'), pad('a', 'Bottom')],
      padB: [pad('b', 'Top'), pad('b', 'Bottom')],
      padC: [pad('c', 'Top'), pad('c', 'Bottom')],
    };
  });
  const expected = `${prefix}/js/module/product/pdc-demo.js?ver=20261111000001`;
  const loaded = requests.includes(expected);
  // 1280px: clamp(72px, 9vw, 120px) = 115.2px · a→b(band)→c 간격 규칙(띠 앞 섹션은 아래 여백 유지, 띠 아래는 0)
  const padOk = JSON.stringify([result.padA, result.padB, result.padC]) === JSON.stringify([['115.2px', '115.2px'], ['115.2px', '0px'], ['0px', '115.2px']]);
  const pass = loaded && result.ok === '3' && result.color === 'rgb(0, 119, 191)' && padOk;
  if (!pass) failed += 1;
  console.log(`${pass ? '통과' : '실패'}  기준 경로 "${prefix || '/'}"  제품 JS 요청 ${loaded ? expected : '없음'}  초기화 ${result.ok}  글자색 ${result.color}  여백 ${JSON.stringify([result.padA, result.padB, result.padC])}`);
  await tab.close();
}
await browser.close();
process.exit(failed ? 1 : 0);
