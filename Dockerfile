# Multi-stage build: build React app, run FastAPI, serve static from FastAPI

# 1) Frontend build
FROM node:18-alpine AS webbuild
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ .
RUN npm run build

# 2) Backend runtime
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=1 \
    PORT=8000

WORKDIR /app

# System deps (if pillow/scikit-image need them)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg62-turbo-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install backend deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/backend/requirements.txt

# Copy backend source
COPY backend/ /app/backend/

# Copy model weights (kept within backend tree already)

# Copy built frontend into backend app static dir
RUN mkdir -p /app/backend/app/static
COPY --from=webbuild /frontend/build/ /app/backend/app/static/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


