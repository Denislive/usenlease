# Use Python 3.11 as the base image
FROM python:3.11

# Set environment variables to prevent Python from buffering output (useful for logging)
ENV PYTHONUNBUFFERED=1

# Create a working directory for the application inside the container
WORKDIR /app

# Copy the requirements.txt file first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL dependencies for Django (if not in the requirements.txt)
RUN pip install psycopg2-binary

# Copy the rest of the project files into the containers
COPY . .

# Expose port 8000 for the Django app
EXPOSE 8000

# Run migrations and then start the Gunicorn server to serve the Django app
CMD ["sh", "-c", "python manage.py migrate && gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000"]
