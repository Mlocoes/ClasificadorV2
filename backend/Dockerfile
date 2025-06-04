FROM python:3.10-slim

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
    && rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios
RUN mkdir -p /app/storage/uploads /app/storage/thumbnails

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Instalar requests para el healthcheck
RUN pip install requests

# Asegurarnos de que los directorios tengan los permisos correctos
RUN chmod -R 777 /app/storage && \
    mkdir -p /app/cache && \
    chmod -R 777 /app/cache

# Agregar script de healthcheck
COPY healthcheck.py /app/
RUN chmod +x /app/healthcheck.py

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python3", "/app/healthcheck.py"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
