# CRM Lite

Легковесная CRM-система для малого и среднего бизнеса. Управление клиентами, сделками, канбан-доска, аналитика и AI-ассистент.

## Стек технологий

**Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16, Redis 7, Alembic, Pydantic 2
**Frontend:** React 19, TypeScript, Vite 6, TailwindCSS v4, shadcn/ui, React Query v5
**Инфраструктура:** Docker, Nginx, GitHub Actions (CI/CD)

## Быстрый старт

### Требования

- Docker и Docker Compose v2+

### Запуск

```bash
git clone https://github.com/AndrewSheff/crm-lite.git
cd crm-lite
cp .env.example .env
# отредактируй .env — поменяй SECRET_KEY, DB_PASSWORD, ADMIN_PASSWORD
docker compose up -d
```

Приложение будет доступно на http://localhost

### Дефолтный вход

- Email: `admin@crm-lite.local`
- Пароль: значение `ADMIN_PASSWORD` из `.env`

## API документация

Swagger UI: http://localhost/docs
OpenAPI JSON: http://localhost/openapi.json

## Функциональность

- **Клиенты** — CRUD, поиск, фильтрация, теги, экспорт/импорт Excel
- **Сделки** — канбан-доска с drag & drop, стадии воронки, приоритеты
- **Аналитика** — дашборд со статистикой, воронка продаж, график выручки
- **Активности** — звонки, встречи, письма, задачи с привязкой к клиентам и сделкам
- **Заметки** — текстовые заметки с пинами
- **AI-ассистент** — анализ клиента и рекомендации (Anthropic / OpenAI)
- **Пользователи** — роли admin/manager, owner-based доступ

## Разработка

### Локальный запуск без Docker

**Backend:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Тесты

```bash
cd backend
python3 -m pytest tests/ -q
```

### Линтинг

```bash
# Backend
ruff check backend/

# Frontend
cd frontend && npm run lint && npx tsc --noEmit
```

## Структура проекта

```
crm-lite/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # роутеры (auth, clients, deals, ...)
│   │   ├── core/            # exceptions, logging, rate_limit, security
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── services/        # бизнес-логика
│   │   ├── config.py        # настройки из env
│   │   ├── database.py      # подключение к БД
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # миграции БД
│   ├── tests/               # pytest тесты
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # HTTP-клиент и API функции
│   │   ├── components/      # UI-компоненты (shadcn/ui)
│   │   ├── contexts/        # AuthContext
│   │   ├── hooks/           # React Query хуки
│   │   ├── lib/             # утилиты
│   │   └── pages/           # страницы приложения
│   └── Dockerfile
├── docker/nginx/             # конфиг Nginx
├── .github/workflows/        # CI/CD
├── docker-compose.yml
└── .env.example
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `DB_USER` | Пользователь PostgreSQL | `crm_user` |
| `DB_PASSWORD` | Пароль PostgreSQL | `secret` |
| `REDIS_URL` | Адрес Redis | `redis://redis:6379/0` |
| `SECRET_KEY` | Секрет для JWT-токенов | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access токена | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh токена | `7` |
| `ADMIN_EMAIL` | Email администратора | `admin@crm-lite.local` |
| `ADMIN_PASSWORD` | Пароль администратора | — |
| `ANTHROPIC_API_KEY` | Ключ Anthropic API | — |
| `OPENAI_API_KEY` | Ключ OpenAI API | — |
| `AI_PROVIDER` | Провайдер AI (anthropic/openai) | `anthropic` |
| `CORS_ORIGINS` | Разрешенные origins | `http://localhost` |
| `APP_PORT` | Порт приложения | `80` |

## Лицензия

MIT
