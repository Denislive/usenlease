# Stage 1: Build Stage for Backend
FROM python:3.11-slim-bullseye AS backend-builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies including PostgreSQL libraries and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
WORKDIR /app/backend
RUN python3 -m venv /app/backend/venv

# Set the virtual environment to be used
ENV VIRTUAL_ENV=/app/backend/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Add build argument for SECRET_KEY
ARG SECRET_KEY

# Set environment variable for SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# Copy backend requirements
COPY backend/requirements.txt /app/backend/

# Upgrade pip, setuptools, and wheel to the latest versions
RUN pip install --upgrade pip setuptools wheel

# Install backend dependencies inside the virtual environment
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Verify package installation
RUN pip list

# Copy the rest of the backend application code
COPY backend/ /app/backend

# Collect static files during the build stage
RUN SECRET_KEY=${SECRET_KEY} python /app/backend/manage.py collectstatic --noinput

# Stage 2: Build Stage for Frontend
FROM node:16-alpine AS frontend-builder

# Set the working directory for the frontend
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json frontend/package-lock.json /app/frontend/
RUN npm install

## Copy the rest of the frontend application code
COPY frontend/ /app/frontend

# Build the frontend application
RUN npm run build

# Stage 3: Production Image
FROM nginx:alpine

# Set the working directory for the final image
WORKDIR /app

# Install bash, Python3, pip, and PostgreSQL client libraries
RUN apk add --no-cache bash python3 py3-pip libpq gettext

# Copy Nginx configuration template (nginx.conf.template)
COPY backend/nginx.conf.template /etc/nginx/nginx.conf.template

# Use envsubst to substitute environment variables into the Nginx config file
RUN envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Remove the default.conf file
RUN rm /etc/nginx/conf.d/default.conf

# Copy the built frontend files to Nginx root
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy backend files from the backend-builder stage
COPY --from=backend-builder /app/backend /app/backend

# Copy start.sh and set executable permissions
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the web server port
EXPOSE 8080

# Start the application using start.sh
CMD ["/bin/sh", "/app/start.sh"]
