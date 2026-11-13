import json
import pathlib

import numpy as np
import pytest

from app.config import fruit_profiles, grading_rules
from app.core import grading, pipeline
from app.core.errors import PipelineError
from tests.synth import make_scene

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPLE = fruit_profiles()["apple"]
RULES = grading_rules()


def analyse(kind, ref=None, **kw):
    result, _ = pipeline.analyze_image(make_scene(kind, with_card=ref is not None, **kw), "apple", ref)
    return result


def test_i18n_files_have_same_keys():
    en = json.loads((ROOT / "i18n" / "en.json").read_text(encoding="utf-8"))
    hi = json.loads((ROOT / "i18n" / "hi.json").read_text(encoding="utf-8"))
    assert en.keys() == hi.keys()


def test_every_reason_and_defect_key_is_translated():
    en = json.loads((ROOT / "i18n" / "en.json").read_text(encoding="utf-8"))
    for key in ("severe_defect", "large_area", "many_defects", "defect_area_c", "overripe", "defect_area_b",
                "few_defects", "unripe", "uneven_colour", "irregular_shape", "undersize", "clean"):
        assert f"reason.{key}" in en


@pytest.mark.parametrize("kind,code", [("blurry", "too_blurry"), ("dark", "too_dark")])
def test_quality_gate_rejects(kind, code):
    with pytest.raises(PipelineError) as e:
        analyse(kind)
    assert e.value.code == code


def test_small_image_rejected():
    with pytest.raises(PipelineError) as e:
        pipeline.analyze_image(np.full((200, 200, 3), 200, np.uint8))
    assert e.value.code == "too_small"


def test_blank_image_has_no_fruit():
    img = np.full((600, 800, 3), 235, np.uint8)
    img += np.random.default_rng(1).integers(0, 3, img.shape, dtype=np.uint8)
    with pytest.raises(PipelineError) as e:
        pipeline.analyze_image(img)
    assert e.value.code == "no_fruit"


def test_reference_card_gives_millimetres():
    r = analyse("good", ref=85.6)
    assert r["size"]["basis"] == "absolute"
    assert abs(r["size"]["diameter_mm"] - 72) < 3          # 72 mm test apple within 3 mm


def test_relative_size_without_card_and_warning_when_card_missing():
    r = analyse("good", ref=None)
    assert r["size"]["basis"] == "relative" and r["size"]["diameter_mm"] is None
    r3, _ = pipeline.analyze_image(make_scene("good", with_card=False), "apple", 85.6)
    assert "reference_not_found" in r3["warnings"]


def test_clean_red_apple_is_grade_a():
    r = analyse("good", ref=85.6)
    assert r["ripeness"]["label"] == "Ripe"
    assert r["defects"] == [] and r["grade"] == "A" and r["recommendation_key"] == "premium"
    assert r["score"] >= 80


def test_green_apple_is_unripe_and_grade_b():
    r = analyse("unripe", ref=85.6)
    assert r["ripeness"]["label"] == "Unripe" and r["grade"] == "B"


def test_single_bruise_gives_grade_b_with_area_about_four_percent():
    r = analyse("bruised", ref=85.6)
    assert len(r["defects"]) == 1 and 0.01 < r["defect_total_ratio"] < 0.07
    assert r["grade"] == "B" and r["experimental"] is True


def test_large_rotten_patch_is_rejected():
    r = analyse("rotten", ref=85.6)
    assert r["grade"] == "Reject" and r["recommendation_key"] == "discard" and r["score"] < 40


def test_many_defects_gives_grade_c():
    r = analyse("multi", ref=85.6)
    assert len(r["defects"]) >= 4 and r["grade"] == "C"


def test_explanation_exists_in_both_languages():
    r = analyse("bruised", ref=85.6)
    assert "Grade B" in r["explanation"]["en"] and "ग्रेड B" in r["explanation"]["hi"]
    assert all(set(x["text"]) == {"en", "hi"} for x in r["reasons"])


# ---- grading rules in isolation ------------------------------------------------
def g(defects, ripeness="Ripe", uniformity=0.8, circ=0.9, size=72):
    return grading.grade_fruit(defects, ripeness, uniformity, circ, size, APPLE, RULES)


def d(t, area, conf=0.9):
    return {"type": t, "confidence": conf, "area_ratio": area}


def test_grading_rules():
    assert g([]).grade == "A"
    assert g([d("bruise", 0.01)]).grade == "B"
    assert g([d("bruise", 0.12)]).grade == "C"
    assert g([d("bruise", 0.30)]).grade == "Reject"
    assert g([d("rot", 0.01)]).grade == "Reject"                      # severe type, confident
    assert g([d("rot", 0.01, conf=0.3)]).grade == "B"                 # severe type but low confidence
    assert g([d("bruise", 0.01)] * 4).grade == "C"
    assert g([], ripeness="Overripe").grade == "C"
    assert g([], ripeness="Unripe").grade == "B"
    assert g([], size=55).grade == "B"                                # undersize caps at B
    assert g([], size=None).grade == "A"                              # size unknown: rule not applied
    assert g([], uniformity=0.3).grade == "B"


def test_score_never_contradicts_grade():
    for defects, ripe in (([], "Ripe"), ([d("bruise", 0.05)], "Ripe"), ([d("bruise", 0.2)], "Overripe"), ([d("rot", 0.4)], "Ripe")):
        res = g(defects, ripe)
        lo, hi = {"A": (80, 100), "B": (60, 89), "C": (40, 69), "Reject": (0, 39)}[res.grade]
        assert lo <= res.score <= hi
