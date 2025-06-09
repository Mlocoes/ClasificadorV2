/**
 * Mapeo de términos para tipos de eventos, tanto para compatibilidad con datos antiguos en inglés
 * como para los nuevos eventos que ya vienen en español del backend
 */
const eventTypeTranslations: {[key: string]: string} = {
    // Términos en inglés (compatibilidad histórica)
    'wedding': 'Boda',
    'conference': 'Conferencia',
    'sports': 'Deportes',
    'concert': 'Concierto',
    'party': 'Fiesta',
    'reunion': 'Reunión',
    'travel': 'Viaje',
    'birthday': 'Cumpleaños',
    'graduation': 'Graduación',
    'family': 'Familiar',
    'business': 'Negocio',
    'religious': 'Religioso',
    'holiday': 'Vacaciones',
    'meeting': 'Reunión',
    'exhibition': 'Exposición',
    'festival': 'Festival',
    'performance': 'Espectáculo',
    'ceremony': 'Ceremonia',
    'protest': 'Protesta',
    'parade': 'Desfile',
    'fair': 'Feria',
    'seminar': 'Seminario',
    'workshop': 'Taller',
    'award': 'Premiación',
    'convention': 'Convención',
    'celebration': 'Celebración',
    'competition': 'Competencia',
    'show': 'Show',
    'presentation': 'Presentación',
    'inauguration': 'Inauguración',
    'anniversary': 'Aniversario',
    'fundraising': 'Recaudación de fondos',
    'gathering': 'Reunión',
    'demonstration': 'Manifestación',
    'other': 'Otro',
    
    // Nuevos formatos de eventos en español que vienen del backend
    'evento deportivo': 'Evento deportivo',
    'sports event or game': 'Evento deportivo',
    'ceremonia religiosa': 'Ceremonia religiosa',
    'religious ceremony': 'Ceremonia religiosa',
    'reunión familiar': 'Reunión familiar',
    'family gathering': 'Reunión familiar',
    'evento gastronómico': 'Evento gastronómico',
    'food event or dining': 'Evento gastronómico',
    'actividad al aire libre': 'Actividad al aire libre',
    'outdoor activity or adventure': 'Actividad al aire libre',
    'evento de negocios': 'Evento de negocios',
    'business event': 'Evento de negocios',
    'evento educativo': 'Evento educativo',
    'educational event': 'Evento educativo',
    'exhibition or art show': 'Exhibición',
    'parade or festival': 'Festival',
    'conference or meeting': 'Conferencia',
    'party or celebration': 'Fiesta',
    'concert or musical performance': 'Concierto',
    'wedding ceremony': 'Boda',
    'graduation ceremony': 'Graduación',
    'protest or demonstration': 'Protesta'
};

/**
 * Traduce tipos de eventos al español.
 * Ahora principalmente para capitalizar primeras letras y manejar casos especiales,
 * ya que los eventos ya vienen en español del backend.
 * 
 * @param eventType Tipo de evento
 * @returns Tipo de evento formateado para presentación
 */
export function translateEventType(eventType: string | null | undefined): string {
    if (!eventType) return 'Sin clasificar';
    
    const normalizedType = eventType.toLowerCase();
    return eventTypeTranslations[normalizedType] || 
           // Capitalizar primera letra si no hay traducción específica
           (eventType.charAt(0).toUpperCase() + eventType.slice(1));
}
