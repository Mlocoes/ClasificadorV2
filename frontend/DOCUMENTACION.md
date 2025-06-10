# Documentación del Frontend de ClasificadorV2

<div align="center">

![Logo ClasificadorV2](https://img.icons8.com/color/96/000000/media-storage.png)

</div>

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Componentes](#componentes)
5. [Servicios](#servicios)
6. [Gestión de Estado](#gestión-de-estado)
7. [Interfaz de Usuario](#interfaz-de-usuario)
8. [Integración con el Backend](#integración-con-el-backend)
9. [Instalación y Ejecución](#instalación-y-ejecución)
10. [Mejores Prácticas y Patrones](#mejores-prácticas-y-patrones)
11. [Funcionalidades Avanzadas](#funcionalidades-avanzadas)

## 📄 Descripción General

El frontend de ClasificadorV2 es una aplicación web moderna desarrollada con React, TypeScript y Vite. Proporciona una interfaz de usuario intuitiva para la gestión, visualización y clasificación de archivos multimedia (imágenes y videos). La aplicación permite a los usuarios cargar, clasificar, buscar, editar y eliminar archivos multimedia, con funcionalidades específicas para la gestión de metadatos como tipos de eventos y ubicaciones geográficas.

## 🛠️ Tecnologías Utilizadas

- **React 18.2.0**: Biblioteca para construir interfaces de usuario
- **TypeScript 5.2.2**: Superset de JavaScript con tipado estático
- **Vite 5.0.0**: Herramienta de construcción moderna para desarrollo web
- **Material UI 5.14.20**: Framework de componentes UI con diseño Material Design
- **React Query 5.80.6**: Librería para gestión de estado del servidor y caché
- **Axios 1.6.2**: Cliente HTTP para realizar peticiones a la API
- **React Dropzone 14.2.3**: Componente para carga de archivos mediante drag-and-drop
- **Date-fns 2.30.0**: Utilidades para manejo de fechas

## 🗂️ Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/        # Componentes reutilizables de la UI
│   │   ├── FileUpload.tsx
│   │   ├── Header.tsx
│   │   ├── LoadingSkeleton.tsx
│   │   ├── MediaGrid.tsx
│   │   ├── MediaTable.tsx
│   │   └── UploadArea.tsx
│   ├── services/          # Servicios para comunicación con la API
│   │   ├── locationService.ts
│   │   ├── mediaService.ts
│   │   └── translationService.ts
│   ├── App.tsx            # Componente principal de la aplicación
│   └── main.tsx           # Punto de entrada de la aplicación
├── package.json           # Dependencias y scripts del proyecto
└── vite.config.ts         # Configuración de Vite
```

## 🧩 Componentes

### Componentes Principales

#### `App.tsx`
Componente raíz que maneja el estado global, la configuración de React Query, el tema de Material UI, y orquesta todos los demás componentes. Implementa la lógica de navegación entre vistas de cuadrícula y tabla.

#### `MediaTable.tsx`
Muestra los archivos multimedia en formato de tabla con capacidades de ordenación, filtrado y edición. Permite ver detalles completos de cada archivo, editar sus metadatos y eliminar archivos.

**Características principales:**
- Visualización tabular de archivos
- Edición inline de metadatos
- Ordenación por columnas
- Acciones contextuales (eliminar, editar)
- Visualización de miniaturas

#### `MediaGrid.tsx`
Presenta los archivos multimedia en formato de cuadrícula visual con tarjetas. Optimizado para la visualización de imágenes y miniaturas de videos.

**Características principales:**
- Vista en cuadrícula de miniaturas
- Información básica en cada tarjeta
- Acciones rápidas (eliminar)
- Visualización adaptable en dispositivos móviles

#### `UploadArea.tsx`
Componente para la carga de archivos mediante arrastrar y soltar o selección de archivos. Implementa React Dropzone para una experiencia de usuario fluida.

**Características principales:**
- Interfaz de arrastrar y soltar
- Validación de tipos de archivos permitidos
- Feedback visual durante la carga
- Indicador de progreso

#### `Header.tsx`
Barra de navegación superior con logo, barra de búsqueda y controles principales.

### Componentes Auxiliares

#### `LoadingSkeleton.tsx`
Componente de esqueleto para mostrar durante la carga de datos, mejorando la experiencia de usuario al proporcionar feedback visual mientras se esperan los resultados.

## 🔌 Servicios

### `mediaService.ts`

Servicio principal para la comunicación con la API del backend relacionada con la gestión de archivos multimedia.

**Funcionalidades:**
- `uploadFile(file)`: Carga un archivo al servidor
- `getAllMedia()`: Obtiene todos los archivos multimedia
- `updateMedia(id, data)`: Actualiza los metadatos de un archivo
- `deleteMedia(id)`: Elimina un archivo del sistema
- `getMediaUrl(path)`: Utilidad para construir URLs de archivos y miniaturas

### `locationService.ts`

Servicio para obtener información de ubicación geográfica a partir de coordenadas.

**Funcionalidades:**
- `getLocationNameFromCoords(lat, lng)`: Traduce coordenadas a nombres de ubicaciones

### `geocodingService.ts`

Servicio para la conversión de nombres de lugares en coordenadas geográficas (geocodificación).

**Funcionalidades:**
- `geocodeAddress(address)`: Convierte una dirección textual en coordenadas geográficas
- `searchPlaces(query)`: Busca lugares que coincidan con el texto de búsqueda y devuelve sugerencias

### `translationService.ts`

Servicio para la traducción y normalización de tipos de eventos y otros textos.

**Funcionalidades:**
- `translateEventType(eventType)`: Traduce los tipos de eventos a formato legible

## 🧠 Gestión de Estado

El proyecto utiliza React Query para la gestión del estado del servidor:

- **Gestión de caché**: Optimiza las peticiones al servidor almacenando en caché los resultados
- **Revalidación inteligente**: Refresca los datos automáticamente cuando el usuario vuelve a la aplicación
- **Estados de carga**: Proporciona estados de `isLoading` e `isRefetching` para mejorar la UX
- **Gestión de errores**: Manejo centralizado de errores de API

El estado local se gestiona mediante hooks de React (`useState`, `useEffect`) para:
- Control de las vistas (grid/list)
- Manejo de diálogos de edición
- Notificaciones de sistema
- Filtros de búsqueda

## 🎨 Interfaz de Usuario

La aplicación utiliza Material UI con un tema personalizado para ofrecer una interfaz moderna y responsive:

- **Tema personalizado**: Colores, tipografías y estilos específicos para la aplicación
- **Diseño responsive**: Adaptado a diferentes tamaños de pantalla
- **Componentes avanzados**: Dialog, Table, Grid, Cards, etc.
- **Iconografía**: Uso de Material Icons
- **Feedback visual**: Loading spinners, skeletons, snackbars para notificaciones
- **Autocompletado inteligente**: Para búsqueda de ubicaciones por nombre

## 🔄 Integración con el Backend

La comunicación con el backend se realiza mediante:

- **Axios**: Para peticiones HTTP al backend
- **React Query**: Para gestión de cache y estado del servidor
- **APIs REST**: Consumo de endpoints definidos en la API

**Endpoints principales utilizados:**
- `GET /api/v1/media/`: Listar todos los archivos
- `POST /api/v1/media/upload/`: Subir archivos
- `PATCH /api/v1/media/{id}`: Actualizar metadatos
- `DELETE /api/v1/media/{id}`: Eliminar archivos

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Node.js 16.x o superior
- npm 7.x o superior

### Instalación de Dependencias

```bash
# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install
```

### Ejecución en Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

### Construcción para Producción

```bash
# Generar build optimizado
npm run build

# Vista previa del build
npm run preview
```

### Variables de Entorno

El frontend requiere las siguientes variables de entorno:

- `VITE_API_URL`: URL base de la API del backend (por defecto: http://localhost:8000/api/v1)
- `VITE_MEDIA_BASE_URL`: URL base para los archivos multimedia (por defecto: http://localhost:8000)

## 🔍 Mejores Prácticas y Patrones

- **Componentes funcionales**: Uso de hooks de React para lógica de componentes
- **Tipado estricto**: Definición de interfaces TypeScript para todos los componentes y servicios
- **Gestión eficiente de recursos**: Carga bajo demanda, lazy loading y optimización de rendimiento
- **Experiencia de usuario optimizada**: Feedback visual durante operaciones, estados de carga, y notificaciones
- **Abstracción de servicios**: Separación clara entre lógica de UI y comunicación con API
- **Validación de datos**: Validación de entradas de usuario antes de enviar al backend
- **Manejo de errores**: Captura y presentación adecuada de errores para el usuario

## 📝 Funcionalidades Avanzadas

### Búsqueda de Ubicaciones por Nombre

Una funcionalidad clave implementada en la versión más reciente es la capacidad de buscar ubicaciones geográficas por nombre (ciudad, país, dirección) y convertirlas automáticamente en coordenadas GPS para asociarlas a los archivos multimedia.

**Características:**
- Autocompletado de nombres de lugares durante la escritura
- Visualización de resultados en tiempo real
- Selección automática de coordenadas al elegir una ubicación
- Integración con OpenStreetMap Nominatim para geocodificación
- Soporte multilenguaje con preferencia para resultados en español
- Opción para limpiar las coordenadas existentes

Esta funcionalidad facilita enormemente la tarea de etiquetar geográficamente los archivos multimedia sin necesidad de conocer las coordenadas exactas.

**Para utilizar esta función:**
1. Editar un archivo multimedia
2. En el campo de búsqueda de ubicación, comenzar a escribir un nombre de lugar (ciudad, país, etc.)
3. Conforme escribes, la aplicación mostrará sugerencias de ubicaciones
4. Seleccionar una ubicación de las sugerencias
5. Las coordenadas de latitud y longitud se completarán automáticamente
6. Si deseas eliminar las coordenadas, puedes usar el botón "Limpiar coordenadas"
7. Guardar los cambios

La búsqueda utiliza la API de OpenStreetMap Nominatim, que proporciona datos geográficos precisos y actualizados para casi cualquier lugar del mundo.

---
