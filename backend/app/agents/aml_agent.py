"""
AML/KYC Agent — Anti-Money Laundering and Know Your Customer checks.
Checks transaction patterns, customer identity, country risk, and velocity.
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.data_sources import check_country_risk, _country_name_to_code  # type: ignore[attr-defined]


# Thresholds
STRUCTURING_THRESHOLD = 9_000       # Just below $10k reporting threshold (structuring red flag)
HIGH_VALUE_THRESHOLD = 50_000       # Unusually high single transaction
VELOCITY_DAILY_LIMIT = 5            # Max transactions per customer per day before flag
ROUND_AMOUNT_MODULO = 1_000         # Round-number amounts are suspicious


# High-risk currencies (simplified)
HIGH_RISK_CURRENCIES = {"VES", "ZWL", "IRR", "KPW"}

# Jurisdictions with weak AML/KYC frameworks (FATF grey/blacklist proxy)
FATF_GREY_BLACK_LIST = {
    "AF", "MM", "KP", "IR", "SY", "YE", "SD", "SO", "CF", "CD",
    "PK", "TJ", "UZ", "HT", "PH",
}


class AMLAgent(BaseAgent):
    name = "AMLAgent"
    screening_type = "AML_KYC"

    async def screen(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        flags: List[str] = []
        risk_contributions: List[float] = []

        # --- Transaction pattern checks ---
        tp_result = self._check_transaction_patterns(order_data)
        flags.extend(tp_result["flags"])
        risk_contributions.append(tp_result["risk_score"])

        # --- KYC check ---
        kyc_result = self._verify_customer_kyc(order_data)
        flags.extend(kyc_result["flags"])
        risk_contributions.append(kyc_result["risk_score"])

        # --- Country risk ---
        country_code = _country_name_to_code(order_data.get("customer_country", ""))
        cr_result = self._check_country_risk(country_code)
        flags.extend(cr_result["flags"])
        risk_contributions.append(cr_result["risk_score"])

        # --- Currency risk ---
        currency = order_data.get("currency", "USD").upper()
        currency_score = 0.7 if currency in HIGH_RISK_CURRENCIES else 0.0
        if currency_score:
            flags.append(f"High-risk currency: {currency}")
            risk_contributions.append(currency_score)

        overall_risk = max(risk_contributions, default=0.0)
        status = self._determine_status(overall_risk)

        findings = {
            "transaction_patterns": tp_result,
            "kyc": kyc_result,
            "country_risk": cr_result,
            "currency_risk": {"currency": currency, "risk_score": currency_score},
        }

        return self._build_result(status, overall_risk, findings, flags)

    # ------------------------------------------------------------------ #
    def _check_transaction_patterns(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect structuring, unusual amounts, and round-number patterns."""
        amount = float(order_data.get("total_amount", 0))
        flags: List[str] = []
        risk_score = 0.0

        # Structuring — just below $10k
        if 8_000 <= amount < 10_000:
            flags.append(f"Possible structuring: amount ${amount:,.2f} just below $10,000 reporting threshold")
            risk_score = max(risk_score, 0.7)

        # Unusually high amount
        if amount > HIGH_VALUE_THRESHOLD:
            flags.append(f"High-value transaction: ${amount:,.2f} exceeds ${HIGH_VALUE_THRESHOLD:,}")
            risk_score = max(risk_score, 0.5)

        # Round-number suspicion
        if amount >= 1_000 and amount % ROUND_AMOUNT_MODULO == 0:
            flags.append(f"Round-number amount: ${amount:,.2f} (potential indicator of structured payment)")
            risk_score = max(risk_score, 0.3)

        return {"check": "transaction_patterns", "flags": flags, "risk_score": risk_score, "amount": amount}

    def _verify_customer_kyc(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify customer identity completeness."""
        flags: List[str] = []
        risk_score = 0.0

        name = order_data.get("customer_name", "").strip()
        email = order_data.get("customer_email", "").strip()
        country = order_data.get("customer_country", "").strip()

        if len(name) < 3:
            flags.append("Customer name too short — KYC incomplete")
            risk_score = max(risk_score, 0.5)

        if not email or "@" not in email:
            flags.append("Invalid or missing customer email — KYC incomplete")
            risk_score = max(risk_score, 0.4)

        if not country:
            flags.append("Missing customer country — KYC incomplete")
            risk_score = max(risk_score, 0.4)

        # Check for generic/placeholder names
        generic_terms = {"test", "unknown", "anonymous", "n/a", "na", "none"}
        if name.lower() in generic_terms:
            flags.append(f"Generic customer name '{name}' indicates incomplete KYC")
            risk_score = max(risk_score, 0.6)

        return {"check": "kyc", "flags": flags, "risk_score": risk_score}

    def _check_country_risk(self, country_code: str) -> Dict[str, Any]:
        """Check AML-specific country risk."""
        flags: List[str] = []
        risk_score = 0.0

        if country_code in FATF_GREY_BLACK_LIST:
            flags.append(f"Country {country_code} on FATF grey/blacklist — enhanced due diligence required")
            risk_score = max(risk_score, 0.65)

        cr = check_country_risk(country_code)
        if cr["restricted"]:
            risk_score = max(risk_score, cr["risk_score"] * 0.6)

        return {"check": "country_risk", "country_code": country_code, "flags": flags, "risk_score": risk_score}
