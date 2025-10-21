# Используем официальный образ Python 3.13
FROM python:3.13-slim

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы проекта
WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY app app
COPY tests tests
COPY alembic.ini .

# Устанавливаем зависимости через Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

# Копируем оставшиеся файлы
COPY . .

# Собираем и применяем миграции
RUN poetry run alembic upgrade head

# Запускаем приложение
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
