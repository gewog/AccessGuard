from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.role import RoleCreate # Схема сущности
from app.models.user import User
from app.models.access_rule import AccessRule
from app.models.role import Role
from app.backend.db_depends import get_session
from .auth import get_current_user_id

router = APIRouter()
session = Annotated[
    AsyncSession, Depends(get_session)
]  # Аннотация типа для зависимости сессии


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Создать роль"""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )

    # Получаем правило доступа для элемента с id=2 ("roles")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 2)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на данный функционал")

    if not rule.create_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не можете создать роль")

    # Создаём роль
    new_role = Role(name=role_data.name, description=role_data.description)
    session.add(new_role)
    await session.commit()

    return {"message": "Роль успешно создана"}

@router.get("/")
async def get_roles(
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    emt_l = []
    """Получить список всех ролей."""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )

    # Получаем правило доступа для элемента с id=2 (например, "access_rules")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 2)  # Предполагаем, что access_rules = element_id=2
    )
    rule = rule_query.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на данный функционал")

    if not rule.read_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не можете создать роль")
    roles_query = await session.execute(
        select(Role))
    result = roles_query.scalars().all()
    for el in result:
        emt_l.append({
            "role_id": el.id,
            "role_name": el.name
        })
    return emt_l



@router.get("/{role_id}")
async def get_role(
    s_role_id: int,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Получить информацию о роли"""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )

    # Получаем правило доступа для элемента с id=2 (например, "access_rules")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 2)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на данный функционал")

    if not rule.read_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не можете получить полную информацию о роле")
    try:
        roles_query = await session.execute(
            select(Role).where(Role.id == s_role_id))
        result = roles_query.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"роли под id {s_role_id} не существует")
        return {"id": result.id, "name": result.name, "descr": result.description}
    except Exception as e:
        return f"Что-то пошло не так: {e}"


@router.put("/{role_id}")
async def update_role(
    s_role_id: int,
    new_info: RoleCreate,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Обновить информацию о роли"""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )

    # Получаем правило доступа для элемента с id=2 (например, "access_rules")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 2)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на данный функционал")

    if not rule.update_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не можете обновить информацию о роле")

    try:
        roles_query = await session.execute(
            select(Role).where(Role.id == s_role_id))
        result = roles_query.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"роли под id {s_role_id} не существует")

        res = await session.execute(update(Role).values(
            {"name": new_info.name,
        "description": new_info.description}).where(Role.id == s_role_id))

        await session.commit()
        return {"message": f"Роль под id {s_role_id} успешно удалена!"}
    except Exception as e:
        return f"Что-то пошло не так: {e}"



@router.delete("/{role_id}")
async def delete_role(
    del_role_id: int,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Удалить роль"""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )

    # Получаем правило доступа для элемента с id=2 (например, "access_rules")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 2)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на на данный функционал")

    if not rule.delete_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не можете удалить данную роль")
    try:
        roles_query = await session.execute(
            select(Role).where(Role.id == del_role_id))
        result = roles_query.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"роли под id {del_role_id} не существует")

        await session.execute(delete(Role).where(Role.id == del_role_id))
        await session.commit()
        return {"message": f"Роль под id {del_role_id} успешно удалена!"}
    except Exception as e:
        return f"Что-то пошло не так: {e}"


