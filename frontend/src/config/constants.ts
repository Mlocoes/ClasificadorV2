/**
 * Configuración centralizada de la aplicación
 */

export const API_CONFIG = {
  // URL base de la API
  API_URL: 'http://localhost:8000/api/v1',
  
  // URL base para recursos multimedia
  MEDIA_BASE_URL: 'http://localhost:8000',
  
  // Tiempo de caché para consultas (en milisegundos)
  CACHE_TIME: 5 * 60 * 1000, // 5 minutos
  
  // Tiempo para considerar datos como obsoletos
  STALE_TIME: 0, // Inmediatamente obsoletos
  
  // Número de reintentos para peticiones fallidas
  RETRY_COUNT: 1,
}

export const UI_CONFIG = {
  // Temas
  THEMES: {
    LIGHT: 'light',
    DARK: 'dark',
  },
  
  // Modos de visualización
  VIEW_MODES: {
    GRID: 'grid',
    TABLE: 'table',
  },
  
  // Tamaños de página
  PAGE_SIZES: [10, 25, 50, 100],
  
  // Tamaño de página por defecto
  DEFAULT_PAGE_SIZE: 25,
}

export const FEATURE_FLAGS = {
  // Habilitar características experimentales
  ENABLE_EXPERIMENTAL: false,
  
  // Habilitar modo oscuro
  ENABLE_DARK_MODE: true,
  
  // Habilitar herramientas de desarrollo
  ENABLE_DEV_TOOLS: import.meta.env.DEV,
  
  // Habilitar localización GPS
  ENABLE_LOCATION: true,
}
