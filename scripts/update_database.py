#!/usr/bin/env python3
"""
Script para actualizar la estructura de la base de datos
Añade la columna processed_file_path a la tabla media si no existe
"""
import os
import sys
import sqlite3
from pathlib import Path

# Obtener la ruta de la base de datos
DB_PATH = os.environ.get('DB_PATH', '/app/storage/db.sqlite3')

def main():
    print(f"Intentando actualizar la base de datos en: {DB_PATH}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la columna existe
        cursor.execute("PRAGMA table_info(media)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'processed_file_path' not in columns:
            print("La columna processed_file_path no existe, añadiéndola...")
            cursor.execute("ALTER TABLE media ADD COLUMN processed_file_path TEXT")
            conn.commit()
            print("Columna añadida exitosamente")
        else:
            print("La columna processed_file_path ya existe. No se requieren cambios.")
        
        print("Verificando las columnas actuales:")
        cursor.execute("PRAGMA table_info(media)")
        columns = cursor.fetchall()
        for column in columns:
            print(f"- {column[1]} ({column[2]})")
        
        conn.close()
        print("Actualización completada exitosamente.")
        return 0
    except Exception as e:
        print(f"Error actualizando la base de datos: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
