# Multi-stage optimized Dockerfile for web-crawler
# Minimalist build with layer caching optimization for production VPS deployment

# Stage 1: Builder (isolated dependency layer for caching)
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependencies with caching optimization
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (minimal production image)
FROM python:3.11-slim

# Environment optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app:$PYTHONPATH

WORKDIR /app

# Copy dependencies from builder stage (efficient layer caching)
COPY --from=builder /root/.local /root/.local

# Copy only essential application files (layer caching: code changes don't rebuild deps)
COPY crawler.py .
COPY crawler_full.py .
COPY config.py .
COPY .env.example .env
COPY requirements.txt .

# Create output directories with proper permissions
RUN mkdir -p /app/site_archive /app/output && \
    chmod -R 755 /app && \
    chown -R nobody:nogroup /app

# Non-root user for security
USER nobody

# Health check (lightweight)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Default entry point
CMD ["python", "crawler.py"]
