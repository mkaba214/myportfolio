# Multi-stage Dockerfile for Django Web Application
# ================================================
# This Dockerfile creates an optimized container image for the Django application
# used in the AWS DevOps Capstone Project.

# Build stage: Install dependencies and build application
FROM python:3.9-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Add metadata labels
LABEL maintainer="Mohamed Adama Kaba <email@example.com>"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.name="Django Web Application"
LABEL org.label-schema.description="Containerized Django app for AWS DevOps pipeline"
LABEL org.label-schema.version=$VERSION
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.schema-version="1.0"

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run tests during build (optional - can be disabled for faster builds)
# RUN python manage.py test

# Production stage: Create final lightweight image
FROM python:3.9-slim as production

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=myproject.settings.production
ENV PORT=8000

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django

# Create directories
RUN mkdir -p /app /app/staticfiles /app/media
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code and static files
COPY --from=builder /app .

# Set ownership of application files
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ || exit 1

# Default command
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT myproject.wsgi:application"]

# Alternative commands for different environments:
# Development: CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Production with Gunicorn: CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
# Production with uWSGI: CMD ["uwsgi", "--http", ":8000", "--module", "myproject.wsgi"]