import asyncio
import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from ..config import fruit_profiles, grading_rules, settings
from ..core import pipeline
from ..core.errors import PipelineError
from ..services import reports, storage

router = APIRouter(prefix="/api")
_slots = asyncio.Semaphore(settings.max_concurrent)
SIGNATURES = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")


def _err(status: int, code: str, **params):
    return HTTPException(status, {"code": code, "params": params})


def _is_image_signature(data: bytes) -> bool:
    return data.startswith(SIGNATURES) or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")


async def read_upload(f: UploadFile) -> np.ndarray:
    """Validate by size, real file signature and successful decoding (never trust the extension)."""
    data = await f.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise _err(413, "file_too_large", max=round(settings.max_upload_bytes / 1048576))
    if not _is_image_signature(data):
        raise _err(400, "invalid_file")
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)   # honours EXIF rotation
    if img is None:
        raise _err(400, "invalid_file")
    if img.shape[0] * img.shape[1] > settings.max_pixels:
        raise _err(413, "too_many_pixels")
    return img


def with_urls(result: dict) -> dict:
    i = result["id"]
    return {**result, "original_url": f"/outputs/{i}_orig.jpg", "annotated_url": f"/outputs/{i}_annotated.jpg"}


def _run(img, fruit, ref):
    result, processed = pipeline.analyze_image(img, fruit, ref)
    analysis_id = storage.save_analysis(result)
    cv2.imwrite(str(settings.outputs_dir / f"{analysis_id}_orig.jpg"), processed, [cv2.IMWRITE_JPEG_QUALITY, 90])
    cv2.imwrite(str(settings.outputs_dir / f"{analysis_id}_annotated.jpg"), pipeline.annotate(processed, result),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    return storage.get_analysis(analysis_id)


@router.post("/analyze")
async def analyze(image: UploadFile = File(...), fruit: str = Form("apple"),
                  reference_width_mm: float | None = Form(None)):
    if fruit not in fruit_profiles():
        raise _err(400, "invalid_file")
    ref = reference_width_mm if reference_width_mm and 20 <= reference_width_mm <= 400 else None
    img = await read_upload(image)
    try:
        await asyncio.wait_for(_slots.acquire(), timeout=20)
    except asyncio.TimeoutError:
        raise _err(503, "busy")
    try:
        result = await run_in_threadpool(_run, img, fruit, ref)
    except PipelineError:
        raise
    finally:
        _slots.release()
    return with_urls(result)


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    result = storage.get_analysis(analysis_id)
    if not result:
        raise _err(404, "not_found")
    return with_urls(result)


@router.delete("/analysis/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: str):
    if not storage.delete_analysis(analysis_id):
        raise _err(404, "not_found")
    return Response(status_code=204)


@router.get("/analysis/{analysis_id}/report.pdf")
def report(analysis_id: str, lang: str = "en"):
    result = storage.get_analysis(analysis_id)
    if not result:
        raise _err(404, "not_found")
    pdf = reports.render_pdf(result, lang)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="agriscan-{analysis_id}-{lang}.pdf"'})


@router.get("/history")
def history():
    return {"limit": settings.history_limit, "items": storage.list_history()}


@router.get("/config")
def config():
    return {"fruits": [{"id": k, "label": v["label"]} for k, v in fruit_profiles().items()],
            "max_upload_mb": round(settings.max_upload_bytes / 1048576),
            "history_limit": settings.history_limit,
            "experimental_defects": pipeline.get_detector().experimental,
            "reference_card_mm": 85.6, "rules": {k: v for k, v in grading_rules().items() if k != "fallback_detector"}}


@router.get("/health")
def health():
    return {"status": "ok", "defect_model_loaded": not pipeline.get_detector().experimental}
