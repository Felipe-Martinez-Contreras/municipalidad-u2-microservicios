FROM python:3.12-slim

LABEL maintainer="Municipalidad La Estrella"
LABEL description="Servicio de IA - Análisis de Inventario con Gemini"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --no-create-home --shell /bin/false appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ai/analisis-inventario/ | grep -qE '401|200' || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "ai_service.wsgi:application"]
