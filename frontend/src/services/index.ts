// Exportar todos los servicios desde un punto central
export { default as mediaService } from './mediaService';
export { default as geocodingService } from './geocodingService';
export { default as configService } from './configService';

// Exportar también funciones específicas
export { getMediaUrl } from './mediaService';
export { getLocationNameFromCoords } from './locationService';
export { translateEventType } from './translationService';
export { geocodeAddress, searchPlaces } from './geocodingService';
export { getSystemConfig, setAIModel } from './configService';
