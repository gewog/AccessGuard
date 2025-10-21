from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Наследуясь от этого класса, другие классы становятся SQLAlchemy-моделями,
    которые могут быть преобразованы в таблицы базы данных.
    """

    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)

    # Внешний ключ для связи с таблицей ролей
    role_id = Column(Integer, ForeignKey("roles.id"), default=2)  # По умолчанию роль "user" (id=2)
