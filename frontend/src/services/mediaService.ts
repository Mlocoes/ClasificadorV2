import axios, { AxiosError } from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export interface Media {
    id: number;
    filename: string;
    file_path: string;
    thumbnail_path: string | null;
    mime_type: string;
    file_size: number;
    width: number | null;
    height: number | null;
    duration: number | null;
    latitude: number | null;
    longitude: number | null;
    creation_date: string | null;
    event_type: string | null;
    event_confidence: number | null;
    uploaded_at: string;
    updated_at: string | null;
}

export interface MediaUpdate {
    event_type?: string;
    latitude?: number;
    longitude?: number;
}

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
            const response = await axios.get(`${API_URL}/media/`);
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
};

export default mediaService;
