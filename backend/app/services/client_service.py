"""Сервис клиентов — CRUD с поиском, фильтрами, тегами и owner-based доступом."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.client import Client
from app.models.deal import Deal
from app.models.tag import Tag
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate

log = get_logger(__name__)


async def create_client(
    data: ClientCreate, user: User, db: AsyncSession
) -> dict:
    """Создание клиента — привязка owner + теги."""
    client = Client(
        name=data.name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        industry=data.industry,
        website=data.website,
        address=data.address,
        status=data.status,
        source=data.source,
        owner_id=user.id,
    )

    # привязываем теги
    if data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        client.tags = list(result.scalars().all())

    db.add(client)
    await db.flush()

    log.info("client_created", client_id=str(client.id))
    return await _to_response(client, db)


async def get_client(client_id: UUID, user: User, db: AsyncSession) -> dict:
    """Получение клиента — owner-based доступ."""
    client = await _get_client_or_404(client_id, db)
    _check_access(client, user)
    return await _to_response(client, db)


async def list_clients(
    user: User,
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    status: str | None = None,
    owner_id: UUID | None = None,
    tag_id: UUID | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> dict:
    """Список клиентов — пагинация, поиск, фильтры, owner-based доступ."""
    query = select(Client).options(joinedload(Client.owner), joinedload(Client.tags))

    # owner-based: manager видит только своих
    if user.role != "admin":
        query = query.where(Client.owner_id == user.id)
    elif owner_id:
        query = query.where(Client.owner_id == owner_id)

    if search:
        safe_search = search.replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{safe_search}%"
        query = query.where(
            or_(
                Client.name.ilike(pattern),
                Client.email.ilike(pattern),
                Client.company.ilike(pattern),
            )
        )

    if status:
        query = query.where(Client.status == status)

    if tag_id:
        query = query.where(Client.tags.any(Tag.id == tag_id))

    # count-запрос без joinedload — строим отдельно с теми же фильтрами
    count_q = select(func.count(Client.id))
    if user.role != "admin":
        count_q = count_q.where(Client.owner_id == user.id)
    elif owner_id:
        count_q = count_q.where(Client.owner_id == owner_id)
    if search:
        count_q = count_q.where(
            or_(
                Client.name.ilike(pattern),
                Client.email.ilike(pattern),
                Client.company.ilike(pattern),
            )
        )
    if status:
        count_q = count_q.where(Client.status == status)
    if tag_id:
        count_q = count_q.where(Client.tags.any(Tag.id == tag_id))
    total = (await db.execute(count_q)).scalar() or 0

    # сортировка — только допустимые поля
    sortable = {"name", "email", "company", "status", "created_at"}
    if sort_by not in sortable:
        sort_by = "created_at"
    sort_col = getattr(Client, sort_by)
    order = sort_col.desc() if sort_order == "desc" else sort_col.asc()
    query = query.order_by(order)
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    clients = result.unique().scalars().all()

    # собираем статистику по сделкам одним запросом — без N+1
    if clients:
        client_ids = [c.id for c in clients]
        stats_q = (
            select(
                Deal.client_id,
                func.count(Deal.id).label("cnt"),
                func.coalesce(func.sum(Deal.amount), 0).label("revenue"),
            )
            .where(Deal.client_id.in_(client_ids))
            .group_by(Deal.client_id)
        )
        stats_result = await db.execute(stats_q)
        stats_map = {row.client_id: (row.cnt, float(row.revenue)) for row in stats_result.all()}
    else:
        stats_map = {}

    items = []
    for c in clients:
        cnt, rev = stats_map.get(c.id, (0, 0.0))
        resp = ClientResponse.model_validate(c)
        resp.deals_count = cnt
        resp.total_revenue = rev
        items.append(resp.model_dump())

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def update_client(
    client_id: UUID, data: ClientUpdate, user: User, db: AsyncSession
) -> dict:
    """Обновление клиента — owner-based доступ."""
    client = await _get_client_or_404(client_id, db)
    _check_access(client, user)

    update_data = data.model_dump(exclude_unset=True)

    # теги отдельно обрабатываем
    tag_ids = update_data.pop("tag_ids", None)
    if tag_ids is not None:
        result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        client.tags = list(result.scalars().all())

    # обновляем только допустимые поля — без id, owner_id, created_at
    allowed = {"name", "email", "phone", "company", "industry", "website", "address", "status", "source"}
    for field, value in update_data.items():
        if field in allowed:
            setattr(client, field, value)

    await db.flush()
    log.info("client_updated", client_id=str(client_id))
    return await _to_response(client, db)


async def delete_client(
    client_id: UUID, user: User, db: AsyncSession
) -> dict:
    """Удаление клиента — owner-based доступ."""
    client = await _get_client_or_404(client_id, db)
    _check_access(client, user)

    await db.delete(client)
    await db.flush()
    log.info("client_deleted", client_id=str(client_id))
    return {"message": "Клиент удален"}


# --- хелперы ---


async def _get_client_or_404(client_id: UUID, db: AsyncSession) -> Client:
    """Ищем клиента или кидаем 404."""
    result = await db.execute(
        select(Client)
        .options(joinedload(Client.owner), joinedload(Client.tags))
        .where(Client.id == client_id)
    )
    client = result.unique().scalar_one_or_none()
    if not client:
        raise NotFoundError("Клиент не найден")
    return client


def _check_access(client: Client, user: User) -> None:
    """Проверяем доступ — manager видит только своих."""
    if user.role != "admin" and client.owner_id != user.id:
        raise ForbiddenError("Нет доступа к этому клиенту")


async def _to_response(client: Client, db: AsyncSession) -> dict:
    """Формируем ответ — считаем deals_count и total_revenue."""
    # подсчет сделок и выручки
    stats = await db.execute(
        select(
            func.count(Deal.id),
            func.coalesce(func.sum(Deal.amount), 0),
        ).where(Deal.client_id == client.id)
    )
    row = stats.one()
    deals_count = row[0]
    total_revenue = float(row[1])

    resp = ClientResponse.model_validate(client)
    resp.deals_count = deals_count
    resp.total_revenue = total_revenue
    return resp.model_dump()
