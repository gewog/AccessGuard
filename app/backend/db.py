"""
Модуль для работы с базой данных.

Этот модуль предоставляет функции для инициализации таблиц,
тестирования подключения к PostgreSQL и получения данных из базы.
"""
import asyncio

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.backend.settings import setting  # Экземпляр класса Settings

from app.models.user import User
from app.models.role import Role
from app.models.business_element import BusinessElement
from app.models.access_rule import AccessRule, Base

engine = create_async_engine(setting.get_path, echo=False)
session = async_sessionmaker(bind=engine)


async def create_tables():
    """
    Создаёт все таблицы в базе данных на основе моделей SQLAlchemy.

    Использует `Base.metadata.create_all()` для создания таблиц.
    В случае ошибки выводит сообщение об ошибке.

    Raises:
        Exception: Если произошла ошибка при создании таблиц.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Таблицы успешно созданы!")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

async def get_version() -> None:
    """
    Тестовая функция для получения версии PostgreSQL.

    Выполняет запрос `SELECT version();` и выводит результат в консоль.
    Эта функция предназначена для проверки подключения к базе данных
    и должна быть удалена после завершения тестирования.
    """
    async with session() as ss:
        res = await ss.execute(text("select version();"))
        print(res.fetchone())

if __name__ == "__main__":
    asyncio.run(create_tables())