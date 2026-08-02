"""Схемы импорта/экспорта."""

from pydantic import BaseModel


class ImportResult(BaseModel):
    created: int = 0
    skipped: int = 0
    errors: list[str] = []
