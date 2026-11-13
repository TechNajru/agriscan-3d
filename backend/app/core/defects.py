"""Defect detection: YOLOv8 when a trained model file exists, otherwise an experimental
colour-anomaly fallback (always flagged experimental)."""
import logging
import os

import cv2
import numpy as np

log = logging.getLogger("agriscan.defects")


class DefectDetector:
    def __init__(self, model_path: str):
        self.model = None
        if os.path.exists(model_path):
            try:
                from ultralytics import YOLO            # optional heavy dependency
                self.model = YOLO(model_path)
                log.info("Loaded defect model %s", model_path)
            except Exception as exc:                     # missing package or bad file -> fallback
                log.warning("Defect model not usable (%s); using experimental fallback", exc)

    @property
    def experimental(self) -> bool:
        return self.model is None

    def detect(self, img_bgr, mask, rules: dict) -> list[dict]:
        return self._yolo(img_bgr, mask) if self.model is not None else self._fallback(img_bgr, mask, rules["fallback_detector"])

    # -- trained model ---------------------------------------------------
    def _yolo(self, img_bgr, mask) -> list[dict]:
        res = self.model(img_bgr, conf=0.25, verbose=False)[0]
        fruit_px = float((mask > 0).sum())
        out = []
        for b in res.boxes:
            x1, y1, x2, y2 = [int(v) for v in b.xyxy[0].tolist()]
            covered = float((mask[y1:y2, x1:x2] > 0).sum())      # fruit pixels inside the box
            name = res.names[int(b.cls)]
            if name == "fruit":
                continue
            out.append({"type": name, "confidence": round(float(b.conf), 3), "bbox": [x1, y1, x2, y2],
                        "area_ratio": round(covered / fruit_px, 4)})
        return out

    # -- experimental fallback --------------------------------------------
    def _fallback(self, img_bgr, mask, cfg) -> list[dict]:
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        inner = cv2.erode(mask, np.ones((15, 15), np.uint8))          # ignore the rim
        if not inner.any():
            return []
        med = np.median(lab[inner > 0], axis=0)
        diff = lab - med
        diff[..., 0] *= 0.4                                           # lighting changes matter less than hue
        anomaly = ((np.linalg.norm(diff, axis=2) > cfg["threshold"]) & (inner > 0)).astype(np.uint8) * 255
        anomaly = cv2.morphologyEx(anomaly, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n, _, stats, _ = cv2.connectedComponentsWithStats(anomaly)
        total = float((mask > 0).sum())
        found = []
        for x, y, w, h, area in stats[1:]:
            if area / total >= cfg["min_area_ratio"]:
                found.append({"type": "discoloration", "confidence": 0.5, "bbox": [int(x), int(y), int(x + w), int(y + h)],
                              "area_ratio": round(float(area) / total, 4)})
        found.sort(key=lambda d: d["area_ratio"], reverse=True)
        return found[: cfg["max_defects"]]
