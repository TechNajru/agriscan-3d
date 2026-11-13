"""End-to-end single-image analysis: gate -> segment -> ripeness -> size -> defects -> grade."""
import time

import cv2
import numpy as np

from ..config import fruit_profiles, grading_rules, i18n, settings
from . import explain, grading, quality, segmentation, shape
from .defects import DefectDetector
from .errors import PipelineError
from .ripeness import estimate_ripeness

_detector: DefectDetector | None = None


def get_detector() -> DefectDetector:
    global _detector
    if _detector is None:
        _detector = DefectDetector(settings.defect_model_path)
    return _detector


def downscale(img_bgr, max_side: int):
    h, w = img_bgr.shape[:2]
    scale = max_side / float(max(h, w))
    return cv2.resize(img_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1 else img_bgr


def analyze_image(img_bgr, fruit: str = "apple", ref_width_mm: float | None = None) -> dict:
    t0 = time.perf_counter()
    rules, profiles = grading_rules(), fruit_profiles()
    if fruit not in profiles:
        raise PipelineError("invalid_file", 400)
    profile = profiles[fruit]
    img = downscale(img_bgr, settings.process_max_side)
    h, w = img.shape[:2]

    metrics = quality.check_basic(img, rules)
    contours = segmentation.segment_objects(img)
    fruit_c, _, px_per_mm, n_other = segmentation.split_fruit_and_card(contours, ref_width_mm)
    if fruit_c is None or cv2.contourArea(fruit_c) < 0.02 * h * w:
        raise PipelineError("no_fruit")
    x, y, bw, bh = cv2.boundingRect(fruit_c)
    fruit_bbox = [int(x), int(y), int(x + bw), int(y + bh)]
    metrics["sharpness"] = quality.check_sharpness(img, fruit_bbox, rules)
    mask = segmentation.contour_mask((h, w), fruit_c)

    warnings = []
    if ref_width_mm and px_per_mm is None:
        warnings.append("reference_not_found")
    if n_other:
        warnings.append("multiple_objects")

    ripe = estimate_ripeness(img, mask, profile)
    feat = shape.shape_features(fruit_c, px_per_mm)
    size = shape.size_info(feat, (h, w), profile)
    detector = get_detector()
    defects = detector.detect(img, mask, rules)
    total_ratio = round(sum(d["area_ratio"] for d in defects), 4)

    g = grading.grade_fruit(defects, ripe["label"], ripe["uniformity"], feat["circularity"],
                            size["diameter_mm"], profile, rules)
    rec_key = g.recommendation_key
    reasons = [{"key": r["key"], "params": r["params"],
                "text": {lang: explain.render_reason(r, lang) for lang in ("en", "hi")}} for r in g.reasons]
    explanation = explain.both(explain.render_explanation, defects=defects, total_pct=round(total_ratio * 100, 1),
                               ripeness=ripe["label"], grade=g.grade, recommendation_key=rec_key,
                               experimental=detector.experimental, reasons=g.reasons)
    return {
        "fruit_type": fruit,
        "image": {"width": w, "height": h},
        "fruit_bbox": fruit_bbox,
        "ripeness": ripe,
        "size": {**size, "aspect_ratio": round(feat["aspect_ratio"], 2), "circularity": round(feat["circularity"], 3)},
        "defects": defects,
        "defect_total_ratio": total_ratio,
        "experimental": detector.experimental,
        "grade": g.grade,
        "score": g.score,
        "recommendation_key": rec_key,
        "recommendation": {lang: i18n(lang)[f"recommendation.{rec_key}"] for lang in ("en", "hi")},
        "reasons": reasons,
        "explanation": explanation,
        "warnings": warnings,
        "quality": metrics,
        "timing_ms": int((time.perf_counter() - t0) * 1000),
    }, img


def annotate(img_bgr, result: dict):
    """Draw the fruit box and defect boxes (English labels; Hindi is shown by the UI overlay)."""
    out = img_bgr.copy()
    x1, y1, x2, y2 = result["fruit_bbox"]
    cv2.rectangle(out, (x1, y1), (x2, y2), (210, 120, 30), 3)
    cv2.putText(out, result["fruit_type"], (x1, max(y1 - 8, 18)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (210, 120, 30), 2, cv2.LINE_AA)
    for d in result["defects"]:
        a, b, c, e = d["bbox"]
        cv2.rectangle(out, (a, b), (c, e), (40, 40, 220), 3)
        label = f"{d['type']} {d['confidence']:.2f}"
        cv2.putText(out, label, (a, max(b - 6, 16)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 220), 2, cv2.LINE_AA)
    return out
