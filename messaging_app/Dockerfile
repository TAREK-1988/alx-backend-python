# Base image: official Python 3.10 slim image
FROM python:3.10-slim

# Do not write .pyc files, and output logs directly (no buffering)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for building MySQL client (mysqlclient)
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

# Copy the rest of the project source code into the container
COPY . /app

# Expose port 8000 (default Django development server port)
EXPOSE 8000

# Default command: run Django development server
# In production you would typically use gunicorn or another WSGI server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
