from sqlalchemy import Boolean, Column, ForeignKey, Integer
from app.models.business_element import Base

class AccessRule(Base):
    """
    Модель правил доступа.
    Эта модель определяет, какие действия может выполнять пользователь с определенной ролью
    над конкретными бизнес-объектами (например, профилями пользователей, правилами доступа и т.д.).
    """

    # Название таблицы в базе данных
    __tablename__ = "access_rules"

    # Уникальный идентификатор правила доступа (первичный ключ)
    id = Column(Integer, primary_key=True, index=True)
    # Внешний ключ, связывающий правило доступа с ролью.
    # Определяет, к какой роли относится данное правило.
    role_id = Column(Integer, ForeignKey("roles.id"))
    # Внешний ключ, связывающий правило доступа с бизнес-объектом.
    # Определяет, к какому бизнес-объекту относится данное правило.
    element_id = Column(Integer, ForeignKey("business_elements.id"))
    # Разрешение на чтение бизнес-объекта.
    # Если True, пользователи с этой ролью могут читать данный бизнес-объект.
    read_permission = Column(Boolean, default=False)
    # Разрешение на создание нового бизнес-объекта.
    # Если True, пользователи с этой ролью могут создавать новые объекты данного типа.
    create_permission = Column(Boolean, default=False)
    # Разрешение на обновление бизнес-объекта.
    # Если True, пользователи с этой ролью могут обновлять данный бизнес-объект.
    update_permission = Column(Boolean, default=False)
    # Разрешение на удаление бизнес-объекта.
    # Если True, пользователи с этой ролью могут удалять данный бизнес-объект.
    delete_permission = Column(Boolean, default=False)
