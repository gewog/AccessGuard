import base64
import json

from fastapi import (APIRouter, Depends, Response, Request, HTTPException, status)
from typing import Annotated

from passlib.context import CryptContext
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from authx import AuthX, AuthXConfig

from app.models.user import User

from app.schemas.user import UserCreate, UserLogin
from app.backend.db_depends import get_session

router = APIRouter()
config = AuthXConfig()
config.JWT_SECRET_KEY = "SUPER_SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_secret_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
security = AuthX(config=config)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

session = Annotated[
    AsyncSession, Depends(get_session)
]  # Аннотация типа для зависимости сессии

async def is_authenticated(request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return False  # Не авторизован
    try:
        decode_token(token)  # Попытаемся декодировать
        return True  # Авторизован
    except Exception:
        return False  # Токен недействителен


@router.post("/register")
async def register(user: UserCreate, session: session, request: Request):
    """Регистрация нового пользователя — только если не авторизован"""

    # Проверяем, авторизован ли пользователь
    if await is_authenticated(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы уже авторизованы. Сначала выйдите из системы."
        )

    # Проверка пароля (остаётся как есть)
    password_bytes = user.password1.encode('utf-8')
    if len(password_bytes) > 72:
        raise HTTPException(status_code=400, detail="Пароль не должен превышать 72 байта")
    if user.password1 != user.password2:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    # Проверка на существование email
    existing_user = await session.scalar(
        select(User).where(User.email == user.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )

    # Регистрация
    query = insert(User).values([
        {
            "email": user.email,
            "hashed_password": bcrypt_context.hash(user.password1),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": True
        }
    ])
    try:
        await session.execute(query)
        await session.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Успешная регистрация"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login")
async def login(user: UserLogin, session: session, response: Response):
    """Логиним пользователя, подправить сонтекст верифай"""

    user_query = await session.scalar(
            select(User).where(User.email == user.email))
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    if not bcrypt_context.verify(
            user.password, user_query.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
        )
    token = security.create_access_token(uid=str(user_query.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}

def decode_token(token: str) -> str:
    try:
        # Разбиваем токен на части
        header, payload, signature = token.split('.')

        # Декодируем payload (base64url)
        payload_bytes = base64.urlsafe_b64decode(payload + '==')  # Добавляем padding
        payload_str = payload_bytes.decode('utf-8')

        # Парсим JSON
        data = json.loads(payload_str)
        return data.get("sub")
    except Exception as e:
        raise ValueError(f"Ошибка при декодировании: {e}")

async def get_current_user_id(request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Вы не в системе")

    user_id = decode_token(token)
    return {"user_id": user_id}


@router.post("/logout")
async def logout(response: Response):
    """Выход пользователя из системы."""
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)  # Удаляем куки с токеном
    return {"detail": "Вы успешно вышли из системы"}