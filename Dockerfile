FROM python:3.13-slim-bookworm

RUN pip install uv

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN uv sync --locked

COPY . .
