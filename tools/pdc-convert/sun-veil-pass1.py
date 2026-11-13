"""Sun Veil 상세 → pdc 체계, 1차(이름만 변환).

구 파일은 읽기만 하고 새 파일을 만든다. 값 · 구조 · 순서는 바꾸지 않는다.

  읽기  sun-veil/cafe24-admin/sun-veil-pdp-figma-sequence-ver-3.production.html
        <스킨>/css/module/product/sun-veil-pdp-figma-sequence-v3.css
  쓰기  sun-veil/cafe24-admin/sun-veil-pdc.html
        <스킨>/css/module/product/pdc-sun-veil.css

Run:  python3 tools/pdc-convert/sun-veil-pass1.py [버전]      버전 기본값 20261111000001

이름 대응 (규칙: 스킨 docs/pdc-convention.md)
  .sv-sequence-pdp                      → .pdc
  sv-sequence-pdp-section               → pdc__section        (--color-block → --band)
  sv-sequence-pdp-section__header …     → pdc__head · pdc__head-title · pdc__head-lead · pdc__head-eyebrow
  sv-sequence-pdp-eyebrow               → pdc__eyebrow
  sv-sequence-pdp-<block>               → pdc-<block>
  data-sv-sequence-pdp-*                → data-pdc-*
  --sv-sequence-pdp-*                   → --pdc-*
  id="sv-sequence-pdp-*"                → id="pdc-*"

1차에서 일부러 남긴 것(2차에서 정리): data-pdc-layout · nav-title="none" · style="font-weight" ·
공통 pdc.css와 겹치는 규칙 · var(--token, 대체값) · @media screen and
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parent.parent
SKIN = PLANNING.parent / "ayrow-cafe24-skin-2026"
VER = sys.argv[1] if len(sys.argv) > 1 else "20261111000001"

SRC_HTML = PLANNING / "sun-veil/cafe24-admin/sun-veil-pdp-figma-sequence-ver-3.production.html"
SRC_CSS = SKIN / "css/module/product/sun-veil-pdp-figma-sequence-v3.css"
OUT_HTML = PLANNING / "sun-veil/cafe24-admin/sun-veil-pdc.html"
OUT_CSS = SKIN / "css/module/product/pdc-sun-veil.css"

OLD = "sv-sequence-pdp"

# 2차-b · 2차-c 이후 결과 파일은 직접 고치는 파일이다 — 덮어쓰지 않는다
for done in (OUT_HTML, OUT_CSS):
    if done.exists() and ("이 파일을 직접 고친다" in done.read_text(encoding="utf-8")[:2000] or "2차-b 적용" in done.read_text(encoding="utf-8")[:2000]):
        sys.exit(f"{done.name}: 이미 직접 고치는 단계입니다. 이 스크립트는 이력으로만 둡니다.")

# 순서가 중요하다 — 긴 이름부터
RENAMES = [
    (re.compile(r"--sv-sequence-pdp-"), "--pdc-"),                                   # CSS 변수
    (re.compile(r"data-sv-sequence-pdp(?![\w])(?!-)"), "data-pdc"),                  # 루트 속성
    (re.compile(r"data-sv-sequence-pdp-"), "data-pdc-"),                             # data 속성
    (re.compile(r"sv-sequence-pdp-section__header"), "pdc__head"),
    (re.compile(r"sv-sequence-pdp-section__title"), "pdc__head-title"),
    (re.compile(r"sv-sequence-pdp-section__lead"), "pdc__head-lead"),
    (re.compile(r"sv-sequence-pdp-section__eyebrow"), "pdc__head-eyebrow"),
    (re.compile(r"sv-sequence-pdp-section--color-block"), "pdc__section--band"),
    (re.compile(r"sv-sequence-pdp-section--"), "pdc__section--"),
    (re.compile(r"sv-sequence-pdp-section(?![\w-])"), "pdc__section"),
    (re.compile(r"sv-sequence-pdp-eyebrow(?![\w-])"), "pdc__eyebrow"),
    (re.compile(r"sv-sequence-pdp-"), "pdc-"),                                       # 블록 · id
    (re.compile(r"sv-sequence-pdp(?![\w-])"), "pdc"),                                # 루트 클래스
]


def rename(text):
    for pattern, new in RENAMES:
        text = pattern.sub(new, text)
    assert OLD not in text, "남은 구 이름: " + text[text.index(OLD) - 40:text.index(OLD) + 60]
    return text


# ---- CSS ----
css = SRC_CSS.read_text(encoding="utf-8")
css_head = """/* ============================================================
   PDC — Sun Veil 제품 전용 (1차: 이름만 변환)
   ------------------------------------------------------------
   sun-veil-pdp-figma-sequence-v3.css를 pdc 이름으로 바꾼 것.
   tools/pdc-convert/sun-veil-pass1.py(기획 레포)가 만든다 — 1차 동안은 직접 고치지 않는다.
   공통: pdc.css · 동작: product-story.js(1차 동안) → pdc-sun-veil.js(2차)
   규칙 문서: docs/pdc-convention.md
   ============================================================ */

"""
OUT_CSS.write_text(css_head + rename(css), encoding="utf-8")

# ---- HTML ----
html = SRC_HTML.read_text(encoding="utf-8")

link = re.compile(r'<link rel="stylesheet" href="/css/module/product/sun-veil-pdp-figma-sequence-v3\.css\?ver=\d+">\n')
assert len(link.findall(html)) == 1
html = link.sub("", html)

# 인라인 스크립트 제거 — 관리자에 저장되지 않아 실제 상세에도 없다(ld+json은 남긴다)
scripts = re.findall(r"[ \t]*<script>.*?</script>\n", html, flags=re.S)
assert len(scripts) == 2, len(scripts)
for block in scripts:
    html = html.replace(block, "")

root_old = '<div class="sv-sequence-pdp" data-sv-sequence-pdp data-product-story itemscope itemtype="https://schema.org/Product">'
root_new = f'<div class="pdc" data-pdc data-pdc-product="sun-veil" data-pdc-ver="{VER}" data-product-story itemscope itemtype="https://schema.org/Product">'
assert html.count(root_old) == 1
html = html.replace(root_old, root_new)

html_head = f"""<!-- Sun Veil 상세 — pdc 체계(1차: 이름만 변환) · 상품 관리 > 상세 설명(HTML)에 이 파일 내용 전체를 붙여 넣는다 -->
<!-- 공통: /css/module/product/pdc.css · pdc.js(스킨 product/detail.html이 불러옴) · 제품: pdc-sun-veil.css(아래 link) · pdc-sun-veil.js(pdc.js가 불러옴) · CSS · JS 수정 후 ?ver= 와 data-pdc-ver 를 함께 올린다 -->
<!-- 원본: sun-veil-pdp-figma-sequence-ver-3.production.html → tools/pdc-convert/sun-veil-pass1.py 가 만든다 -->
<link rel="stylesheet" href="/css/module/product/pdc-sun-veil.css?ver={VER}">
"""
OUT_HTML.write_text(html_head + rename(html), encoding="utf-8")

print("css ", OUT_CSS.relative_to(SKIN), len(css.splitlines()), "줄")
print("html", OUT_HTML.relative_to(PLANNING), len(html.splitlines()), "줄")
