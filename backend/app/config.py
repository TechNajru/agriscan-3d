"""Runtime settings (environment variables) and editable rule files (JSON)."""
import json
import os
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # backend/
ROOT = BASE.parent                                      # repository root


class Settings:
    def __init__(self):
        self.data_dir = Path(os.getenv("DATA_DIR", BASE / "data"))
        self.db_path = Path(os.getenv("DB_PATH", self.data_dir / "agriscan.db"))
        self.outputs_dir = Path(os.getenv("OUTPUTS_DIR", self.data_dir / "outputs"))
        self.config_dir = Path(os.getenv("CONFIG_DIR", BASE / "config"))
        self.i18n_dir = Path(os.getenv("I18N_DIR", ROOT / "i18n"))
        self.fonts_dir = Path(os.getenv("FONTS_DIR", BASE / "assets" / "fonts"))
        self.defect_model_path = os.getenv("DEFECT_MODEL_PATH", str(BASE / "models" / "defect.pt"))
        self.max_upload_bytes = int(float(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024)
        self.max_pixels = int(os.getenv("MAX_PIXELS", "40000000"))
        self.process_max_side = int(os.getenv("PROCESS_MAX_SIDE", "1280"))
        self.history_limit = int(os.getenv("HISTORY_LIMIT", "10"))
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_ANALYSES", "2"))
        self.cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()


@lru_cache(maxsize=1)
def grading_rules() -> dict:
    return json.loads((settings.config_dir / "grading.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def fruit_profiles() -> dict:
    return json.loads((settings.config_dir / "fruits.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def i18n(lang: str) -> dict:
    lang = lang if lang in ("en", "hi") else "en"
    return json.loads((settings.i18n_dir / f"{lang}.json").read_text(encoding="utf-8"))
