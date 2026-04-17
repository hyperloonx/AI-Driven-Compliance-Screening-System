# AI-Driven Compliance Screening System

An agentic AI application that screens orders in real time against sanctions lists, AML/KYC rules, and regulatory requirements — generating audit-ready reports instantly.

## Features

- **Real-time order screening** — screens orders in < 2 seconds (rule-based mode)
- **Sanctions checks** — OFAC SDN, UN Security Council, EU Consolidated Sanctions, PEP lists
- **AML/KYC checks** — structuring detection, transaction pattern analysis, country risk
- **Regulatory compliance** — ITAR/EAR export controls, HS code lookups, product restrictions
- **Audit-ready reports** — structured JSON + downloadable PDF reports with full audit trail
- **Real-time updates** — WebSocket streaming of screening progress
- **Dual mode** — `RULE_BASED` (default, no API key) or `AI_MODE` (OpenAI)

## Quick Start

### Docker Compose (Recommended)

```bash
cp .env.example .env
docker compose up --build
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install --legacy-peer-deps
npm start
```

### Run Tests

```bash
pip install pytest pytest-asyncio httpx aiosqlite
python -m pytest tests/ -v
# 42/42 tests pass ✅
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/          # Compliance screening agents
│   │   │   ├── sanctions_agent.py    # OFAC, UN, EU, PEP checks
│   │   │   ├── aml_agent.py          # AML/KYC checks
│   │   │   ├── regulatory_agent.py   # Export controls
│   │   │   ├── report_agent.py       # PDF/JSON report generation
│   │   │   └── orchestrator.py       # Master coordinator
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # FastAPI route handlers
│   │   └── services/        # Business logic + mock data sources
├── frontend/                # React TypeScript dashboard
├── tests/                   # 42 unit + integration tests
└── docs/                    # Architecture, deployment, validation
```

## Architecture

```
React Dashboard ──── REST + WebSocket ──── FastAPI Backend
                                               │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                        SanctionsAgent    AMLAgent    RegulatoryAgent
                              │                │                │
                              └────────────────┴────────────────┘
                                               │
                                        ReportAgent
                                    (JSON + PDF output)
                                               │
                                    PostgreSQL / SQLite
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders` | Submit order for screening |
| GET | `/api/v1/orders` | List all orders |
| GET | `/api/v1/orders/{id}` | Get order details |
| GET | `/api/v1/orders/{id}/compliance` | Get compliance result |
| WS | `/api/v1/orders/ws/{id}` | Real-time screening updates |
| GET | `/api/v1/reports` | List audit reports |
| GET | `/api/v1/reports/{id}` | Get specific report |
| GET | `/api/v1/reports/{id}/download` | Download PDF report |

## Risk Scoring

| Score Range | Status | Action |
|-------------|--------|--------|
| 0.0 – 0.39 | PASS ✅ | Process normally |
| 0.4 – 0.79 | FLAG ⚠️ | Hold, enhanced due diligence |
| 0.8 – 1.0 | FAIL 🚫 | Block, escalate to compliance |

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Validation Report](docs/validation_report.md)
