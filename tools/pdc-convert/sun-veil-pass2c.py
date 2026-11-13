"""Sun Veil pdc 2차-c: 동작을 product-story.js에서 pdc-sun-veil.js로 옮긴다.

product-story.js(페이지 엔진)에서 Sun Veil 상세가 실제로 쓰는 동작과 그것이 부르는 함수만 골라,
접두어를 pdc로 고정해 <스킨>/js/module/product/pdc-sun-veil.js 를 만든다. 함수 본문은 옮기기만 하고 고치지 않는다.

옮기는 동작(ROOTS)은 sun-veil-pdc.html에 대상 요소가 있는 것만.
페이지 엔진에 남기는 것: 목차 · 다국어 글꼴 처리 · 전체 화면 버튼 · 이미지 로드 표시(접두어 없이 모든 상세에 동작).

Run:  python3 tools/pdc-convert/sun-veil-pass2c.py     → 만든 뒤 사람이 다듬는다(머리말의 "이력" 참고)
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent.parent.parent / "ayrow-cafe24-skin-2026"
SRC = SKIN / "js/module/product/product-story.js"
OUT = SKIN / "js/module/product/pdc-sun-veil.js"

ROOTS = [
    "initProofDataSwipers",
    "initQuickFaqSwipers",
    "initAtGlanceSwipers",
    "initCountUps",
    "initScrollHighlights",
    "initScrollPans",
    "initStandardCardHeights",
    "initFullFaqAccordions",
    "initHowWorksScroll",
    "initViewportVideos",
    "initUsageVideoSteps",
]
# 접두어 처리용 — 새 파일에서는 상수로 바뀌므로 옮기지 않는다
HELPERS = {
    "STORY_DATA_PREFIXES", "STORY_CLASS_PREFIXES", "getStoryDataAttrNames", "storyDataSelector", "storyClassSelector",
    "getStoryPrefixFromElement", "getStoryDataValue", "setStoryDataValue", "getStoryClassName", "getStoryCssVarName",
    "isV2Scope", "SELECTORS",
}
# 페이지 엔진의 시작 함수 — Swiper 옵션의 `init` 같은 낱말과 이름이 같아 딸려 오지 않게 뺀다
ENGINE = {"init", "initLayout", "observeLayout", "getTopLevelLayouts", "initDynamicContent"}

if OUT.exists() and len(OUT.read_text(encoding="utf-8").splitlines()) > 100:
    raise SystemExit("pdc-sun-veil.js: 이미 만들어 직접 고치는 파일입니다. 이 스크립트는 이력으로만 둡니다.")

lines = SRC.read_text(encoding="utf-8").splitlines()

# ---- 최상위 선언 단위로 나누기(들여쓰기 2칸) ----
START = re.compile(r"^  (?:function |const |let )([A-Za-z_$][\w$]*)")
starts = [(i, START.match(l).group(1)) for i, l in enumerate(lines) if START.match(l)]
end_of_body = max(i for i, l in enumerate(lines) if l.startswith("  CAFE24.module.ProductStory"))
chunks = {}
order = []
for n, (i, name) in enumerate(starts):
    j = starts[n + 1][0] if n + 1 < len(starts) else end_of_body
    # 다음 선언 바로 앞의 주석은 다음 선언에 붙인다
    while j > i and re.match(r"^  (//|/\*)", lines[j - 1]):
        j -= 1
    k = i
    while k > 0 and re.match(r"^  (//|/\*)", lines[k - 1]):
        k -= 1
    chunks[name] = "\n".join(lines[k:j]).rstrip()
    order.append(name)

# ---- ROOTS가 부르는 선언 모으기 ----
need = []
todo = list(ROOTS)
while todo:
    name = todo.pop()
    if name in need or name in HELPERS or name in ENGINE:
        continue
    need.append(name)
    body = chunks[name]
    for other in order:
        if other != name and other not in need and re.search(r"(?<![\w$.])" + re.escape(other) + r"(?![\w$])", body):
            todo.append(other)
need = [n for n in order if n in need]

# ---- SELECTORS → 쓰는 키만, pdc 이름의 문자열로 ----
sel_src = chunks["SELECTORS"]
used_keys = sorted(set(re.findall(r"SELECTORS\.(\w+)", "\n".join(chunks[n] for n in need))))
sel_lines = []
for key in used_keys:
    m = re.search(r"^\s*" + key + r":\s*(.+?),?\s*$", sel_src, flags=re.M)
    assert m, key
    val = m.group(1).rstrip(",")
    val = re.sub(r"storyDataSelector\('([^']+)'\)", r"'[data-pdc-\1]'", val)
    val = re.sub(r"storyClassSelector\('([^']+)'\)", r"'.pdc-\1'", val)
    assert "story" not in val.lower(), (key, val)
    sel_lines.append(f"    {key}: {val},")


def convert(text):
    text = re.sub(r"\$\{storyDataSelector\('([^']+)'\)\}", r"[data-pdc-\1]", text)
    text = re.sub(r"\$\{storyClassSelector\('([^']+)'\)\}", r".pdc-\1", text)
    text = re.sub(r"storyDataSelector\('([^']+)'\)", r"'[data-pdc-\1]'", text)
    text = re.sub(r"storyClassSelector\('([^']+)'\)", r"'.pdc-\1'", text)
    text = re.sub(r"getStoryClassName\(\s*[\w.]+\s*,\s*'([^']+)'\s*\)", r"'pdc-\1'", text)
    text = re.sub(r"getStoryCssVarName\(\s*[\w.]+\s*,\s*'([^']+)'\s*\)", r"'--pdc-\1'", text)
    text = text.replace("getStoryDataValue(", "attr(").replace("setStoryDataValue(", "setAttr(")
    text = re.sub(r"isV2Scope\(\s*[\w.]+\s*\)", "true", text)
    text = text.replace("__productStory", "__pdc")
    return text


body = "\n\n".join(convert(chunks[n]) for n in need)
left = sorted(set(re.findall(r"\b\w*[sS]tory\w*\b|sv-(?:sequence-)?pdp[\w-]*", body)))

head = """/**
 * PDC — Sun Veil 제품 전용 동작
 * pdc.js가 data-pdc-product="sun-veil"을 읽어 불러온다. 규칙 문서: docs/pdc-convention.md
 *
 * 하는 일: 검증 데이터 · Quick FAQ · At a Glance 스와이퍼 · 카운트업 · 문장 스크롤 강조 ·
 *          이미지 가로 흐름(모바일) · 기준 카드 높이 · FAQ · How It Protects 스크롤 · 화면 안 영상 재생 · 사용법 단계
 * 페이지 엔진(product-story.js)에 남긴 것: 목차 · 다국어 글꼴 처리 · 전체 화면 버튼 · 이미지 로드 표시
 * 스크롤 등장(is-revealed)은 스킨 js/components/scroll-reveal.js
 *
 * 이력: product-story.js에서 Sun Veil이 쓰는 함수만 옮기고 접두어를 pdc로 고정
 *       (기획 레포 tools/pdc-convert/sun-veil-pass2c.py). 이후 이 파일을 직접 고친다.
 */
(function (window, document) {
  'use strict';

  if (!window.PDC) return;

  const SELECTORS = {
""" + "\n".join(sel_lines) + """
  };

  function attr(element, name) {
    if (!element || typeof element.getAttribute !== 'function') return '';
    const value = element.getAttribute(name ? `data-pdc-${name}` : 'data-pdc');
    return value === null ? '' : value;
  }

  function setAttr(element, name, value = '') {
    if (!element || typeof element.setAttribute !== 'function') return;
    element.setAttribute(name ? `data-pdc-${name}` : 'data-pdc', value);
  }

"""

tail = """

  function initAll(root) {
""" + "\n".join(f"    {name}(root);" for name in ROOTS) + """

    // Swiper가 아직 실리지 않았으면 잠시 뒤 다시
    if (typeof window.Swiper === 'undefined' && !root.__pdcSwiperRetry) {
      root.__pdcSwiperRetry = window.setTimeout(() => {
        root.__pdcSwiperRetry = null;
        initAll(root);
      }, 160);
    }
  }

  window.PDC.register('sun-veil', (root) => {
    initAll(root);

    // 상세 안에 요소가 나중에 들어오면 다시 초기화(각 동작은 이미 처리한 요소를 건너뛴다)
    if ('MutationObserver' in window) {
      new MutationObserver(() => initAll(root)).observe(root, { childList: true, subtree: true });
    }
  });
})(window, document);
"""

OUT.write_text(head + body + tail, encoding="utf-8")
print("옮긴 선언", len(need), "개 ·", len((head + body + tail).splitlines()), "줄")
print("SELECTORS 키", len(used_keys))
print("남은 구 이름:", left or "없음")
