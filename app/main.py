from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import reports, views
from app.core.auth import basic_auth_dependency
from app.core.logging import setup_logging
from app.core.settings import settings
from app.db.session import create_db_and_tables, get_engine_url, init_async_engine
from app.services.watcher import start_watcher, stop_watcher


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_logging()
    await create_db_and_tables()
    await start_watcher()
    yield
    await stop_watcher()


app = FastAPI(
    title=settings.app_name,
    description="Plateforme locale d'analyse d'exports FaxCloud",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=[],
)

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(views.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, _=Depends(basic_auth_dependency)):
    return templates.TemplateResponse("redirect.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "engine": get_engine_url()}
