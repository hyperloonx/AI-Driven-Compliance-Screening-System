"""Pytest configuration and shared fixtures."""
import asyncio
import sys
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Use SQLite in-memory for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_compliance.db"
os.environ["AGENT_MODE"] = "RULE_BASED"
os.environ["REPORTS_DIR"] = "test_reports"


@pytest_asyncio.fixture(scope="session")
async def app():
    """Create the FastAPI app with tables initialised."""
    from app.main import app as fastapi_app
    from app.database import create_tables
    await create_tables()
    yield fastapi_app


@pytest_asyncio.fixture
async def client(app):
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_order():
    return {
        "customer_name": "John Smith",
        "customer_country": "United States",
        "customer_email": "john.smith@example.com",
        "items": [
            {
                "product_id": "PRD-001",
                "product_name": "Office Supplies Pack",
                "quantity": 10,
                "unit_price": 25.00,
                "category": "OFFICE",
            }
        ],
        "total_amount": 250.00,
        "currency": "USD",
    }


@pytest.fixture
def sanctioned_order():
    return {
        "customer_name": "Viktor Antonov",
        "customer_country": "Russia",
        "customer_email": "v.antonov@test.ru",
        "items": [
            {
                "product_id": "PRD-002",
                "product_name": "Electronic Components",
                "quantity": 5,
                "unit_price": 1000.00,
                "category": "ELECTRONICS",
            }
        ],
        "total_amount": 5000.00,
        "currency": "USD",
    }


@pytest.fixture
def high_risk_order():
    return {
        "customer_name": "Test Customer",
        "customer_country": "Iran",
        "customer_email": "test@domain.ir",
        "items": [
            {
                "product_id": "PRD-003",
                "product_name": "Cryptography Software",
                "quantity": 1,
                "unit_price": 9500.00,
                "category": "SOFTWARE",
                "hs_code": "8542",
            }
        ],
        "total_amount": 9500.00,
        "currency": "USD",
    }
