# Stage 1: Backend Build Stage
FROM python:3.11-slim-bullseye AS backend-builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies including PostgreSQL libraries and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app/backend

# Create and activate virtual environment
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/backend/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Add build argument for SECRET_KEY
ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# Copy backend requirements and install dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Debug: List installed packages
RUN pip list

# Copy the rest of the backend application code
COPY backend/ /app/backend

# Collect static files
RUN python /app/backend/manage.py collectstatic --noinput

# ---------------------------------------------------------------

# Stage 2: Frontend Build Stage
FROM node:18-alpine AS frontend-builder

# Set the working directory for the frontend
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json frontend/package-lock.json /app/frontend/
RUN npm ci  # Clean install for dependencies

# Debugging: List installed packages
RUN npm list

# Copy the rest of the frontend application code
COPY frontend/ /app/frontend

# Debugging: Ensure files exist
RUN ls -la

# Build the frontend application
RUN npm run build || { echo "Build failed"; exit 1; }

# ---------------------------------------------------------------

# Stage 3: Production Image
FROM nginx:alpine

# Set working directory
WORKDIR /app

# Install necessary system dependencies
RUN apk add --no-cache bash python3 py3-pip libpq gettext

# Copy Nginx configuration template
COPY backend/nginx.conf.template /etc/nginx/nginx.conf.template

# Replace environment variables in Nginx config
RUN envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Remove the default.conf file
RUN rm /etc/nginx/conf.d/default.conf

# Copy frontend build files
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy backend files from backend-builder
COPY --from=backend-builder /app/backend /app/backend

# Copy start script and set executable permissions
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose web server port
EXPOSE 8080

# Start the application
CMD ["/bin/sh", "/app/start.sh"]
