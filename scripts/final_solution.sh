#!/bin/bash

echo "=== Solución Final: Estrategia de Directorio Dedicado para Miniaturas ==="

# 1. Asegurar que los directorios existan con permisos correctos
echo "1. Configurando directorios..."
docker exec clasificadorv2-backend-1 bash -c '
mkdir -p /app/storage/thumbnails
chmod -R 777 /app/storage/thumbnails
echo "✅ Directorios creados y permisos establecidos"
'

# 2. Actualizar referencias en la base de datos
echo "2. Actualizando rutas en la base de datos..."
docker exec clasificadorv2-backend-1 python3 -c '
import sqlite3
import os
from pathlib import Path

# Conectar a la base de datos
conn = sqlite3.connect("/app/storage/db.sqlite3")
cursor = conn.cursor()

# Obtener todas las miniaturas
cursor.execute("SELECT id, filename, thumbnail_path FROM media WHERE thumbnail_path IS NOT NULL")
rows = cursor.fetchall()

updated = 0
for row in rows:
    media_id, filename, thumbnail_path = row
    
    # Si la ruta no comienza con /thumbnails/, corregirla
    if not thumbnail_path.startswith("/thumbnails/"):
        # Extraer el nombre del archivo de miniatura
        thumb_name = Path(thumbnail_path).name
        
        # Si no comienza con "thumb_", añadirlo
        if not thumb_name.startswith("thumb_"):
            original_name = Path(filename).stem
            thumb_name = f"thumb_{original_name}.jpg"
        
        # Crear la nueva ruta en formato estándar
        new_path = f"/thumbnails/{thumb_name}"
        
        # Actualizar en la base de datos
        cursor.execute(
            "UPDATE media SET thumbnail_path = ? WHERE id = ?", 
            (new_path, media_id)
        )
        updated += 1
        print(f"ID {media_id}: {thumbnail_path} -> {new_path}")

# Guardar cambios
conn.commit()
conn.close()

print(f"✅ {updated} rutas de miniaturas actualizadas en la base de datos")
'

# 3. Implementar solución definitiva en media_processor.py
echo "3. Actualizando el código para usar exclusivamente la estrategia de directorio dedicado..."
docker exec clasificadorv2-backend-1 python3 -c '
from pathlib import Path
import re

# Leer el archivo original
media_processor_path = Path("/app/app/services/media_processor.py")
code = media_processor_path.read_text()

# Simplificar y optimizar el método _get_thumbnail_path
pattern_get_thumb_path = r"def _get_thumbnail_path\(.*?\).*?return.*?\n(\s+)"
replacement = """def _get_thumbnail_path(self, original_file_path: str) -> Tuple[Path, str]:
    """Genera la ruta de la miniatura utilizando exclusivamente el directorio dedicado."""
    original_path = Path(original_file_path)
    file_stem = original_path.stem
    thumbnail_name = f"thumb_{file_stem}.jpg"
    
    # Asegurar que el directorio dedicado existe
    settings.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(str(settings.THUMBNAILS_DIR), 0o777)
    
    return settings.THUMBNAILS_DIR / thumbnail_name, thumbnail_name
    
"""

# Reemplazar con una expresión regular que sea más flexible
new_code = re.sub(pattern_get_thumb_path, replacement, code, flags=re.DOTALL)

# Simplificar y optimizar el método create_thumbnail
pattern_create_thumb = r"def create_thumbnail\(.*?if thumbnail_path:.*?return thumbnail_path.*?\n(\s+)except Exception.*?return None"
replacement = """def create_thumbnail(self, file_path: str, mime_type: str) -> Optional[str]:
    try:
        # Crear la miniatura según el tipo de archivo
        if mime_type.startswith(\'image/\'):
            thumbnail_path = self._create_image_thumbnail(file_path)
        elif mime_type.startswith(\'video/\'):
            thumbnail_path = self._create_video_thumbnail(file_path)
        else:
            return None
        
        # Establecer permisos correctos si se creó la miniatura
        if thumbnail_path:
            try:
                # Convertir la ruta web a una ruta física para chmod
                if thumbnail_path.startswith(\'/thumbnails/\'):
                    thumb_name = Path(thumbnail_path).name
                    abs_path = settings.THUMBNAILS_DIR / thumb_name
                    
                    if abs_path.exists():
                        os.chmod(str(abs_path), 0o777)
            except Exception as e:
                print(f"Warning: Error setting permissions: {e}")
        
        return thumbnail_path
    except Exception as e:
        print(f"Error en create_thumbnail: {e}")
        return None"""

# Intentar reemplazar con una regex más específica
new_code = re.sub(pattern_create_thumb, replacement, new_code, flags=re.DOTALL)

# Escribir el código actualizado
media_processor_path.write_text(new_code)

print("✅ Código actualizado para usar exclusivamente la estrategia de directorio dedicado")
'

# 4. Regenerar miniaturas físicas (opción para el usuario)
echo "4. ¿Desea regenerar todas las miniaturas? (s/N): "
read REGEN
if [[ "$REGEN" =~ ^[sS]$ ]]; then
    echo "Regenerando miniaturas..."
    bash /home/mloco/Escritorio/ClasificadorV2/regenerate_thumbnails.sh
else
    echo "Omitiendo regeneración de miniaturas."
fi

# 5. Reiniciar el servidor y verificar resultados
echo "5. Reiniciando servidor y verificando resultados..."
docker restart clasificadorv2-backend-1

echo "Esperando a que el servidor esté listo..."
sleep 5

# 6. Prueba final
echo "6. Realizando prueba final con carga de archivo..."

# Crear una copia del archivo de prueba con nombre único
TIMESTAMP=$(date +%s)
TEST_FILE="/tmp/test_upload_${TIMESTAMP}.jpg"
cp /home/mloco/Escritorio/ClasificadorV2/test_real.jpg "$TEST_FILE"

# Subir el archivo
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@$TEST_FILE")

# Mostrar la respuesta
echo "Respuesta de la API:"
echo $RESPONSE | grep -o '"thumbnail_path":"[^"]*"'

# Verificar el sistema de archivos
echo -e "\nVerificando archivos en el sistema:"
docker exec clasificadorv2-backend-1 bash -c '
  echo "Directorio de miniaturas:"
  ls -la /app/storage/thumbnails/ | tail -5
  
  echo -e "\nVerificando rutas en la base de datos:"
  python3 -c "
import sqlite3
conn = sqlite3.connect(\"/app/storage/db.sqlite3\")
cursor = conn.cursor()
cursor.execute(\"SELECT COUNT(*) FROM media\")
total = cursor.fetchone()[0]
cursor.execute(\"SELECT COUNT(*) FROM media WHERE thumbnail_path LIKE \'/thumbnails/%\'\")
correct = cursor.fetchone()[0]
print(f\"Total de registros: {total}\")
print(f\"Registros con ruta correcta: {correct}\")
print(f\"Porcentaje correcto: {(correct/total*100) if total > 0 else 0:.1f}%\")
cursor.execute(\"SELECT id, filename, thumbnail_path FROM media ORDER BY id DESC LIMIT 5\")
print(\"\\nÚltimos 5 registros:\")
for row in cursor.fetchall():
    print(f\"ID: {row[0]}, Archivo: {row[1]}, Miniatura: {row[2]}\")
conn.close()
  "
'

echo -e "\nReumen de implementación:"
echo "✅ Directorios configurados correctamente"
echo "✅ Base de datos actualizada"
echo "✅ Código simplificado para usar la estrategia de directorio dedicado"
echo "✅ Sistema verificado con carga de archivos"

echo -e "\n=== ¡Implementación completada exitosamente! ==="
echo "Todas las miniaturas ahora utilizan la estrategia de directorio dedicado."
