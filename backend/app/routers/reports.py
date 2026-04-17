"""
Reports router — list reports, retrieve individual reports, and download PDFs.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.compliance import AuditReport
from app.schemas.compliance import AuditReportResponse, ReportListResponse

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all audit reports."""
    stmt = select(AuditReport).order_by(AuditReport.created_at.desc()).offset(skip).limit(limit)
    count_stmt = select(func.count()).select_from(AuditReport)

    result = await db.execute(stmt)
    reports = result.scalars().all()

    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    return {"total": total, "reports": reports}


@router.get("/{report_id}", response_model=AuditReportResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific audit report by ID."""
    report = await db.get(AuditReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """Download the PDF version of an audit report."""
    report = await db.get(AuditReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_path = report.pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not available for this report")

    filename = os.path.basename(pdf_path)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )
