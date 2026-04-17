"""Base agent class shared by all compliance agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.config import settings


class BaseAgent(ABC):
    """Abstract base for all compliance screening agents."""

    name: str = "BaseAgent"
    screening_type: str = "BASE"

    def __init__(self):
        self.mode = settings.AGENT_MODE  # "AI_MODE" or "RULE_BASED"
        self.openai_available = bool(settings.OPENAI_API_KEY)

    def _build_result(
        self,
        status: str,
        risk_score: float,
        findings: Dict[str, Any],
        flags: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Standard result structure returned by every agent."""
        return {
            "agent": self.name,
            "screening_type": self.screening_type,
            "status": status,       # PASS / FLAG / FAIL
            "risk_score": round(min(max(risk_score, 0.0), 1.0), 4),
            "findings": findings,
            "flags": flags or [],
            "screened_at": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
        }

    @abstractmethod
    async def screen(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the screening and return a standardised result dict."""

    def _determine_status(self, risk_score: float) -> str:
        """Map a 0-1 risk score to PASS / FLAG / FAIL."""
        if risk_score >= 0.8:
            return "FAIL"
        if risk_score >= 0.4:
            return "FLAG"
        return "PASS"
