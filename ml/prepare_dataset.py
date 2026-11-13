"""Merge several YOLO-format datasets into one training set with the project's class list.

Each source folder must contain: data.yaml (with `names`), images/ + labels/ (any sub-folders), and a LICENSE.txt
(or LICENSE.md) so that no dataset is used without its licence being recorded.

Splitting is done per GROUP (one physical fruit) so near-duplicate photos of the same fruit never leak between
train/val/test. The group id is taken from the file name with --group-regex (first capture group), otherwise
the file stem is the group.

    python ml/prepare_dataset.py --sources data/raw/* --class-map ml/class_map.json --out data/yolo
"""
import argparse
import hashlib
import json
import random
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

TARGET = ["bruise", "cut", "fungal spot", "rot", "crack", "insect damage"]
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def read_names(src: Path) -> list[str]:
    text = (src / "data.yaml").read_text(encoding="utf-8")
    m = re.search(r"names:\s*(\[.*?\]|(?:\n\s+-.*)+|(?:\n\s+\d+:.*)+)", text, re.S)
    if not m:
        raise SystemExit(f"{src}: cannot read names from data.yaml")
    body = m.group(1)
    if body.strip().startswith("["):
        return [s.strip(" '\"") for s in body.strip()[1:-1].split(",") if s.strip()]
    items = re.findall(r"(?:-\s*|\d+:\s*)(.+)", body)
    return [s.strip(" '\"") for s in items]


def group_of(path: Path, regex: str | None) -> str:
    if regex:
        m = re.search(regex, path.stem)
        if m:
            return m.group(1)
    return path.stem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--class-map", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--group-regex", default=None)
    ap.add_argument("--split", default="0.7,0.2,0.1")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    cmap = json.loads(Path(a.class_map).read_text(encoding="utf-8"))
    ratios = [float(x) for x in a.split.split(",")]
    out = Path(a.out)

    samples = []                                   # (image, label_lines, group, source)
    for s in map(Path, a.sources):
        if not s.is_dir():
            continue
        if not any((s / n).exists() for n in ("LICENSE.txt", "LICENSE.md", "LICENSE")):
            raise SystemExit(f"{s}: add a LICENSE.txt (record the dataset licence) before using it")
        mapping = cmap.get(s.name)
        if mapping is None:
            raise SystemExit(f"{s.name}: not found in the class map")
        names = read_names(s)
        for img in (p for p in s.rglob("*") if p.suffix.lower() in IMG_EXT):
            lbl = next((c for c in (img.with_suffix(".txt"), Path(str(img).replace("/images/", "/labels/")).with_suffix(".txt")) if c.exists()), None)
            if lbl is None:
                continue
            lines = []
            for ln in lbl.read_text().splitlines():
                parts = ln.split()
                if len(parts) < 5:
                    continue
                tgt = mapping.get(names[int(parts[0])])
                if tgt in TARGET:
                    lines.append(" ".join([str(TARGET.index(tgt))] + parts[1:]))
            samples.append((img, lines, group_of(img, a.group_regex), s.name))

    groups = sorted({(g, src) for _, _, g, src in samples})
    random.Random(a.seed).shuffle(groups)
    n = len(groups)
    cut1, cut2 = int(n * ratios[0]), int(n * (ratios[0] + ratios[1]))
    split_of = {g: ("train" if i < cut1 else "val" if i < cut2 else "test") for i, g in enumerate(groups)}

    if out.exists():
        shutil.rmtree(out)
    counts, per_split = defaultdict(Counter), Counter()
    for img, lines, g, src in samples:
        split = split_of[(g, src)]
        tag = hashlib.md5(str(img).encode()).hexdigest()[:8]
        name = f"{src}_{tag}"
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)
        shutil.copy(img, out / "images" / split / f"{name}{img.suffix.lower()}")
        (out / "labels" / split / f"{name}.txt").write_text("\n".join(lines) + ("\n" if lines else ""))
        per_split[split] += 1
        for ln in lines:
            counts[split][TARGET[int(ln.split()[0])]] += 1
    (out / "data.yaml").write_text("path: " + str(out.resolve()) + "\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n"
                                   + "".join(f"  {i}: {c}\n" for i, c in enumerate(TARGET)))
    print("images per split:", dict(per_split))
    for split in ("train", "val", "test"):
        print(split, "boxes per class:", dict(counts[split]))
    weak = [c for c in TARGET if counts["train"][c] < 100]
    if weak:
        print("WARNING: fewer than 100 training boxes for:", weak, "-> merge or drop these classes instead of claiming them")


if __name__ == "__main__":
    main()
