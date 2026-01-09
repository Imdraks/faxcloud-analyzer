# Multi-architecture Dockerfile (AMD64, ARM64 - Raspberry Pi)
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt gunicorn==22.0.0

# Production stage
FROM python:3.12-slim

# Labels
LABEL maintainer="FaxCloud Analyzer"
LABEL description="Analyseur FaxCloud - Compatible Raspberry Pi"
LABEL version="1.2.0"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . ./

# Create necessary directories with correct permissions
RUN mkdir -p /app/data/imports /app/data/reports /app/data/reports_qr /app/database /app/logs \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV TZ=Europe/Paris
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

EXPOSE 8000

# Use gunicorn with optimized settings
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "src.wsgi:app"]
