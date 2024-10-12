# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run migrations
RUN python manage.py migrate

# Expose port 8000
EXPOSE 8000

# Define the command to start the Gunicorn server
CMD ["gunicorn", "usenlease.wsgi:application", "--bind", "0.0.0.0:8000"]
