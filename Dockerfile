# Multi-stage production build for NUMPE TRADING SOFTWARE
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend serving REST API and Frontend SPA
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY backend/app/ ./app/

# Copy Frontend Build into /app/frontend/dist so main.py serves it
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Environment defaults
ENV PORT=8000
ENV DATABASE_URL=sqlite+aiosqlite:///./numpe.db
ENV CORS_ORIGINS=*
ENV LOG_LEVEL=INFO

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

