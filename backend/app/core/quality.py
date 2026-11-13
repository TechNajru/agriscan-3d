"""Quality gate: refuse unusable photos before any analysis (clear, translatable reasons)."""
import cv2
import numpy as np

from .errors import PipelineError


def check_basic(img_bgr, rules: dict) -> dict:
    """Resolution and brightness. Raises PipelineError(too_small | too_dark)."""
    gate = rules["quality_gate"]
    h, w = img_bgr.shape[:2]
    if min(h, w) < gate["min_side_px"]:
        raise PipelineError("too_small", params={"min_side": gate["min_side_px"]})
    small = cv2.resize(img_bgr, None, fx=640.0 / w, fy=640.0 / w, interpolation=cv2.INTER_AREA)
    brightness = float(cv2.cvtColor(small, cv2.COLOR_BGR2HSV)[..., 2].mean())
    if brightness < gate["dark_min"]:
        raise PipelineError("too_dark", metrics={"brightness": round(brightness, 1)})
    return {"brightness": round(brightness, 1)}


def sharpness_on_fruit(img_bgr, bbox, rules: dict) -> float:
    """Variance of the Laplacian measured on the fruit region only.
    (Measuring the whole frame penalises smooth plain backgrounds.)"""
    x1, y1, x2, y2 = bbox
    roi = img_bgr[max(y1, 0):y2, max(x1, 0):x2]
    gray = cv2.cvtColor(cv2.resize(roi, (320, max(int(320 * roi.shape[0] / max(roi.shape[1], 1)), 1))), cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def check_sharpness(img_bgr, bbox, rules: dict) -> float:
    s = sharpness_on_fruit(img_bgr, bbox, rules)
    if s < rules["quality_gate"]["blur_min"]:
        raise PipelineError("too_blurry", metrics={"sharpness": round(s, 1)})
    return round(s, 1)
