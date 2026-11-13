"""Plain-background segmentation, reference-card detection and fruit mask."""
import cv2
import numpy as np


def segment_objects(img_bgr):
    """Separate objects from a plain light background.
    Background colour = median colour of the image border in LAB space."""
    lab = cv2.cvtColor(cv2.GaussianBlur(img_bgr, (5, 5), 0), cv2.COLOR_BGR2LAB).astype(np.float32)
    border = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.linalg.norm(lab - bg, axis=2)
    dist8 = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, mask = cv2.threshold(dist8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 0.005 * img_bgr.shape[0] * img_bgr.shape[1]
    return [c for c in cnts if cv2.contourArea(c) > min_area]


def split_fruit_and_card(contours, card_long_mm: float | None = 85.6):
    """Find the reference card (4 corners, aspect ratio about 1.586), then treat the
    largest remaining contour as the fruit. Returns (fruit, card, px_per_mm or None, n_other)."""
    card, px_per_mm = None, None
    if card_long_mm:
        for c in sorted(contours, key=cv2.contourArea):
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):
                (_, _), (w, h), _ = cv2.minAreaRect(c)
                long_side, short_side = max(w, h), min(w, h)
                if short_side > 0 and 1.4 < long_side / short_side < 1.75:
                    card, px_per_mm = c, long_side / card_long_mm
                    break
    rest = [c for c in contours if card is None or c is not card]
    fruit = max(rest, key=cv2.contourArea) if rest else None
    return fruit, card, px_per_mm, max(len(rest) - 1, 0)


def contour_mask(shape_hw, contour):
    mask = np.zeros(shape_hw, np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    return mask
