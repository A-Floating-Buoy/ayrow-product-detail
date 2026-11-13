"""제품 CSS에서 절대 일치할 수 없는 선택자 찾기.

상세 HTML의 class와 제품 JS에 나오는 pdc-* 이름에 없는 클래스를 요구하는 선택자는 일치할 수 없다.
:not() · :where() · :is() · :has() 안의 클래스는 판단에서 뺀다.

Run:  python3 tools/pdc-convert/dead-selectors.py [제품]            집계만(기본 sun-veil, 또는 elixir)
      python3 tools/pdc-convert/dead-selectors.py [제품] --apply    제거(그 뒤 tools/pdc-compare 로 화면 · 동작 확인)
"""
import re, sys, pathlib
PLAN = pathlib.Path(__file__).resolve().parent.parent.parent
SKIN = PLAN.parent / 'ayrow-cafe24-skin-2026'
PRODUCT = next((a for a in sys.argv[1:] if not a.startswith('--')), 'sun-veil')
HTML = {'sun-veil': 'sun-veil/cafe24-admin/sun-veil-pdc.html', 'elixir': 'bio-elixir/cafe24-admin/bio-elixir-pdc.html'}[PRODUCT]
css_path = SKIN / f'css/module/product/pdc-{PRODUCT}.css'
css = css_path.read_text(encoding='utf-8')
html = (PLAN / HTML).read_text(encoding='utf-8')
js = (SKIN / f'js/module/product/pdc-{PRODUCT}.js').read_text(encoding='utf-8')
used = set()
for m in re.finditer(r'class="([^"]*)"', html):
    used |= set(m.group(1).split())
used |= set(re.findall(r'pdc[\w-]+', js))          # JS가 붙이는 클래스 · 선택자
CLASS = re.compile(r'\.(pdc[\w-]*)')

def split_selectors(sel):
    out, depth, cur = [], 0, ''
    for ch in sel:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return out

def dead(selector):
    # :not(...) · :where(...) · :is(...) 안의 클래스는 "없어도 되는" 조건일 수 있어 판단에서 뺀다
    bare = re.sub(r':(not|where|is|has)\((?:[^()]|\([^()]*\))*\)', '', selector)
    return any(c not in used for c in CLASS.findall(bare))

out, i, n = [], 0, len(css)
stats = {'rules_removed': 0, 'selectors_removed': 0, 'classes': set()}
# 규칙 단위 토큰화: selector { body } / @media ... { ... }
def process(block):
    res, pos = [], 0
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', block):
        pre = block[pos:m.start()]
        res.append(pre)
        head, body = m.group(1), m.group(2)
        lead = re.match(r'\s*(?:/\*.*?\*/\s*)*', head, flags=re.S).group(0)
        sel = head[len(lead):]
        if sel.strip().startswith('@') or re.match(r'\s*(from|to|\d+%)', sel):
            res.append(m.group(0)); pos = m.end(); continue
        parts = split_selectors(sel)
        keep = [p for p in parts if not dead(p)]
        for p in parts:
            if dead(p):
                stats['selectors_removed'] += 1
                stats['classes'] |= {c for c in CLASS.findall(p) if c not in used}
        if not keep:
            stats['rules_removed'] += 1
            res.append(lead if lead.strip() else '')
        elif len(keep) == len(parts):
            res.append(m.group(0))
        else:
            first_indent = re.match(r'\s*', parts[0]).group(0)
            joined = ','.join(keep)
            if not joined.startswith(('\n', ' ')) or keep[0] is not parts[0]:
                joined = first_indent + joined.lstrip()
            res.append(lead + joined + '{' + body + '}')
        pos = m.end()
    res.append(block[pos:])
    return ''.join(res)

new = process(css)
# 빈 @media · @supports 제거, 빈 줄 정리
for _ in range(3):
    new = re.sub(r'@(media|supports)[^{}]*\{\s*\}\n?', '', new)
new = re.sub(r'\n{3,}', '\n\n', new)
print('규칙 제거', stats['rules_removed'], '· 선택자 제거', stats['selectors_removed'], '· 죽은 클래스', len(stats['classes']))
print(len(css.splitlines()), '줄 →', len(new.splitlines()), '줄')
blocks = sorted({re.sub(r'(__|--).*', '', c) for c in stats['classes']})
print('블록:', ', '.join(blocks))
if '--apply' in sys.argv:
    css_path.write_text(new, encoding='utf-8'); print('적용함')
