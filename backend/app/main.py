import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .core import pipeline
from .core.errors import PipelineError
from .routers import analyze
from .services import storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("agriscan")


@asynccontextmanager
async def lifespan(_: FastAPI):
    storage.init_db()
    pipeline.get_detector()          # load the model once at start-up
    yield


app = FastAPI(title="AgriScan 3D API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["GET", "POST", "DELETE"],
                   allow_headers=["*"], expose_headers=["Content-Disposition"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(PipelineError)
async def pipeline_error(_: Request, exc: PipelineError):
    return JSONResponse(status_code=exc.status, content={"detail": exc.detail()})


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    log.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": {"code": "server", "params": {}}})


app.include_router(analyze.router)
app.mount("/outputs", StaticFiles(directory=settings.outputs_dir), name="outputs")
