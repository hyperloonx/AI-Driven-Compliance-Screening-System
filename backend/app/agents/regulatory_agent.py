"""
Regulatory Compliance Agent — checks export controls (ITAR/EAR),
product restrictions, financial regulations, and industry-specific rules.
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.data_sources import check_hs_code, check_industry_risk, check_country_risk, _country_name_to_code


# Countries subject to ITAR/EAR export restrictions (sampled)
ITAR_RESTRICTED_COUNTRIES = {
    "KP", "IR", "SY", "CU", "SD", "RU", "BY", "VE", "MM", "LY", "AF",
}

# Products/keywords triggering export control review
EXPORT_CONTROL_KEYWORDS = [
    "military", "weapon", "firearm", "explosive", "nuclear", "radioactive",
    "drone", "uav", "missile", "rocket", "satellite", "encryption",
    "cipher", "biometric", "surveillance", "chemical weapon", "biological",
    "toxic", "nerve agent",
]

# Financial thresholds
LARGE_TRANSACTION_REPORT_THRESHOLD = 10_000   # CTR threshold (USD)
SUSPICIOUS_ACTIVITY_THRESHOLD = 5_000

# Restricted product categories (simplified)
RESTRICTED_PRODUCT_CATEGORIES = {
    "WEAPONS", "MILITARY", "NUCLEAR", "BIOTECH_DUAL", "CHEMICALS_DUAL",
    "CYBER_OFFENSIVE", "SURVEILLANCE",
}


class RegulatoryAgent(BaseAgent):
    name = "RegulatoryAgent"
    screening_type = "REGULATORY"

    async def screen(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        flags: List[str] = []
        risk_contributions: List[float] = []

        country_code = _country_name_to_code(order_data.get("customer_country", ""))

        # Export controls
        ec_result = self._check_export_controls(order_data, country_code)
        flags.extend(ec_result["flags"])
        risk_contributions.append(ec_result["risk_score"])

        # Product restrictions
        pr_result = self._check_product_restrictions(order_data)
        flags.extend(pr_result["flags"])
        risk_contributions.append(pr_result["risk_score"])

        # Financial regulations
        fr_result = self._check_financial_regulations(order_data)
        flags.extend(fr_result["flags"])
        risk_contributions.append(fr_result["risk_score"])

        # Industry-specific regulations
        ir_result = self._check_industry_regulations(order_data)
        flags.extend(ir_result["flags"])
        risk_contributions.append(ir_result["risk_score"])

        overall_risk = max(risk_contributions, default=0.0)
        status = self._determine_status(overall_risk)

        findings = {
            "export_controls": ec_result,
            "product_restrictions": pr_result,
            "financial_regulations": fr_result,
            "industry_regulations": ir_result,
        }

        return self._build_result(status, overall_risk, findings, flags)

    # ------------------------------------------------------------------ #

    def _check_export_controls(self, order_data: Dict[str, Any], country_code: str) -> Dict[str, Any]:
        """Check ITAR and EAR export controls."""
        flags: List[str] = []
        risk_score = 0.0
        items = order_data.get("items", [])

        if country_code in ITAR_RESTRICTED_COUNTRIES:
            flags.append(f"Export to {country_code} subject to ITAR/EAR restrictions")
            risk_score = max(risk_score, 0.7)

        for item in items:
            product_name = (item.get("product_name") or "").lower()
            hs_code = item.get("hs_code") or ""

            # Keyword scan
            for kw in EXPORT_CONTROL_KEYWORDS:
                if kw in product_name:
                    flags.append(f"Export-controlled keyword '{kw}' in product '{item.get('product_name')}'")
                    risk_score = max(risk_score, 0.8)
                    break

            # HS code check
            if hs_code:
                hs_result = check_hs_code(hs_code)
                if hs_result["controlled"]:
                    flags.append(
                        f"Controlled HS code {hs_code}: {hs_result['description']}"
                    )
                    risk_score = max(risk_score, hs_result["risk_score"])

        return {"check": "export_controls", "flags": flags, "risk_score": risk_score}

    def _check_product_restrictions(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for restricted product categories."""
        flags: List[str] = []
        risk_score = 0.0
        items = order_data.get("items", [])

        for item in items:
            category = (item.get("category") or "").upper()
            if not category:
                continue

            if category in RESTRICTED_PRODUCT_CATEGORIES:
                flags.append(f"Restricted product category: {category}")
                risk_score = max(risk_score, 0.9)

            # Industry risk database check
            ir = check_industry_risk(category)
            if ir["restricted"]:
                flags.append(
                    f"High-risk industry: {ir['industry']['name']} (regulation: {ir['industry']['regulation']})"
                )
                risk_score = max(risk_score, ir["risk_score"])

        return {"check": "product_restrictions", "flags": flags, "risk_score": risk_score}

    def _check_financial_regulations(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check financial compliance rules (CTR, SAR thresholds)."""
        flags: List[str] = []
        risk_score = 0.0
        amount = float(order_data.get("total_amount", 0))

        if amount >= LARGE_TRANSACTION_REPORT_THRESHOLD:
            flags.append(
                f"Transaction amount ${amount:,.2f} meets Currency Transaction Report (CTR) threshold"
            )
            risk_score = max(risk_score, 0.35)

        if amount >= SUSPICIOUS_ACTIVITY_THRESHOLD:
            flags.append(
                f"Transaction amount ${amount:,.2f} meets Suspicious Activity Report (SAR) review threshold"
            )
            risk_score = max(risk_score, 0.25)

        return {"check": "financial_regulations", "flags": flags, "risk_score": risk_score}

    def _check_industry_regulations(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check sector-specific regulatory requirements."""
        flags: List[str] = []
        risk_score = 0.0
        items = order_data.get("items", [])

        for item in items:
            category = item.get("category") or ""
            product_name = (item.get("product_name") or "").lower()

            # Defence sector
            if "defence" in product_name or "defense" in product_name:
                flags.append(f"Defence-related product detected: '{item.get('product_name')}'")
                risk_score = max(risk_score, 0.7)

            # Pharma/biotech dual-use
            if "pharmaceutical" in product_name or "biotech" in product_name:
                flags.append(f"Pharmaceutical/biotech product may require export licence: '{item.get('product_name')}'")
                risk_score = max(risk_score, 0.4)

            # Semiconductor / microchip advanced
            if "semiconductor" in product_name or "microchip" in product_name:
                flags.append(f"Semiconductor product subject to export controls: '{item.get('product_name')}'")
                risk_score = max(risk_score, 0.5)

        return {"check": "industry_regulations", "flags": flags, "risk_score": risk_score}
