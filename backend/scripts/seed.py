"""Сид-скрипт — заполняет БД демо-данными для презентации."""

import asyncio
import random
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# чтобы можно было запускать из корня бэкенда
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.database import async_session  # noqa: E402
from app.models.activity import Activity  # noqa: E402
from app.models.client import Client  # noqa: E402
from app.models.deal import Deal  # noqa: E402
from app.models.note import Note  # noqa: E402
from app.models.stage import Stage  # noqa: E402
from app.models.tag import Tag  # noqa: E402
from app.models.user import User  # noqa: E402

# дефолтный пароль для демо-пользователей
DEMO_PASSWORD = hash_password("demo1234")  # noqa: S106


async def seed_admin() -> User:
    """Создаем дефолтного админа если его еще нет."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  Админ {settings.ADMIN_EMAIL} уже существует")
            return existing

        admin = User(
            email=settings.ADMIN_EMAIL,
            name="Администратор",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role="admin",
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        print(f"  Создан админ: {settings.ADMIN_EMAIL}")
        return admin


async def seed_users() -> list[User]:
    """Создаем менеджеров и вьювера."""
    users_data = [
        ("Иван Петров", "ivan@example.com", "manager"),
        ("Мария Сидорова", "maria@example.com", "manager"),
        ("Алексей Козлов", "alexey@example.com", "manager"),
        ("Ольга Наблюдатель", "olga@example.com", "viewer"),
    ]
    result = []
    async with async_session() as session:
        for name, email, role in users_data:
            existing = await session.execute(
                select(User).where(User.email == email)
            )
            user = existing.scalar_one_or_none()
            if user:
                print(f"  Пользователь {email} уже существует")
                result.append(user)
                continue

            user = User(
                email=email,
                name=name,
                hashed_password=DEMO_PASSWORD,
                role=role,
            )
            session.add(user)
            await session.flush()
            result.append(user)
        await session.commit()
        print(f"  Создано {len(users_data)} пользователей")
    return result


async def seed_stages() -> list[Stage]:
    """Создаем 6 стадий воронки продаж."""
    stages_data = [
        ("Новая заявка", 0, "#64748b", False, False),
        ("Квалификация", 1, "#3b82f6", False, False),
        ("Предложение", 2, "#8b5cf6", False, False),
        ("Переговоры", 3, "#f59e0b", False, False),
        ("Выиграна", 4, "#22c55e", True, False),
        ("Проиграна", 5, "#ef4444", False, True),
    ]
    result = []
    async with async_session() as session:
        existing = await session.execute(select(Stage))
        if existing.scalars().first():
            # стадии уже есть — получаем их
            all_stages = await session.execute(
                select(Stage).order_by(Stage.position)
            )
            result = list(all_stages.scalars().all())
            print(f"  Стадии уже существуют ({len(result)} шт.)")
            return result

        for name, pos, color, is_won, is_lost in stages_data:
            stage = Stage(
                name=name, position=pos, color=color,
                is_won=is_won, is_lost=is_lost,
            )
            session.add(stage)
            await session.flush()
            result.append(stage)
        await session.commit()
        print(f"  Создано {len(stages_data)} стадий")
    return result


async def seed_tags() -> list[Tag]:
    """Создаем 5 тегов."""
    tags_data = [
        ("VIP", "#eab308"),
        ("Горячий", "#ef4444"),
        ("Холодный", "#3b82f6"),
        ("Повторный", "#22c55e"),
        ("Корпоративный", "#8b5cf6"),
    ]
    result = []
    async with async_session() as session:
        existing = await session.execute(select(Tag))
        if existing.scalars().first():
            all_tags = await session.execute(select(Tag))
            result = list(all_tags.scalars().all())
            print(f"  Теги уже существуют ({len(result)} шт.)")
            return result

        for name, color in tags_data:
            tag = Tag(name=name, color=color)
            session.add(tag)
            await session.flush()
            result.append(tag)
        await session.commit()
        print(f"  Создано {len(tags_data)} тегов")
    return result


async def seed_clients(managers: list[User], tags: list[Tag]) -> list[Client]:
    """Создаем 18 демо-клиентов."""
    clients_data = [
        ("ООО Альфа-Тех", "alpha@tech.ru", "+7 (495) 111-11-11", "Альфа-Тех", "IT", "active"),
        ("ИП Борисов", "borisov@mail.ru", "+7 (812) 222-22-22", None, "Торговля", "lead"),
        ("ЗАО Гамма Строй", "info@gamma.ru", "+7 (495) 333-33-33", "Гамма Строй", "Строительство", "active"),
        ("ООО Дельта Логистик", "delta@logistics.ru", "+7 (495) 444-44-44", "Дельта Логистик", "Логистика", "active"),
        ("ИП Егоров А.С.", "egorov@bk.ru", "+7 (903) 555-55-55", None, "Услуги", "lead"),
        ("ПАО Зета Банк", "corp@zetabank.ru", "+7 (495) 666-66-66", "Зета Банк", "Финансы", "active"),
        ("ООО Йота Медиа", "hello@iotamedia.ru", "+7 (495) 777-77-77", "Йота Медиа", "Медиа", "active"),
        ("ИП Климов Р.Д.", "klimov@ya.ru", "+7 (916) 888-88-88", None, "Консалтинг", "lead"),
        ("ООО Лямбда Софт", "sales@lambda.dev", "+7 (495) 999-99-99", "Лямбда Софт", "IT", "active"),
        ("ЗАО Мю Фарма", "info@mu-pharma.ru", "+7 (495) 101-01-01", "Мю Фарма", "Фармацевтика", "churned"),
        ("ООО Ню Энерго", "nu@energy.ru", "+7 (495) 102-02-02", "Ню Энерго", "Энергетика", "active"),
        ("ИП Павлова Е.Н.", "pavlova@inbox.ru", "+7 (926) 103-03-03", None, "Образование", "lead"),
        ("ООО Ро Авто", "ro@auto.ru", "+7 (495) 104-04-04", "Ро Авто", "Автомобили", "active"),
        ("ООО Сигма Клауд", "info@sigma.cloud", "+7 (495) 105-05-05", "Сигма Клауд", "IT", "active"),
        ("ИП Тихонов В.П.", "tikhonov@gmail.com", "+7 (905) 106-06-06", None, "Ритейл", "lead"),
        ("ООО Фи Дизайн", "hello@phi-design.ru", "+7 (495) 107-07-07", "Фи Дизайн", "Дизайн", "active"),
        ("ЗАО Хи Продакшн", "hi@chi-prod.ru", "+7 (495) 108-08-08", "Хи Продакшн", "Медиа", "churned"),
        ("ООО Омега Груп", "contact@omega.ru", "+7 (495) 109-09-09", "Омега Груп", "Холдинг", "active"),
    ]
    result = []
    async with async_session() as session:
        existing = await session.execute(select(Client))
        if existing.scalars().first():
            all_clients = await session.execute(select(Client))
            result = list(all_clients.scalars().all())
            print(f"  Клиенты уже существуют ({len(result)} шт.)")
            return result

        for i, (name, email, phone, company, industry, status) in enumerate(clients_data):
            owner = managers[i % len(managers)]
            source = random.choice(["website", "referral", "cold_call", "ad", "event"])  # noqa: S311
            client = Client(
                name=name, email=email, phone=phone, company=company,
                industry=industry, status=status, source=source,
                owner_id=owner.id,
                created_at=datetime.now(UTC) - timedelta(days=random.randint(5, 120)),  # noqa: S311
            )
            # навешиваем теги (1-2 случайных)
            client_tags_sample = random.sample(tags, k=min(random.randint(1, 2), len(tags)))  # noqa: S311
            client.tags = client_tags_sample
            session.add(client)
            await session.flush()
            result.append(client)
        await session.commit()
        print(f"  Создано {len(clients_data)} клиентов")
    return result


async def seed_deals(
    clients: list[Client],
    stages: list[Stage],
    managers: list[User],
    tags: list[Tag],
) -> list[Deal]:
    """Создаем 25 демо-сделок на разных стадиях."""
    deal_titles = [
        "Внедрение CRM-системы", "Поставка серверов", "Разработка мобильного приложения",
        "SEO-продвижение сайта", "Аудит информационной безопасности", "Годовое обслуживание",
        "Поставка оргтехники", "Интеграция 1С", "Обучение персонала", "Создание лендинга",
        "Миграция на облако", "Поставка лицензий Microsoft", "Техподдержка 24/7",
        "Разработка API-интеграции", "Редизайн корпоративного портала",
        "Автоматизация складского учета", "Внедрение ERP-системы",
        "Поставка сетевого оборудования", "Консалтинг по GDPR",
        "Разработка чат-бота", "Настройка VPN", "Облачное хранилище",
        "AI-аналитика продаж", "Видеонаблюдение офиса", "Digital-маркетинг кампания",
    ]
    amounts = [
        150_000, 320_000, 850_000, 95_000, 200_000, 480_000, 60_000, 420_000,
        180_000, 75_000, 1_200_000, 550_000, 360_000, 290_000, 700_000,
        450_000, 2_500_000, 680_000, 130_000, 240_000, 90_000, 110_000,
        1_800_000, 350_000, 500_000,
    ]
    priorities = ["low", "medium", "medium", "high", "medium"]

    result = []
    async with async_session() as session:
        existing = await session.execute(select(Deal))
        if existing.scalars().first():
            all_deals = await session.execute(select(Deal))
            result = list(all_deals.scalars().all())
            print(f"  Сделки уже существуют ({len(result)} шт.)")
            return result

        for i in range(25):
            client = clients[i % len(clients)]
            # распределяем по стадиям: больше в начале воронки
            stage_weights = [5, 5, 4, 3, 5, 3]
            stage_idx = random.choices(range(len(stages)), weights=stage_weights, k=1)[0]  # noqa: S311
            stage = stages[stage_idx]
            owner = managers[i % len(managers)]
            days_ago = random.randint(3, 90)  # noqa: S311
            created = datetime.now(UTC) - timedelta(days=days_ago)

            deal = Deal(
                title=deal_titles[i],
                client_id=client.id,
                stage_id=stage.id,
                owner_id=owner.id,
                amount=Decimal(str(amounts[i])),
                probability=random.choice([10, 25, 50, 75, 90]),  # noqa: S311
                priority=random.choice(priorities),  # noqa: S311
                position=i,
                created_at=created,
                updated_at=created + timedelta(days=random.randint(0, days_ago)),  # noqa: S311
                closed_at=created + timedelta(days=random.randint(5, 30)) if stage.is_won or stage.is_lost else None,  # noqa: S311
            )
            # 1-2 случайных тега
            deal.tags = random.sample(tags, k=min(random.randint(0, 2), len(tags)))  # noqa: S311
            session.add(deal)
            await session.flush()
            result.append(deal)
        await session.commit()
        print("  Создано 25 сделок")
    return result


async def seed_notes(
    clients: list[Client], deals: list[Deal], managers: list[User],
) -> None:
    """Создаем 22 демо-заметки."""
    note_contents = [
        "Клиент заинтересован в долгосрочном сотрудничестве, запросил прайс-лист.",
        "Обсудили детали проекта, нужно подготовить коммерческое предложение до пятницы.",
        "Запросили референсы по аналогичным проектам. Отправил 3 кейса.",
        "Встреча прошла продуктивно, договорились о пилотном проекте на 2 месяца.",
        "Клиент сравнивает нас с конкурентами. Нужна скидка ~10% для закрытия.",
        "Контактное лицо сменилось — новый ЛПР Смирнов Д.А., +7-999-XXX-XX-XX.",
        "Оплата задерживается, бухгалтерия на согласовании. Обещали до конца недели.",
        "Подписали NDA, можем приступать к аудиту.",
        "Клиент попросил перенести старт на 2 недели — отпуска у команды.",
        "Демо прошло отлично, ЛПР доволен. Ждем финальное согласование бюджета.",
        "Конкурент предложил дешевле на 15%, но без поддержки. Наш козырь — SLA.",
        "Нужно подготовить презентацию для совета директоров — формат PDF, до 10 слайдов.",
        "Договор на юр. проверке, обещали вернуть с правками в понедельник.",
        "Клиент доволен первым этапом, обсуждаем расширение скоупа.",
        "Жалоба на скорость отклика поддержки. Эскалировал тимлиду.",
        "Запросили интеграцию с их CRM — нужна доработка API.",
        "Провели воркшоп, обучили 12 сотрудников. Фидбэк положительный.",
        "Тестовый период заканчивается через 5 дней, нужно связаться для продления.",
        "Отправил акт выполненных работ, ждем подпись.",
        "Клиент рекомендовал нас партнерам — ожидаем входящий запрос от ООО Вектор.",
        "Пересмотрели условия: вместо единоразовой оплаты — подписка на 12 месяцев.",
        "Финальная презентация назначена на среду в 14:00, онлайн.",
    ]

    async with async_session() as session:
        existing = await session.execute(select(Note))
        if existing.scalars().first():
            print("  Заметки уже существуют")
            return

        for i, content in enumerate(note_contents):
            author = managers[i % len(managers)]
            # половину привязываем к клиентам, половину к сделкам
            if i < len(note_contents) // 2:
                client_id = clients[i % len(clients)].id
                deal_id = None
            else:
                client_id = None
                deal_id = deals[i % len(deals)].id

            note = Note(
                content=content,
                author_id=author.id,
                client_id=client_id,
                deal_id=deal_id,
                is_pinned=(i % 5 == 0),
                created_at=datetime.now(UTC) - timedelta(days=random.randint(1, 60)),  # noqa: S311
            )
            session.add(note)
        await session.commit()
        print(f"  Создано {len(note_contents)} заметок")


async def seed_activities(
    clients: list[Client], deals: list[Deal], managers: list[User],
) -> None:
    """Создаем 18 демо-активностей."""
    activities_data = [
        ("call", "Первичный звонок", "Познакомились, выявили потребности"),
        ("meeting", "Встреча с ЛПР", "Обсудили бюджет и сроки"),
        ("email", "Отправка КП", "Коммерческое предложение на 3 варианта"),
        ("task", "Подготовить договор", "Шаблон + условия SLA"),
        ("call", "Звонок-напоминание", "Напомнить про оплату счета"),
        ("meeting", "Демонстрация продукта", "Показали личный кабинет и дашборд"),
        ("email", "Рассылка новостей", "Кейс + обновления продукта за месяц"),
        ("task", "Обновить прайс", "Новые цены с 1-го числа"),
        ("call", "Фолоу-ап после встречи", "Уточнили сроки подписания"),
        ("meeting", "Онбординг-сессия", "Настройка аккаунта и обучение"),
        ("email", "Благодарственное письмо", "За участие в конференции"),
        ("task", "Подготовить отчет", "Квартальный отчет по проекту"),
        ("call", "Сбор обратной связи", "NPS-опрос по телефону"),
        ("meeting", "Планирование спринта", "Совместное планирование следующего этапа"),
        ("email", "Отправка акта", "Акт выполненных работ за июль"),
        ("task", "Ревью контракта", "Проверить условия пролонгации"),
        ("call", "Холодный звонок", "Первый контакт по рекомендации"),
        ("meeting", "Стратегическая сессия", "Планирование на следующий год"),
    ]

    async with async_session() as session:
        existing = await session.execute(select(Activity))
        if existing.scalars().first():
            print("  Активности уже существуют")
            return

        for i, (act_type, title, desc) in enumerate(activities_data):
            author = managers[i % len(managers)]
            days_ago = random.randint(1, 45)  # noqa: S311
            is_completed = i < 12  # первые 12 — завершены

            activity = Activity(
                type=act_type,
                title=title,
                description=desc,
                author_id=author.id,
                client_id=clients[i % len(clients)].id,
                deal_id=deals[i % len(deals)].id if i % 3 != 0 else None,
                is_completed=is_completed,
                scheduled_at=datetime.now(UTC) - timedelta(days=days_ago),
                completed_at=datetime.now(UTC) - timedelta(days=days_ago - 1) if is_completed else None,
                created_at=datetime.now(UTC) - timedelta(days=days_ago + 1),
            )
            session.add(activity)
        await session.commit()
        print(f"  Создано {len(activities_data)} активностей")


async def main():
    """Полный сид — заполняет БД демо-данными."""
    print("=== Сид-скрипт CRM Lite ===\n")

    print("[1/7] Админ...")
    admin = await seed_admin()

    print("[2/7] Пользователи...")
    users = await seed_users()
    managers = [u for u in users if u.role == "manager"]
    # добавляем админа к менеджерам чтобы у него тоже были данные
    managers.insert(0, admin)

    print("[3/7] Стадии воронки...")
    stages = await seed_stages()

    print("[4/7] Теги...")
    tags = await seed_tags()

    print("[5/7] Клиенты...")
    clients = await seed_clients(managers, tags)

    print("[6/7] Сделки...")
    deals = await seed_deals(clients, stages, managers, tags)

    print("[7/7] Заметки и активности...")
    await seed_notes(clients, deals, managers)
    await seed_activities(clients, deals, managers)

    print("\n=== Готово! Демо-данные загружены ===")
    print(f"  Пользователей: {len(users) + 1}")
    print(f"  Стадий: {len(stages)}")
    print(f"  Тегов: {len(tags)}")
    print(f"  Клиентов: {len(clients)}")
    print(f"  Сделок: {len(deals)}")
    print("  Заметок: 22")
    print("  Активностей: 18")


if __name__ == "__main__":
    asyncio.run(main())
