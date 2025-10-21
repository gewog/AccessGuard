from sqlalchemy import Column, Integer, String
from app.models.user import Base


class Role(Base):
    """
    Модель роли.
    Эта модель описывает роли пользователей в системе.
    Роли используются для группировки пользователей и назначения им прав доступа.
    """

    # Название таблицы в базе данных
    __tablename__ = "roles"

    # Уникальный идентификатор роли (первичный ключ)
    id = Column(Integer, primary_key=True, index=True)

    # Название роли (например, "admin", "user").
    # Должно быть уникальным, чтобы избежать дублирования.
    name = Column(String, unique=True, index=True)

    # Описание роли (например, "Администратор системы", "Менеджер").
    # Может быть пустым, если описание не требуется.
    description = Column(String, nullable=True)
