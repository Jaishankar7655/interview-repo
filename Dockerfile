# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*




# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

CMD ["sh", "-c", "until nc -z $MYSQL_HOST 3306; do echo Waiting for MySQL...; sleep 3; done; \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000"]