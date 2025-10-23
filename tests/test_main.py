"""
Модуль содержит асинхронные тесты для проверки основных эндпоинтов приложения.
Использует AsyncClient с ASGITransport для тестирования асинхронных FastAPI приложений.

Зависимости:
    - pytest: Фреймворк для написания тестов
    - httpx.AsyncClient: Асинхронный HTTP-клиент для выполнения запросов
    - httpx.ASGITransport: Транспорт для тестирования ASGI-приложений
    - app.main: Основное приложение FastAPI
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_main():
    """
    Асинхронный тест корневого эндпоинта приложения.

    Проверяет, что корневой эндпоинт ("/") возвращает ожидаемый ответ.
    Этот тест важен, так как проверяет базовую работоспособность приложения.

    Тест выполняет следующие проверки:
        1. Отправляет GET-запрос на корневой эндпоинт ("/")
        2. Проверяет, что статус ответа равен 200 (OK)
        3. Проверяет, что тело ответа содержит ожидаемое сообщение {"message": "ok"}

    Использует:
        - AsyncClient с ASGITransport для выполнения асинхронных запросов
        - Контекстный менеджер async with для корректного управления ресурсами

    Asserts:
        - res.status_code == 200: Проверка статуса ответа
        - res.json() == {"message": "ok"}: Проверка тела ответа

    Примечания:
        - Тест помечен декоратором @pytest.mark.asyncio для асинхронного выполнения
        - Использует тестовый базовый URL "http://test"
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert res.json() == {"message": "ok"}
