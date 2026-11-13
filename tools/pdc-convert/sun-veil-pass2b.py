"""Sun Veil pdc 2차-b: 공통 pdc.css와 겹치는 규칙 제거 · 값의 token 대응(화면 변화 없음).

<스킨>/css/module/product/pdc-sun-veil.css 를 제자리에서 고친다. 2차-a 다음에 한 번만 돌린다
(이미 돌린 파일에 다시 돌리면 "이미 적용됨"으로 끝난다).

  1. 공통 pdc.css가 이미 정의하는 규칙 제거: 루트 · color 상속 · eyebrow · 섹션 틀 · 섹션 머리말 · 스크롤 등장 기본
  2. 공통 변수 이름으로: --pdc-card-padding → --pdc-card-pad · --pdc-section-padding-y → --pdc-section-pad-y
  3. 목록 규칙은 공통이 맡는 ul:not([class])를 빼고 Sun Veil 전용 선택자만 남김
  4. 스킨 token · 상세 공통 변수와 같은 값 대응: 이징 · 220ms · 900ms · 반경 999px · 색 · 간격

Run:  python3 tools/pdc-convert/sun-veil-pass2b.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent.parent.parent / "ayrow-cafe24-skin-2026"
CSS = SKIN / "css/module/product/pdc-sun-veil.css"

css = CSS.read_text(encoding="utf-8")
if "2차-b 적용" in css:
    print("이미 적용됨")
    sys.exit(0)

log = []


def remove_rule(selector, must_contain=None, count=1):
    """선택자가 정확히 일치하는 규칙 블록을 지운다(중괄호 한 단계)."""
    global css
    # 들여쓰기까지 일치해야 한다 — @media 안의 같은 선택자와 구분
    pattern = re.compile(r"(?m)^" + re.escape(selector) + r" \{[^{}]*\}\n\n?")
    blocks = [m.group(0) for m in pattern.finditer(css)]
    assert len(blocks) == count, (selector, len(blocks))
    if must_contain:
        assert all(must_contain in b for b in blocks), (selector, must_contain)
    css = pattern.sub("", css)
    log.append(f"규칙 제거  {selector.splitlines()[0][:70]}")


def replace(old, new, count=None):
    global css
    n = css.count(old)
    assert n > 0 and (count is None or n == count), (old, n, count)
    css = css.replace(old, new)
    log.append(f"대응 {n:>3}곳  {old[:44]} → {new[:44]}")


# ---- 1. 공통과 겹치는 규칙 ----
remove_rule(".pdc", must_contain="--pdc-eyebrow-font-size")
remove_rule(".pdc *", must_contain="box-sizing")            # 스킨 base.css가 전역으로 정의
remove_rule(".pdc :where(h1, h2, h3, h4, h5, h6, p, span, strong, em, small, li, dt, dd)")
remove_rule(".pdc .pdc__eyebrow", must_contain="!important")
remove_rule(".pdc .pdc__eyebrow strong")

remove_rule(".pdc__section", must_contain="scroll-margin-top")
remove_rule(".pdc__section + .pdc__section")
remove_rule(".pdc__section:has(+ .pdc__section)")
remove_rule(".pdc__section + .pdc__section--band")
remove_rule(".pdc__section:has(+ .pdc__section--band)")
remove_rule(".pdc__section--band", must_contain="padding-bottom")   # 뒤에 섹션이 없을 때만 쓰이고, 그때는 기본 여백과 같은 값
remove_rule(".pdc__section--full,\n.pdc__section[data-pdc-layout=\"full\"]")
remove_rule(".pdc__section--contained,\n.pdc__section[data-pdc-layout=\"container\"]", must_contain="overflow-x: clip")
remove_rule(".pdc__section--contained > .container,\n.pdc__section[data-pdc-layout=\"container\"] > .container")
remove_rule("  .pdc__section", must_contain="--pdc-section-padding-y: var(--spacing-16)")  # 767px 이하 — 공통 루트가 맡음

remove_rule(".pdc__head", must_contain="max-width: 680px")
remove_rule(".pdc__head-eyebrow")
remove_rule(".pdc__head-title")
remove_rule(".pdc__head-lead")

remove_rule(".pdc [data-scroll-reveal]", must_contain="will-change: opacity, transform")
remove_rule(".pdc [data-scroll-direction=\"left\"]")
remove_rule(".pdc [data-scroll-direction=\"right\"]")
remove_rule(".pdc .swiper[data-scroll-reveal]:not([data-scroll-reveal=\"stagger-slides\"])", must_contain="opacity: 0")

# ---- 2. 공통 변수 이름 ----
replace("--pdc-card-padding", "--pdc-card-pad")
replace("--pdc-section-padding-y", "--pdc-section-pad-y")

# ---- 3. 목록 — Sun Veil 전용 선택자만 ----
replace(".pdc :where(\n  ul:not([class]),\n  .pdc-list,", ".pdc :where(\n  .pdc-list,", count=3)
replace("  --pdc-list-bullet-size: 0.35em;\n  --pdc-list-bullet-gap: 0.6em;\n", "  --pdc-list-bullet: 0.35em;\n", count=1)
replace("calc(var(--pdc-list-bullet-size) + var(--pdc-list-bullet-gap))", "calc(var(--pdc-list-bullet) + 0.6em)", count=1)
replace("var(--pdc-list-bullet-size)", "var(--pdc-list-bullet)", count=2)

# ---- 4. 값 대응 ----
replace("cubic-bezier(0.22, 1, 0.36, 1)", "var(--pdc-ease)")
replace("transform 220ms ease, opacity 220ms ease", "transform var(--pdc-dur-fast) ease, opacity var(--pdc-dur-fast) ease", count=2)
replace("opacity 900ms var(--pdc-ease)", "opacity var(--pdc-dur-reveal) var(--pdc-ease)", count=2)  # 세 번째는 위에서 지운 스와이퍼 규칙에 있었다
replace("border-radius: 999px;", "border-radius: var(--radius-full);", count=1)
replace("--pdc-at-glance-overlay-tint: #bbd5fd;", "--pdc-at-glance-overlay-tint: var(--primitive-ciel);", count=1)
replace("--pdc-at-glance-overlay-tint: #f7f1a0;", "--pdc-at-glance-overlay-tint: var(--primitive-creme);", count=1)
replace("rgba(0, 119, 191, 0.22)", "color-mix(in srgb, var(--pdc-accent) 22%, transparent)", count=1)

# 간격 — 여백 · 간격으로 쓰인 값만. 위치를 맞추는 값(calc의 ± px, 툴팁 top · bottom 등)은 숫자 그대로 둔다
replace("  padding-left: 24px;", "  padding-left: var(--spacing-6);", count=1)
replace("--pdc-proof-data-swiper-spacing: 20px;", "--pdc-proof-data-swiper-spacing: var(--spacing-5);", count=1)
replace("--pdc-proof-data-swiper-spacing: 8px;", "--pdc-proof-data-swiper-spacing: var(--spacing-2);", count=1)
replace("  padding-bottom: 60px;", "  padding-bottom: var(--spacing-15);", count=1)
replace("  padding-top: 60px;", "  padding-top: var(--spacing-15);", count=1)
replace("    padding-top: 20px;\n    padding-bottom: 20px;", "    padding-top: var(--spacing-5);\n    padding-bottom: var(--spacing-5);", count=2)
replace("clamp(36px, 4.5vw, 60px)", "clamp(var(--spacing-9), 4.5vw, var(--spacing-15))", count=2)
replace("clamp(var(--spacing-12), 6vw, 96px)", "clamp(var(--spacing-12), 6vw, var(--spacing-24))", count=1)
replace("clamp(96px, 12vw, 160px)", "clamp(var(--spacing-24), 12vw, 160px)", count=1)
replace("clamp(56px, 14vw, 80px) 0 clamp(80px, 18vw, 112px)", "clamp(var(--spacing-14), 14vw, var(--spacing-20)) 0 clamp(var(--spacing-20), 18vw, 112px)", count=1)

# ---- 머리말 ----
head_old = css[:css.index("*/") + 2]
head_new = """/* ============================================================
   PDC — Sun Veil 제품 전용
   ------------------------------------------------------------
   공통(pdc.css)에 없는 Sun Veil 블록만 담는다. 규칙 문서: docs/pdc-convention.md
   동작: product-story.js(이전 중) → pdc-sun-veil.js

   이력: v3 CSS에서 이름 변환(1차) → 대체값 · screen and 제거(2차-a) → 2차-b 적용(공통과 겹치는 규칙 제거 · token 대응)
   기획 레포 tools/pdc-convert/ 의 스크립트로 만들었다. 2차-b부터는 이 파일을 직접 고친다.
   ============================================================ */"""
css = css.replace(head_old, head_new, 1)

CSS.write_text(css, encoding="utf-8")
print("\n".join(log))
print(f"\n{len(css.splitlines())}줄")
