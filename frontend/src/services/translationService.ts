/**
 * Mapeo de términos en inglés a español para tipos de eventos
 */
const eventTypeTranslations: {[key: string]: string} = {
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
    'other': 'Otro'
};

/**
 * Traduce tipos de eventos al español
 * @param eventType Tipo de evento en inglés
 * @returns Tipo de evento traducido al español
 */
export function translateEventType(eventType: string | null | undefined): string {
    if (!eventType) return 'Sin clasificar';
    
    const normalizedType = eventType.toLowerCase();
    return eventTypeTranslations[normalizedType] || eventType;
}
