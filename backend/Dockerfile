# Use Python 3.11 as the base image
FROM python:3.11

# Set environment variables to avoid Python output buffering
ENV PYTHONUNBUFFERED 1

# Create a working directory
WORKDIR /app

# Copy requirements.txt first for better caching of Docker layers
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container, including db.sqlite3
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Specify the command to run your application with Gunicorn
CMD ["gunicorn", "EquipRentHub.wsgi:application", "--bind", "0.0.0.0:8000"]
