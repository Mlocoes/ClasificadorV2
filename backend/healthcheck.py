#!/usr/bin/env python3
import sys
import requests

try:
    response = requests.get('http://localhost:8000/api/v1/media/')
    if response.status_code in [200, 404]:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f"Error en healthcheck: {e}")
    sys.exit(1)
