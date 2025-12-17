import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import basic_auth_dependency
from app.core.settings import settings
from app.db.models import Report, ReportRun, Transmission
from app.db.session import get_session
from app.services.analyzer import AnalyzerService
from app.services.importer import FileImporterService, ImportErrorDetail
from app.services.qr import generate_qr

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    _=Depends(basic_auth_dependency),
    session: AsyncSession = Depends(get_session),
):
    temp_path = Path("/tmp") / file.filename
    contents = await file.read()
    temp_path.write_bytes(contents)

    importer = FileImporterService()
    checksum = importer.compute_checksum(temp_path)

    if not settings.allow_duplicates:
        existing = await session.exec(select(Report).where(Report.checksum == checksum))
        if existing.first():
            raise HTTPException(status_code=409, detail="Fichier déjà importé")

    try:
        records, meta = importer.import_file(temp_path)
    except ImportErrorDetail as e:
        raise e
    finally:
        await file.close()

    report = Report(
        filename=file.filename,
        checksum=checksum,
        original_path="",
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)

    stored = importer.save_original(temp_path, report.id, Path(file.filename).suffix)
    report.original_path = str(stored)
    session.add(report)
    await session.commit()

    analyzer = AnalyzerService(records)
    stats = analyzer.compute_stats()

    run = ReportRun(
        report_id=report.id,
        stats_json=AnalyzerService.stats_json(stats),
        error_summary=json.dumps(stats.get("top_error_codes", []), ensure_ascii=False),
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    report.latest_run_id = run.id
    session.add(report)
    await session.commit()

    trans_rows = [
        Transmission(report_run_id=run.id, **row) for row in records  # type: ignore[arg-type]
    ]
    session.add_all(trans_rows)
    await session.commit()

    qr_path = generate_qr(report.public_token)

    return {
        "report_id": report.id,
        "run_id": run.id,
        "stats": stats,
        "public_token": report.public_token,
        "qr_path": str(qr_path),
        "meta": meta,
    }


@router.get("")
async def list_reports(
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[str] = None,
    has_errors: Optional[bool] = None,
    date_min: Optional[str] = None,
    date_max: Optional[str] = None,
    _=Depends(basic_auth_dependency),
    session: AsyncSession = Depends(get_session),
):
    query = select(Report).order_by(Report.created_at.desc()).offset(offset).limit(limit)
    results = await session.exec(query)
    reports = results.all()

    payload = []
    for rep in reports:
        stats = {}
        if rep.latest_run_id:
            run = await session.get(ReportRun, rep.latest_run_id)
            if run:
                stats = json.loads(run.stats_json)
        payload.append(
            {
                "id": rep.id,
                "filename": rep.filename,
                "created_at": rep.created_at,
                "public_token": rep.public_token,
                "stats": stats,
            }
        )
    return {"items": payload, "limit": limit, "offset": offset}


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    _=Depends(basic_auth_dependency),
    session: AsyncSession = Depends(get_session),
):
    report = await session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report introuvable")
    run = None
    stats = {}
    if report.latest_run_id:
        run = await session.get(ReportRun, report.latest_run_id)
        if run:
            stats = json.loads(run.stats_json)
    return {
        "report": report,
        "latest_run": run,
        "stats": stats,
        "qr_url": f"/q/{report.public_token}.png",
        "mobile_url": f"/r/{report.public_token}",
    }


@router.get("/{report_id}/download")
async def download_original(
    report_id: str,
    _=Depends(basic_auth_dependency),
    session: AsyncSession = Depends(get_session),
):
    report = await session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report introuvable")
    if not report.original_path or not Path(report.original_path).exists():
        raise HTTPException(status_code=404, detail="Fichier original introuvable")
    return FileResponse(path=report.original_path, filename=Path(report.original_path).name)


@router.get("/{report_id}/export.json")
async def export_json(
    report_id: str,
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
    return {"report": report, "run": run, "stats": stats, "transmissions": transmissions}
