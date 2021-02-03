FROM python:3.8-slim

WORKDIR /app

RUN pip install poetry==1.1.4

ENV POETRY_VIRTUALENVS_CREATE=0

ENV PYTHONPATH=/app

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

CMD ["python", "bot.py"]