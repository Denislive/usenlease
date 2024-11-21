# Stage 1: Build Stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY backend/requirements.txt /app/
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Verify installation of Django and other dependencies
RUN /app/venv/bin/pip show django

# Copy the rest of the backend code
COPY backend /app/backend

# Stage 2: Production Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy the virtual environment and the application code from the builder stage
COPY --from=builder /app /app

# Set the working directory for the application
WORKDIR /app/backend

# Ensure the virtual environment is activated and available in the container's PATH
ENV PATH="/app/venv/bin:$PATH"

# Expose the application port
EXPOSE 8000

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && exec gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000"]
