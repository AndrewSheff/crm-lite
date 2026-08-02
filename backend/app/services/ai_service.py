"""AI-сервис — генерация резюме по сделке через Anthropic или OpenAI."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AppError, NotFoundError
from app.core.logging import get_logger
from app.models.activity import Activity
from app.models.deal import Deal
from app.models.note import Note

log = get_logger(__name__)

# кешируем клиенты — один HTTP-пул на все запросы
_anthropic_client = None
_openai_client = None


async def generate_deal_summary(deal_id: UUID, db: AsyncSession) -> dict:
    """Собираем контекст по сделке и генерируем AI-резюме."""
    # получаем сделку
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise NotFoundError("Сделка не найдена")

    # собираем заметки
    notes_result = await db.execute(
        select(Note.content)
        .where(Note.deal_id == deal_id)
        .order_by(Note.created_at)
    )
    notes = [row[0] for row in notes_result.all()]

    # собираем активности
    activities_result = await db.execute(
        select(Activity.type, Activity.title, Activity.description)
        .where(Activity.deal_id == deal_id)
        .order_by(Activity.created_at)
    )
    activities = [
        f"[{row[0]}] {row[1]}" + (f": {row[2]}" if row[2] else "")
        for row in activities_result.all()
    ]

    # формируем промпт
    context_parts = [f"Сделка: {deal.title}"]
    if deal.amount:
        context_parts.append(f"Сумма: {deal.amount} {deal.currency}")
    if deal.description:
        context_parts.append(f"Описание: {deal.description}")
    if notes:
        context_parts.append("Заметки:\n" + "\n".join(f"- {n}" for n in notes))
    if activities:
        context_parts.append(
            "Активности:\n" + "\n".join(f"- {a}" for a in activities)
        )

    context = "\n\n".join(context_parts)
    prompt = (
        "Составь краткое резюме по сделке на основе данных ниже. "
        "Выдели ключевые моменты, текущий статус и рекомендации. "
        "Ответ на русском, 3-5 предложений.\n\n" + context
    )

    # вызываем AI
    try:
        summary = await _call_ai(prompt)
    except Exception as e:
        log.error("ai_summary_failed", deal_id=str(deal_id), error=str(e))
        raise AppError("Не удалось сгенерировать резюме. Попробуйте позже.") from e

    return {"summary": summary}


async def _call_ai(prompt: str) -> str:
    """Вызов AI-провайдера — Anthropic или OpenAI."""
    provider = settings.AI_PROVIDER

    if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _call_anthropic(prompt)
    elif provider == "openai" and settings.OPENAI_API_KEY:
        return await _call_openai(prompt)
    else:
        raise AppError(
            "AI-провайдер не настроен. Укажите ANTHROPIC_API_KEY или OPENAI_API_KEY."
        )


def _get_anthropic_client():
    """Ленивое создание Anthropic-клиента — переиспользуем HTTP-пул."""
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic

        _anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _get_openai_client():
    """Ленивое создание OpenAI-клиента — переиспользуем HTTP-пул."""
    global _openai_client
    if _openai_client is None:
        from openai import AsyncOpenAI

        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


async def _call_anthropic(prompt: str) -> str:
    """Вызов Anthropic Claude API."""
    client = _get_anthropic_client()
    message = await client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


async def _call_openai(prompt: str) -> str:
    """Вызов OpenAI API."""
    client = _get_openai_client()
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""
