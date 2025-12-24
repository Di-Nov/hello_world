FROM python:3.13.5 as app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==2.2.1

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

RUN chmod +x /app/configs/start.sh

CMD ["/app/configs/start.sh"]