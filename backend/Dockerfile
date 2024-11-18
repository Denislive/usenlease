# Stage 1: Build Stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend"

# Create a working directory
WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Debug installed packages
RUN pip freeze

# Copy backend code
COPY backend /app/backend

# Install PostgreSQL dependencies if not in requirements.txt
RUN pip install psycopg2-binary

# Debug application directory
RUN ls -al /app/backend

# Stage 2: Production Image
FROM python:3.11-alpine

# Install bash
RUN apk add --no-cache bash

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend"

# Copy built app from builder stage
COPY --from=builder /app /app

WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000"]
