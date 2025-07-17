FROM python:3.11-slim-bullseye AS backend-builder

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    redis-server \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app/backend

# Copy only requirements.txt first
COPY backend/requirements.txt /app/backend/

RUN python3 -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN pip install celery[redis] django-celery-beat

RUN pip list

# Now copy the rest of the backend code
COPY backend/ /app/backend
RUN export DOCKER_BUILD=1 && \
    DJANGO_SETTINGS_MODULE=EquipRentHub.settings python /app/backend/manage.py collectstatic --noinput --clear || echo "Skipping database-dependent collectstatic errors"

ENV DOCKER_BUILD=0

# ---------------------------------------------------------------

FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json /app/frontend/

RUN rm -f package-lock.json

RUN npm install --package-lock-only

COPY frontend/package-lock.json /app/frontend/

RUN npm ci  # Clean install for dependencies
RUN npm list

COPY frontend/ /app/frontend
RUN ls -la

RUN npm run build || { echo "Build failed"; exit 1; }

# ---------------------------------------------------------------

# Stage 3: Production Image (Nginx + Gunicorn + Celery + Redis)
FROM nginx:alpine

WORKDIR /app

RUN apk add --no-cache bash python3 py3-pip libpq gettext redis

# Create a virtual environment
RUN python3 -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY backend/nginx.conf.template /etc/nginx/nginx.conf.template

RUN envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

RUN rm /etc/nginx/conf.d/default.conf

COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html
COPY --from=backend-builder /app/backend /app/backend

# Install Python dependencies inside the venv
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN pip install celery[redis] django-celery-beat

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/start.sh"]