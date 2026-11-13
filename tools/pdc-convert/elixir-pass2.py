"""BIO Elixir pdc 2차: 공통 pdc.css와 겹치는 규칙 제거 · 값 대응 · 태블릿 경계(1024/1025 → 1023/1024).

<스킨>/css/module/product/pdc-elixir.css · js/module/product/pdc-elixir.js 를 제자리에서 고친다.
1차(elixir-pass1.py → sun-veil-pass2a.py elixir → dead-selectors.py elixir --apply) 다음에 한 번만 돌린다.

  1. 공통 pdc.css가 이미 정의하는 규칙 제거: 루트 · 섹션 틀 · 섹션 머리말 · eyebrow · 목록 · 스크롤 등장
     엘릭서만 다른 값은 .pdc--elixir 범위로 남긴다(세트 상세에서 다른 제품에 번지지 않게)
  2. 엘릭서 상세에 없는 구조의 규칙 제거: 스와이퍼 등장 · 좌우 등장 · 구 Sun Veil 섹션 짝 간격 · 비교 섹션 container
  3. 공통 변수 이름으로: --pdc-pad-y → --pdc-section-pad-y (값은 공통 루트가 정의)
  4. 값 대응: 220ms · 896px · rgba(0,119,191,…) · var(--pdc-accent, 대체값)
  5. 태블릿 경계: max-width 1024px → 1023px · min-width 1025px → 1024px (CSS · JS). 폭 1024px 화면만 달라진다

화면이 달라지는 것은 5번(폭 1024px)뿐이다.

Run:  python3 tools/pdc-convert/elixir-pass2.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent.parent.parent / "ayrow-cafe24-skin-2026"
CSS = SKIN / "css/module/product/pdc-elixir.css"
JS = SKIN / "js/module/product/pdc-elixir.js"

css = CSS.read_text(encoding="utf-8")
if "이 파일을 직접 고친다" in css[:2500]:
    print("이미 적용됨")
    sys.exit(0)

log = []


def remove_rule(selector, must_contain=None, count=1):
    """선택자가 정확히 일치하는 규칙 블록을 지운다(중괄호 한 단계). 들여쓰기까지 일치해야 한다."""
    global css
    pattern = re.compile(r"(?m)^" + re.escape(selector) + r" \{[^{}]*\}\n\n?")
    blocks = [m.group(0) for m in pattern.finditer(css)]
    assert len(blocks) == count, (selector, len(blocks))
    if must_contain:
        assert all(must_contain in b for b in blocks), (selector, must_contain)
    css = pattern.sub("", css)
    log.append(f"규칙 제거  {selector.splitlines()[0][:76]}")


def replace(old, new, count=None):
    global css
    n = css.count(old)
    assert n > 0 and (count is None or n == count), (old, n, count)
    css = css.replace(old, new)
    log.append(f"대응 {n:>3}곳  {old.strip().splitlines()[0][:44]} → {new.strip().splitlines()[0][:44] if new.strip() else '(삭제)'}")


# ---- 1. 공통과 겹치는 규칙 ----
remove_rule(".pdc", must_contain="--pdc-text: var(--pdc-accent)")
remove_rule(".pdc *,\n.pdc *::before,\n.pdc *::after", must_contain="box-sizing")   # 스킨 base.css가 전역으로 정의
# color 상속은 공통이 맡고, margin 초기화는 엘릭서만 쓴다
replace(
    ".pdc :where(h1, h2, h3, h4, h5, h6, p, span, strong, em, small, li, dt, dd) {\n  margin: 0;\n  color: inherit;\n}",
    ".pdc--elixir :where(h1, h2, h3, h4, h5, h6, p, span, strong, em, small, li, dt, dd) {\n  margin: 0;\n}", count=1)
replace("\n.pdc strong {", "\n.pdc--elixir strong {", count=1)
replace("\n.pdc :is(h1, h2) strong {", "\n.pdc--elixir :is(h1, h2) strong {", count=1)

remove_rule(".pdc__eyebrow", must_contain="font-weight: var(--font-weight-semibold) !important")
remove_rule(".pdc__eyebrow strong")
remove_rule(".pdc--elixir .pdc__eyebrow", must_contain="font-weight: var(--font-weight-bold) !important")   # 공통이 bold
remove_rule(".pdc-clinical--sv .pdc__eyebrow", must_contain="font-size: var(--font-size-heading-s) !important")

for sel in (".pdc :where(ul:not([class]), .pdc__list)", ".pdc :where(ul:not([class]), .pdc__list) > li",
            ".pdc :where(ul:not([class]), .pdc__list) > li::before"):
    remove_rule(sel)

remove_rule(".pdc__section", must_contain="scroll-margin-top: 96px")
remove_rule(".pdc__section--full")
remove_rule(".pdc__section--contained", must_contain="overflow-x: clip")
replace("@supports not (overflow: clip) {\n  .pdc__section--contained {\n    overflow-x: hidden;\n  }\n}\n\n", "", count=1)
remove_rule(".pdc__section + .pdc__section", must_contain="padding-top: 0")
remove_rule(".pdc__section:has(+ .pdc__section)")
# 띠 자체의 위아래 여백: 위는 아래 .pdc--elixir 규칙이, 아래는 .pdc--elixir .pdc-clinical 이 정한다
remove_rule(".pdc__section--band", must_contain="padding-bottom")
remove_rule(".pdc__section:has(+ .pdc__section--band)")
remove_rule(".pdc__section + .pdc__section--band")
# 구 Sun Veil 섹션 짝 — 엘릭서에서는 usage + faq만 해당하고, 그 값은 아래 .pdc--elixir 규칙과 같다
remove_rule('[data-pdc-section="intro"] + [data-pdc-section="hero"],\n[data-pdc-section="compare"] + [data-pdc-section="glance"],\n'
            '[data-pdc-section="highlight"] + [data-pdc-section="usage"],\n[data-pdc-section="usage"] + [data-pdc-section="faq"]')
remove_rule("  .pdc--elixir .pdc__section", must_contain="--pdc-pad-y: var(--spacing-16)")   # 767px 이하 — 공통 루트가 맡음

remove_rule(".pdc__head", must_contain="max-width: 680px")
remove_rule(".pdc-clinical--sv .pdc__head", must_contain="max-width: 680px")
remove_rule(".pdc__head-title,\n.pdc__head-lead", must_contain="text-wrap: pretty")
replace(".pdc--elixir .pdc__head-lead {\n  word-break: keep-all;\n}", ".pdc--elixir .pdc__head-lead {\n  text-wrap: pretty;\n  word-break: keep-all;\n}", count=1)
remove_rule(".pdc-clinical--sv .pdc__head-title", must_contain="text-wrap: pretty")   # .pdc--elixir .pdc__head-title 과 같은 값
remove_rule(".pdc-clinical--sv .pdc__head-lead", must_contain="font-weight: var(--font-weight-medium)")

remove_rule(".pdc [data-scroll-reveal]", must_contain="will-change: opacity, transform")
remove_rule('.pdc [data-scroll-direction="none"]')
remove_rule(".pdc [data-scroll-reveal].is-revealed")
replace("@media (prefers-reduced-motion: reduce) {\n  .pdc [data-scroll-reveal],\n  .pdc [data-scroll-reveal] .swiper-slide {\n"
        "    opacity: 1;\n    transform: none;\n    transition: none;\n  }\n}\n\n", "", count=1)

# ---- 2. 엘릭서 상세에 없는 구조 ----
remove_rule('.pdc [data-scroll-direction="left"]')
remove_rule('.pdc [data-scroll-direction="right"]')
remove_rule('.pdc .swiper[data-scroll-reveal]:not([data-scroll-reveal="stagger-slides"])')
remove_rule('.pdc .swiper[data-scroll-reveal]:not([data-scroll-reveal="stagger-slides"]).is-revealed')
remove_rule('.pdc [data-scroll-reveal="stagger-slides"]')
remove_rule('.pdc [data-scroll-reveal="stagger-slides"] .swiper-slide')
remove_rule('.pdc [data-scroll-reveal="stagger-slides"].is-revealed .swiper-slide')
css, n = re.subn(r'(?m)^\.pdc \[data-scroll-reveal="stagger-slides"\]\.is-revealed \.swiper-slide:nth-child\([^)]*\) \{[^{}]*\}\n\n?', "", css)
assert n == 4, n
remove_rule(".pdc-elixir-compare > .container", must_contain="896px")   # 구 Sun Veil 비교 섹션의 것. 엘릭서의 비교 슬라이더에는 container가 없다
replace("@media (max-width: 767px) {\n  .pdc-elixir-compare > .container {\n    gap: var(--spacing-10);\n  }\n}\n\n", "", count=1)
css, n = re.subn(r"@keyframes pdcGlanceTrace \{.*?\n\}\n\n", "", css, flags=re.S)
assert n == 1

# 빈 구획 주석(구 공통 파일의 Sun Veil 섹션 제목)
css, n = re.subn(r"(?m)^/\* (?:===== \d+\. (?:Intro|Hero|Problem|Choice|At a glance|Why \(use cases\)|Standard|How it works|Bonding|Formula|Proof / data|Why highlight) =====|"
                 r"---- (?:Theme: product palette → framework tokens|Swiper pagination|Scroll reveal|Section header|Section system|Reduced motion) ----|"
                 r"word-by-word highlight[^\n]*|JS measures intrinsic copy height[^\n]*|Accordion \(shared accordion-ui[^\n]*|Flow list|Friendly-explanation disclosure|"
                 r"Metrics row|Shared two-column divider[^\n]*|Quick FAQ carousel|Swiper variant[^\n]*|Bulleted lists[^\n]*) \*/\n\n?", "", css)
log.append(f"빈 구획 주석 제거 {n}개")
css, n = re.subn(r"/\* Vertical rhythm — collapse.*?chains\. \*/\n", "", css, flags=re.S)
assert n == 1
css, n = re.subn(r"/\* Pairs that re-open a top gap \*/\n", "", css)
assert n == 1
css, n = re.subn(r"/\* ={60}\n   PDP — Sequence product detail.*?={60} \*/\n\n", "", css, flags=re.S)
assert n == 1
css, n = re.subn(r"/\* ={60}\n   SECTIONS\n.*?={60} \*/\n\n", "", css, flags=re.S)
assert n == 1

# ---- 3. 공통 변수 이름 ----
replace("  --pdc-pad-y: clamp(72px, 9vw, 120px);\n\n  padding-block: var(--pdc-pad-y);", "  padding-block: var(--pdc-pad-y);", count=1)
remove_rule("  .pdc--elixir .pdc-clinical--sv", must_contain="--pdc-pad-y: var(--spacing-16)")
replace("var(--pdc-pad-y)", "var(--pdc-section-pad-y)")
assert "--pdc-pad-y" not in css

# 공통 루트와 같은 값은 제품 루트에서 뺀다
for line in ("  --pdc-accent: var(--semantic-brand);\n", "  --pdc-accent-deep: #0082c8;\n", "  --pdc-on-accent: var(--semantic-on-surface-inverse);\n",
             "  --pdc-surface: var(--semantic-bg-default);\n", "  --pdc-rule: rgba(0, 119, 191, 0.18);\n"):
    replace(line, "", count=1)

# ---- 4. 값 대응 ----
replace("transform 220ms ease, opacity 220ms ease", "transform var(--pdc-dur-fast) ease, opacity var(--pdc-dur-fast) ease", count=2)
replace("var(--pdc-accent, #0077bf)", "var(--pdc-accent)", count=2)
for alpha, pct in (("0.15", "15"), ("0.6", "60"), ("0.85", "85")):
    replace(f"rgba(0, 119, 191, {alpha})", f"color-mix(in srgb, var(--pdc-accent) {pct}%, transparent)", count=1)
assert "rgba(0, 119, 191" not in css

# ---- 5. 태블릿 경계 ----
replace("@media (max-width: 1024px)", "@media (max-width: 1023px)", count=6)
replace("@media (min-width: 1025px)", "@media (min-width: 1024px)", count=4)

# ---- 머리말 ----
head_old = css[:css.index("*/") + 2]
head_new = """/* ============================================================
   PDC — BIO Elixir 제품 전용
   ------------------------------------------------------------
   공통(pdc.css)에 없는 엘릭서 블록만 담는다. 규칙 문서: docs/pdc-convention.md
   동작: pdc-elixir.js

   이력: pdp.css + pdp-elixir.css를 이어 붙여 이름 변환(1차) → 스킨 token 대체값 제거 → 일치할 수 없는 선택자 제거
         → 2차(공통과 겹치는 규칙 제거 · 값 대응 · 태블릿 경계 1023/1024)
   기획 레포 tools/pdc-convert/ 의 스크립트로 만들었다. 2차부터는 이 파일을 직접 고친다.

   구획: "구 공통 파일에서"는 구 pdp.css에서 엘릭서가 쓰던 블록(전후 비교 · 사용법 · FAQ),
         "구 엘릭서 파일에서"는 구 pdp-elixir.css. 뒤쪽 규칙이 앞쪽 규칙을 다시 덮는 곳이 있다(순서를 바꾸지 말 것).
   ============================================================ */"""
css = css.replace(head_old, head_new, 1)
css = re.sub(r"\n{3,}", "\n\n", css)
CSS.write_text(css, encoding="utf-8")

# ---- JS: 같은 경계 ----
js = JS.read_text(encoding="utf-8")
assert js.count("(max-width: 1024px)") == 1 and js.count("≤1024px") == 1
js = js.replace("(max-width: 1024px)", "(max-width: 1023px)").replace("≤1024px", "≤1023px")
js = js.replace(" (1차: 이름만 변환)", "", 1)
JS.write_text(js, encoding="utf-8")

print("\n".join(log))
print(f"\ncss {len(css.splitlines())}줄 · js 경계 1곳")
