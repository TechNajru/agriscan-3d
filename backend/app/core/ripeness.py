"""Rule-based ripeness from the HSV colour mix inside the fruit mask (profile per fruit)."""
import cv2
import numpy as np


def estimate_ripeness(img_bgr, mask, profile: dict) -> dict:
    p = profile["ripeness"]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = [ch[mask > 0] for ch in cv2.split(hsv)]
    green = float(np.mean((h >= p["green_hue"][0]) & (h <= p["green_hue"][1]) & (s > 60)))
    brown = float(np.mean((h >= p["brown_hue"][0]) & (h <= p["brown_hue"][1]) & (s > 80) & (v < 140)))
    if brown > p["overripe_brown"]:
        label, margin = "Overripe", brown - p["overripe_brown"]
    elif green > p["unripe_green"]:
        label, margin = "Unripe", green - p["unripe_green"]
    elif green > p["partial_green"]:
        label, margin = "Partially Ripe", min(green - p["partial_green"], p["unripe_green"] - green)
    else:
        label, margin = "Ripe", p["partial_green"] - green
    confidence = float(np.clip(0.5 + margin * 2, 0.5, 0.99))     # heuristic score, not a probability
    # Colour uniformity: hue is circular (red wraps around 0/180), so use the mean
    # resultant length of the hue angles (1.0 = every pixel has the same hue).
    angles = np.deg2rad(h.astype(float) * 2.0)
    uniformity = float(np.hypot(np.mean(np.cos(angles)), np.mean(np.sin(angles))))
    return {"label": label, "confidence": round(confidence, 2), "uniformity": round(uniformity, 3),
            "green_share": round(green, 3), "brown_share": round(brown, 3)}
