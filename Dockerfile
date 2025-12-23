# Multi-stage Docker build untuk production
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/documents/incoming_letters \
    storage/documents/outgoing_letters \
    storage/documents/employee_archives \
    storage/documents/finance_archives \
    storage/documents/diplomas \
    logs

# Set proper permissions
RUN chown -R app:app /app && \
    chmod +x run.bat setup.bat dev.bat

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from app.core.database import health_check; exit(0 if health_check() else 1)" || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "serve.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/documents/incoming_letters \
    storage/documents/outgoing_letters \
    storage/documents/employee_archives \
    storage/documents/finance_archives \
    storage/documents/diplomas \
    logs

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Run in development mode
CMD ["python", "main.py"]