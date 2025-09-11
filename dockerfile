# Base Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (psycopg2 needs these)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set Python path so src folder modules are found
ENV PYTHONPATH="/app/src"

# Default command (felülírja majd docker-compose)
CMD ["python", "main.py"]
