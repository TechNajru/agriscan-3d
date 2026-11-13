"""PDF report (English or Hindi). WeasyPrint shapes Devanagari correctly (Pango + HarfBuzz)."""
import base64
from datetime import datetime
from html import escape

from weasyprint import HTML

from ..config import i18n, settings

GRADE_COLOR = {"A": "#2F7D43", "B": "#B98A1E", "C": "#CC6A1B", "Reject": "#B3261E"}


def _img_data_uri(path) -> str:
    if not path.exists():
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def render_html(result: dict, lang: str) -> str:
    d = i18n(lang)
    grade = result["grade"]
    size = result["size"]
    size_txt = (f"{size['diameter_mm']} {d['unit.mm']}" if size["basis"] == "absolute"
                else f"{d['size.' + size['class']]} ({d['size.fill'].format(pct=size['frame_pct'])})")
    defects = "".join(
        f"<tr><td>{escape(d.get('defect.' + x['type'], x['type']))}</td><td>{x['confidence']:.2f}</td>"
        f"<td>{x['area_ratio'] * 100:.1f}%</td></tr>" for x in result["defects"]) or \
        f"<tr><td colspan='3'>{escape(d['result.no_defects'])}</td></tr>"
    reasons = "".join(f"<li>{escape(r['text'][lang])}</li>" for r in result["reasons"])
    note = f"<p class='note'>{escape(d['result.experimental_note'])}</p>" if result.get("experimental") else ""
    created = datetime.fromisoformat(result["created_at"]).strftime("%d %b %Y, %H:%M UTC")
    annotated = _img_data_uri(settings.outputs_dir / f"{result['id']}_annotated.jpg")
    font_uri = (settings.fonts_dir / "NotoSansDevanagari.ttf").as_uri()
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'NotoDeva'; src: url('{font_uri}'); font-weight: 100 900; }}
@page {{ size: A4; margin: 16mm 16mm 18mm; @bottom-center {{ content: counter(page); font-size: 9pt; color: #777; }} }}
body {{ font-family: 'NotoDeva', 'DejaVu Sans', Arial, sans-serif; color: #1b2a1f; font-size: 10.5pt; line-height: 1.5; }}
h1 {{ font-size: 20pt; margin: 0 0 2mm; color: #2f5d3a; }} h2 {{ font-size: 12pt; margin: 6mm 0 2mm; color: #2f5d3a; }}
.meta {{ color: #6b6b60; font-size: 9pt; }} .head {{ display: flex; justify-content: space-between; align-items: flex-start; }}
.badge {{ background: {GRADE_COLOR[grade]}; color: #fff; border-radius: 50%; width: 22mm; height: 22mm; text-align: center;
  font-size: 22pt; font-weight: 700; line-height: 22mm; }}
table {{ border-collapse: collapse; width: 100%; }} td, th {{ border-bottom: 1px solid #ddd5c3; padding: 1.6mm 2mm; text-align: left; vertical-align: top; }}
th {{ background: #f3eee3; font-weight: 600; }} .kv td:first-child {{ width: 38%; color: #6b6b60; }}
img {{ max-width: 100%; max-height: 105mm; object-fit: contain; border: 1px solid #ddd5c3; border-radius: 2mm; }}
.rec {{ background: #f3eee3; border-left: 3mm solid {GRADE_COLOR[grade]}; padding: 3mm 4mm; margin: 4mm 0; }}
.note {{ color: #8a4b00; background: #fff4e0; padding: 2mm 3mm; border-radius: 1.5mm; }}
.foot {{ margin-top: 8mm; font-size: 8.5pt; color: #6b6b60; border-top: 1px solid #ddd5c3; padding-top: 2mm; }}
</style></head><body>
<div class="head"><div><h1>{escape(d['report.title'])}</h1>
<div class="meta">{escape(d['report.id'])}: {result['id']} &middot; {escape(d['report.generated'])}: {created}</div></div>
<div class="badge">{grade}</div></div>
<div class="rec"><b>{escape(d['grade.' + grade])}</b><br>{escape(d['result.recommendation'])}: {escape(result['recommendation'][lang])}</div>
<p>{escape(result['explanation'][lang])}</p>{note}
<h2>{escape(d['report.summary'])}</h2>
<table class="kv"><tr><td>{escape(d['result.fruit'])}</td><td>{escape(d.get('fruit.' + result['fruit_type'], result['fruit_type']))}</td></tr>
<tr><td>{escape(d['result.ripeness'])}</td><td>{escape(d['ripeness.' + result['ripeness']['label']])} ({result['ripeness']['confidence']:.2f}, {escape(d['result.heuristic'])})</td></tr>
<tr><td>{escape(d['result.size'])}</td><td>{escape(size_txt)}</td></tr>
<tr><td>{escape(d['result.score'])}</td><td>{result['score']} / 100</td></tr>
<tr><td>{escape(d['result.uniformity'])}</td><td>{result['ripeness']['uniformity']:.2f}</td></tr>
<tr><td>{escape(d['result.shape'])}</td><td>{result['size']['circularity']:.2f}</td></tr></table>
<h2>{escape(d['result.defects'])}</h2>
<table><tr><th></th><th>{escape(d['result.confidence'])}</th><th>{escape(d['result.area'])}</th></tr>{defects}</table>
<h2>{escape(d['result.why'])}</h2><ul>{reasons}</ul>
<h2>{escape(d['report.annotated'])}</h2>{f'<img src="{annotated}">' if annotated else ''}
<div class="foot">{escape(d['footer.disclaimer'])}</div></body></html>"""


def render_pdf(result: dict, lang: str) -> bytes:
    lang = lang if lang in ("en", "hi") else "en"
    return HTML(string=render_html(result, lang), base_url=str(settings.fonts_dir)).write_pdf()
