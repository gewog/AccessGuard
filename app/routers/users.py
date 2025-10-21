from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserLogin
from app.backend.db_depends import get_session
from app.models.user import User
from .auth import bcrypt_context

from .auth import security, get_current_user_id

router = APIRouter()
session = Annotated[
    AsyncSession, Depends(get_session)
]  # Аннотация типа для зависимости сессии


@router.get("/me")
async def get_current_user(
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Получить информацию о текущем пользователе."""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

@router.put("/me")
async def update_current_user(new_info: UserCreate, session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Получить информацию о текущем пользователе."""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы ен можете поменять данные пользователя"
        )

    update_query = update(User).values(
        {
            "email": new_info.email,
            "hashed_password": bcrypt_context.hash(new_info.password1),
            "first_name": new_info.first_name,
            "last_name": new_info.last_name
        }).where(User.id == int(user_id))
    try:
        await session.execute(update_query)
        await session.commit()
        await session.refresh(user)  # Обновляем объект после коммита
        return {"Message": "Данные успешно изменены"}

    except Exception as e:
        return f"Что-то пошло не так: {e}"


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    session: session,
    current_user: dict = Depends(get_current_user_id),
):
    user_id = current_user["user_id"]
    user = await session.get(User, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Пользователь не найден или уже деактивирован")

    user.is_active = False
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
