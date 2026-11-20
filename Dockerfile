# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

COPY requirements-dev.lock ./

RUN python -m pip install \
    --no-cache-dir \
    --requirement requirements-dev.lock

COPY app ./app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]


FROM python:3.11-slim AS automation

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

RUN python -m pip install --no-cache-dir uv==0.12.9

COPY automation/pyproject.toml automation/uv.lock ./

RUN uv sync --frozen --no-install-project

RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

RUN uv run playwright install --with-deps chromium

COPY automation/ ./

CMD ["uv", "run", "pytest", "--env=dev", "-q"]