import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import basic_auth_dependency
from app.core.settings import settings
from app.db.models import Report, ReportRun, Transmission
from app.db.session import get_session

logger = logging.getLogger(__name__)
router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parents[2] / "templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, _=Depends(basic_auth_dependency), session: AsyncSession = Depends(get_session)):
    reports = await session.exec(select(Report).order_by(Report.created_at.desc()).limit(50))
    items = []
    for rep in reports:
        stats = {}
        if rep.latest_run_id:
            run = await session.get(ReportRun, rep.latest_run_id)
            if run:
                stats = json.loads(run.stats_json)
        items.append({"report": rep, "stats": stats})
    return templates.TemplateResponse("dashboard.html", {"request": request, "reports": items})


@router.get("/dashboard/reports/{report_id}", response_class=HTMLResponse)
async def report_detail(
    report_id: str,
    request: Request,
    _=Depends(basic_auth_dependency),
    session: AsyncSession = Depends(get_session),
):
    report = await session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report introuvable")
    run = None
    stats = {}
    transmissions = []
    if report.latest_run_id:
        run = await session.get(ReportRun, report.latest_run_id)
        if run:
            stats = json.loads(run.stats_json)
            rows = await session.exec(select(Transmission).where(Transmission.report_run_id == run.id))
            transmissions = rows.all()
    return templates.TemplateResponse(
        "report_detail.html",
        {
            "request": request,
            "report": report,
            "run": run,
            "stats": stats,
            "transmissions": transmissions[:200],
        },
    )


@router.get("/r/{public_token}", response_class=HTMLResponse)
async def mobile_view(public_token: str, request: Request, session: AsyncSession = Depends(get_session)):
    report = await session.exec(select(Report).where(Report.public_token == public_token))
    report = report.first()
    if not report:
        raise HTTPException(status_code=404, detail="Token invalide")
    if not settings.public_qr_allowed:
        await basic_auth_dependency()
    stats = {}
    if report.latest_run_id:
        run = await session.get(ReportRun, report.latest_run_id)
        if run:
            stats = json.loads(run.stats_json)
    return templates.TemplateResponse(
        "mobile.html",
        {"request": request, "stats": stats, "report": report},
    )


@router.get("/q/{public_token}.png")
async def qr_image(public_token: str):
    path = settings.qrcodes_dir / f"{public_token}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="QR introuvable")
    return FileResponse(path)
