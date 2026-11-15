"""키트(세트) 상세 조립 — 키트 전용 섹션(sections/)과 두 제품 상세의 섹션을 차례로 놓는다.

제품 섹션은 원본에서 그대로 꺼낸다(카피 · 마크업을 고치지 않는다). 키트 전용 섹션은 sections/*.html을 직접 고친다.
set-pdc.html은 직접 고치지 않고 이 스크립트로 다시 만든다.

  읽기  bio-elixir/cafe24-admin/bio-elixir-pdc.html · sun-veil/cafe24-admin/sun-veil-pdc.html · tools/pdc-set/sections/*.html
  쓰기  set/cafe24-admin/set-pdc.html

Run:  python3 tools/pdc-set/build.py [--full] [--no-launch] [--out=<파일>] [--ver=<버전>]
      --no-launch  런칭 배너(sections/launch.html)를 뺀 판 — 런칭 기간이 끝난 뒤
      --full  기획안이 뺀 제품 섹션까지 모두 실은 판(길이 비교용)

구성 (2026-11-14 — docs/enhancement/skin-longevity-kit/brief.md)
  1 KIT CONCEPT · 2 TWO FORMS   sections/concept.html
    LAUNCH SPECIAL              sections/launch.html (런칭 기간 한정 — 1과 2 사이에 놓는다 · 2026-11-15)
  3 CLINICAL PROOF              sections/clinical.html
  4 엘릭서      hero(구간 표지) · concentrate(2026-11-15에 되살림) · clinical · origin · botanical · ltve · harmony
  5 선베일      hero(구간 표지) · film-membrane · film-membrane-standard · how-it-works · how-it-bonds ·
                reverse-ag-code-formula · proven-data · makeup-routine
                (제품별 사용방법 usage · how-to-use는 2026-11-14에 뺌 — 키트 사용 순서는 6이 맡는다)
  6 THE KIT RITUAL · WHEREABLE BEAUTY   sections/ritual.html (시안 없음 — 임시 구현)
  7 FAQ         탭 3개 — 키트(sections/faq-kit.html) / 엘릭서 faq / 선베일 full-faq

제품 섹션에서 고친 것은 목차 제목(제품 이름을 앞에 붙임 — NAV)과 엘릭서 Hero의 섹션 키뿐이다.
뺀 것: 선베일 banner(웰니스 기프팅 배너) · JSON-LD(키트 상품용은 따로 써야 한다) · 위 목록에 없는 제품 섹션(--full로 되살림)
이력: docs/changelog/2026-11-13.md(주제별 섞기 · 공통 요소 구간 폐기) · 2026-11-14.md(키트 기획안 반영)
"""
import re
import sys
from pathlib import Path

PLANNING = Path(__file__).resolve().parent.parent.parent
flags = dict(a[2:].split("=", 1) if "=" in a else (a[2:], "1") for a in sys.argv[1:] if a.startswith("--"))
VER = flags.get("ver", "20261115000004")
FULL = "full" in flags
IMG = "https://ecimg.cafe24img.com/pg2475b11771033004/ayrow/web/src/set"
SECTIONS = Path(__file__).resolve().parent / "sections"
OUT = Path(flags["out"]) if "out" in flags else PLANNING / "set/cafe24-admin/set-pdc.html"

SRC = {
    "elixir": (PLANNING / "bio-elixir/cafe24-admin/bio-elixir-pdc.html").read_text(encoding="utf-8"),
    "sun-veil": (PLANNING / "sun-veil/cafe24-admin/sun-veil-pdc.html").read_text(encoding="utf-8"),
}
CSS_VER = {name: re.search(r"pdc-%s\.css\?ver=(\d+)" % name, text).group(1) for name, text in SRC.items()}


def section(product, key):
    """원본에서 섹션 하나를 그대로 꺼낸다. 목차 제목만 뗀다(장 제목은 아래에서 다시 붙인다)."""
    found = re.findall(r'^  <section\b[^>]*data-pdc-section="%s"[^>]*>\n.*?^  </section>\n' % re.escape(key), SRC[product], re.M | re.S)
    assert len(found) == 1, (product, key, len(found))
    return found[0]


def no_nav(html):
    return re.sub(r' data-pdc-nav-title="[^"]*"', "", html, count=1)


def swap(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def group(product, *sections, attrs=""):
    return '  <div class="pdc--%s pdc-set__group"%s>\n%s  </div>\n' % (product, attrs, "".join(sections))


def part(name):
    """키트 전용 섹션 조각. {{IMG}}는 키트 이미지 폴더 주소로 바꾼다."""
    return (SECTIONS / name).read_text(encoding="utf-8").replace("{{IMG}}", IMG)


def only_full(*keys):
    return keys if FULL else ()


# ---- FAQ 탭 ----
faq_tabs = """  <section class="pdc__section pdc__section--contained pdc-set-faq" data-pdc-nav-title="자주 묻는 질문" data-pdc-section="set-faq">
    <div class="container container--md">
      <h2 class="pdc-set-faq__title heading-xxxl">FAQ</h2>
      <div class="pdc-set-tabs" role="tablist" aria-label="제품별 자주 묻는 질문" data-pdc-set-tabs>
        <button class="pdc-set-tabs__tab heading-s" type="button" role="tab" data-pdc-set-tab="kit">레디 키트</button>
        <button class="pdc-set-tabs__tab heading-s" type="button" role="tab" data-pdc-set-tab="elixir">바이오 엘릭서</button>
        <button class="pdc-set-tabs__tab heading-s" type="button" role="tab" data-pdc-set-tab="sun-veil">선베일</button>
      </div>
    </div>
  </section>
"""

E, S = "elixir", "sun-veil"

# ---- 목차 제목 — 제품 이름이 없는 제목 앞에 제품 이름을 붙인다(두 제품에 같은 제목이 있다) ----
NAV = {E: "엘릭서", S: "선베일"}


def named(product, html):
    def add(match):
        title = match.group(1)
        return match.group(0) if ("엘릭서" in title or "선베일" in title) else ' data-pdc-nav-title="%s · %s"' % (NAV[product], title)
    return re.sub(r' data-pdc-nav-title="([^"]*)"', add, html, count=1)


def sections(product, *keys):
    return [named(product, section(product, k)) for k in keys]


# 제품 Hero는 구간 표지로 쓴다(2026-11-13 결정). 구간 첫 목차 제목은 원래 그 제목을 갖던 섹션에서 Hero로 넘긴다
# (엘릭서 concentrate "바이오 엘릭서는 무엇인가요?" · 선베일 membrane-intro "선베일은 무엇인가요?").
def cover(product, hero_key, nav_from, new_key=None):
    nav = re.search(r' data-pdc-nav-title="[^"]*"', section(product, nav_from)).group(0)
    key = ' data-pdc-section="%s"' % hero_key
    return swap(section(product, hero_key), key, ' data-pdc-section="%s"%s' % (new_key or hero_key, nav))


elixir_hero = cover(E, "hero", "concentrate", "elixir-hero")  # 선베일 hero와 키가 겹친다
sun_veil_hero = cover(S, "hero", "membrane-intro")


def rest(product, *keys):
    """--full에서만 싣는 섹션. 목차 제목은 Hero로 넘긴 것이 있어 겹치지 않게 뗀다."""
    return [no_nav(section(product, k)) if k in ("concentrate", "membrane-intro") else named(product, section(product, k)) for k in only_full(*keys)]


chapters = [
    ("3. CLINICAL PROOF", [part("clinical.html")]),
    ("4. 엘릭서", [
        group(E, elixir_hero, no_nav(section(E, "concentrate")), *sections(E, "clinical", "origin", "botanical", "ltve", "harmony"), *rest(E, "ritual", "usage")),
    ]),
    ("5. 선베일", [
        group(S, sun_veil_hero, *rest(S, "membrane-intro", "problem", "film-membrane-pain", "film-membrane-choice"), *sections(S, "film-membrane"),
              *rest(S, "at-a-glance", "why-intro", "why-highlight"),
              *sections(S, "film-membrane-standard", "how-it-works", "how-it-bonds", "reverse-ag-code-formula", "proven-data"), *rest(S, "how-to-use"), *sections(S, "makeup-routine")),
    ]),
    ("6. THE KIT RITUAL · WHEREABLE BEAUTY", [part("ritual.html")]),
    ("7. FAQ — 탭", [
        faq_tabs,
        # 키트 FAQ는 엘릭서 FAQ 블록(pdc-faq)을 쓰므로 엘릭서 범위 안에 둔다
        group(E, part("faq-kit.html"), attrs=' role="tabpanel" data-pdc-set-panel="kit"'),
        group(E, no_nav(section(E, "faq")), attrs=' role="tabpanel" data-pdc-set-panel="elixir"'),
        group(S, no_nav(section(S, "full-faq")), attrs=' role="tabpanel" data-pdc-set-panel="sun-veil"'),
    ]),
]

head = f"""<!-- SKIN LONGEVITY READY KIT 상세 — pdc 체계 · tools/pdc-set/build.py 가 조립한다(직접 고치지 않는다) -->
<!-- 제품 섹션의 문구 · 마크업은 원본 그대로. 제품 섹션은 <div class="pdc--제품 pdc-set__group">으로 묶는다 · 규칙: 스킨 레포 docs/pdc-convention.md -->
<link rel="stylesheet" href="/css/module/product/pdc-elixir.css?ver={CSS_VER['elixir']}">
<link rel="stylesheet" href="/css/module/product/pdc-sun-veil.css?ver={CSS_VER['sun-veil']}">
<link rel="stylesheet" href="/css/module/product/pdc-set.css?ver={VER}">
<div class="pdc pdc--set" data-pdc data-pdc-product="elixir sun-veil set" data-pdc-ver="{VER}">
"""
# 런칭 배너는 01 KIT CONCEPT 아래 · 02 TWO FORMS 위에 놓는다(2026-11-15)
concept, forms = part("concept.html").split("  <!-- 02. TWO FORMS -->\n")
launch = "" if "no-launch" in flags else part("launch.html") + "\n"
body = concept + launch + "  <!-- 02. TWO FORMS -->\n" + forms + "".join("\n  <!-- %s -->\n%s" % (label, "".join(parts)) for label, parts in chapters)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(head + body + "</div>\n", encoding="utf-8")

keys = re.findall(r'data-pdc-section="([^"]+)"', body)
assert len(keys) == len(set(keys)), "섹션 키가 겹침"
ids = re.findall(r'\sid="([^"]+)"', body)
assert len(ids) == len(set(ids)), "id가 겹침"
print(OUT.name, len((head + body).splitlines()), "줄 · 섹션", len(keys), "· 목차", len(re.findall("data-pdc-nav-title", body)))
