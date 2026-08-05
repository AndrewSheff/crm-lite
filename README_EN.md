<!--
  BANNER: см. github_resume/DESIGN_SYSTEM.md — CRM Lite
  Сохранить как assets/banner.png и раскомментировать:
-->
<!-- <img src="assets/banner.png" alt="CRM Lite" width="100%"> -->

<div align="center">

> **[Русская версия / Russian version](README.md)**

# CRM Lite

### Lightweight CRM for Growing Teams

[![CI/CD](https://github.com/AndrewSheff/crm-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/AndrewSheff/crm-lite/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Manage clients, track deals on a Kanban board, analyze your sales pipeline, and get AI-powered insights — all self-hosted, zero monthly fees.**

[Quick Start](#-quick-start) · [Features](#-features) · [Screenshots](#-screenshots) · [Architecture](#-architecture) · [API](#-api-documentation)

</div>

---

> **The Problem:** Small businesses track clients in spreadsheets, deals in notebooks, and tasks in their heads. Enterprise CRMs cost $50-150/user/month and take weeks to set up. When a sales rep leaves, all contacts and deal history disappear.

**CRM Lite** is a self-hosted CRM that deploys in 5 minutes. Kanban board for visual deal management, sales pipeline analytics, AI assistant for deal recommendations, and Excel import to migrate from spreadsheets instantly.

<div align="center">

| Lines of Code | API Endpoints | DB Models | Pages | Tests | Docker Services |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **10,000+** | **47** | **9** | **15** | **8 files** | **5** |

</div>

---

## Screenshots

| Kanban Board | Dashboard |
|:------------:|:---------:|
| ![Kanban](screenshots/kanban.png) | ![Dashboard](screenshots/dashboard.png) |

---

## Features

**Kanban Deal Board** — visual pipeline with drag & drop (@dnd-kit). Move deals between stages, see win/loss indicators, filter by priority. Real-time stage counts and total values.

**Client Management** — full CRUD with search, filtering, and color-coded tags. Owner-based access control. Contact history and linked deals in one place.

**Sales Pipeline Analytics** — dashboard with revenue trends, conversion funnel, average deal size, and win rate. Activity feed showing team actions in real time.

**AI Assistant** — Claude or GPT analyzes deals and recommends next best action. Risk assessment, closing probability, and suggested follow-up strategy.

**Activities & Notes** — log calls, meetings, emails, and tasks with due dates. Pin important notes to deals. Full activity timeline per client and deal.

**Excel Import/Export** — bulk migration from spreadsheets with column mapping and duplicate detection. Export clients and deals to XLSX for reporting.

**Customizable Pipeline** — define your own stages (New, Negotiation, Proposal, Closed Won, etc.) with colors and order. Adapt to any sales process.

**Role-Based Access** — Admin (full access), Manager (own clients and deals), Viewer (read-only). JWT authentication with refresh tokens.

**Enterprise Security** — bcrypt password hashing, rate limiting, CORS configuration, structured JSON logging with request tracing.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    Nginx :80                      │
│               Reverse Proxy + Headers             │
├──────────────────┬───────────────────────────────┤
│  Frontend :3000  │        Backend :8000           │
│  React 19 + Vite │     FastAPI + Uvicorn          │
│  TailwindCSS v4  │     SQLAlchemy 2.0 (async)     │
│  @dnd-kit Kanban │   ┌────────────────────────┐   │
│  Recharts        │   │     Business Logic      │   │
│  15 pages        │   │  Clients · Deals · AI   │   │
│                  │   │  Activities · Export     │   │
│                  │   └────────────────────────┘   │
├──────────────────┴───────────────────────────────┤
│   PostgreSQL 16              Redis 7              │
│   9 models, Alembic          Rate Limiting        │
│   Indexes, FKs               Session Cache        │
└──────────────────────────────────────────────────┘
```

### Kanban Data Flow

```
User drags deal card
        |
        v
  [@dnd-kit DragEnd]
        |
        v
  PATCH /api/v1/deals/{id}
  { "stage_id": new_stage }
        |
        v
  [Backend validates transition]
  [Updates deal + creates activity log]
        |
        v
  [React Query invalidates cache]
  [Kanban re-renders with new position]
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose v2+
- (Optional) Anthropic or OpenAI API key for AI assistant

### 1. Clone and configure

```bash
git clone https://github.com/AndrewSheff/crm-lite.git
cd crm-lite
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-random-64-char-string    # required
ADMIN_PASSWORD=SecurePass123             # required
ANTHROPIC_API_KEY=sk-ant-...             # optional, for AI assistant
```

### 2. Launch

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|:--------|:----|
| Application | http://localhost |
| API Docs (Swagger) | http://localhost/docs |

Login with admin credentials from `.env`.

---

## Tech Stack

| Layer | Technology | Version |
|:------|:-----------|:--------|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Alembic | 3.13, 0.115, 2.0 |
| **Frontend** | React, TypeScript, Vite, TailwindCSS, shadcn/ui | 19, 5+, 6, v4 |
| **Kanban** | @dnd-kit (drag & drop) | Latest |
| **Charts** | Recharts | 2.15 |
| **Database** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **AI** | Anthropic Claude, OpenAI GPT | Latest |
| **Export** | openpyxl | XLSX |
| **Auth** | JWT (access + refresh) + bcrypt | HS256 |
| **Infra** | Docker Compose, Nginx, GitHub Actions CI/CD | Multi-stage |
| **Logging** | structlog (JSON) | Request tracing |

---

## API Documentation

Interactive Swagger at `/docs`. **47 endpoints** across 11 groups:

| Group | Prefix | Endpoints |
|:------|:-------|:----------|
| Auth | `/api/v1/auth` | Register, login, token refresh, profile |
| Clients | `/api/v1/clients` | CRUD, search, filtering, tags |
| Deals | `/api/v1/deals` | CRUD, stage transitions, AI analysis |
| Notes | `/api/v1/notes` | Create, pin, list per deal/client |
| Activities | `/api/v1/activities` | Log calls, meetings, tasks |
| Tags | `/api/v1/tags` | Tag management |
| Stages | `/api/v1/stages` | Pipeline stage configuration |
| Users | `/api/v1/users` | User management and roles |
| Dashboard | `/api/v1/dashboard` | Stats, funnel, revenue trends |
| Export | `/api/v1/export` | Excel import/export |
| Health | `/api/v1/health` | Liveness probe |

---

## Project Structure

```
crm-lite/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with lifespan
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── api/v1/              # 11 REST API routers
│   │   ├── models/              # 9 SQLAlchemy models
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── services/            # Business logic + AI
│   │   └── core/                # Security, logging, exceptions
│   ├── tests/                   # Pytest tests (8 files)
│   ├── alembic/                 # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API clients
│   │   ├── components/          # UI + Kanban board
│   │   ├── contexts/            # Auth context
│   │   ├── pages/               # 15 page components
│   │   └── lib/                 # Utilities
│   └── Dockerfile
├── docker/nginx/
├── .github/workflows/           # CI/CD
├── docker-compose.yml           # 5 services
└── .env.example
```

---

## Environment Variables

| Variable | Required | Default | Description |
|:---------|:---------|:--------|:------------|
| `SECRET_KEY` | Yes | -- | JWT signing key (min 32 chars) |
| `ADMIN_PASSWORD` | Yes | -- | Initial admin password |
| `DATABASE_URL` | No | Auto | PostgreSQL connection |
| `REDIS_URL` | No | Auto | Redis connection |
| `ANTHROPIC_API_KEY` | No | -- | For Claude AI assistant |
| `OPENAI_API_KEY` | No | -- | For GPT AI assistant |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `CORS_ORIGINS` | No | `localhost` | Allowed CORS origins |

---

## Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest tests/ -v

# Lint
ruff check backend/
cd frontend && npm run lint && npx tsc --noEmit
```

---

## License

[MIT](LICENSE) — free for commercial use.
