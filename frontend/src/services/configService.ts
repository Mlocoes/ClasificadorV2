import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Obtiene la configuración actual del sistema
 */
export const getSystemConfig = async () => {
  try {
    const response = await axios.get(`${API_URL}/config/`);
    return response.data;
  } catch (error) {
    console.error('Error al obtener la configuración:', error);
    throw error;
  }
};

/**
 * Cambia el modelo de IA a utilizar
 * @param model - Modelo a utilizar ('clip', 'opencv_dnn' o 'opencv_yolo')
 */
export const setAIModel = async (model: 'clip' | 'opencv_dnn' | 'opencv_yolo') => {
  try {
    const response = await axios.post(`${API_URL}/config/ai-model`, {
      model
    });
    return response.data;
  } catch (error) {
    console.error('Error al cambiar el modelo de IA:', error);
    throw error;
  }
};

export default {
  getSystemConfig,
  setAIModel
};
