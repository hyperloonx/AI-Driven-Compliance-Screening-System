"""
Master orchestrator — runs all agents, aggregates results, calculates
overall risk score, and triggers report generation.
"""
import asyncio
from typing import Dict, Any, List, Callable, Optional

from app.agents.sanctions_agent import SanctionsAgent
from app.agents.aml_agent import AMLAgent
from app.agents.regulatory_agent import RegulatoryAgent
from app.agents.report_agent import ReportAgent


class ComplianceOrchestrator:
    """Runs all compliance agents and aggregates their results."""

    def __init__(self):
        self.sanctions_agent = SanctionsAgent()
        self.aml_agent = AMLAgent()
        self.regulatory_agent = RegulatoryAgent()
        self.report_agent = ReportAgent()

    async def run_screening(
        self,
        order_data: Dict[str, Any],
        progress_callback: Optional[Callable[[str, str, float], None]] = None,
    ) -> Dict[str, Any]:
        """
        Run all screening agents (sanctions + AML + regulatory) in parallel,
        then generate an audit report.

        Args:
            order_data: Full order dictionary.
            progress_callback: Optional async-friendly callable(agent_name, message, progress_pct).

        Returns:
            Aggregated compliance result dict.
        """
        async def _notify(agent: str, msg: str, pct: float):
            if progress_callback:
                try:
                    await progress_callback(agent, msg, pct)
                except Exception:
                    pass

        await _notify("orchestrator", "Starting compliance screening…", 0.0)

        # Run the three screening agents concurrently
        sanctions_task = asyncio.create_task(self.sanctions_agent.screen(order_data))
        aml_task = asyncio.create_task(self.aml_agent.screen(order_data))
        regulatory_task = asyncio.create_task(self.regulatory_agent.screen(order_data))

        await _notify("orchestrator", "Running sanctions checks…", 20.0)
        sanctions_result = await sanctions_task

        await _notify("SanctionsAgent", f"Sanctions screening complete — {sanctions_result['status']}", 40.0)
        aml_result = await aml_task

        await _notify("AMLAgent", f"AML/KYC screening complete — {aml_result['status']}", 60.0)
        regulatory_result = await regulatory_task

        await _notify("RegulatoryAgent", f"Regulatory screening complete — {regulatory_result['status']}", 80.0)

        screening_results = [sanctions_result, aml_result, regulatory_result]

        # Aggregate
        overall_risk_score = self._calculate_overall_risk(screening_results)
        overall_status = self._determine_overall_status(screening_results, overall_risk_score)

        # Generate audit report
        report = await self.report_agent.generate_report(
            order_data, screening_results, overall_status, overall_risk_score
        )

        await _notify("ReportAgent", "Audit report generated", 100.0)

        return {
            "overall_status": overall_status,
            "overall_risk_score": overall_risk_score,
            "screening_results": screening_results,
            "report": report,
        }

    # ------------------------------------------------------------------ #

    def _calculate_overall_risk(self, results: List[Dict[str, Any]]) -> float:
        """
        Weighted aggregation:
        - If ANY result is FAIL (score >= 0.8) → overall is at least 0.85
        - Otherwise use weighted max (sanctions heaviest)
        """
        weights = {
            "SANCTIONS": 0.5,
            "AML_KYC": 0.3,
            "REGULATORY": 0.2,
        }
        weighted_score = 0.0
        for result in results:
            s_type = result.get("screening_type", "")
            w = weights.get(s_type, 0.1)
            weighted_score += result.get("risk_score", 0.0) * w

        # Hard override: any individual FAIL elevates overall
        max_individual = max(r.get("risk_score", 0.0) for r in results)
        if max_individual >= 0.8:
            return max(max_individual, 0.85)

        return round(min(weighted_score, 1.0), 4)

    def _determine_overall_status(
        self, results: List[Dict[str, Any]], overall_risk: float
    ) -> str:
        """Determine status — if any agent FAILs, overall is FAIL."""
        statuses = [r.get("status", "PASS") for r in results]
        if "FAIL" in statuses:
            return "FAIL"
        if "FLAG" in statuses or overall_risk >= 0.4:
            return "FLAG"
        return "PASS"
