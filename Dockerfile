# Use an official Python runtime as a parent image
FROM python:3.9  # Changed to a larger base image

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Update the package list and install system dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* || (cat /var/log/apt/term.log && exit 1)  # Print logs on failure

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "usenlease.wsgi:application"]
