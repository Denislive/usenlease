FROM python:3.11

# Set environment variables to avoid Python output buffering
ENV PYTHONUNBUFFERED 1

# Create a working directory
WORKDIR /app

# Copy requirements.txt first for better caching of Docker layers
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your application
CMD ["gunicorn", "EquipRentHub.wsgi:application", "--bind", "0.0.0.0:8000"]