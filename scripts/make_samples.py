"""Generates the synthetic demo images used by the app and the docs (no real photos, no licences involved).
Run from the repo root:  python scripts/make_samples.py"""
import json
import pathlib
import sys

import cv2

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from tests.synth import make_scene        # noqa: E402

SPECS = {"good": dict(seed=1, with_card=True), "bruised": dict(seed=2, with_card=True),
         "unripe": dict(seed=3, with_card=False), "rotten": dict(seed=4, with_card=True)}
out_dirs = [ROOT / "samples", ROOT / "frontend" / "public" / "samples"]
for d in out_dirs:
    d.mkdir(parents=True, exist_ok=True)
expected = {}
for name, kw in SPECS.items():
    img = make_scene(name, **kw)
    for d in out_dirs:
        cv2.imwrite(str(d / f"{name}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    expected[name] = {"reference_card_in_photo": kw["with_card"]}
(ROOT / "samples" / "README.md").write_text(
    "# Samples\n\nComputer-generated apple illustrations used for demos and automated tests. They are **not** photographs of real fruit.\n"
    "Run the backend tests (`pytest`) to see the grade each sample produces.\n\n" + json.dumps(expected, indent=2) + "\n")
print("samples written:", list(SPECS))
