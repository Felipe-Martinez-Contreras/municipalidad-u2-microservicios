FROM python:3.12-slim
LABEL maintainer="Municipalidad La Estrella"
LABEL description="Portal Web Municipal - Frontend"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*
RUN useradd --no-create-home --shell /bin/false appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /tmp/django_sessions && chown -R appuser:appuser /app /tmp/django_sessions
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 --workers 3 portal_service.wsgi:application"]
