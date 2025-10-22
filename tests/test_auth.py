import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app

from app.routers.auth import register
from app.schemas.user import UserCreate

client = TestClient(app)

def test_logout():
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["detail"] == "Вы успешно вышли из системы"

@pytest.mark.asyncio
async def test_register_success(mocker):
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
        "last_name": "User"
    }

    # Вызываем функцию напрямую с моками
    result = await register(UserCreate(**user_data), mock_session, MagicMock())

    # Проверяем результат
    assert result == {"status_code": status.HTTP_201_CREATED, "transaction": "Успешная регистрация"}
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_register_user_exists(mocker):
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
        "last_name": "User"
    }

    # Проверяем, что будет выброшено исключение
    with pytest.raises(HTTPException) as excinfo:
        await register(UserCreate(**user_data), mock_session, MagicMock())

    assert excinfo.value.status_code == status.HTTP_409_CONFLICT
    assert "Пользователь с таким email уже существует" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_register_password_mismatch(mocker):
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
        "last_name": "User"
    }

    # Проверяем, что будет выброшено исключение ValueError при создании UserCreate
    with pytest.raises(ValueError) as excinfo:
        UserCreate(**user_data)

    assert "Пароли не совпадают" in str(excinfo.value)

@pytest.mark.asyncio
async def test_register_already_authenticated(mocker):
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
        "last_name": "User"
    }

    # Проверяем, что будет выброшено исключение
    with pytest.raises(HTTPException) as excinfo:
        await register(UserCreate(**user_data), mock_session, MagicMock())

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Вы уже авторизованы" in str(excinfo.value.detail)