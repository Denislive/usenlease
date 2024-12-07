# Stage 1: Build Stage
FROM python:3.11-slim-bullseye AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Add build argument for SECRET_KEY
ARG SECRET_KEY

# Set environment variable
ENV SECRET_KEY=${SECRET_KEY}

# Copy requirements.txt and install dependencies
COPY ../backend/requirements.txt /app/
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the backend code
COPY ../backend /app/backend

# Set STATIC_ROOT for static file collection
ENV STATIC_ROOT=/app/backend/staticfiles

# Collect static files during the build stage
RUN /app/venv/bin/python /app/backend/manage.py collectstatic --noinput

# Stage 2: Production Image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

# Add build argument for SECRET_KEY
ARG SECRET_KEY

# Set environment variable
ENV SECRET_KEY=${SECRET_KEY}

# Copy the virtual environment and the application code from the builder stage
COPY --from=builder /app /app

# Set the working directory for the application
WORKDIR /app/backend

# Ensure the staticfiles directory exists
RUN mkdir -p /app/backend/staticfiles

# Expose the application port
EXPOSE 8000

# Run migrations, create a superuser (if not exists), and start Gunicorn
CMD ["sh", "-c", "python manage.py wait_for_db && python manage.py migrate && python manage.py create_superuser && exec gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000 --workers=3 --timeout 240 --graceful-timeout 240"]
