// 상품 상세 섹션별 스크린샷 (이전 전후 화면 비교용)
//   준비: npm install (이 폴더에서 한 번)
//   실행: node shoot.mjs <url> <outDir> [widths]
//   예)   node shoot.mjs "https://ayrow.cafe24.com/skin-skin10/product/detail.html?product_no=18" after/sun-veil
//   비교: python3 compare.py sun-veil
//   올리기 · 붙여 넣기 전 확인: node shoot.mjs "<url>" after/sun-veil --html=../../sun-veil/cafe24-admin/sun-veil-pdc.html
//   창으로 직접 보기: 위 명령 끝에 --open=1 (찍지 않는다)
// 움직임 줄이기 상태로 찍는다 — 움직임 자체는 눈으로 따로 확인한다.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const flags = Object.fromEntries(args.filter((a) => a.startsWith('--')).map((a) => a.slice(2).split('=')));
const [url, out, widthsArg] = args.filter((a) => !a.startsWith('--'));
const widths = (widthsArg || '375,768,1024,1280,1920').split(',').map(Number);

// --html=<상세 HTML 파일>  실제 페이지의 상세 내용을 이 파일로 바꿔서 찍는다(관리자에 붙여 넣기 전 확인용).
//                          스킨 CSS · JS도 올리기 전의 로컬 파일로 바꿔 끼운다(--skin=<스킨 레포>, 기본은 옆 폴더).
let LOCAL_HTML = flags.html ? fs.readFileSync(flags.html, 'utf8') : null;
const SKIN = path.resolve(flags.skin || path.join(import.meta.dirname, '../../../ayrow-cafe24-skin-2026'));
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
const TYPES = { '.css': 'text/css', '.js': 'application/javascript' };
const skinBase = new URL(url).pathname.match(/^\/skin-[^/]+/)?.[0] || '';
const origin = new URL(url).origin;
const remoteCache = new Map();
const patched = new Set();
const STAMP = Date.now();

async function remoteText(href) {
  if (!remoteCache.has(href)) remoteCache.set(href, fetch(href, { headers: { 'user-agent': UA } }).then((r) => (r.ok ? r.text() : null)));
  return remoteCache.get(href);
}

// 실제 페이지에서 상세 내용 구간(제품 CSS <link> ~ 루트 </div>)을 로컬 HTML로 바꾼다
function spliceDetail(page) {
  const start = page.search(/<link rel="stylesheet" href="[^"]*\/css\/module\/product\/(sun-veil-pdp|pdp|pdc)[^"]*">/);
  const lastRoot = Math.max(page.lastIndexOf('data-sv-sequence-pdp'), page.lastIndexOf('data-pdp-'), page.lastIndexOf('data-pdc-'));
  const reviews = page.indexOf('product-story-reviews', lastRoot);
  const end = page.lastIndexOf('</div>', page.lastIndexOf('<script', reviews));
  if (start < 0 || end < start) throw new Error('상세 내용 구간을 찾지 못함');
  const detail = LOCAL_HTML.replace(/(href|src)="\/(css|js)\//g, `$1="${skinBase}/$2/`);
  return page.slice(0, start) + detail + '\n      ' + page.slice(end);
}

// 묶음(optimizer) 안에 원문 그대로 들어 있는 스킨 파일을 로컬 파일로 바꾼다
async function patchBundle(text, ext) {
  const dirs = ext === '.js' ? ['js/module/product', 'js/components'] : ['css/module/product'];
  for (const dir of dirs) {
    for (const name of fs.readdirSync(path.join(SKIN, dir)).filter((f) => f.endsWith(ext))) {
      const local = fs.readFileSync(path.join(SKIN, dir, name), 'utf8');
      // ?t= 를 붙여 CDN 캐시가 아닌 서버의 지금 파일을 받는다(캐시본은 묶음과 달라 바꿔 끼우기가 실패한다)
      const remote = await remoteText(`${origin}${skinBase}/${dir}/${name}?t=${STAMP}`);
      if (remote && remote !== local && text.includes(remote)) text = text.replace(remote, () => local);
      // CSS 묶음은 카페24가 가공해 넣어 원문이 그대로 없다 — 바뀐 파일은 묶음 끝에 덧붙인다(같은 선택자는 뒤가 이긴다. 지운 규칙은 남는다)
      else if (ext === '.css' && remote && remote !== local && text.includes(`.${name.replace('.css', '')}`)) {
        if (!patched.has(name)) console.log('  (CSS 묶음 끝에 로컬 파일 덧붙임:', name + ')');
        patched.add(name);
        text += `\n${local}`;
      }
    }
  }
  return text;
}

async function intercept(page) {
  if (!LOCAL_HTML) return;
  await page.setRequestInterception(true);
  page.on('request', async (req) => {
    try {
      const u = new URL(req.url());
      if (u.origin !== origin) return req.continue();
      if (req.isNavigationRequest() && req.frame() === page.mainFrame()) {
        if (flags.open) LOCAL_HTML = fs.readFileSync(flags.html, 'utf8');
        return req.respond({ contentType: 'text/html; charset=utf-8', body: spliceDetail(await remoteText(req.url())) });
      }
      if (u.pathname.includes('/ind-script/optimizer')) {
        const ext = u.search.includes('type=css') ? '.css' : '.js';
        return req.respond({ contentType: TYPES[ext], body: await patchBundle(await remoteText(req.url()), ext) });
      }
      const file = path.join(SKIN, u.pathname.slice(skinBase.length));
      if (/^\/(css|js)\//.test(u.pathname.slice(skinBase.length)) && fs.existsSync(file)) {
        return req.respond({ contentType: TYPES[path.extname(file)] || 'text/plain', body: fs.readFileSync(file) });
      }
      return req.continue();
    } catch (e) {
      console.error('intercept', e.message);
      return req.continue();
    }
  });
}
const SECTION = '[data-pdc-section],[data-pdp-section],[data-sv-sequence-pdp-section]';
const HIDE = '#header,.site-header,header,.product-actions,.toc-bar,.announcement-bar,.alpha_widget,iframe{visibility:hidden!important}'
  + '*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;transition-duration:0s!important;transition-delay:0s!important}';

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: flags.open ? false : 'new',
  defaultViewport: flags.open ? null : undefined,
  args: flags.open ? ['--window-size=1440,960'] : ['--hide-scrollbars'],
});

// --open=1: 찍지 않고 창을 띄워 직접 본다(로컬 HTML · 스킨 파일을 끼운 상태 · 움직임 켜짐). 파일을 고치면 새로 고침, 창을 닫으면 끝난다
if (flags.open) {
  const page = (await browser.pages())[0] || (await browser.newPage());
  page.on('pageerror', (e) => console.log('  페이지 오류:', String(e.message).slice(0, 160)));
  await intercept(page);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await new Promise((resolve) => browser.on('disconnected', resolve));
  process.exit(0);
}

for (const w of widths) {
  const page = await browser.newPage();
  await page.setViewport({ width: w, height: w < 768 ? 812 : 900, deviceScaleFactor: 1 });
  if (!flags.probe) await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  page.on('pageerror', (e) => console.log('  페이지 오류:', String(e.message).slice(0, 160)));
  await intercept(page);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 90000 });
  if (flags.probe) {
    // --probe: 움직임을 켠 채 섹션마다 스크롤해 동작 상태를 적는다(스크린샷 없음). 구 · 신 결과 파일을 diff로 비교한다
    const dirP = `${out}/${w}`;
    fs.mkdirSync(dirP, { recursive: true });
    const state = await page.evaluate(async (SECTION) => {
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      const norm = (name) => name.replace(/sv-sequence-pdp-|pd[pc]__?|pd[pc]-/g, '');
      const rows = [];
      for (const section of document.querySelectorAll(SECTION)) {
        const rect = section.getBoundingClientRect();
        // 섹션 위 · 가운데 · 아래를 차례로 지나간다
        for (const part of [0.05, 0.5, 0.95]) {
          scrollTo(0, scrollY + section.getBoundingClientRect().top + rect.height * part - innerHeight / 2);
          await wait(450);
        }
        await wait(1500);
        const all = [section, ...section.querySelectorAll('*')];
        const states = {};
        all.forEach((el) => el.classList.forEach((c) => { if (/^is-/.test(c)) states[c] = (states[c] || 0) + 1; }));
        rows.push({
          key: section.getAttribute('data-pdc-section') || section.getAttribute('data-sv-sequence-pdp-section') || section.getAttribute('data-pdp-section'),
          states,
          counts: [...section.querySelectorAll('[data-count-to]')].map((el) => el.textContent.trim()),
          expanded: section.querySelectorAll('[aria-expanded="true"]').length,
          step: [...section.querySelectorAll('[aria-current]')].map((el) => el.getAttribute('aria-current')).join(','),
          swiper: [...section.querySelectorAll('.swiper')].map((el) => `${el.swiper ? el.swiper.slides.length : 'x'}/${el.swiper ? el.swiper.params.slidesPerView : 'x'}/${el.swiper && el.swiper.params.autoplay && el.swiper.params.autoplay.enabled ? 'auto' : 'manual'}`),
          playing: [...section.querySelectorAll('video')].map((v) => (v.paused ? 'paused' : 'playing')),
          vars: [...new Set(all.flatMap((el) => [...el.style]).filter((n) => n.startsWith('--')).map(norm))].sort(),
          lines: section.querySelectorAll('[class*="choice__line"]').length,
        });
      }
      // 사용법 2단계 누르기 → 영상 위치
      const step = document.querySelectorAll('[data-pdc-usage-step],[data-sv-sequence-pdp-usage-step]')[1];
      if (step) {
        step.scrollIntoView({ block: 'center' });
        await wait(400);
        step.click();
        await wait(900);
        const video = step.closest(SECTION).querySelector('video');
        rows.push({ key: 'usage-click', current: step.getAttribute('aria-current'), time: Math.round(video.currentTime) >= 10 ? '>=10' : String(Math.round(video.currentTime)) });
      }
      return rows;
    }, SECTION);
    fs.writeFileSync(`${dirP}/probe.json`, JSON.stringify(state, null, 1));
    console.log(w, 'probe', state.length);
    await page.close();
    continue;
  }
  await page.addStyleTag({ content: HIDE });
  // 끝까지 천천히 스크롤 → 지연 이미지 · 등장 효과 발동
  await page.evaluate(async () => {
    const step = Math.round(innerHeight * 0.6);
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
      scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 180));
    }
    scrollTo(0, 0);
    document.querySelectorAll('video').forEach((v) => { try { v.pause(); v.currentTime = 0; } catch (e) {} });
    await Promise.all([...document.images].filter((i) => !i.complete).map((i) => new Promise((r) => {
      i.onload = i.onerror = r;
      setTimeout(r, 8000);
    })));
  });
  await new Promise((r) => setTimeout(r, 1500));

  const dir = `${out}/${w}`;
  fs.mkdirSync(dir, { recursive: true });
  const els = await page.$$(SECTION);
  const meta = [];
  let n = 0;
  for (const el of els) {
    const info = await el.evaluate((e) => ({
      key: e.getAttribute('data-pdc-section') || e.getAttribute('data-pdp-section') || e.getAttribute('data-sv-sequence-pdp-section'),
      h: Math.round(e.getBoundingClientRect().height),
      w: Math.round(e.getBoundingClientRect().width),
      // 섹션 사이 간격 확인용(세트 상세): 문서 기준 위치와 위아래 여백
      top: Math.round(e.getBoundingClientRect().top + scrollY),
      pt: Math.round(parseFloat(getComputedStyle(e).paddingTop)),
      pb: Math.round(parseFloat(getComputedStyle(e).paddingBottom)),
    }));
    n += 1;
    const name = `${String(n).padStart(2, '0')}-${info.key}.png`;
    try {
      await el.screenshot({ path: `${dir}/${name}`, captureBeyondViewport: true });
      meta.push({ ...info, file: name });
    } catch (e) {
      meta.push({ ...info, error: String(e.message).slice(0, 80) });
    }
  }
  fs.writeFileSync(`${dir}/meta.json`, JSON.stringify(meta, null, 1));
  const kind = await page.evaluate(() => ({
    pdc: document.querySelectorAll('[data-pdc-section]').length,
    old: document.querySelectorAll('[data-pdp-section],[data-sv-sequence-pdp-section]').length,
    nav: document.querySelectorAll('[data-product-story-nav] .sidebar-nav__subitem').length,
    scripts: [...document.querySelectorAll('script[data-pdc-script]')].map((el) => el.getAttribute('src')).join(' '),
    done: Object.keys((document.querySelector('[data-pdc]') || {}).__pdcDone || {}).join(' '),
    // 동작 상태 — 구 화면과 숫자가 같아야 한다
    swipers: document.querySelectorAll('.product-story-content .swiper-initialized').length,
    bullets: document.querySelectorAll('.product-story-content .swiper-pagination-bullet').length,
    revealed: document.querySelectorAll('.product-story-content .is-revealed').length,
    counts: [...document.querySelectorAll('[data-count-to]')].map((el) => el.textContent.trim()).join('|'),
    faq: (() => {
      const buttons = [...document.querySelectorAll('[data-pdc-full-faq-button],[data-sv-sequence-pdp-full-faq-button],[data-pdc-faq-button],[data-pdp-faq-button]')];
      const target = buttons[2] || buttons[0];
      if (!target) return 'none';
      const before = target.getAttribute('aria-expanded');
      target.click();
      const after = target.getAttribute('aria-expanded');
      target.click();
      return `${buttons.length}:${before}>${after}>${target.getAttribute('aria-expanded')}`;
    })(),
    // 세트 상세 탭 — 두 번째 탭을 눌러 패널 전환과 숨겨져 있던 스와이퍼 폭을 본다
    tabs: (() => {
      const tabs = [...document.querySelectorAll('[data-pdc-set-tab]')];
      if (tabs.length < 2) return 'none';
      const state = () => [...document.querySelectorAll('[data-pdc-set-panel]')].map((p) => (p.hidden ? 'x' : 'o')).join('');
      const before = state();
      tabs[1].click();
      const slide = document.querySelector('[data-pdc-set-panel]:not([hidden]) .swiper-slide');
      const after = `${state()}/slide ${slide ? Math.round(slide.getBoundingClientRect().width) : '-'}`;
      tabs[0].click();
      return `${before}>${after}>${state()}`;
    })(),
    steps: document.querySelectorAll('[aria-current="step"]').length,
    videos: [...document.querySelectorAll('.product-story-content video')].filter((v) => v.muted && v.playsInline).length,
  }));
  console.log(w, JSON.stringify(kind));
  console.log(w, 'sections', meta.length, 'errors', meta.filter((m) => m.error).length, 'total h', meta.reduce((a, m) => a + m.h, 0));
  await page.close();
}
await browser.close();
