"""
Orders router — submit orders for screening, list/retrieve orders,
and provide a WebSocket endpoint for real-time screening updates.
"""
import uuid
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.schemas.compliance import ComplianceSummary, ComplianceResultResponse, AuditReportResponse
from app.services.compliance_service import ComplianceService, register_ws, unregister_ws

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
compliance_service = ComplianceService()


def _generate_order_number() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    suffix = str(uuid.uuid4())[:6].upper()
    return f"ORD-{ts}-{suffix}"


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Submit a new order for compliance screening."""
    order = Order(
        id=str(uuid.uuid4()),
        order_number=_generate_order_number(),
        customer_name=order_in.customer_name,
        customer_country=order_in.customer_country,
        customer_email=order_in.customer_email,
        items=[item.model_dump() for item in order_in.items],
        total_amount=order_in.total_amount,
        currency=order_in.currency,
        status="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    await db.flush()

    # Run screening asynchronously so response is immediate
    async def run_screening():
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as bg_session:
            bg_order = await bg_session.get(Order, order.id)
            if bg_order:
                await compliance_service.screen_order(bg_order, bg_session)
                await bg_session.commit()

    background_tasks.add_task(run_screening)
    return order


@router.get("", response_model=OrderListResponse)
async def list_orders(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all orders with optional status filter."""
    stmt = select(Order)
    if status:
        stmt = stmt.where(Order.status == status.upper())
    stmt = stmt.order_by(Order.created_at.desc()).offset(skip).limit(limit)

    count_stmt = select(func.count()).select_from(Order)
    if status:
        count_stmt = count_stmt.where(Order.status == status.upper())

    result = await db.execute(stmt)
    orders = result.scalars().all()

    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    return {"total": total, "orders": orders}


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific order by ID."""
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/compliance", response_model=ComplianceSummary)
async def get_order_compliance(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get the compliance result for a specific order."""
    summary = await compliance_service.get_compliance_summary(order_id, db)
    if not summary:
        raise HTTPException(status_code=404, detail="Compliance results not found for this order")

    results = [
        ComplianceResultResponse.model_validate(cr)
        for cr in summary["compliance_results"]
    ]
    audit = (
        AuditReportResponse.model_validate(summary["audit_report"])
        if summary["audit_report"]
        else None
    )

    return ComplianceSummary(
        order_id=summary["order_id"],
        order_number=summary["order_number"],
        overall_status=summary["overall_status"],
        overall_risk_score=summary["overall_risk_score"],
        screening_results=results,
        audit_report=audit,
        screened_at=summary["screened_at"],
    )


@router.websocket("/ws/{order_id}")
async def websocket_order_updates(websocket: WebSocket, order_id: str):
    """WebSocket endpoint for real-time screening status updates."""
    await websocket.accept()
    register_ws(order_id, websocket)
    try:
        while True:
            # Keep alive — client can send pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        unregister_ws(order_id, websocket)
