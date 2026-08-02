"""Кастомные исключения — иерархия ошибок приложения."""

from fastapi import HTTPException


class AppError(HTTPException):
    """Базовая ошибка приложения — все остальные наследуются от нее."""

    def __init__(self, detail: str = "Внутренняя ошибка", status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    """404 — ресурс не найден."""

    def __init__(self, detail: str = "Не найдено"):
        super().__init__(detail=detail, status_code=404)


class ConflictError(AppError):
    """409 — конфликт данных (дубликат и т.п.)."""

    def __init__(self, detail: str = "Конфликт данных"):
        super().__init__(detail=detail, status_code=409)


class ForbiddenError(AppError):
    """403 — нет прав доступа."""

    def __init__(self, detail: str = "Доступ запрещен"):
        super().__init__(detail=detail, status_code=403)


class UnauthorizedError(AppError):
    """401 — не аутентифицирован."""

    def __init__(self, detail: str = "Не авторизован"):
        super().__init__(detail=detail, status_code=401)
        self.headers = {"WWW-Authenticate": "Bearer"}
