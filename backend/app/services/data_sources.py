"""
Compliance data sources with realistic mock data.
Simulates OFAC SDN, UN, EU sanctions lists, PEP lists, and restricted country/industry data.
"""
from typing import List, Dict, Any, Optional
import re


# ---------------------------------------------------------------------------
# OFAC Specially Designated Nationals (SDN) mock list
# ---------------------------------------------------------------------------
OFAC_SDN_LIST: List[Dict[str, Any]] = [
    {
        "id": "OFAC-001",
        "name": "Viktor Antonov",
        "aliases": ["Victor Antonov", "V. Antonov"],
        "nationality": "Russia",
        "dob": "1965-03-14",
        "program": "UKRAINE-EO13661",
        "type": "individual",
    },
    {
        "id": "OFAC-002",
        "name": "Gazprom Neft",
        "aliases": ["Gazprom-Neft", "GPN"],
        "nationality": "Russia",
        "program": "UKRAINE-EO13662",
        "type": "entity",
    },
    {
        "id": "OFAC-003",
        "name": "Ali Hassan Al-Rashidi",
        "aliases": ["Ali Al Rashidi", "Abu Hassan"],
        "nationality": "Iran",
        "dob": "1972-07-22",
        "program": "IRAN",
        "type": "individual",
    },
    {
        "id": "OFAC-004",
        "name": "Tehran Trading Co",
        "aliases": ["TTC", "Tehran Trade"],
        "nationality": "Iran",
        "program": "IRAN",
        "type": "entity",
    },
    {
        "id": "OFAC-005",
        "name": "Kim Jong-nam",
        "aliases": ["Kim Chol", "Pang Xiuying"],
        "nationality": "North Korea",
        "program": "DPRK",
        "type": "individual",
    },
    {
        "id": "OFAC-006",
        "name": "Korea Mining Development Trading",
        "aliases": ["KOMID", "Korea Mining"],
        "nationality": "North Korea",
        "program": "DPRK",
        "type": "entity",
    },
    {
        "id": "OFAC-007",
        "name": "Ramzan Kadyrov",
        "aliases": ["R. Kadyrov"],
        "nationality": "Russia",
        "dob": "1976-10-05",
        "program": "MAGNITSKY",
        "type": "individual",
    },
    {
        "id": "OFAC-008",
        "name": "Semion Mogilevich",
        "aliases": ["Seva", "Don Semyon"],
        "nationality": "Russia",
        "dob": "1946-06-30",
        "program": "TCO",
        "type": "individual",
    },
    {
        "id": "OFAC-009",
        "name": "Syrian Arab Airlines",
        "aliases": ["Syrianair", "Syrian Air"],
        "nationality": "Syria",
        "program": "SYRIA",
        "type": "entity",
    },
    {
        "id": "OFAC-010",
        "name": "Bashar Al-Assad",
        "aliases": ["B. Assad"],
        "nationality": "Syria",
        "program": "SYRIA",
        "type": "individual",
    },
    {
        "id": "OFAC-011",
        "name": "Cuba Petroleum",
        "aliases": ["Cubapetroleo", "CUPET"],
        "nationality": "Cuba",
        "program": "CUBA",
        "type": "entity",
    },
    {
        "id": "OFAC-012",
        "name": "Jorge Luis Fernandez",
        "aliases": ["Jorge Fernandez"],
        "nationality": "Venezuela",
        "program": "VENEZUELA-EO13850",
        "type": "individual",
    },
]

# ---------------------------------------------------------------------------
# UN Security Council sanctions list
# ---------------------------------------------------------------------------
UN_SANCTIONS_LIST: List[Dict[str, Any]] = [
    {
        "id": "UN-001",
        "name": "Al-Qaida",
        "aliases": ["Al Qaeda", "AQ", "Base"],
        "type": "entity",
        "committee": "1267",
        "reason": "Terrorism",
    },
    {
        "id": "UN-002",
        "name": "Islamic State in Iraq and the Levant",
        "aliases": ["ISIL", "ISIS", "Daesh"],
        "type": "entity",
        "committee": "1267",
        "reason": "Terrorism",
    },
    {
        "id": "UN-003",
        "name": "Abubakar Shekau",
        "aliases": ["Abu Shekau", "Darul Tawhid"],
        "nationality": "Nigeria",
        "type": "individual",
        "committee": "1267",
        "reason": "Terrorism - Boko Haram",
    },
    {
        "id": "UN-004",
        "name": "Pyongyang Special Economic Zone",
        "aliases": ["PSEZ"],
        "nationality": "North Korea",
        "type": "entity",
        "committee": "1718",
        "reason": "WMD proliferation",
    },
    {
        "id": "UN-005",
        "name": "Muammar Gaddafi",
        "aliases": ["Gaddafi", "Qadhafi"],
        "nationality": "Libya",
        "type": "individual",
        "committee": "1970",
        "reason": "Human rights violations",
    },
    {
        "id": "UN-006",
        "name": "Haftar Armed Forces",
        "aliases": ["LNA", "HAF"],
        "nationality": "Libya",
        "type": "entity",
        "committee": "1970",
        "reason": "Arms embargo violation",
    },
]

# ---------------------------------------------------------------------------
# EU Consolidated Sanctions List
# ---------------------------------------------------------------------------
EU_SANCTIONS_LIST: List[Dict[str, Any]] = [
    {
        "id": "EU-001",
        "name": "Igor Sechin",
        "aliases": ["I. Sechin"],
        "nationality": "Russia",
        "type": "individual",
        "regulation": "EU/269/2014",
        "reason": "Ukraine destabilisation",
    },
    {
        "id": "EU-002",
        "name": "Rosneft",
        "aliases": ["Rosneft Oil", "OJSC Rosneft"],
        "nationality": "Russia",
        "type": "entity",
        "regulation": "EU/833/2014",
        "reason": "Energy sector restrictions",
    },
    {
        "id": "EU-003",
        "name": "Alexander Lukashenko",
        "aliases": ["A. Lukashenko", "Lukashenka"],
        "nationality": "Belarus",
        "type": "individual",
        "regulation": "EU/2020/1798",
        "reason": "Human rights violations",
    },
    {
        "id": "EU-004",
        "name": "Belarusian State Military Industrial Committee",
        "aliases": ["Goskomvoenrom"],
        "nationality": "Belarus",
        "type": "entity",
        "regulation": "EU/2021/1031",
        "reason": "Arms export",
    },
    {
        "id": "EU-005",
        "name": "Huawei Technologies",
        "aliases": ["Huawei"],
        "nationality": "China",
        "type": "entity",
        "regulation": "EU-TECH-2023",
        "reason": "Technology restrictions",
    },
    {
        "id": "EU-006",
        "name": "Wagner Group",
        "aliases": ["PMC Wagner", "The Wagner Group"],
        "nationality": "Russia",
        "type": "entity",
        "regulation": "EU/2023/391",
        "reason": "Mercenary activities",
    },
]

# ---------------------------------------------------------------------------
# PEP (Politically Exposed Persons) list
# ---------------------------------------------------------------------------
PEP_LIST: List[Dict[str, Any]] = [
    {
        "id": "PEP-001",
        "name": "Vladimir Putin",
        "aliases": ["V. Putin"],
        "country": "Russia",
        "position": "President of Russia",
        "risk_level": "HIGH",
    },
    {
        "id": "PEP-002",
        "name": "Xi Jinping",
        "aliases": ["Xi Jin Ping"],
        "country": "China",
        "position": "President of China",
        "risk_level": "HIGH",
    },
    {
        "id": "PEP-003",
        "name": "Nicolas Maduro",
        "aliases": ["N. Maduro"],
        "country": "Venezuela",
        "position": "President of Venezuela",
        "risk_level": "HIGH",
    },
    {
        "id": "PEP-004",
        "name": "Robert Mugabe",
        "aliases": ["R. Mugabe"],
        "country": "Zimbabwe",
        "position": "Former President of Zimbabwe",
        "risk_level": "HIGH",
    },
    {
        "id": "PEP-005",
        "name": "Kim Jong-un",
        "aliases": ["Kim Jung-un", "Supreme Leader"],
        "country": "North Korea",
        "position": "Supreme Leader of North Korea",
        "risk_level": "CRITICAL",
    },
    {
        "id": "PEP-006",
        "name": "Ali Khamenei",
        "aliases": ["Khamenei", "Supreme Leader Iran"],
        "country": "Iran",
        "position": "Supreme Leader of Iran",
        "risk_level": "CRITICAL",
    },
    {
        "id": "PEP-007",
        "name": "Ebrahim Raisi",
        "aliases": ["E. Raisi"],
        "country": "Iran",
        "position": "President of Iran",
        "risk_level": "HIGH",
    },
    {
        "id": "PEP-008",
        "name": "Nicolás Maduro Moros",
        "aliases": ["Maduro"],
        "country": "Venezuela",
        "position": "President of Venezuela",
        "risk_level": "HIGH",
    },
]

# ---------------------------------------------------------------------------
# High-risk / sanctioned countries
# ---------------------------------------------------------------------------
RESTRICTED_COUNTRIES: Dict[str, Dict[str, Any]] = {
    "IR": {"name": "Iran", "risk_level": "CRITICAL", "sanctions": ["OFAC", "UN", "EU"], "restrictions": "Comprehensive"},
    "KP": {"name": "North Korea", "risk_level": "CRITICAL", "sanctions": ["OFAC", "UN", "EU"], "restrictions": "Comprehensive"},
    "SY": {"name": "Syria", "risk_level": "CRITICAL", "sanctions": ["OFAC", "UN", "EU"], "restrictions": "Comprehensive"},
    "CU": {"name": "Cuba", "risk_level": "HIGH", "sanctions": ["OFAC"], "restrictions": "Partial"},
    "RU": {"name": "Russia", "risk_level": "HIGH", "sanctions": ["OFAC", "EU"], "restrictions": "Sector-based"},
    "BY": {"name": "Belarus", "risk_level": "HIGH", "sanctions": ["EU", "OFAC"], "restrictions": "Sector-based"},
    "VE": {"name": "Venezuela", "risk_level": "HIGH", "sanctions": ["OFAC"], "restrictions": "Sector-based"},
    "MM": {"name": "Myanmar", "risk_level": "HIGH", "sanctions": ["OFAC", "EU"], "restrictions": "Partial"},
    "SD": {"name": "Sudan", "risk_level": "HIGH", "sanctions": ["OFAC"], "restrictions": "Partial"},
    "ZW": {"name": "Zimbabwe", "risk_level": "MEDIUM", "sanctions": ["OFAC", "EU"], "restrictions": "Targeted"},
    "LY": {"name": "Libya", "risk_level": "MEDIUM", "sanctions": ["UN", "EU"], "restrictions": "Arms embargo"},
    "SO": {"name": "Somalia", "risk_level": "HIGH", "sanctions": ["UN"], "restrictions": "Arms embargo"},
    "CF": {"name": "Central African Republic", "risk_level": "MEDIUM", "sanctions": ["UN"], "restrictions": "Arms embargo"},
    "CD": {"name": "Congo (DRC)", "risk_level": "MEDIUM", "sanctions": ["UN"], "restrictions": "Arms embargo"},
    "YE": {"name": "Yemen", "risk_level": "HIGH", "sanctions": ["UN"], "restrictions": "Arms embargo"},
    "AF": {"name": "Afghanistan", "risk_level": "HIGH", "sanctions": ["UN", "OFAC"], "restrictions": "Terror financing"},
}

# ---------------------------------------------------------------------------
# High-risk industries / product categories
# ---------------------------------------------------------------------------
HIGH_RISK_INDUSTRIES: List[Dict[str, Any]] = [
    {"code": "WEAPONS", "name": "Weapons and Military Equipment", "risk_level": "CRITICAL", "regulation": "ITAR/EAR"},
    {"code": "NUCLEAR", "name": "Nuclear Materials and Technology", "risk_level": "CRITICAL", "regulation": "NRC/IAEA"},
    {"code": "BIOTECH_DUAL", "name": "Dual-use Biological Technology", "risk_level": "CRITICAL", "regulation": "EAR"},
    {"code": "CRYPTO_EXPORT", "name": "Cryptography Exports", "risk_level": "HIGH", "regulation": "EAR"},
    {"code": "SURVEILLANCE", "name": "Mass Surveillance Technology", "risk_level": "HIGH", "regulation": "EAR/EU"},
    {"code": "CHEMICALS_DUAL", "name": "Dual-use Chemicals", "risk_level": "HIGH", "regulation": "CWC/EAR"},
    {"code": "TELECOM_SENSITIVE", "name": "Sensitive Telecommunications", "risk_level": "MEDIUM", "regulation": "EAR"},
    {"code": "AEROSPACE", "name": "Aerospace Components (Controlled)", "risk_level": "HIGH", "regulation": "ITAR"},
    {"code": "CYBER_OFFENSIVE", "name": "Offensive Cyber Tools", "risk_level": "CRITICAL", "regulation": "EAR/Wassenaar"},
]

# HS codes associated with export controls (sample)
CONTROLLED_HS_CODES: Dict[str, str] = {
    "9301": "Military weapons",
    "9302": "Revolvers and pistols",
    "9303": "Firearms",
    "9304": "Other arms",
    "9305": "Parts of weapons",
    "2844": "Radioactive chemical elements",
    "8542": "Electronic integrated circuits",
    "8471": "Automatic data processing machines",
    "8802": "Aircraft and spacecraft",
    "8803": "Parts of aircraft",
    "2921": "Amine-function compounds (potential dual-use)",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _normalize_name(name: str) -> str:
    """Lowercase, strip punctuation for fuzzy comparison."""
    return re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()


def _name_matches(query: str, candidate: str) -> bool:
    """Check if query name matches candidate (exact or token overlap)."""
    q = _normalize_name(query)
    c = _normalize_name(candidate)
    if q == c:
        return True
    q_tokens = set(q.split())
    c_tokens = set(c.split())
    if len(q_tokens) >= 2 and len(q_tokens & c_tokens) >= 2:
        return True
    # substring match for longer names
    if len(q) >= 5 and (q in c or c in q):
        return True
    return False


def check_ofac_sdn(name: str, country: Optional[str] = None) -> Dict[str, Any]:
    """Check a name against the OFAC SDN list."""
    matches = []
    for entry in OFAC_SDN_LIST:
        names_to_check = [entry["name"]] + entry.get("aliases", [])
        if any(_name_matches(name, n) for n in names_to_check):
            matches.append(entry)
        elif country and entry.get("nationality", "").lower() == country.lower():
            pass  # country alone is not a match

    return {
        "source": "OFAC_SDN",
        "matched": len(matches) > 0,
        "matches": matches,
        "risk_score": 1.0 if matches else 0.0,
    }


def check_un_sanctions(name: str, country: Optional[str] = None) -> Dict[str, Any]:
    """Check a name against the UN Security Council sanctions list."""
    matches = []
    for entry in UN_SANCTIONS_LIST:
        names_to_check = [entry["name"]] + entry.get("aliases", [])
        if any(_name_matches(name, n) for n in names_to_check):
            matches.append(entry)

    return {
        "source": "UN_SANCTIONS",
        "matched": len(matches) > 0,
        "matches": matches,
        "risk_score": 1.0 if matches else 0.0,
    }


def check_eu_sanctions(name: str, country: Optional[str] = None) -> Dict[str, Any]:
    """Check a name against the EU Consolidated Sanctions list."""
    matches = []
    for entry in EU_SANCTIONS_LIST:
        names_to_check = [entry["name"]] + entry.get("aliases", [])
        if any(_name_matches(name, n) for n in names_to_check):
            matches.append(entry)

    return {
        "source": "EU_SANCTIONS",
        "matched": len(matches) > 0,
        "matches": matches,
        "risk_score": 1.0 if matches else 0.0,
    }


def check_pep_list(name: str, country: Optional[str] = None) -> Dict[str, Any]:
    """Check a name against the PEP list."""
    matches = []
    for entry in PEP_LIST:
        names_to_check = [entry["name"]] + entry.get("aliases", [])
        if any(_name_matches(name, n) for n in names_to_check):
            matches.append(entry)

    risk_map = {"CRITICAL": 0.9, "HIGH": 0.7, "MEDIUM": 0.4, "LOW": 0.2}
    risk_score = max((risk_map.get(m.get("risk_level", "LOW"), 0.2) for m in matches), default=0.0)

    return {
        "source": "PEP",
        "matched": len(matches) > 0,
        "matches": matches,
        "risk_score": risk_score,
    }


def check_country_risk(country_code: str) -> Dict[str, Any]:
    """Get risk profile for a country by ISO alpha-2 code."""
    country_code = country_code.upper()
    entry = RESTRICTED_COUNTRIES.get(country_code)
    if entry:
        risk_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2}
        return {
            "source": "COUNTRY_RISK",
            "restricted": True,
            "country": entry,
            "risk_score": risk_map.get(entry["risk_level"], 0.3),
        }
    return {"source": "COUNTRY_RISK", "restricted": False, "country": None, "risk_score": 0.0}


def check_hs_code(hs_code: str) -> Dict[str, Any]:
    """Check if a HS code relates to controlled goods."""
    prefix4 = hs_code[:4] if len(hs_code) >= 4 else hs_code
    if prefix4 in CONTROLLED_HS_CODES:
        return {
            "source": "HS_CODE",
            "controlled": True,
            "description": CONTROLLED_HS_CODES[prefix4],
            "risk_score": 0.8,
        }
    return {"source": "HS_CODE", "controlled": False, "description": None, "risk_score": 0.0}


def check_industry_risk(category: str) -> Dict[str, Any]:
    """Check if a product category is high-risk."""
    cat_upper = category.upper()
    for industry in HIGH_RISK_INDUSTRIES:
        if industry["code"] in cat_upper or cat_upper in industry["name"].upper():
            risk_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5}
            return {
                "source": "INDUSTRY_RISK",
                "restricted": True,
                "industry": industry,
                "risk_score": risk_map.get(industry["risk_level"], 0.3),
            }
    return {"source": "INDUSTRY_RISK", "restricted": False, "industry": None, "risk_score": 0.0}


# ---------------------------------------------------------------------------
# Country name → ISO-2 mapping (common names only)
# ---------------------------------------------------------------------------
_COUNTRY_MAP: Dict[str, str] = {
    "iran": "IR",
    "islamic republic of iran": "IR",
    "north korea": "KP",
    "democratic people's republic of korea": "KP",
    "dprk": "KP",
    "syria": "SY",
    "syrian arab republic": "SY",
    "cuba": "CU",
    "russia": "RU",
    "russian federation": "RU",
    "belarus": "BY",
    "venezuela": "VE",
    "myanmar": "MM",
    "burma": "MM",
    "sudan": "SD",
    "zimbabwe": "ZW",
    "libya": "LY",
    "somalia": "SO",
    "central african republic": "CF",
    "congo": "CD",
    "democratic republic of the congo": "CD",
    "drc": "CD",
    "yemen": "YE",
    "afghanistan": "AF",
}


def _country_name_to_code(name: str) -> str:
    """Convert a country name to ISO alpha-2 code."""
    if not name:
        return ""
    # Check if already ISO code (2 chars)
    if len(name) == 2:
        return name.upper()
    return _COUNTRY_MAP.get(name.strip().lower(), "")
