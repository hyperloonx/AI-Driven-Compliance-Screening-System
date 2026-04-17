# Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.11+ (for local dev)
- Node.js 20+ (for frontend local dev)

---

## Quick Start with Docker Compose

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd AI-Driven-Compliance-Screening-System

# 2. Configure environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY if using AI_MODE

# 3. Start all services
docker compose up --build

# 4. Access the application
#    Frontend:  http://localhost:3000
#    Backend:   http://localhost:8000
#    API docs:  http://localhost:8000/docs
```

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Uses SQLite by default (no PostgreSQL needed)
export AGENT_MODE=RULE_BASED
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start   # opens http://localhost:3000
```

---

## Running Tests

```bash
cd <repo root>
pip install pytest pytest-asyncio httpx aiosqlite
python -m pytest tests/ -v
```

---

## Production Checklist

- [ ] Set a strong `SECRET_KEY` in `.env`
- [ ] Set real PostgreSQL credentials (not the dev defaults)
- [ ] Enable HTTPS (add TLS termination via nginx/Caddy in front)
- [ ] Remove `"*"` from `CORS_ORIGINS`
- [ ] Set `DEBUG=false`
- [ ] Configure log aggregation (ELK / CloudWatch)
- [ ] Schedule database backups
- [ ] Rotate PDF report storage to S3 or similar

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `AGENT_MODE` | `RULE_BASED` | `RULE_BASED` or `AI_MODE` |
| `OPENAI_API_KEY` | _(empty)_ | Required for `AI_MODE` |
| `DATABASE_URL` | SQLite | SQLAlchemy async URL |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |
| `SECRET_KEY` | dev key | JWT signing secret |
| `REPORTS_DIR` | `reports` | PDF storage path |
| `DEBUG` | `false` | SQLAlchemy echo |
