
# Stage 1: Build Python dependencies
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.lock .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --require-hashes -r requirements.lock


# Stage 2: Run the Django application
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only the MySQL runtime library
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app \
    && useradd -r -g app app

# Copy the installed Python environment
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Copy application source code
COPY . .

# Collect static assets using build-only dummy configuration
RUN DEBUG=False SECRET_KEY=build-only DB_NAME=x DB_USER=x DB_PASSWORD=x DB_HOST=x \
    python manage.py collectstatic --noinput \
    && mkdir -p /app/media \
    && chown -R app:app /app/media /app/staticfiles

# Do not run the app as root
USER app

EXPOSE 8000

# Container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request as u; r=u.Request('http://127.0.0.1:8000/healthz/', headers={'X-Forwarded-Proto':'https'}); u.urlopen(r, timeout=3)" || exit 1

# Start Django through Gunicorn
CMD ["gunicorn", "resume_bank.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
