# Architecture — AI-Driven Compliance Screening System

## Overview

The system follows a layered architecture with four main concerns:

```
Browser (React/TypeScript)
    ↕ REST + WebSocket
FastAPI Backend
    ↕ async SQLAlchemy
SQLite / PostgreSQL            Redis (cache / pub-sub)
    ↕
Compliance Agents (rule-based or AI)
    ↕
Mock Data Sources (OFAC, UN, EU, PEP)
```

## Components

### Backend (FastAPI)

| Module | Responsibility |
|---|---|
| `app/main.py` | FastAPI app, CORS, lifespan |
| `app/config.py` | Settings from env vars |
| `app/database.py` | Async SQLAlchemy engine + session |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response schemas |
| `app/agents/` | Compliance screening agents |
| `app/services/` | Business logic layer |
| `app/routers/` | API route handlers |

### Compliance Agents

```
ComplianceOrchestrator
├── SanctionsAgent   → OFAC SDN, UN, EU, PEP checks
├── AMLAgent         → AML/KYC, structuring detection, country risk
├── RegulatoryAgent  → ITAR/EAR export controls, product restrictions
└── ReportAgent      → JSON + PDF audit report generation
```

All agents extend `BaseAgent` and implement the `screen(order_data)` interface.

### Agent Modes

- **RULE_BASED** (default): deterministic, fast (<2s), no API key required
- **AI_MODE**: delegates reasoning to OpenAI; requires `OPENAI_API_KEY`

### Data Flow

1. Client POSTs an order → `POST /api/v1/orders`
2. Order saved with status `PENDING`
3. Background task triggers `ComplianceService.screen_order()`
4. Orchestrator fans out to 3 agents (async parallel)
5. Results aggregated, risk score calculated, status determined
6. PDF report generated via `reportlab`
7. Results persisted to DB; WebSocket broadcasts updates
8. Client polls or receives WS updates

### Database Schema

```
orders
  id, order_number, customer_name, customer_country,
  customer_email, items (JSON), total_amount, currency,
  status, created_at, updated_at

compliance_results
  id, order_id (FK), screening_type, status,
  risk_score, findings (JSON), created_at

audit_reports
  id, order_id (FK), report_data (JSON), pdf_path, created_at
```

### Risk Scoring

- Each agent produces a `risk_score` in [0, 1]
- Orchestrator applies weighted aggregation:
  - Sanctions: 50%
  - AML/KYC: 30%
  - Regulatory: 20%
- Any individual score ≥ 0.8 → overall is at least 0.85
- Status mapping: PASS (<0.4), FLAG (0.4–0.8), FAIL (≥0.8)

### Real-time Updates

WebSocket endpoint `/api/v1/orders/ws/{order_id}` streams:
```json
{ "order_id": "...", "status": "SCREENING", "agent": "SanctionsAgent",
  "message": "Sanctions screening complete — FAIL", "progress": 40.0 }
```
