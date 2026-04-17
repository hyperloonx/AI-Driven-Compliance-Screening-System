"""Tests for the compliance screening workflow and data sources."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.data_sources import (
    check_ofac_sdn,
    check_un_sanctions,
    check_eu_sanctions,
    check_pep_list,
    check_country_risk,
    check_hs_code,
    check_industry_risk,
)


# ------------------------------------------------------------------ #
# Data source tests
# ------------------------------------------------------------------ #

def test_ofac_sdn_match():
    result = check_ofac_sdn("Viktor Antonov")
    assert result["matched"] is True
    assert result["risk_score"] == 1.0
    assert len(result["matches"]) > 0


def test_ofac_sdn_alias_match():
    result = check_ofac_sdn("Victor Antonov")
    assert result["matched"] is True


def test_ofac_sdn_no_match():
    result = check_ofac_sdn("John Smith")
    assert result["matched"] is False
    assert result["risk_score"] == 0.0


def test_un_sanctions_match():
    result = check_un_sanctions("Al-Qaida")
    assert result["matched"] is True


def test_un_sanctions_alias():
    result = check_un_sanctions("Daesh")
    assert result["matched"] is True


def test_eu_sanctions_match():
    result = check_eu_sanctions("Wagner Group")
    assert result["matched"] is True


def test_pep_match():
    result = check_pep_list("Kim Jong-un")
    assert result["matched"] is True
    assert result["risk_score"] >= 0.7


def test_pep_no_match():
    result = check_pep_list("Regular Person")
    assert result["matched"] is False
    assert result["risk_score"] == 0.0


def test_country_risk_iran():
    result = check_country_risk("IR")
    assert result["restricted"] is True
    assert result["risk_score"] == 1.0


def test_country_risk_safe():
    result = check_country_risk("DE")  # Germany
    assert result["restricted"] is False
    assert result["risk_score"] == 0.0


def test_hs_code_controlled():
    result = check_hs_code("9301")
    assert result["controlled"] is True
    assert result["risk_score"] == 0.8


def test_hs_code_not_controlled():
    result = check_hs_code("1234")
    assert result["controlled"] is False


def test_industry_risk_weapons():
    result = check_industry_risk("WEAPONS")
    assert result["restricted"] is True
    assert result["risk_score"] == 1.0


def test_industry_risk_normal():
    result = check_industry_risk("CLOTHING")
    assert result["restricted"] is False


# ------------------------------------------------------------------ #
# End-to-end screening workflow
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_full_screening_clean_order(sample_order):
    from app.agents.orchestrator import ComplianceOrchestrator
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(sample_order)

    assert result["overall_status"] == "PASS"
    assert result["overall_risk_score"] < 0.4
    assert result["report"] is not None
    assert result["report"]["order"]["customer_name"] == sample_order["customer_name"]


@pytest.mark.asyncio
async def test_full_screening_sanctioned(sanctioned_order):
    from app.agents.orchestrator import ComplianceOrchestrator
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(sanctioned_order)

    assert result["overall_status"] in ("FLAG", "FAIL")
    assert result["overall_risk_score"] >= 0.4


@pytest.mark.asyncio
async def test_report_contains_required_fields(sample_order):
    from app.agents.orchestrator import ComplianceOrchestrator
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(sample_order)

    report = result["report"]
    assert "report_id" in report
    assert "generated_at" in report
    assert "order" in report
    assert "compliance_summary" in report
    assert "screening_results" in report
    assert "recommendations" in report
    assert "audit_trail" in report


@pytest.mark.asyncio
async def test_report_recommendations_for_fail(sanctioned_order):
    from app.agents.orchestrator import ComplianceOrchestrator
    orch = ComplianceOrchestrator()
    result = await orch.run_screening(sanctioned_order)
    recs = result["report"].get("recommendations", [])
    assert len(recs) > 0
