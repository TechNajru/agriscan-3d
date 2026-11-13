"""Procedurally generated apple scenes (clearly synthetic, no copyrighted photos).
Used by the tests and by scripts/make_samples.py for the demo samples."""
import cv2
import numpy as np

PX_PER_MM = 5.0


def make_scene(kind="good", seed=0, with_card=False, size=(1280, 900), diameter_mm=72.0):
    rng = np.random.default_rng(seed)
    W, H = size
    img = np.full((H, W, 3), (236, 238, 238), np.float32) + rng.normal(0, 1.2, (H, W, 3))
    cx, cy, r = 470, 470, int(diameter_mm / 2 * PX_PER_MM)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    inside = d <= 1.0
    base = {"unripe": (70, 175, 80), "overripe": (30, 70, 120)}.get(kind, (48, 55, 188))   # BGR
    light = 1.08 - 0.28 * d ** 2 + 0.12 * np.exp(-(((xx - cx + 0.35 * r) ** 2 + (yy - cy + 0.4 * r) ** 2) / (0.25 * r) ** 2))
    tex = rng.normal(0, 9, (H, W, 1)) + cv2.GaussianBlur(rng.normal(0, 14, (H, W)).astype(np.float32), (0, 0), 14)[..., None]
    apple = np.clip(np.array(base, np.float32)[None, None, :] * light[..., None] + tex, 0, 255)
    img[inside] = apple[inside]

    def patch(dx, dy, radius, color, soft=6):
        m = np.zeros((H, W), np.float32)
        cv2.ellipse(m, (int(cx + dx * r), int(cy + dy * r)), (int(radius * r), int(radius * r * 0.8)), 25, 0, 360, 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), soft) * inside
        col = np.array(color, np.float32)[None, None, :] + rng.normal(0, 6, (H, W, 1))
        return m[..., None], col

    if kind == "bruised":                   # one bruise, about 4% of the fruit area
        m, col = patch(0.35, 0.15, 0.20, (28, 62, 108)); img = img * (1 - m) + col * m
    if kind == "rotten":                    # a large rotten patch, about a third of the area
        m, col = patch(0.10, 0.05, 0.68, (18, 30, 52)); img = img * (1 - m) + col * m
    if kind == "multi":                     # four small defects
        for dx, dy in ((0.4, 0.3), (-0.4, 0.4), (0.0, -0.55), (-0.45, -0.2)):
            m, col = patch(dx, dy, 0.11, (28, 62, 108), soft=3); img = img * (1 - m) + col * m
    cv2.line(img, (cx, cy - r + 6), (cx + 8, cy - r - 28), (40, 60, 90), 7)
    if with_card:                           # a 85.6 x 54 mm card, 5 px per mm
        x0, y0 = 760, 300
        cv2.rectangle(img, (x0, y0), (x0 + int(85.6 * PX_PER_MM), y0 + int(53.98 * PX_PER_MM)), (150, 120, 90), -1)
        cv2.rectangle(img, (x0 + 20, y0 + 30), (x0 + 120, y0 + 70), (200, 190, 170), -1)
    img = np.clip(img, 0, 255).astype(np.uint8)
    if kind == "blurry":
        img = cv2.GaussianBlur(img, (0, 0), 14)
    if kind == "dark":
        img = (img * 0.12).astype(np.uint8)
    return img


def encode(img, ext=".jpg") -> bytes:
    ok, buf = cv2.imencode(ext, img)
    assert ok
    return buf.tobytes()
