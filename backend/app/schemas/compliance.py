"""Pydantic schemas for compliance results and reports."""
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


class ComplianceResultResponse(BaseModel):
    id: str
    order_id: str
    screening_type: str
    status: str
    risk_score: float
    findings: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditReportResponse(BaseModel):
    id: str
    order_id: str
    report_data: Dict[str, Any]
    pdf_path: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplianceSummary(BaseModel):
    order_id: str
    order_number: str
    overall_status: str
    overall_risk_score: float
    screening_results: List[ComplianceResultResponse]
    audit_report: Optional[AuditReportResponse]
    screened_at: datetime


class ReportListResponse(BaseModel):
    total: int
    reports: List[AuditReportResponse]


class ScreeningStatusUpdate(BaseModel):
    order_id: str
    status: str
    message: str
    agent: Optional[str] = None
    risk_score: Optional[float] = None
    timestamp: datetime
