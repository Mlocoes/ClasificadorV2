FROM python:3.10-slim

# Crear usuario no root
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    libmagic1 \
    ffmpeg \
    libsm6 \
    libxext6 \
    wget \
    libheif-dev \
    libde265-0 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios y establecer permisos
RUN mkdir -p /app/storage/uploads /app/storage/thumbnails /app/cache && \
    chown -R appuser:appuser /app/storage /app/cache && \
    chmod -R 755 /app/storage /app/cache

# Copiar y dar permisos al script de healthcheck
COPY healthcheck.py /app/healthcheck.py
RUN chmod +x /app/healthcheck.py && \
    chown appuser:appuser /app/healthcheck.py

# Copiar el código de la aplicación
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Cambiar al usuario no root
USER appuser

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Configurar el healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["./healthcheck.py"]
