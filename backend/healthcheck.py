#!/usr/bin/env python3
import sys
import requests
import time
from pathlib import Path

def check_directories():
    """Verificar que los directorios necesarios existen"""
    required_dirs = [
        Path("/app/storage"),
        Path("/app/storage/uploads"),
        Path("/app/storage/thumbnails"),
        Path("/app/cache")
    ]
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"Error: Directorio {dir_path} no existe")
            return False
    return True

def check_api():
    """Verificar que la API está respondiendo"""
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            return True
        print(f"Error: API respondió con código {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error conectando con la API: {e}")
        return False

# Esperar un poco antes de hacer el healthcheck
# Esto da tiempo a que uvicorn inicie completamente
time.sleep(2)

# Verificar directorios y API
if check_directories() and check_api():
    sys.exit(0)
else:
    sys.exit(1)
