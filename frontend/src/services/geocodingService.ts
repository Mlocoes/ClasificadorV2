// Servicio de geocodificación para convertir direcciones en coordenadas
import axios from 'axios';

// API utilizada: OpenStreetMap Nominatim
// Documentación: https://nominatim.org/release-docs/develop/api/Search/

interface GeocodingResult {
    lat: number;
    lon: number;
    display_name: string;
}

/**
 * Convierte una dirección (ciudad, país, etc.) en coordenadas geográficas
 * @param address Dirección a convertir (ej: "Madrid, España")
 * @returns Promesa con las coordenadas y el nombre del lugar
 */
export const geocodeAddress = async (address: string): Promise<{
    latitude: number;
    longitude: number;
    displayName: string;
}> => {
    try {
        // Usamos la API pública de Nominatim (OSM)
        const response = await axios.get('https://nominatim.openstreetmap.org/search', {
            params: {
                q: address,
                format: 'json',
                limit: 1,
                addressdetails: 1,
            },
            headers: {
                'User-Agent': 'ClasificadorV2',
                'Accept-Language': 'es' // Para obtener resultados en español
            }
        });

        if (response.data && response.data.length > 0) {
            const result = response.data[0] as GeocodingResult;
            return {
                latitude: result.lat,
                longitude: result.lon,
                displayName: result.display_name
            };
        }
        throw new Error('No se encontró la ubicación');
    } catch (error) {
        console.error('Error geocodificando la dirección:', error);
        throw error;
    }
};

/**
 * Sugerencias de lugares basadas en texto de búsqueda
 * @param query Texto para buscar lugares
 * @returns Lista de lugares sugeridos
 */
export const searchPlaces = async (query: string): Promise<{
    id: string;
    name: string;
    displayName: string;
    latitude: number;
    longitude: number;
}[]> => {
    if (!query || query.length < 3) return [];

    try {
        const response = await axios.get('https://nominatim.openstreetmap.org/search', {
            params: {
                q: query,
                format: 'json',
                limit: 5,
                addressdetails: 1,
            },
            headers: {
                'User-Agent': 'ClasificadorV2',
                'Accept-Language': 'es'
            }
        });

        if (response.data && response.data.length > 0) {
            return response.data.map((item: any) => ({
                id: String(item.place_id),
                name: item.name || item.display_name.split(',')[0],
                displayName: item.display_name,
                latitude: parseFloat(String(item.lat)),
                longitude: parseFloat(String(item.lon))
            }));
        }
        return [];
    } catch (error) {
        console.error('Error buscando lugares:', error);
        return [];
    }
};

export default {
    geocodeAddress,
    searchPlaces
};
