"""Rule-based grading. The worst grade triggered by any rule wins. Every trigger is
recorded as a reason (i18n key + parameters) so the decision is explainable."""
from dataclasses import dataclass, field

ORDER = ["A", "B", "C", "Reject"]
RECOMMENDATION_KEY = {"A": "premium", "B": "local_market", "C": "processing", "Reject": "discard"}
RIPENESS_PENALTY = {"Unripe": 10, "Partially Ripe": 3, "Ripe": 0, "Overripe": 25}


@dataclass
class GradeResult:
    grade: str
    score: int
    reasons: list = field(default_factory=list)       # [{"key": ..., "params": {...}, "grade": ...}]

    @property
    def recommendation_key(self) -> str:
        return RECOMMENDATION_KEY[self.grade]


def quality_score(defects, ripeness, uniformity, circularity, grade, rules) -> int:
    """Continuous 0-100 score used to rank fruit inside one grade (batch sorting, trends)."""
    total = sum(d["area_ratio"] for d in defects)
    score = 100.0
    score -= min(60.0, total * 200.0)
    score -= min(24.0, 8.0 * len(defects))
    score -= RIPENESS_PENALTY.get(ripeness, 0)
    score -= max(0.0, rules["min_uniformity_A"] + 0.25 - uniformity) * 40.0
    score -= max(0.0, 0.90 - circularity) * 30.0
    caps = {"A": 100, "B": 89, "C": 69, "Reject": 39}          # a score never contradicts the grade
    floors = {"A": 80, "B": 60, "C": 40, "Reject": 0}
    return int(round(max(floors[grade], min(caps[grade], score))))


def grade_fruit(defects, ripeness, uniformity, circularity, size_mm, profile, rules) -> GradeResult:
    total = sum(d["area_ratio"] for d in defects)
    pct = round(total * 100, 1)
    n = len(defects)
    reasons, worst = [], 0

    def trigger(grade, key, **params):
        nonlocal worst
        worst = max(worst, ORDER.index(grade))
        reasons.append({"key": key, "params": params, "grade": grade})

    severe = any(d["type"] in rules["severe_types"] and d["confidence"] >= rules["severe_min_conf"] for d in defects)
    if severe:
        trigger("Reject", "severe_defect")
    if total > rules["reject_area"]:
        trigger("Reject", "large_area", limit=round(rules["reject_area"] * 100))
    if total > rules["c_area"]:
        trigger("C", "defect_area_c", pct=pct, limit=round(rules["c_area"] * 100))
    if n >= rules["c_defect_count"]:
        trigger("C", "many_defects", count=n)
    if ripeness == "Overripe":
        trigger("C", "overripe")
    if total > rules["b_area"]:
        trigger("B", "defect_area_b", pct=pct)
    elif 1 <= n < rules["c_defect_count"]:
        trigger("B", "few_defects", count=n)
    if ripeness == "Unripe":
        trigger("B", "unripe")
    if uniformity < rules["min_uniformity_A"]:
        trigger("B", "uneven_colour")
    if circularity < rules["min_circularity_A"]:
        trigger("B", "irregular_shape")
    if size_mm is not None and size_mm < profile["min_size_mm_for_A"]:
        trigger("B", "undersize")
    grade = ORDER[worst]
    if not reasons:
        reasons.append({"key": "clean", "params": {}, "grade": "A"})
    # keep only the reasons that explain the final grade (the strictest rules)
    reasons = [r for r in reasons if r["grade"] == grade] or reasons
    return GradeResult(grade, quality_score(defects, ripeness, uniformity, circularity, grade, rules), reasons)
