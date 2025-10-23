"""
Этот модуль содержит набор тестов для проверки функциональности роутера аутентификации.
Тесты покрывают основные сценарии работы с регистрацией и выходом пользователей.

Тестируемые функции:
    - logout: Выход пользователя из системы
    - register: Регистрация нового пользователя

Зависимости:
    - pytest: Фреймворк для написания тестов
    - fastapi.testclient: Клиент для тестирования FastAPI приложений
    - unittest.mock: Мокирование объектов для изоляции тестов
    - app.main: Основное приложение FastAPI
    - app.routers.auth: Модуль с функциями аутентификации
    - app.schemas.user: Схемы данных для пользователей

Примечания:
    - Тесты используют асинхронное выполнение с pytest.mark.asyncio
    - Для изоляции тестов используются моки (mock) базы данных и функций
    - Тесты проверяют как успешные сценарии, так и обработку ошибок
"""

import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app

from app.routers.auth import register
from app.schemas.user import UserCreate

client = TestClient(app)


def test_logout():
    """
    Тест функции выхода пользователя из системы.

    Проверяет, что эндпоинт /auth/logout корректно обрабатывает запрос на выход
    и возвращает ожидаемый статус и сообщение.

    Asserts:
        - Статус ответа должен быть 200 (OK)
        - В теле ответа должно содержаться сообщение об успешном выходе
    """
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["detail"] == "Вы успешно вышли из системы"


@pytest.mark.asyncio
async def test_register_success(mocker):
    """
    Тест успешной регистрации нового пользователя.

    Проверяет сценарий успешной регистрации, когда:
    - Пользователь не авторизован
    - Email не занят
    - Пароли совпадают

    Args:
        mocker: Объект для мокирования зависимостей

    Asserts:
        - Функция должна вернуть статус 201 и сообщение об успешной регистрации
        - Должен быть вызван метод execute для добавления пользователя
        - Должен быть вызван метод commit для сохранения изменений
    """
    # Создаем мок для сессии
    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    mock_session.execute.return_value = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock

    # Мокаем is_authenticated
    mocker.patch("app.routers.auth.is_authenticated", return_value=False)

    # Создаем тестовые данные
    user_data = {
        "email": "test@example.com",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }

    # Вызываем функцию напрямую с моками
    result = await register(UserCreate(**user_data), mock_session, MagicMock())

    # Проверяем результат
    assert result == {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Успешная регистрация",
    }
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user_exists(mocker):
    """
    Тест регистрации пользователя с существующим email.

    Проверяет сценарий, когда пользователь пытается зарегистрироваться
    с email, который уже существует в системе.

    Args:
        mocker: Объект для мокирования зависимостей

    Asserts:
        - Должно быть выброшено исключение HTTPException с кодом 409
        - Сообщение об ошибке должно содержать информацию о существующем email
    """
    # Создаем мок для сессии
    mock_session = AsyncMock()
    mock_session.scalar.return_value = MagicMock(id=1)

    # Мокаем is_authenticated
    mocker.patch("app.routers.auth.is_authenticated", return_value=False)

    # Создаем тестовые данные
    user_data = {
        "email": "test@example.com",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }

    # Проверяем, что будет выброшено исключение
    with pytest.raises(HTTPException) as excinfo:
        await register(UserCreate(**user_data), mock_session, MagicMock())

    assert excinfo.value.status_code == status.HTTP_409_CONFLICT
    assert "Пользователь с таким email уже существует" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_register_password_mismatch(mocker):
    """
    Тест регистрации с несовпадающими паролями.

    Проверяет сценарий, когда пользователь вводит несовпадающие пароли
    при попытке регистрации.

    Args:
        mocker: Объект для мокирования зависимостей

    Asserts:
        - Должно быть выброшено исключение ValueError при создании UserCreate
        - Сообщение об ошибке должно содержать информацию о несовпадении паролей
    """
    # Создаем мок для сессии
    mock_session = AsyncMock()

    # Мокаем is_authenticated
    mocker.patch("app.routers.auth.is_authenticated", return_value=False)

    # Создаем тестовые данные с несовпадающими паролями
    user_data = {
        "email": "test@example.com",
        "password1": "testpassword1",
        "password2": "testpassword2",
        "first_name": "Test",
        "last_name": "User",
    }

    # Проверяем, что будет выброшено исключение ValueError при создании UserCreate
    with pytest.raises(ValueError) as excinfo:
        UserCreate(**user_data)

    assert "Пароли не совпадают" in str(excinfo.value)


@pytest.mark.asyncio
async def test_register_already_authenticated(mocker):
    """
    Тест попытки регистрации уже авторизованного пользователя.

    Проверяет сценарий, когда авторизованный пользователь пытается
    зарегистрировать нового пользователя.

    Args:
        mocker: Объект для мокирования зависимостей

    Asserts:
        - Должно быть выброшено исключение HTTPException с кодом 403
        - Сообщение об ошибке должно содержать информацию о том, что пользователь уже авторизован
    """
    # Создаем мок для сессии
    mock_session = AsyncMock()

    # Мокаем is_authenticated, чтобы вернуть True
    mocker.patch("app.routers.auth.is_authenticated", return_value=True)

    # Создаем тестовые данные
    user_data = {
        "email": "test@example.com",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }

    # Проверяем, что будет выброшено исключение
    with pytest.raises(HTTPException) as excinfo:
        await register(UserCreate(**user_data), mock_session, MagicMock())

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Вы уже авторизованы" in str(excinfo.value.detail)
