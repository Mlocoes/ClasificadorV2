FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios
RUN mkdir -p /app/storage/uploads /app/storage/thumbnails

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Asegurarnos de que el directorio de storage tenga los permisos correctos
RUN chown -R root:root /app/storage && \
    chmod -R 777 /app/storage

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
