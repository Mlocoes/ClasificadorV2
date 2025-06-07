const NOMINATIM_API_BASE = 'https://nominatim.openstreetmap.org';

interface LocationDetails {
    city?: string;
    town?: string;
    village?: string;
    municipality?: string;
    suburb?: string;
    district?: string;
    county?: string;
    state?: string;
    country?: string;
}

function formatLocation(address: LocationDetails): string {
    // Obtener la localidad (ciudad, pueblo, villa, etc.)
    const locality = address.city || 
                    address.town || 
                    address.village || 
                    address.municipality ||
                    address.suburb ||
                    address.district ||
                    address.county;
    
    // Construir la cadena de ubicación
    let location = '';
    
    if (locality) {
        location = locality;
        // Agregar el estado si existe y es diferente de la localidad
        if (address.state && address.state !== locality) {
            location += `, ${address.state}`;
        }
        // Agregar el país si existe y es diferente del estado y la localidad
        if (address.country && address.country !== address.state && address.country !== locality) {
            location += `, ${address.country}`;
        }
    } else if (address.state) {
        location = address.state;
        if (address.country && address.country !== address.state) {
            location += `, ${address.country}`;
        }
    } else if (address.country) {
        location = address.country;
    }
    
    return location;
}

export async function getLocationNameFromCoords(lat: number, lon: number): Promise<string> {
    try {
        const url = `${NOMINATIM_API_BASE}/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=es`;
        
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'ClasificadorV2'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (!data || !data.address) {
            return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
        }

        const location = formatLocation(data.address);
        return location || `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
    } catch (error) {
        console.error('Error obteniendo ubicación:', error);
        return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
    }
}
