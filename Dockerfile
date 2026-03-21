# ═══════════════════════════════════════════════════════════════
#  Stage 1 — builder
#  Instala dependencias en un entorno aislado.
#  Al no copiarse al stage final, mantiene la imagen limpia.
# ═══════════════════════════════════════════════════════════════
FROM python:3.12-slim AS builder

WORKDIR /build

# Copiar solo requirements para aprovechar la caché de capas
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ═══════════════════════════════════════════════════════════════
#  Stage 2 — producción
#  Imagen final mínima, sin herramientas de build.
# ═══════════════════════════════════════════════════════════════
FROM python:3.12-slim AS production

# Metadatos de la imagen
LABEL maintainer="proyecto-cicd" \
      description="API REST de Tareas – Flask + PostgreSQL" \
      version="1.0.0"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /install /usr/local

# Copiar código fuente de la aplicación
COPY app/ ./app/
COPY wsgi.py .

# Crear usuario no-root para mayor seguridad
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

# Health check interno del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Arrancar con Gunicorn: 2 workers síncronos, adecuado para contenedores
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "wsgi:app"]
