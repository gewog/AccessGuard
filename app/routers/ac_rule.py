from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.access_rule import AccessRule
from app.models.user import User
from app.models.role import Role
from app.models.business_element import BusinessElement
from app.schemas.access_rule import AccessRuleCreate

from app.backend.db_depends import get_session
from .auth import get_current_user_id

router = APIRouter()
session = Annotated[
    AsyncSession, Depends(get_session)
]  # Аннотация типа для зависимости сессии


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rule(
        access_rule: AccessRuleCreate,
        session: session,
        current_user: dict = Depends(get_current_user_id)
):
    """Создать новое правило доступа."""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )
    # Получаем правило доступа для элемента с id=3 ("rule")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 3)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule or not rule.create_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на создание правил доступа"
        )

    # Проверяем существование роли и элемента
    role = await session.scalar(select(Role).where(Role.id == int(access_rule.role_id)))
    element = await session.scalar(select(BusinessElement).where(BusinessElement.id == int(access_rule.element_id)))
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такой роли не существует!")
    if not element:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такой бизнес-сущности не существует!")

    # Создаём правило
    new_rule = AccessRule(
        role_id=access_rule.role_id,
        element_id=access_rule.element_id,
        # Заполните остальные поля, если они есть!
    )
    session.add(new_rule)
    await session.commit()
    return {"message": "Правило успешно создано"}

@router.get("/")
async def get_access_rules(
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Получить список всех правил доступа (доступных для чтения)."""
    emt_l = []
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )
    # Получаем правило доступа для элемента с id=3 ("rule")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 3)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule or not rule.read_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на чтение правил доступа"
        )

    rules_query = await session.execute(select(AccessRule))
    result = rules_query.scalars().all()
    for el in result:
        emt_l.append({
            "id": el.id,
            "role_id": el.role_id,
            "element_id": el.element_id
        })
    return emt_l


@router.get("/{access_rule_id}")
async def get_access_rule(
    s_rule_id: int,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Получить информацию о правиле доступа."""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )
    # Получаем правило доступа для элемента с id=3 ("rule")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 3)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule or not rule.read_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на чтение правил доступа"
        )

    rule_query = await session.execute(select(AccessRule).where(AccessRule.id == s_rule_id))
    result = rule_query.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Правила под id {s_rule_id} не существует")

    return {"id": result.id,
            "rule_id": result.role_id,
            "element_id": result.element_id}

@router.put("/{access_rule_id}")
async def update_access_rule(
    s_rule_id: int,
    new_info: AccessRuleCreate,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Обновить информацию о правиле доступа."""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )
    # Получаем правило доступа для элемента с id=3 ("rule")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 3)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule or not rule.update_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на обновление правил доступа"
        )

    try:
        rule_query = await session.execute(select(AccessRule).where(AccessRule.id == s_rule_id))
        result = rule_query.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Правила под id {s_rule_id} не существует")

        res = await session.execute(update(AccessRule).values(
                {
                "role_id": new_info.role_id,
                "element_id": new_info.element_id,
                "read_permission": new_info.read_permission,
                "create_permission": new_info.create_permission,
                "update_permission": new_info.update_permission,
                "delete_permission": new_info.delete_permission
                 }

        ).where(AccessRule.id == s_rule_id))

        await session.commit()
        return {"message": f"Правило под id {s_rule_id} успешно обновлена!"}

    except Exception as e:
        return f"Что-то пошло не так: {e}"



@router.delete("/{role_id}")
async def delete_role(
    del_rule_id: int,
    session: session,
    current_user: dict = Depends(get_current_user_id)
):
    """Удалить правило доступа"""
    user_id = current_user["user_id"]
    user = await session.scalar(select(User).where(User.id == int(user_id)))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен"
        )
    # Получаем правило доступа для элемента с id=3 ("rule")
    rule_query = await session.execute(
        select(AccessRule)
        .where(AccessRule.role_id == user.role_id)
        .where(AccessRule.element_id == 3)
    )
    rule = rule_query.scalar_one_or_none()

    if not rule or not rule.delete_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на чтение правил доступа"
        )

    try:
        rule_query = await session.execute(
            select(AccessRule).where(AccessRule.id == del_rule_id))
        result = rule_query.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Правила под id {del_rule_id} не существует")

        await session.execute(delete(AccessRule).where(AccessRule.id == del_rule_id))
        await session.commit()
        return {"message": f"Правило под id {del_rule_id} успешно удалена!"}
    except Exception as e:
        return f"Что-то пошло не так: {e}"
