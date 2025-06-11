#!/usr/bin/env python3
"""
Script para probar la implementación del modelo YOLO en el ClasificadorV2.
Este script cargará y ejecutará el modelo YOLO para detectar objetos en una imagen de prueba.
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path

# Obtener rutas absolutas para evitar problemas de importación
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, ".."))

# Importar primero el módulo module_loader_v2 para configurar el entorno
sys.path.insert(0, script_dir)
print("Configurando el entorno...")
try:
    import module_loader_v2
    
    # Utilizar el cargador de módulos mejorado
    config, media_processor_module = module_loader_v2.import_app_modules()
    
    if config is None or media_processor_module is None:
        print("❌ No se pudieron cargar los módulos necesarios")
        sys.exit(1)
        
    # Obtener las clases/objetos necesarios de los módulos
    settings = config.settings
    MediaProcessor = media_processor_module.MediaProcessor
    
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error al importar module_loader_v2.py: {e}")
    print("Asegúrese de que el archivo module_loader_v2.py está en el mismo directorio")
    sys.exit(1)

def test_model():
    """Prueba la detección de objetos con YOLO"""
    print("\n=== Prueba de YOLO para detección de objetos ===")
    
    # Inicializar el procesador de medios
    media_processor = MediaProcessor()
    
    # Definir la ruta a una imagen de prueba
    # Usamos una imagen existente en el repositorio o cualquier otra imagen disponible
    test_image = str(Path(__file__).parent.parent / "Contexto" / "test_real.jpg")
    
    if not os.path.exists(test_image):
        print(f"No se encontró la imagen de prueba: {test_image}")
        print("Buscando una imagen alternativa...")
        
        # Intentar encontrar cualquier imagen en el sistema
        for img_path in [
            Path(__file__).parent.parent / "Contexto" / "tela.png",
            Path(__file__).parent.parent / "storage" / "uploads",
            Path(__file__).parent.parent / "storage" / "processed",
        ]:
            if img_path.is_dir():
                for file in img_path.glob("*.jpg"):
                    test_image = str(file)
                    print(f"Se utilizará la imagen: {test_image}")
                    break
                for file in img_path.glob("*.png"):
                    test_image = str(file)
                    print(f"Se utilizará la imagen: {test_image}")
                    break
            if os.path.exists(test_image):
                break
                
        if not os.path.exists(test_image):
            print("No se encontró ninguna imagen para probar. Por favor, especifique una ruta válida.")
            sys.exit(1)
    
    print(f"Utilizando imagen de prueba: {test_image}")
    
    try:
        # Cargar el modelo YOLO
        print("Cargando modelo YOLO...")
        media_processor._load_opencv_dnn_model()
        
        # Cargar la imagen
        img = cv2.imread(test_image)
        if img is None:
            print(f"Error: No se pudo cargar la imagen {test_image}")
            sys.exit(1)
            
        # Preparar el blob para YOLO
        blob = cv2.dnn.blobFromImage(
            img, 
            1/255.0,
            (416, 416),
            swapRB=False,
            crop=False
        )
        
        # Pasar la imagen por la red
        media_processor.opencv_dnn_model.setInput(blob)
        
        # Obtener las predicciones
        outputs = media_processor.opencv_dnn_model.forward(media_processor.yolo_output_layers)
        
        # Procesar resultados
        print("\nObjetos detectados:")
        detected_objects = []
        
        # Umbral de confianza para las detecciones
        conf_threshold = 0.5
        
        # Procesar cada salida
        for output in outputs:
            # Cada fila es una detección
            for detection in output:
                # Los primeros 4 valores son x, y, w, h (centro y dimensiones del bounding box)
                # Resto de valores son las confianzas para cada clase
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > conf_threshold:
                    class_name = media_processor.opencv_classes[class_id]
                    detected_objects.append((class_name, float(confidence)))
        
        # Mostrar los objetos detectados
        for obj, conf in detected_objects:
            print(f"  - {obj}: {conf:.4f}")
            
        # Realizar la predicción del evento
        print("\nPredecir evento basado en objetos detectados:")
        # Forzar el uso del modelo YOLO para la predicción
        old_model = settings.AI_MODEL
        settings.AI_MODEL = "opencv_yolo"
        
        event_type, confidence = media_processor.predict_event(test_image)
        print(f"\nEvento detectado: {event_type} (confianza: {confidence:.4f})")
        
        # Restaurar el modelo original
        settings.AI_MODEL = old_model
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n=== Prueba completada ===")

if __name__ == "__main__":
    test_model()
