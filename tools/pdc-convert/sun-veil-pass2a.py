"""pdc 2차-a: 기계적으로 할 수 있는 정리(화면 변화 없음). Sun Veil에서 처음 썼고 제품 이름을 인자로 받는다.

<스킨>/css/module/product/pdc-sun-veil.css 를 제자리에서 고친다. 여러 번 돌려도 결과가 같다.

  1. var(--스킨token, 대체값) → var(--스킨token)
     스킨 token(css/core/tokens.css · tokens-ayrow-v3.css)에 정의된 이름만. 그 밖의 변수의 대체값은 그대로 둔다.
  2. @media screen and (…) → @media (…)

Run:  python3 tools/pdc-convert/sun-veil-pass2a.py [제품]      기본 sun-veil
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent.parent.parent / "ayrow-cafe24-skin-2026"
import sys

PRODUCT = sys.argv[1] if len(sys.argv) > 1 else "sun-veil"   # 예) python3 … elixir
CSS = SKIN / f"css/module/product/pdc-{PRODUCT}.css"

tokens = set()
for name in ("tokens.css", "tokens-ayrow-v3.css"):
    text = re.sub(r"/\*.*?\*/", "", (SKIN / "css/core" / name).read_text(encoding="utf-8"), flags=re.S)
    tokens |= set(re.findall(r"(--[\w.\\-]+)\s*:", text))


def strip_fallbacks(text):
    """var( 를 찾아 괄호 짝을 맞춰 가며, 스킨 token이면 쉼표 뒤 대체값을 뺀다."""
    out = []
    i = 0
    removed = 0
    while True:
        j = text.find("var(", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        depth = 0
        k = j + 3
        while True:
            ch = text[k]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        inner = text[j + 4:k]
        name, comma, fallback = inner.partition(",")
        name = name.strip()
        if comma and name in tokens:
            out.append(f"var({name})")
            removed += 1
        elif comma:
            inner_fixed, n = strip_fallbacks(fallback)
            removed += n
            out.append(f"var({name},{inner_fixed})")
        else:
            out.append(text[j:k + 1])
        i = k + 1
    return "".join(out), removed


css = CSS.read_text(encoding="utf-8")
css, removed = strip_fallbacks(css)
css, screens = re.subn(r"@media\s+screen\s+and\s+\(", "@media (", css)

left = len(re.findall(r"var\(--[\w-]+\s*,", css))
CSS.write_text(css, encoding="utf-8")
print(f"대체값 제거 {removed}곳 · screen and 제거 {screens}곳 · 남은 대체값 {left}곳(스킨 token이 아닌 변수)")
