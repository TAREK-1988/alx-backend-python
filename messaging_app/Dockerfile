# Use an official lightweight Python image as the base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for MySQL client compilation (mysqlclient)
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port that Django will run on (default 8000)
EXPOSE 8000

# Example of how to run this image directly without docker-compose:
# docker build -t messaging_app_image .
# docker run -p 8000:8000 messaging_app_image
#                ^^^
# The "-p" flag maps container port 8000 to host port 8000.

# Default command to run the development server
# For production, you would typically use gunicorn or another WSGI server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
