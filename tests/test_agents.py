"""Tests for individual compliance agents."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.sanctions_agent import SanctionsAgent
from app.agents.aml_agent import AMLAgent
from app.agents.regulatory_agent import RegulatoryAgent
from app.agents.report_agent import ReportAgent
from app.agents.orchestrator import ComplianceOrchestrator


# ------------------------------------------------------------------ #
# Sanctions Agent
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_sanctions_agent_pass(sample_order):
    agent = SanctionsAgent()
    result = await agent.screen(sample_order)
    assert result["screening_type"] == "SANCTIONS"
    assert result["status"] == "PASS"
    assert result["risk_score"] < 0.4


@pytest.mark.asyncio
async def test_sanctions_agent_fail_on_sdl(sanctioned_order):
    agent = SanctionsAgent()
    result = await agent.screen(sanctioned_order)
    assert result["screening_type"] == "SANCTIONS"
    assert result["status"] in ("FLAG", "FAIL")
    assert result["risk_score"] >= 0.4
    assert len(result["flags"]) > 0


@pytest.mark.asyncio
async def test_sanctions_agent_restricted_country():
    agent = SanctionsAgent()
    order = {
        "customer_name": "Generic Customer",
        "customer_country": "Iran",
        "customer_email": "test@test.ir",
        "items": [],
        "total_amount": 100.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert result["risk_score"] > 0.0
    assert any("Iran" in f or "iran" in f.lower() or "Restricted" in f for f in result["flags"])


@pytest.mark.asyncio
async def test_sanctions_pep_match():
    agent = SanctionsAgent()
    order = {
        "customer_name": "Vladimir Putin",
        "customer_country": "Russia",
        "customer_email": "vp@kremlin.ru",
        "items": [],
        "total_amount": 1000.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert result["risk_score"] >= 0.4


# ------------------------------------------------------------------ #
# AML Agent
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_aml_agent_clean_order(sample_order):
    agent = AMLAgent()
    result = await agent.screen(sample_order)
    assert result["screening_type"] == "AML_KYC"
    assert result["status"] == "PASS"


@pytest.mark.asyncio
async def test_aml_agent_structuring_detection():
    agent = AMLAgent()
    order = {
        "customer_name": "Jane Doe",
        "customer_country": "United States",
        "customer_email": "jane@example.com",
        "items": [],
        "total_amount": 9_500.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert result["risk_score"] >= 0.4
    assert any("structuring" in f.lower() or "9" in f for f in result["flags"])


@pytest.mark.asyncio
async def test_aml_agent_incomplete_kyc():
    agent = AMLAgent()
    order = {
        "customer_name": "X",
        "customer_country": "",
        "customer_email": "bademail",
        "items": [],
        "total_amount": 100.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert result["risk_score"] > 0.0
    assert len(result["flags"]) > 0


@pytest.mark.asyncio
async def test_aml_agent_high_risk_country():
    agent = AMLAgent()
    order = {
        "customer_name": "Ali Hassan",
        "customer_country": "Afghanistan",
        "customer_email": "a@test.af",
        "items": [],
        "total_amount": 500.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert result["risk_score"] > 0.0


# ------------------------------------------------------------------ #
# Regulatory Agent
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_regulatory_agent_clean(sample_order):
    agent = RegulatoryAgent()
    result = await agent.screen(sample_order)
    assert result["screening_type"] == "REGULATORY"
    assert result["status"] == "PASS"


@pytest.mark.asyncio
async def test_regulatory_agent_export_control():
    agent = RegulatoryAgent()
    order = {
        "customer_name": "Bob Builder",
        "customer_country": "North Korea",
        "customer_email": "bob@dprk.kp",
        "items": [
            {
                "product_id": "P1",
                "product_name": "Missile guidance system",
                "quantity": 1,
                "unit_price": 50000.0,
                "category": "AEROSPACE",
            }
        ],
        "total_amount": 50000.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert result["risk_score"] >= 0.7
    assert result["status"] in ("FLAG", "FAIL")


@pytest.mark.asyncio
async def test_regulatory_agent_hs_code():
    agent = RegulatoryAgent()
    order = {
        "customer_name": "Alice",
        "customer_country": "Germany",
        "customer_email": "alice@de.com",
        "items": [
            {
                "product_id": "P2",
                "product_name": "Electronic Component",
                "quantity": 100,
                "unit_price": 5.0,
                "category": "ELECTRONICS",
                "hs_code": "9301",
            }
        ],
        "total_amount": 500.0,
        "currency": "USD",
    }
    result = await agent.screen(order)
    assert any("9301" in f for f in result["flags"])


# ------------------------------------------------------------------ #
# Orchestrator
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_orchestrator_clean_order(sample_order):
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(sample_order)
    assert "overall_status" in result
    assert "overall_risk_score" in result
    assert "screening_results" in result
    assert len(result["screening_results"]) == 3
    assert "report" in result


@pytest.mark.asyncio
async def test_orchestrator_sanctioned_order(sanctioned_order):
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(sanctioned_order)
    assert result["overall_status"] in ("FLAG", "FAIL")
    assert result["overall_risk_score"] >= 0.4


@pytest.mark.asyncio
async def test_orchestrator_high_risk(high_risk_order):
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(high_risk_order)
    assert result["overall_status"] in ("FLAG", "FAIL")
