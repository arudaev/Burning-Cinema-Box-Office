FROM python:3.12-slim
WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock README.md ./
COPY src/ ./src/
RUN poetry install --only main --no-ansi

CMD ["python", "-m", "burningbackend"]
