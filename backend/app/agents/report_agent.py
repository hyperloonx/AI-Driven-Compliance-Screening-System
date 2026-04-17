"""
Report Generation Agent — produces structured JSON and PDF audit reports.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.config import settings


class ReportAgent(BaseAgent):
    name = "ReportAgent"
    screening_type = "REPORT"

    async def screen(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """This agent doesn't screen — it generates; always returns PASS."""
        return self._build_result("PASS", 0.0, {}, [])

    async def generate_report(
        self,
        order_data: Dict[str, Any],
        screening_results: List[Dict[str, Any]],
        overall_status: str,
        overall_risk_score: float,
    ) -> Dict[str, Any]:
        """Generate a complete audit-ready report."""
        report = self._build_json_report(
            order_data, screening_results, overall_status, overall_risk_score
        )
        pdf_path = await self._generate_pdf(report)
        report["pdf_path"] = pdf_path
        return report

    # ------------------------------------------------------------------ #

    def _build_json_report(
        self,
        order_data: Dict[str, Any],
        screening_results: List[Dict[str, Any]],
        overall_status: str,
        overall_risk_score: float,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()

        all_flags: List[str] = []
        for result in screening_results:
            all_flags.extend(result.get("flags", []))

        recommendations = self._build_recommendations(overall_status, overall_risk_score, all_flags)

        return {
            "report_version": "1.0",
            "generated_at": now.isoformat(),
            "report_id": f"RPT-{now.strftime('%Y%m%d%H%M%S')}",
            "order": {
                "order_id": order_data.get("id", ""),
                "order_number": order_data.get("order_number", ""),
                "customer_name": order_data.get("customer_name", ""),
                "customer_country": order_data.get("customer_country", ""),
                "customer_email": order_data.get("customer_email", ""),
                "total_amount": order_data.get("total_amount", 0),
                "currency": order_data.get("currency", "USD"),
                "items_count": len(order_data.get("items", [])),
            },
            "compliance_summary": {
                "overall_status": overall_status,
                "overall_risk_score": round(overall_risk_score, 4),
                "total_flags": len(all_flags),
                "flags": all_flags,
            },
            "screening_results": screening_results,
            "recommendations": recommendations,
            "audit_trail": {
                "screened_by": "AI-Driven Compliance Screening System v1.0",
                "screening_mode": settings.AGENT_MODE,
                "timestamp": now.isoformat(),
                "agents_used": [r.get("agent", "") for r in screening_results],
            },
        }

    def _build_recommendations(
        self, status: str, risk_score: float, flags: List[str]
    ) -> List[str]:
        recs = []
        if status == "FAIL":
            recs.append("BLOCK order — immediately escalate to Compliance Officer.")
            recs.append("Do not process payment or ship goods until review is complete.")
            recs.append("File Suspicious Activity Report (SAR) if required by regulation.")
        elif status == "FLAG":
            recs.append("HOLD order pending enhanced due diligence review.")
            recs.append("Request additional KYC documentation from customer.")
            if risk_score > 0.6:
                recs.append("Consider filing SAR with relevant financial intelligence unit.")
        else:
            recs.append("Order cleared — proceed with normal processing.")
            recs.append("Retain this report for 5 years per record-keeping requirements.")

        if any("OFAC" in f or "sanctions" in f.lower() for f in flags):
            recs.append("Review OFAC obligations and potential penalties before any action.")
        if any("export" in f.lower() or "ITAR" in f or "EAR" in f for f in flags):
            recs.append("Consult export control legal counsel before shipping.")

        return recs

    async def _generate_pdf(self, report: Dict[str, Any]) -> Optional[str]:
        """Generate a PDF version of the compliance report."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            )
        except ImportError:
            return None

        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        report_id = report.get("report_id", "REPORT")
        pdf_filename = f"{report_id}.pdf"
        pdf_path = os.path.join(settings.REPORTS_DIR, pdf_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        story = []

        # ---- Title ----
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1a365d")
        )
        story.append(Paragraph("AI-Driven Compliance Screening Report", title_style))
        story.append(Spacer(1, 0.1 * inch))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a365d")))
        story.append(Spacer(1, 0.15 * inch))

        # ---- Report metadata ----
        meta_data = [
            ["Report ID:", report.get("report_id", "")],
            ["Generated At:", report.get("generated_at", "")],
            ["Screening Mode:", report["audit_trail"]["screening_mode"]],
        ]
        meta_table = Table(meta_data, colWidths=[1.8 * inch, 4.5 * inch])
        meta_table.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.2 * inch))

        # ---- Overall status banner ----
        status = report["compliance_summary"]["overall_status"]
        status_color = {
            "PASS": colors.HexColor("#22543d"),
            "FLAG": colors.HexColor("#7b341e"),
            "FAIL": colors.HexColor("#63171b"),
        }.get(status, colors.grey)

        status_bg = {
            "PASS": colors.HexColor("#c6f6d5"),
            "FLAG": colors.HexColor("#feebc8"),
            "FAIL": colors.HexColor("#fed7d7"),
        }.get(status, colors.lightgrey)

        status_style = ParagraphStyle(
            "Status",
            parent=styles["Normal"],
            fontSize=14,
            textColor=status_color,
            backColor=status_bg,
            borderPad=6,
            borderRadius=4,
            spaceAfter=4,
        )
        risk_score = report["compliance_summary"]["overall_risk_score"]
        story.append(
            Paragraph(
                f"Overall Status: <b>{status}</b> — Risk Score: <b>{risk_score:.2f}</b>",
                status_style,
            )
        )
        story.append(Spacer(1, 0.2 * inch))

        # ---- Order details ----
        story.append(Paragraph("Order Details", styles["Heading2"]))
        order = report["order"]
        order_data_table = [
            ["Order Number:", order.get("order_number", "")],
            ["Customer Name:", order.get("customer_name", "")],
            ["Customer Country:", order.get("customer_country", "")],
            ["Customer Email:", order.get("customer_email", "")],
            ["Total Amount:", f"{order.get('currency', 'USD')} {order.get('total_amount', 0):,.2f}"],
        ]
        t = Table(order_data_table, colWidths=[1.8 * inch, 4.5 * inch])
        t.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

        # ---- Flags ----
        flags = report["compliance_summary"].get("flags", [])
        if flags:
            story.append(Paragraph("Compliance Flags", styles["Heading2"]))
            flag_style = ParagraphStyle("Flag", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#742a2a"))
            for flag in flags:
                story.append(Paragraph(f"⚠ {flag}", flag_style))
            story.append(Spacer(1, 0.2 * inch))

        # ---- Screening results summary ----
        story.append(Paragraph("Screening Results", styles["Heading2"]))
        headers = ["Agent", "Type", "Status", "Risk Score"]
        rows = [headers]
        for r in report["screening_results"]:
            rows.append([
                r.get("agent", ""),
                r.get("screening_type", ""),
                r.get("status", ""),
                f"{r.get('risk_score', 0):.2f}",
            ])
        sr_table = Table(rows, colWidths=[1.8 * inch, 1.8 * inch, 1.3 * inch, 1.4 * inch])
        sr_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
            ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(sr_table)
        story.append(Spacer(1, 0.2 * inch))

        # ---- Recommendations ----
        story.append(Paragraph("Recommendations", styles["Heading2"]))
        rec_style = ParagraphStyle("Rec", parent=styles["Normal"], fontSize=9)
        for i, rec in enumerate(report.get("recommendations", []), 1):
            story.append(Paragraph(f"{i}. {rec}", rec_style))
        story.append(Spacer(1, 0.2 * inch))

        # ---- Audit trail ----
        story.append(Paragraph("Audit Trail", styles["Heading2"]))
        audit = report["audit_trail"]
        at_data = [
            ["Screened By:", audit.get("screened_by", "")],
            ["Timestamp:", audit.get("timestamp", "")],
            ["Agents Used:", ", ".join(audit.get("agents_used", []))],
        ]
        at_table = Table(at_data, colWidths=[1.8 * inch, 4.5 * inch])
        at_table.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ]))
        story.append(at_table)

        doc.build(story)
        return pdf_path
