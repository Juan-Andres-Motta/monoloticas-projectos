FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main --no-interaction --no-ansi

COPY . .

CMD ["python", "main.py"]