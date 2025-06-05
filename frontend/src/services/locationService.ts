const NOMINATIM_API_BASE = 'https://nominatim.openstreetmap.org';

export async function getLocationNameFromCoords(lat: number, lon: number): Promise<string> {
    try {
        const response = await fetch(
            `${NOMINATIM_API_BASE}/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10&addressdetails=1`
        );
        
        if (!response.ok) {
            throw new Error('Error al obtener la ubicación');
        }
        
        const data = await response.json();
        
        // Extraer ciudad (usando varios campos posibles)
        const city = data.address.city || 
                    data.address.town || 
                    data.address.village || 
                    data.address.municipality ||
                    data.address.suburb;
                    
        // Obtener el país
        const country = data.address.country;
        
        if (city && country) {
            return `${city}, ${country}`;
        } else if (country) {
            return country;
        } else {
            return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
        }
    } catch (error) {
        console.error('Error al obtener la ubicación:', error);
        return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
    }
}
