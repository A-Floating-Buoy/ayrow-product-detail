"""섹션별 스크린샷 전후 비교.

Run:  python3 compare.py <제품>            예) python3 compare.py sun-veil
      before/<제품>/<폭>/NN-키.png  ↔  after/<제품>/<폭>/NN-키.png
      다른 섹션은 diff/<제품>/<폭>/ 에 [전 | 후 | 차이] 이미지를 만든다.

섹션은 순서(NN)로 짝짓는다 — 이전하면서 섹션 키 이름이 바뀌어도 비교할 수 있다.
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
TOLERANCE = 8  # 채널 차이가 이 값 이하면 같은 픽셀로 본다(글자 가장자리 등)


def compare(before: Path, after: Path, out: Path):
    a = Image.open(before).convert("RGB")
    b = Image.open(after).convert("RGB")
    size_same = a.size == b.size
    w, h = max(a.width, b.width), max(a.height, b.height)
    pa = Image.new("RGB", (w, h), "white")
    pb = Image.new("RGB", (w, h), "white")
    pa.paste(a, (0, 0))
    pb.paste(b, (0, 0))
    mask = ImageChops.difference(pa, pb).convert("L").point(lambda v: 255 if v > TOLERANCE else 0)
    changed = mask.histogram()[255]
    ratio = changed / (w * h)
    if changed or not size_same:
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet = Image.new("RGB", (w * 3 + 40, h), "#888")
        sheet.paste(pa, (0, 0))
        sheet.paste(pb, (w + 20, 0))
        red = Image.new("RGB", (w, h), "red")
        sheet.paste(Image.composite(red, pa.point(lambda v: 200 + v // 5), mask), (w * 2 + 40, 0))
        sheet.save(out)
    return a.size, b.size, ratio


def main():
    product = sys.argv[1]
    total = bad = 0
    for width_dir in sorted((HERE / "before" / product).iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else 0):
        if not width_dir.is_dir():
            continue
        after_dir = HERE / "after" / product / width_dir.name
        after_by_no = {p.name[:2]: p for p in after_dir.glob("*.png")} if after_dir.exists() else {}
        for before in sorted(width_dir.glob("*.png")):
            total += 1
            after = after_by_no.get(before.name[:2])
            if not after:
                bad += 1
                print(f"{width_dir.name:>5}  {before.name:<34} 후 화면 없음")
                continue
            sa, sb, ratio = compare(before, after, HERE / "diff" / product / width_dir.name / before.name)
            if ratio or sa != sb:
                bad += 1
                size = "" if sa == sb else f"  크기 {sa[0]}x{sa[1]} → {sb[0]}x{sb[1]}"
                print(f"{width_dir.name:>5}  {before.name:<34} 다름 {ratio * 100:.2f}%{size}")
    print(f"\n{product}: 섹션 {total}개 중 {bad}개 다름" if bad else f"\n{product}: 섹션 {total}개 모두 같음")


if __name__ == "__main__":
    main()
