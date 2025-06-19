import axios from 'axios';
import type { Media, MediaUpdate } from '../types/media';
import { API_CONFIG } from '../config/constants';

// Configuración global de axios
const apiClient = axios.create({
  baseURL: API_CONFIG.API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
  },
  timeout: 10000
});

// Interceptores para manejo centralizado de errores
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Manejar errores comunes
    if (error.response) {
      // El servidor respondió con un código de estado fuera del rango 2xx
      console.error('Error de respuesta del servidor:', error.response.status, error.response.data);
    } else if (error.request) {
      // La solicitud fue hecha pero no se recibió respuesta
      console.error('No se recibió respuesta del servidor:', error.request);
    } else {
      // Ocurrió un error al configurar la solicitud
      console.error('Error al configurar la solicitud:', error.message);
    }
    
    return Promise.reject(error);
  }
);

/**
 * Servicio para la gestión de medios
 */
export const mediaService = {
  /**
   * Obtiene todos los medios
   */
  async getAllMedia(): Promise<Media[]> {
    try {
      const response = await apiClient.get('/media/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener los medios:', error);
      throw error;
    }
  },
  
  /**
   * Obtiene un medio por su ID
   */
  async getMediaById(id: number): Promise<Media> {
    try {
      const response = await apiClient.get(`/media/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener el medio con ID ${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Sube un nuevo archivo
   */
  async uploadMedia(file: File): Promise<Media> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/media/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error al subir el archivo:', error);
      throw error;
    }
  },
  
  /**
   * Actualiza los datos de un medio
   */
  async updateMedia(id: number, data: MediaUpdate): Promise<Media> {
    try {
      const response = await apiClient.patch(`/media/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar el medio con ID ${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Elimina un medio por su ID
   */
  async deleteMedia(id: number): Promise<void> {
    try {
      await apiClient.delete(`/media/${id}`);
    } catch (error) {
      console.error(`Error al eliminar el medio con ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Regenera archivos procesados
   */
  async regenerateProcessedFiles(): Promise<void> {
    try {
      await apiClient.post('/media/regenerate/');
    } catch (error) {
      console.error('Error al regenerar archivos procesados:', error);
      throw error;
    }
  },
  
  /**
   * Obtiene la URL completa de un medio
   */
  getMediaUrl(path: string): string {
    if (!path) return '';
    return `${API_CONFIG.MEDIA_BASE_URL}${path}`;
  }
};

/**
 * Servicio para la gestión de configuración
 */
export const configService = {
  /**
   * Obtiene el modelo de IA actual
   */
  async getAIModel(): Promise<string> {
    try {
      const response = await apiClient.get('/config/ai-model');
      return response.data.model;
    } catch (error) {
      console.error('Error al obtener el modelo de IA:', error);
      throw error;
    }
  },
  
  /**
   * Establece el modelo de IA
   */
  async setAIModel(model: string): Promise<void> {
    try {
      await apiClient.post('/config/ai-model', { model });
    } catch (error) {
      console.error(`Error al establecer el modelo de IA a ${model}:`, error);
      throw error;
    }
  }
};

/**
 * Servicio para geocodificación y ubicaciones
 */
export const locationService = {
  /**
   * Obtiene el nombre de una ubicación a partir de sus coordenadas
   */
  async getLocationNameFromCoords(
    latitude: number | null | undefined, 
    longitude: number | null | undefined
  ): Promise<string> {
    if (!latitude || !longitude) return 'Ubicación desconocida';
    
    try {
      // Aquí se podría usar una API de geocodificación inversa real
      return `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
    } catch (error) {
      console.error('Error al obtener la ubicación:', error);
      return 'Error al obtener ubicación';
    }
  }
};

/**
 * Servicio para traducciones
 */
export const translationService = {
  /**
   * Traduce un tipo de evento
   */
  translateEventType(eventType: string | null | undefined): string {
    if (!eventType) return 'Desconocido';
    
    const translations: Record<string, string> = {
      'party': 'Fiesta',
      'graduation': 'Graduación',
      'wedding': 'Boda',
      'concert': 'Concierto',
      'sport': 'Deporte',
      'conference': 'Conferencia',
      'meeting': 'Reunión',
      'family': 'Familia',
      'travel': 'Viaje',
      'food': 'Comida',
      'nature': 'Naturaleza',
      'pet': 'Mascota'
    };
    
    return translations[eventType.toLowerCase()] || eventType;
  }
};
