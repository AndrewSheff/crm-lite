"""CRM Lite — главный файл приложения. Lifespan, middleware, роутеры."""

import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import limiter

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения — инициализация при старте."""
    setup_logging(settings.DEBUG)
    log.info("starting_app", version=settings.APP_VERSION)

    # Миграции
    try:
        subprocess.run(  # noqa: S603
            ["alembic", "upgrade", "head"],  # noqa: S607
            cwd=".",
            check=True,
            capture_output=True,
        )
        log.info("migrations_applied")
    except Exception as e:
        log.warning("migrations_skipped", error=str(e))

    yield

    log.info("shutting_down")


app = FastAPI(
    title="CRM Lite",
    description="Легковесная CRM для малого и среднего бизнеса",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Обработчик кастомных ошибок — отдаем JSON."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Роутеры
from app.api.v1.activities import router as activities_router  # noqa: E402
from app.api.v1.auth import router as auth_router  # noqa: E402
from app.api.v1.clients import router as clients_router  # noqa: E402
from app.api.v1.dashboard import router as dashboard_router  # noqa: E402
from app.api.v1.deals import router as deals_router  # noqa: E402
from app.api.v1.export import router as export_router  # noqa: E402
from app.api.v1.health import router as health_router  # noqa: E402
from app.api.v1.notes import router as notes_router  # noqa: E402
from app.api.v1.stages import router as stages_router  # noqa: E402
from app.api.v1.tags import router as tags_router  # noqa: E402
from app.api.v1.users import router as users_router  # noqa: E402

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(stages_router, prefix="/api/v1")
app.include_router(deals_router, prefix="/api/v1")
app.include_router(notes_router, prefix="/api/v1")
app.include_router(activities_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
