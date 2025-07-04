import axios, { AxiosError } from 'axios';

const API_URL = 'http://localhost:8000/api/v1';
const MEDIA_BASE_URL = 'http://localhost:8000';

// Configurar axios para evitar caché
axios.defaults.headers.common['Cache-Control'] = 'no-cache, no-store, must-revalidate';
axios.defaults.headers.common['Pragma'] = 'no-cache';
axios.defaults.headers.common['Expires'] = '0';

// Definición de tipos
export interface Media {
    id: number;
    filename: string;
    file_path: string;
    file_size: number;
    created_at: string;
    updated_at: string;
    creation_date?: string;
    uploaded_at?: string;
    thumbnail_path?: string | null;
    processed_file_path?: string | null;
    file_type: string;
    width?: number | null;
    height?: number | null;
    latitude?: number | null;
    longitude?: number | null;
    event_type?: string | null;
    event_confidence?: number | null;
}

export interface MediaUpdate {
    event_type?: string | null;
    latitude?: number | null;
    longitude?: number | null;
}

// Función para construir URLs de medios (archivos originales y miniaturas)
export const getMediaUrl = (path: string | null | undefined): string => {
    if (!path) return '';
    
    // Si la ruta ya es una URL completa, devolverla tal como está
    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path;
    }
    
    // Asegurarse de que la ruta comience con /
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    
    return `${MEDIA_BASE_URL}${normalizedPath}`;
};

const handleError = (error: unknown) => {
    if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ detail: string }>;
        if (axiosError.response?.data?.detail) {
            throw new Error(axiosError.response.data.detail);
        }
        throw new Error(axiosError.message);
    }
    throw error;
};

const mediaService = {
    async uploadFile(file: File): Promise<Media> {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await axios.post(`${API_URL}/media/upload/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            handleError(error);
            throw error; // TypeScript necesita esto
        }
    },
    
    async getAllMedia(): Promise<Media[]> {
        try {
            // Añadir un timestamp como parámetro de consulta para evitar caché
            const cacheBuster = new Date().getTime();
            const response = await axios.get(`${API_URL}/media/?timestamp=${cacheBuster}`);
            return response.data;
        } catch (error) {
            handleError(error);
            throw error;
        }
    },
    
    async updateMedia(id: number, data: MediaUpdate): Promise<Media> {
        try {
            const response = await axios.patch(`${API_URL}/media/${id}`, data);
            return response.data;
        } catch (error) {
            handleError(error);
            throw error;
        }
    },
    
    async deleteMedia(id: number): Promise<void> {
        try {
            await axios.delete(`${API_URL}/media/${id}`);
        } catch (error) {
            handleError(error);
            throw error;
        }
    },

    async regenerateProcessedFiles(): Promise<{ success_count: number, failed_count: number }> {
        try {
            const response = await axios.post(`${API_URL}/media/regenerate-processed-files/`);
            return response.data;
        } catch (error) {
            handleError(error);
            throw error;
        }
    },
};

// Función para actualizar un medio
export const updateMedia = async (id: number, data: MediaUpdate): Promise<Media> => {
    try {
        const response = await axios.put(`${API_URL}/media/${id}`, data);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

export default mediaService;
