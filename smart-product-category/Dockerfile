# Multi-stage build for a production Python application

# Build stage for dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependencies file
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not use virtualenvs
RUN poetry config virtualenvs.create false \
    && poetry export -f requirements.txt > requirements.txt

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy dependencies from builder stage
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir backoff

# Copy application code
COPY ./app /app

# Create directory for prompts and ensure it's writable
RUN mkdir -p /app/prompts && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port the app will run on
EXPOSE 8000

# Use tini as entrypoint to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
