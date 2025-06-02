import axios from 'axios';

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

const mediaService = {
    async uploadFile(file: File): Promise<Media> {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(`${API_URL}/media/upload/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
    
    async getAllMedia(): Promise<Media[]> {
        const response = await axios.get(`${API_URL}/media/`);
        return response.data;
    },
    
    async updateMedia(id: number, data: MediaUpdate): Promise<Media> {
        const response = await axios.patch(`${API_URL}/media/${id}`, data);
        return response.data;
    },
    
    async deleteMedia(id: number): Promise<void> {
        await axios.delete(`${API_URL}/media/${id}`);
    },
};

export default mediaService;
