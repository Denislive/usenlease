# Stage 1: Build Stage for Frontend
FROM node:16-alpine AS frontend_builder

WORKDIR /frontend_app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Build Stage for Backend
FROM python:3.11-slim-bullseye AS backend_builder

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend_app

COPY backend/requirements.txt ./
RUN python3 -m venv /backend_app/venv \
    && /backend_app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

RUN SECRET_KEY=${SECRET_KEY} /backend_app/venv/bin/python manage.py collectstatic --noinput

# Stage 3: Production Image
FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

COPY --from=backend_builder /backend_app /app
COPY --from=frontend_builder /frontend_app/build /app/frontend/build

WORKDIR /app

RUN mkdir -p /app/backend/staticfiles /app/backend/media

RUN npm install -g serve

EXPOSE 8000

# Backend Command
CMD ["sh", "-c", "python manage.py wait_for_db && python manage.py migrate && exec gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000 --workers=3 --timeout 240 --graceful-timeout 240"]
