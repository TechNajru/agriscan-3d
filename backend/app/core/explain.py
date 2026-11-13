"""Bilingual explanations built from fixed templates (no machine translation)."""
from ..config import i18n


def _fmt(text: str, **p) -> str:
    return text.format(**p)


def render_reason(reason: dict, lang: str) -> str:
    return _fmt(i18n(lang)[f"reason.{reason['key']}"], **reason["params"])


def render_explanation(lang: str, *, defects, total_pct, ripeness, grade, recommendation_key, experimental, reasons) -> str:
    d = i18n(lang)
    parts = []
    if not defects:
        parts.append(d["explain.no_defects"])
    else:
        types = ", ".join(dict.fromkeys(d.get(f"defect.{x['type']}", x["type"]) for x in defects))
        key = "explain.defects_one" if len(defects) == 1 else "explain.defects_other"
        parts.append(_fmt(d[key], count=len(defects), types=types, pct=total_pct))
    parts.append(_fmt(d["explain.ripeness"], ripeness=d[f"ripeness.{ripeness}"]))
    if experimental and defects:
        parts.append(d["explain.experimental"])
    parts.append(_fmt(d["explain.conclusion"], recommendation=d[f"recommendation.{recommendation_key}"], grade=grade))
    return " ".join(parts)


def both(fn, **kw) -> dict:
    return {lang: fn(lang, **kw) for lang in ("en", "hi")}
