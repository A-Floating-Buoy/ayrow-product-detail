"""세트 상세 초안 조립 — 두 제품 상세에서 섹션을 그대로 가져와 놓는다.

하는 일은 섹션 고르기 · 순서 · 목차 제목에 제품 이름 붙이기다. 카피는 고치지 않는다.
구조가 확정될 때까지 set-pdc.html은 직접 고치지 않고 이 스크립트를 고쳐 다시 만든다.

  읽기  bio-elixir/cafe24-admin/bio-elixir-pdc.html · sun-veil/cafe24-admin/sun-veil-pdc.html
  쓰기  set/cafe24-admin/set-pdc.html

Run:  python3 tools/pdc-set/build.py [--no-problem] [--out=<파일>] [--ver=<버전>]
      --no-problem  선베일 문제 제기 4개와 강조 배너를 뺀 판(길이 비교용)

구성 (2026-11-13 8차 — 두 제품 상세를 차례로 놓고 FAQ만 탭으로 합친다. 공통 요소 구간은 없다)
  1 Hero        세트 히어로 자리(빈 틀)
  2 엘릭서      hero · concentrate · clinical · origin · botanical · ltve · harmony · ritual · usage   (원본 순서 그대로)
  3 선베일      hero(구간 표지 — 도입과 자리 바꿈) · membrane-intro · 문제 제기 4개 · at-a-glance · why-intro · why-highlight ·
                film-membrane-standard · how-it-works · how-it-bonds · reverse-ag-code-formula · proven-data · how-to-use · makeup-routine
  4 FAQ         탭 2개 — 엘릭서 faq / 선베일 full-faq

카피는 고치지 않는다. 고친 것은 목차 제목(제품 이름을 앞에 붙임 — NAV)뿐이다.
뺀 것: 선베일 banner(웰니스 기프팅 배너) · 선베일 JSON-LD(세트 상품용은 따로 써야 한다)
이력: 주제별로 섞기 · 공통 요소 구간(LTVE · Reverse AG Code) · LTVE 일반 설명과 적용 카드는 모두 폐기 — docs/changelog/2026-11-13.md
"""
import re
import sys
from pathlib import Path

PLANNING = Path(__file__).resolve().parent.parent.parent
flags = dict(a[2:].split("=", 1) if "=" in a else (a[2:], "1") for a in sys.argv[1:] if a.startswith("--"))
VER = flags.get("ver", "20261113000009")
NO_PROBLEM = "no-problem" in flags
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


PROBLEM_KEYS = () if NO_PROBLEM else ("problem", "film-membrane-pain", "film-membrane-choice", "film-membrane")
HIGHLIGHT_KEYS = () if NO_PROBLEM else ("why-highlight",)

# ---- 세트 전용 틀 ----
hero = """  <!-- 1. Hero — 자리만 잡아 둠. 문구 · 이미지는 클라이언트 확인 뒤 -->
  <section class="pdc__section pdc__section--contained pdc-set-hero" data-pdc-section="set-hero">
    <div class="container container--md">
      <div class="pdc-set-hero__placeholder" aria-hidden="true"></div>
    </div>
  </section>
"""

faq_tabs = """  <section class="pdc__section pdc__section--contained pdc-set-faq" data-pdc-nav-title="자주 묻는 질문" data-pdc-section="set-faq">
    <div class="container container--md">
      <h2 class="pdc-set-faq__title heading-xxxl">FAQ</h2>
      <div class="pdc-set-tabs" role="tablist" aria-label="제품별 자주 묻는 질문" data-pdc-set-tabs>
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


elixir_hero = swap(section(E, "hero"), 'data-pdc-section="hero"', 'data-pdc-section="elixir-hero"')  # 선베일 hero와 키가 겹친다
# 브릿지(엘릭서 → 선베일): 선베일 Hero를 구간 표지로 쓴다 — 엘릭서 구간이 Hero로 시작하는 것과 짝.
# 원본은 도입("우리가 붙이고 있던 건 '필름'이었습니다") → Hero 순서라서, 세트에서는 둘의 자리를 바꾼다.
# 구간 첫 목차 제목("선베일은 무엇인가요?")은 도입에서 Hero로 넘긴다.
_intro = section(S, "membrane-intro")
_intro_nav = re.search(r' data-pdc-nav-title="[^"]*"', _intro).group(0)
sun_veil_intro = no_nav(_intro)
sun_veil_hero = swap(section(S, "hero"), ' data-pdc-section="hero"', ' data-pdc-section="hero"' + _intro_nav)

chapters = [
    ("2. 엘릭서", [
        group(E, elixir_hero, *sections(E, "concentrate", "clinical", "origin", "botanical", "ltve", "harmony", "ritual", "usage")),
    ]),
    ("3. 선베일", [
        group(S, sun_veil_hero, sun_veil_intro, *sections(S, *PROBLEM_KEYS), *sections(S, "at-a-glance", "why-intro"), *sections(S, *HIGHLIGHT_KEYS),
              *sections(S, "film-membrane-standard", "how-it-works", "how-it-bonds", "reverse-ag-code-formula", "proven-data", "how-to-use", "makeup-routine")),
    ]),
    ("4. FAQ — 제품별 탭", [
        faq_tabs,
        group(E, no_nav(section(E, "faq")), attrs=' role="tabpanel" data-pdc-set-panel="elixir"'),
        group(S, no_nav(section(S, "full-faq")), attrs=' role="tabpanel" data-pdc-set-panel="sun-veil"'),
    ]),
]

head = f"""<!-- 세트 상세 초안 — pdc 체계 · tools/pdc-set/build.py 가 두 제품 상세에서 조립한다(구조 확정 전까지 직접 고치지 않는다) -->
<!-- 제품 섹션의 문구 · 마크업은 원본 그대로. 제품 섹션은 <div class="pdc--제품 pdc-set__group">으로 묶는다 · 규칙: 스킨 레포 docs/pdc-convention.md -->
<link rel="stylesheet" href="/css/module/product/pdc-elixir.css?ver={CSS_VER['elixir']}">
<link rel="stylesheet" href="/css/module/product/pdc-sun-veil.css?ver={CSS_VER['sun-veil']}">
<link rel="stylesheet" href="/css/module/product/pdc-set.css?ver={VER}">
<div class="pdc pdc--set" data-pdc data-pdc-product="elixir sun-veil set" data-pdc-ver="{VER}">
"""
body = hero + "".join("\n  <!-- %s -->\n%s" % (label, "".join(parts)) for label, parts in chapters)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(head + body + "</div>\n", encoding="utf-8")

keys = re.findall(r'data-pdc-section="([^"]+)"', body)
assert len(keys) == len(set(keys)), "섹션 키가 겹침"
ids = re.findall(r'\sid="([^"]+)"', body)
assert len(ids) == len(set(ids)), "id가 겹침"
print(OUT.name, len((head + body).splitlines()), "줄 · 섹션", len(keys), "· 목차", len(re.findall("data-pdc-nav-title", body)))
