# Stage 1: Build Stage for Frontend
FROM node:20-alpine AS frontend_builder

# Set the working directory for the frontend application
WORKDIR /frontend_app

# Copy package.json and package-lock.json to leverage Docker's cache for dependencies
COPY frontend/package.json frontend/package-lock.json ./

# Install the dependencies for frontend
RUN npm install

# Copy the rest of the frontend application code into the container
COPY frontend/ .

# Build the frontend application
RUN npm run build

# Stage 2: Build Stage for Backend
FROM python:3.11-slim-bullseye AS backend_builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Update apt-get sources and install system dependencies
RUN apt-get update && \
    apt-get install -y gnupg2 build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Create a working directory for the backend
WORKDIR /backend_app

# Add build argument for SECRET_KEY
ARG SECRET_KEY

# Set environment variable for SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# Copy requirements.txt and install dependencies
COPY backend/requirements.txt /backend_app/
RUN python3 -m venv /backend_app/venv \
    && /backend_app/venv/bin/pip install --no-cache-dir -r /backend_app/requirements.txt

# Copy the rest of the backend application code
COPY backend/ /backend_app/backend

# Set STATIC_ROOT and MEDIA_ROOT for static and media file collection
ENV STATIC_ROOT=/backend_app/backend/staticfiles
ENV MEDIA_ROOT=/backend_app/backend/media

# Collect static files during the build stage
RUN SECRET_KEY=${SECRET_KEY} /backend_app/venv/bin/python /backend_app/backend/manage.py collectstatic --noinput

# Stage 3: Production Image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:/usr/local/bin:/usr/local/lib/node_modules:/usr/bin:/usr/local/sbin:/usr/sbin"

# Add build argument for SECRET_KEY
ARG SECRET_KEY

# Set environment variable for SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# Update apt-get sources and install necessary utilities
RUN apt-get update && \
    apt-get install -y gnupg2 build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Add Node.js official PPA and install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Copy the virtual environment and the backend application code from the builder stage
COPY --from=backend_builder /backend_app /app

# Copy the frontend build output from the frontend builder stage
COPY --from=frontend_builder /frontend_app /app/frontend

# Set the working directory for the backend application
WORKDIR /app/backend

# Ensure the staticfiles and media directories exist
RUN mkdir -p /app/backend/staticfiles /app/backend/media

# Install `supervisord`
RUN apt-get update && apt-get install -y supervisor

# Copy `supervisord.conf` to the appropriate location
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the application port
EXPOSE 8000

# Start `supervisord` to run both frontend and backend
CMD ["/usr/bin/supervisord"]
