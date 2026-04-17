"""
Sanctions Agent — checks OFAC SDN, UN, and EU sanctions lists plus the PEP list.
Operates in RULE_BASED mode by default; falls back to rule-based if OpenAI unavailable.
"""
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.data_sources import (
    check_ofac_sdn,
    check_un_sanctions,
    check_eu_sanctions,
    check_pep_list,
    check_country_risk,
    _country_name_to_code,
)


class SanctionsAgent(BaseAgent):
    name = "SanctionsAgent"
    screening_type = "SANCTIONS"

    async def screen(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        customer_name = order_data.get("customer_name", "")
        customer_country = order_data.get("customer_country", "")

        # Map country name to ISO code for country-risk lookup
        country_code = _country_name_to_code(customer_country)

        # Run all four checks
        ofac_result = check_ofac_sdn(customer_name, customer_country)
        un_result = check_un_sanctions(customer_name, customer_country)
        eu_result = check_eu_sanctions(customer_name, customer_country)
        pep_result = check_pep_list(customer_name, customer_country)
        country_result = check_country_risk(country_code) if country_code else {
            "source": "COUNTRY_RISK", "restricted": False, "country": None, "risk_score": 0.0
        }

        flags = []
        max_score = 0.0

        for result, label in [
            (ofac_result, "OFAC SDN"),
            (un_result, "UN Sanctions"),
            (eu_result, "EU Sanctions"),
        ]:
            if result["matched"]:
                flags.append(f"{label} match: {', '.join(m['name'] for m in result['matches'])}")
                max_score = max(max_score, result["risk_score"])

        if pep_result["matched"]:
            flags.append(
                f"PEP match: {', '.join(m['name'] for m in pep_result['matches'])}"
            )
            max_score = max(max_score, pep_result["risk_score"])

        if country_result["restricted"]:
            country_info = country_result["country"]
            flags.append(
                f"Restricted country: {country_info['name']} ({country_info['risk_level']})"
            )
            max_score = max(max_score, country_result["risk_score"] * 0.7)  # weighted lower than direct match

        findings = {
            "ofac": ofac_result,
            "un_sanctions": un_result,
            "eu_sanctions": eu_result,
            "pep": pep_result,
            "country_risk": country_result,
        }

        status = self._determine_status(max_score)
        return self._build_result(status, max_score, findings, flags)
