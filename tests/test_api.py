"""Tests for API endpoints."""
import asyncio
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["mode"] == "RULE_BASED"


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()


@pytest.mark.asyncio
async def test_create_order(client, sample_order):
    resp = await client.post("/api/v1/orders", json=sample_order)
    assert resp.status_code == 201
    data = resp.json()
    assert data["order_number"].startswith("ORD-")
    assert data["status"] == "PENDING"
    assert data["customer_name"] == sample_order["customer_name"]


@pytest.mark.asyncio
async def test_create_order_invalid_email(client):
    order = {
        "customer_name": "Test User",
        "customer_country": "US",
        "customer_email": "not-an-email",
        "items": [{"product_id": "P1", "product_name": "Item", "quantity": 1, "unit_price": 10}],
        "total_amount": 10.0,
        "currency": "USD",
    }
    # Schema uses EmailStr, so invalid emails are rejected with 422
    resp = await client.post("/api/v1/orders", json=order)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_orders(client, sample_order):
    await client.post("/api/v1/orders", json=sample_order)
    resp = await client.get("/api/v1/orders")
    assert resp.status_code == 200
    data = resp.json()
    assert "orders" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_order_not_found(client):
    resp = await client.get("/api/v1/orders/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_order(client, sample_order):
    create_resp = await client.post("/api/v1/orders", json=sample_order)
    order_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


@pytest.mark.asyncio
async def test_list_reports(client):
    resp = await client.get("/api/v1/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert "reports" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_report_not_found(client):
    resp = await client.get("/api/v1/reports/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_order_status_filter(client, sample_order):
    await client.post("/api/v1/orders", json=sample_order)
    resp = await client.get("/api/v1/orders?status=PENDING")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["orders"], list)
