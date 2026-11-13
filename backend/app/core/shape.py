"""Size and shape from the fruit contour."""
import cv2
import numpy as np


def shape_features(contour, px_per_mm=None) -> dict:
    area = cv2.contourArea(contour)
    # Pixel contours are jagged and overstate the perimeter; smooth it before measuring circularity.
    peri = cv2.arcLength(cv2.approxPolyDP(contour, 0.004 * cv2.arcLength(contour, True), True), True)
    (_, _), (w, h), _ = cv2.minAreaRect(contour)
    out = {
        "area_px": float(area),
        "aspect_ratio": float(max(w, h) / max(min(w, h), 1e-6)),
        "circularity": float(min(4 * np.pi * area / (peri ** 2), 1.0)),   # 1.0 = circle
        "equiv_diameter_px": float(np.sqrt(4 * area / np.pi)),
    }
    if px_per_mm:
        out["diameter_mm"] = out["equiv_diameter_px"] / px_per_mm
    return out


def size_info(feat: dict, image_hw, profile: dict) -> dict:
    """Absolute size (mm) when a reference card was found, otherwise relative size."""
    frame_fraction = feat["area_px"] / float(image_hw[0] * image_hw[1])
    if "diameter_mm" in feat:
        d = feat["diameter_mm"]
        cls = profile["size_classes_mm"]
        klass = "small" if d < cls["small_below"] else "large" if d > cls["large_above"] else "medium"
        return {"basis": "absolute", "diameter_mm": round(d, 1), "class": klass, "frame_pct": round(100 * frame_fraction, 1)}
    cls = profile["relative_size_classes"]
    klass = "small" if frame_fraction < cls["small_below"] else "large" if frame_fraction > cls["large_above"] else "medium"
    return {"basis": "relative", "diameter_mm": None, "class": klass, "frame_pct": round(100 * frame_fraction, 1)}
