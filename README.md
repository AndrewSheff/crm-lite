<div align="center">

# CRM Lite

### Lightweight CRM for Small & Medium Business

[![CI/CD](https://github.com/AndrewSheff/crm-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/AndrewSheff/crm-lite/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript 5.7](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A modern CRM that's actually simple to use.**
Manage clients, track deals on a Kanban board, analyze your sales pipeline, and get AI-powered insights -- all in one self-hosted application.

[Quick Start](#-quick-start) &bull; [Features](#-features) &bull; [Architecture](#-architecture) &bull; [API](#-api-documentation) &bull; [Screenshots](#-screenshots)

</div>

---

## The Problem

> Small businesses track clients in spreadsheets, deals in notebooks, and activities in their heads. Enterprise CRMs (Salesforce, HubSpot) are too complex and expensive ($50-150/user/month). When a manager quits, client relationships leave with them.

**CRM Lite** is a self-hosted CRM designed for teams of 2-30 people. It takes 5 minutes to deploy, has zero monthly fees, and covers the essentials: client management, deal tracking with a Kanban board, activity logging, analytics dashboard, and an AI assistant that helps close deals.

**Key metrics:**
- 10,000+ lines of production-ready code
- 47 API endpoints with Swagger documentation
- 9 database models with Alembic migrations
- 15 frontend pages including Kanban board with drag & drop
- 8 test files with automated tests
- AI assistant (Claude / GPT) for deal analysis
- Excel import/export
- CI/CD pipeline with GitHub Actions
- Docker Compose: one command to deploy

---

## Screenshots

| Login | Dashboard | Clients |
|:-----:|:---------:|:-------:|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) | ![Clients](screenshots/clients.png) |

| Kanban Board | Deal Detail | AI Assistant |
|:------------:|:-----------:|:------------:|
| ![Kanban](screenshots/kanban.png) | ![Deal](screenshots/deal-detail.png) | ![AI](screenshots/ai-assistant.png) |

---

## Features

### Client Management
Full CRUD with search, filtering, and tagging. Track company, industry, source, status, and contact details. Owner-based access control -- managers see only their clients, admins see everything.

### Kanban Deal Board
Visual deal pipeline with drag & drop. Move deals between stages, set probability and expected close date. Automatic position tracking within stages. Color-coded stage columns with win/loss indicators.

### Sales Pipeline Analytics
Dashboard with key metrics: total revenue, deal count, conversion rate, average deal size. Sales funnel visualization showing conversion at each stage. Revenue chart over time. Activity feed showing latest actions across the team.

### Activities & Notes
Track calls, meetings, emails, and tasks with due dates. Pin important notes to the top. Link activities to clients and/or deals for full context. Mark as completed with timestamps.

### AI Assistant
Claude or GPT analyzes client data, deal history, and activities to generate recommendations: next best action, risk assessment, closing probability, and suggested follow-ups.

### Excel Import/Export
Export clients to XLSX with all fields. Import from Excel with automatic column mapping, duplicate detection (by email), and validation. Bulk operations for data migration.

### Role-Based Access
Three roles: **Admin** (full access, user management), **Manager** (CRUD on own clients/deals), **Viewer** (read-only). Owner-based filtering ensures data isolation between managers.

### Enterprise Security
JWT authentication with access + refresh tokens. bcrypt password hashing. Rate limiting on auth endpoints. Forced password change on first login. Structured JSON logging with structlog.

---

## Architecture

```
                     +------------------+
                     |   Nginx:80       |
                     |  Reverse Proxy   |
                     +--------+---------+
                              |
               +--------------+--------------+
               |                             |
       +-------+-------+           +--------+--------+
       | Frontend:3000 |           |  Backend:8000   |
       | React 19 SPA  |           |  FastAPI        |
       | Kanban DnD    |           |  47 endpoints   |
       | Recharts      |           +---+--------+----+
       +---------------+               |        |
                              +--------+--+  +--+--------+
                              | PostgreSQL|  |   Redis   |
                              |   :5432   |  |   :6379   |
                              |  9 models |  | Rate Limit|
                              +-----------+  +-----------+
```

### Data Model

```
Users (admin/manager/viewer)
  |
  +---> Clients (name, company, industry, tags, status)
  |       |
  |       +---> Notes (text, pinned, author)
  |       +---> Activities (call/meeting/email/task, scheduled_at)
  |       +---> Deals
  |
  +---> Deals (title, amount, probability, expected_close)
          |
          +---> Stage (pipeline position, color, won/lost)
          +---> Notes
          +---> Activities
          +---> Tags (M2M)
```

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Alembic | 3.13, 0.115, 2.0 |
| **Frontend** | React, TypeScript, Vite, TailwindCSS, shadcn/ui | 19, 5.7, 6.3, v4 |
| **Kanban** | @dnd-kit (drag & drop) | Latest |
| **Charts** | Recharts | 2.15 |
| **Database** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **AI** | Anthropic Claude, OpenAI GPT | Latest |
| **Auth** | JWT (access + refresh) + bcrypt | HS256 |
| **Export** | openpyxl | XLSX |
| **Infra** | Docker Compose, Nginx, GitHub Actions | Multi-stage |
| **Logging** | structlog (JSON) | Production-ready |
| **Testing** | Pytest (async) | 8 test files |

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
SECRET_KEY=your-random-64-char-secret-key-here
ADMIN_PASSWORD=SecurePass123
DB_PASSWORD=strong-db-password
ANTHROPIC_API_KEY=sk-ant-...     # optional, for AI assistant
```

### 2. Launch

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|---------|-----|
| Application | http://localhost |
| API Docs (Swagger) | http://localhost/docs |

Login with `admin@crm-lite.local` / password from `.env`. You'll be prompted to change the password on first login.

### 4. Get started

1. Go to **Clients** and add your first clients
2. Set up **Stages** for your sales pipeline (Settings)
3. Create **Deals** and drag them on the Kanban board
4. Try the **AI Assistant** on any deal for recommendations

---

## API Documentation

Interactive Swagger documentation at `/docs`. **47 endpoints** across 11 groups:

| Group | Prefix | Description |
|-------|--------|-------------|
| **Auth** | `/api/v1/auth` | Register, login, refresh, change password, profile |
| **Clients** | `/api/v1/clients` | Client CRUD, search, filtering |
| **Deals** | `/api/v1/deals` | Deal CRUD, Kanban view, stage moves |
| **Notes** | `/api/v1/notes` | Notes CRUD with pinning |
| **Activities** | `/api/v1/activities` | Call/meeting/email/task tracking |
| **Tags** | `/api/v1/tags` | Tag management |
| **Stages** | `/api/v1/stages` | Pipeline stage management |
| **Users** | `/api/v1/users` | Admin user management |
| **Dashboard** | `/api/v1/dashboard` | Stats, pipeline, revenue, activity feed |
| **Export** | `/api/v1/export` | Excel export/import |
| **Health** | `/api/v1/health` | Liveness probe |

All endpoints use Pydantic v2 validation, structured error responses, and rate limiting.

---

## Project Structure

```
crm-lite/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app with lifespan
│   │   ├── config.py                # Pydantic settings from .env
│   │   ├── database.py              # Async SQLAlchemy engine
│   │   ├── api/v1/                  # 11 REST API routers
│   │   ├── models/                  # 9 SQLAlchemy models
│   │   ├── schemas/                 # Pydantic v2 schemas
│   │   ├── services/                # 13 business logic files
│   │   │   ├── deal_service.py      # Kanban logic, stage transitions
│   │   │   ├── ai_service.py        # Claude/GPT integration
│   │   │   ├── export_service.py    # Excel import/export
│   │   │   └── dashboard_service.py # Analytics aggregation
│   │   └── core/                    # Security, logging, exceptions
│   ├── tests/                       # 8 pytest test files
│   ├── alembic/                     # Database migrations
│   └── Dockerfile                   # Multi-stage Python build
├── frontend/
│   ├── src/
│   │   ├── api/                     # 12 typed API client modules
│   │   ├── hooks/                   # 9 React Query hooks
│   │   ├── contexts/                # Auth context provider
│   │   ├── components/              # 21 UI components + Kanban
│   │   │   ├── kanban/              # KanbanBoard, Column, Card (DnD)
│   │   │   └── ui/                  # shadcn/ui primitives
│   │   ├── pages/                   # 15 page components
│   │   └── lib/                     # Utilities
│   └── Dockerfile                   # Node build + Nginx serve
├── docker/nginx/                    # Reverse proxy config
├── .github/workflows/               # CI (lint+test+build) + CD
├── docker-compose.yml               # 5 services with health checks
└── .env.example
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | -- | JWT signing key (min 32 chars) |
| `ADMIN_PASSWORD` | Yes | -- | Initial admin password |
| `DB_USER` | No | `crm_user` | PostgreSQL username |
| `DB_PASSWORD` | No | `secret` | PostgreSQL password |
| `REDIS_URL` | No | Auto-configured | Redis connection |
| `ANTHROPIC_API_KEY` | No | -- | Anthropic API key for Claude |
| `OPENAI_API_KEY` | No | -- | OpenAI API key for GPT |
| `AI_PROVIDER` | No | `anthropic` | AI provider choice |
| `CORS_ORIGINS` | No | `localhost` | Allowed CORS origins |
| `DEBUG` | No | `false` | Debug mode |

---

## Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

docker compose up -d postgres redis
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Testing

```bash
cd backend && pytest tests/ -v
```

### Linting

```bash
ruff check backend/                  # Python
cd frontend && npm run lint          # TypeScript (ESLint)
npx tsc --noEmit                     # Type check
```

---

## License

[MIT](LICENSE) -- free for commercial use.
