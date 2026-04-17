"""
Compliance service — orchestrates the screening workflow, persists results,
and broadcasts real-time WebSocket updates.
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.order import Order
from app.models.compliance import ComplianceResult, AuditReport
from app.agents.orchestrator import ComplianceOrchestrator


# In-process WebSocket connection registry: order_id → set of WebSocket connections
_ws_connections: Dict[str, Set] = {}


def register_ws(order_id: str, websocket) -> None:
    _ws_connections.setdefault(order_id, set()).add(websocket)


def unregister_ws(order_id: str, websocket) -> None:
    conns = _ws_connections.get(order_id, set())
    conns.discard(websocket)


async def _broadcast(order_id: str, message: Dict[str, Any]) -> None:
    """Send a JSON message to all WebSocket listeners for an order."""
    conns = _ws_connections.get(order_id, set())
    dead = set()
    for ws in conns:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            dead.add(ws)
    for ws in dead:
        conns.discard(ws)


class ComplianceService:
    def __init__(self):
        self.orchestrator = ComplianceOrchestrator()

    async def screen_order(
        self, order: Order, db: AsyncSession
    ) -> Dict[str, Any]:
        """Run full compliance screening for an order and persist results."""

        # Update order status to SCREENING
        order.status = "SCREENING"
        order.updated_at = datetime.utcnow()
        db.add(order)
        await db.flush()

        await _broadcast(order.id, {
            "order_id": order.id,
            "status": "SCREENING",
            "message": "Compliance screening started",
            "timestamp": datetime.utcnow().isoformat(),
        })

        order_data = {
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "customer_country": order.customer_country,
            "customer_email": order.customer_email,
            "items": order.items if isinstance(order.items, list) else [],
            "total_amount": float(order.total_amount),
            "currency": order.currency,
        }

        async def progress_callback(agent: str, message: str, pct: float):
            await _broadcast(order.id, {
                "order_id": order.id,
                "status": "SCREENING",
                "agent": agent,
                "message": message,
                "progress": pct,
                "timestamp": datetime.utcnow().isoformat(),
            })

        try:
            result = await self.orchestrator.run_screening(order_data, progress_callback)
        except Exception as exc:
            order.status = "ERROR"
            order.updated_at = datetime.utcnow()
            db.add(order)
            await db.flush()
            await _broadcast(order.id, {
                "order_id": order.id,
                "status": "ERROR",
                "message": f"Screening error: {exc}",
                "timestamp": datetime.utcnow().isoformat(),
            })
            raise

        # Persist individual screening results
        compliance_records = []
        for sr in result["screening_results"]:
            cr = ComplianceResult(
                id=str(uuid.uuid4()),
                order_id=order.id,
                screening_type=sr["screening_type"],
                status=sr["status"],
                risk_score=sr["risk_score"],
                findings=sr,
            )
            db.add(cr)
            compliance_records.append(cr)

        # Persist audit report
        report_data = result["report"]
        audit_report = AuditReport(
            id=str(uuid.uuid4()),
            order_id=order.id,
            report_data=report_data,
            pdf_path=report_data.get("pdf_path"),
        )
        db.add(audit_report)

        # Update order status
        final_status = result["overall_status"]
        order.status = final_status
        order.updated_at = datetime.utcnow()
        db.add(order)
        await db.flush()

        await _broadcast(order.id, {
            "order_id": order.id,
            "status": final_status,
            "overall_risk_score": result["overall_risk_score"],
            "message": f"Screening complete — {final_status}",
            "timestamp": datetime.utcnow().isoformat(),
        })

        return result

    async def get_compliance_summary(
        self, order_id: str, db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Retrieve compliance results for an order."""
        order = await db.get(Order, order_id)
        if not order:
            return None

        cr_stmt = select(ComplianceResult).where(ComplianceResult.order_id == order_id)
        cr_result = await db.execute(cr_stmt)
        compliance_results = cr_result.scalars().all()

        ar_stmt = select(AuditReport).where(AuditReport.order_id == order_id)
        ar_result = await db.execute(ar_stmt)
        audit_report = ar_result.scalars().first()

        if not compliance_results:
            return None

        overall_risk = max((c.risk_score for c in compliance_results), default=0.0)
        statuses = [c.status for c in compliance_results]
        if "FAIL" in statuses:
            overall_status = "FAIL"
        elif "FLAG" in statuses:
            overall_status = "FLAG"
        else:
            overall_status = order.status

        return {
            "order_id": order_id,
            "order_number": order.order_number,
            "overall_status": overall_status,
            "overall_risk_score": overall_risk,
            "compliance_results": compliance_results,
            "audit_report": audit_report,
            "screened_at": min(c.created_at for c in compliance_results),
        }
