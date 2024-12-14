# Stage 1: Build Stage for Frontend
FROM node:16-alpine AS frontend-builder

# Set the working directory for the frontend application
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json ./

# Install the frontend dependencies
RUN npm install

# Copy the rest of the frontend application code
COPY frontend/ .

# Build the frontend application
RUN npm run build

# Stage 2: Build Stage for Backend
FROM python:3.11-slim-bullseye AS backend-builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app/backend

# Add build argument for SECRET_KEY
ARG SECRET_KEY

# Set environment variable
ENV SECRET_KEY=${SECRET_KEY}

# Copy backend requirements
COPY backend/requirements.txt .

# Install backend dependencies
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY backend/ .

# Set STATIC_ROOT for static file collection
ENV STATIC_ROOT=/app/backend/staticfiles

# Collect static files during the build stage
RUN SECRET_KEY=${SECRET_KEY} /app/venv/bin/python manage.py collectstatic --noinput

# Stage 3: Production Image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

# Copy the virtual environment and the application code from the backend builder stage
COPY --from=backend-builder /app /app

# Copy built frontend files to the backend static directory
COPY --from=frontend-builder /app/frontend/dist /app/backend/static/frontend

# Set the working directory for the backend application
WORKDIR /app/backend

# Ensure the staticfiles directory exists
RUN mkdir -p /app/backend/staticfiles

# Expose the application port
EXPOSE $PORT

# Run migrations, create a superuser (if not exists), and start Gunicorn
CMD ["sh", "-c", "python manage.py wait_for_db && python manage.py migrate && python manage.py create_superuser && exec gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:$PORT --workers=3 --timeout 240 --graceful-timeout 240"]
