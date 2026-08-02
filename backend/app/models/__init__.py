"""Модели — тут экспортируем все, чтобы Alembic их подхватил."""

from app.models.activity import Activity
from app.models.client import Client
from app.models.deal import Deal
from app.models.note import Note
from app.models.stage import Stage
from app.models.tag import Tag, client_tags, deal_tags
from app.models.user import User

__all__ = [
    "Activity",
    "Client",
    "Deal",
    "Note",
    "Stage",
    "Tag",
    "User",
    "client_tags",
    "deal_tags",
]
