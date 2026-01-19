FROM python:3.11-slim

LABEL org.opencontainers.image.title="Tara Assistant"
LABEL org.opencontainers.image.description="AI-powered Home Assistant controller"
LABEL org.opencontainers.image.source="https://github.com/TaraHome/taraassistant-public"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy requirements first for caching
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code only (source is inside container - not easily accessible)
COPY app/ ./app/
COPY scripts.yaml ./scripts.yaml

# Create data directory for encrypted credentials
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
