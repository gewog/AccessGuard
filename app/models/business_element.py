from sqlalchemy import Column, Integer, String
from app.models.role import Base

class BusinessElement(Base):
    """
    Модель бизнес-сущностей.
    Эта модель описывает бизнес-объекты, к которым применяются правила доступа.
    Например, это могут быть профили пользователей, настройки системы, правила доступа и т.д.
    """

    # Название таблицы в базе данных
    __tablename__ = "business_elements"

    # Уникальный идентификатор бизнес-объекта (первичный ключ)
    id = Column(Integer, primary_key=True, index=True)

    # Название бизнес-объекта (например, "user_profiles", "access_rules").
    # Должно быть уникальным, чтобы избежать дублирования.
    name = Column(String, unique=True, index=True)

    # Описание бизнес-объекта (например, "Профиль пользователя", "Правило доступа").
    # Может быть пустым, если описание не требуется.
    description = Column(String, nullable=True)