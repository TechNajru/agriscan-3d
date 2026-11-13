import os
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="agriscan-test-")
os.environ["DATA_DIR"] = _tmp
os.environ["HISTORY_LIMIT"] = "3"
os.environ["DEFECT_MODEL_PATH"] = str(Path(_tmp) / "no-model.pt")       # force the experimental fallback
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest                                                          # noqa: E402
from fastapi.testclient import TestClient                              # noqa: E402


@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c
