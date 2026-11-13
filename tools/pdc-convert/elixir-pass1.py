"""BIO Elixir 상세 → pdc 체계, 1차(이름만 변환).

구 파일은 읽기만 하고 새 파일을 만든다. 값 · 구조 · 순서는 바꾸지 않는다.

  읽기  bio-elixir/cafe24-admin/bio-elixir-pdp.html
        <스킨>/css/module/product/pdp.css + pdp-elixir.css
        <스킨>/js/module/product/pdp-elixir.js + pdp.js(FAQ만)
  쓰기  bio-elixir/cafe24-admin/bio-elixir-pdc.html
        <스킨>/css/module/product/pdc-elixir.css      (pdp.css 뒤에 pdp-elixir.css를 이어 붙인 것 — 불러오던 순서 그대로)
        <스킨>/js/module/product/pdc-elixir.js

Run:  python3 tools/pdc-convert/elixir-pass1.py [버전]      버전 기본값 20261112000001

이름 대응 (규칙: 스킨 docs/pdc-convention.md)
  .pdp · .pdp--elixir          → .pdc · .pdc--elixir
  pdp__<요소> · pdp-<block>    → pdc__<요소> · pdc-<block>
  data-pdp-* · --pdp-*         → data-pdc-* · --pdc-*
  pdp-compare                  → pdc-elixir-compare   Sun Veil의 pdc-compare(비교표)와 다른 블록(전후 비교 슬라이더)
  pdp-usage · pdp-elixir-usage → pdc-elixir-usage     Sun Veil의 pdc-usage와 이름이 겹침. 두 클래스의 요소 이름은 서로 겹치지 않아 하나로 합침

1차에서 일부러 남긴 것(2차에서 정리): 공통 pdc.css와 겹치는 규칙 · pdp.css에서 온 Sun Veil용 규칙(죽은 선택자) ·
var(--token, 대체값) · 1024/1025 분기점 · pdc-tm(공통 pdc__tm과 통합)
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parent.parent
SKIN = PLANNING.parent / "ayrow-cafe24-skin-2026"
VER = sys.argv[1] if len(sys.argv) > 1 else "20261112000001"

SRC_HTML = PLANNING / "bio-elixir/cafe24-admin/bio-elixir-pdp.html"
OUT_HTML = PLANNING / "bio-elixir/cafe24-admin/bio-elixir-pdc.html"
OUT_CSS = SKIN / "css/module/product/pdc-elixir.css"
OUT_JS = SKIN / "js/module/product/pdc-elixir.js"

for done in (OUT_HTML, OUT_CSS, OUT_JS):
    if done.exists() and "이 파일을 직접 고친다" in done.read_text(encoding="utf-8")[:2500]:
        sys.exit(f"{done.name}: 이미 직접 고치는 단계입니다. 이 스크립트는 이력으로만 둡니다.")

# 클래스 이름만(앞이 data- · -- 가 아닌 것). 순서 중요
RENAMES = [
    # 블록 자체 · 요소(__) · 수식어(--)까지. pdp-compare-xxx 같은 다른 이름과 data-pdp-compare · --pdp-compare는 제외
    (re.compile(r"(?<![\w-])pdp-compare(?![a-zA-Z0-9]|-[a-zA-Z0-9])"), "pdc-elixir-compare"),
    (re.compile(r"(?<![\w-])pdp-usage(?![a-zA-Z0-9]|-[a-zA-Z0-9])"), "pdc-elixir-usage"),
    (re.compile(r"pdp"), "pdc"),
]


def rename(text):
    for pattern, new in RENAMES:
        text = pattern.sub(new, text)
    return text


# ---- CSS ----
css_head = """/* ============================================================
   PDC — BIO Elixir 제품 전용 (1차: 이름만 변환)
   ------------------------------------------------------------
   pdp.css + pdp-elixir.css를 불러오던 순서대로 이어 붙이고 pdc 이름으로 바꾼 것.
   tools/pdc-convert/elixir-pass1.py(기획 레포)가 만든다 — 1차 동안은 직접 고치지 않는다.
   공통: pdc.css · 동작: pdc-elixir.js · 규칙 문서: docs/pdc-convention.md
   ============================================================ */

"""
parts = []
for name in ("pdp.css", "pdp-elixir.css"):
    label = "구 공통 파일" if name == "pdp.css" else "구 엘릭서 파일"
    parts.append(f"/* ======== {label}에서 ======== */\n" + rename((SKIN / "css/module/product" / name).read_text(encoding="utf-8").rstrip()) + "\n")
css = "\n".join(parts)
OUT_CSS.write_text(css_head + css, encoding="utf-8")

# ---- JS ----
js = (SKIN / "js/module/product/pdp-elixir.js").read_text(encoding="utf-8")
base = (SKIN / "js/module/product/pdp.js").read_text(encoding="utf-8")
faq = base[base.index("  /* ---- FAQ accordion ---- */"):base.index("  /* ---- At-a-glance overlay height")]

boot_at = js.index("  /* ---- Boot ---- */")
boot = js[boot_at:]
assert "function boot()" in boot and "initCremaMove(root);" in boot
init_fn = boot[boot.index("  function init(root) {"):boot.index("  function boot()")].rstrip()
init_fn = init_fn.replace("    if (!root) return;\n", "    if (!root) return;\n    initFaq(root);\n", 1)
tail = """

  window.PDC.register('elixir', function (root) {
    init(root);
    // 이미지 · 글꼴이 다 실린 뒤 한 번 더(각 동작은 이미 처리한 요소를 건너뛰거나 다시 잰다)
    window.addEventListener('load', function () { init(root); });
  });
})(window, document);
"""
js = js[:boot_at] + faq + "  /* ---- 시작 ---- */\n" + init_fn + tail

# 머리말 · 루트 선택
head_end = js.index("(function (window, document) {")
js_head = """/**
 * PDC — BIO Elixir 제품 전용 동작 (1차: 이름만 변환)
 * pdc.js가 data-pdc-product="elixir"를 읽어 불러온다. 규칙 문서: docs/pdc-convention.md
 * pdp-elixir.js + pdp.js의 FAQ를 pdc 이름으로 바꾼 것. tools/pdc-convert/elixir-pass1.py(기획 레포)가 만든다.
 *
"""
old_head = js[:head_end]
body_doc = old_head[old_head.index(" *   .pdp-elixir-hero"):]  # 동작 목록 주석은 그대로 가져온다
js = js_head + body_doc + js[head_end:]
js = js.replace("  'use strict';\n", "  'use strict';\n\n  if (!window.PDC) return;\n", 1)
js = rename(js)
OUT_JS.write_text(js, encoding="utf-8")

# ---- HTML ----
html = SRC_HTML.read_text(encoding="utf-8")
links = re.findall(r'<link rel="stylesheet" href="/css/module/product/pdp(?:-elixir)?\.css\?ver=\d+">\n', html)
assert len(links) == 2, links
root_old = '<div class="pdp pdp--elixir" data-pdp itemscope itemtype="https://schema.org/Product">'
assert html.count(root_old) == 1
start = html.index(links[0])
body = html[start:]
for link in links:
    body = body.replace(link, "")
body = body.replace(root_old, f'<div class="pdp pdp--elixir" data-pdp data-pdp-product="elixir" data-pdp-ver="{VER}" itemscope itemtype="https://schema.org/Product">')
body = rename(body)


def dedupe(match):
    seen = []
    for name in match.group(1).split():
        if name not in seen:
            seen.append(name)
    return 'class="' + " ".join(seen) + '"'


body = re.sub(r'class="([^"]*)"', dedupe, body)
html_head = f"""<!-- BIO Elixir 상세 — pdc 체계(1차: 이름만 변환) · 상품 관리 > 상세 설명(HTML)에 이 파일 내용 전체를 붙여 넣는다 -->
<!-- 공통: /css/module/product/pdc.css · pdc.js(스킨 product/detail.html이 불러옴) · 제품: pdc-elixir.css(아래 link) · pdc-elixir.js(pdc.js가 불러옴) · CSS · JS 수정 후 ?ver= 와 data-pdc-ver 를 함께 올린다 -->
<!-- 이미지: 관리자 /web/src/bio-elixir/ 업로드 · HTML에는 CDN 절대경로 · CSS mask는 CDN이 CORS를 막아 data URI -->
<!-- 원본: bio-elixir-pdp.html → tools/pdc-convert/elixir-pass1.py 가 만든다 -->
<link rel="stylesheet" href="/css/module/product/pdc-elixir.css?ver={VER}">
"""
OUT_HTML.write_text(html_head + body, encoding="utf-8")

for label, path in (("css ", OUT_CSS), ("js  ", OUT_JS), ("html", OUT_HTML)):
    text = path.read_text(encoding="utf-8")
    print(label, path.name, len(text.splitlines()), "줄 · 남은 pdp:", len(re.findall(r"pdp", text)))
