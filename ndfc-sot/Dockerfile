FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH so alembic can find the 'app' module
ENV PYTHONPATH=/app

# Make startup script executable
RUN chmod +x startup.sh

EXPOSE 8000

CMD ["./startup.sh"]
