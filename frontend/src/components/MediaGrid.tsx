import React from 'react';
import { 
    Grid, 
    Card, 
    CardMedia, 
    CardContent, 
    Typography, 
    Box,
    Button,
    CircularProgress,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import DeleteIcon from '@mui/icons-material/Delete';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import type { Media } from '../services/mediaService';
import { getMediaUrl } from '../services/mediaService';
import { getLocationNameFromCoords } from '../services/locationService';
import { translateEventType } from '../services/translationService';
import { LoadingSkeleton } from './LoadingSkeleton';

interface MediaGridProps {
    media: Media[];
    onMediaSelect?: (media: Media) => void;
    onMediaDelete?: (id: number) => Promise<void>;
    isLoading?: boolean;
}

const MediaCard: React.FC<{ 
    media: Media; 
    onSelect?: (m: Media) => void; 
    onDelete?: (id: number) => Promise<void>;
}> = ({ media: item, onSelect, onDelete }) => {
    const [locationName, setLocationName] = React.useState<string>('');
    const [isLoadingLocation, setIsLoadingLocation] = React.useState(false);

    React.useEffect(() => {
        const loadLocation = async () => {
            if (item.latitude !== null && item.latitude !== undefined && 
                item.longitude !== null && item.longitude !== undefined) {
                setIsLoadingLocation(true);
                try {
                    const name = await getLocationNameFromCoords(item.latitude, item.longitude);
                    setLocationName(name || `${item.latitude.toFixed(4)}, ${item.longitude.toFixed(4)}`);
                } catch (error) {
                    console.error('Error cargando ubicación:', error);
                    setLocationName(item.latitude && item.longitude 
                        ? `${item.latitude.toFixed(4)}, ${item.longitude.toFixed(4)}` 
                        : 'Sin ubicación'
                    );
                } finally {
                    setIsLoadingLocation(false);
                }
            } else {
                setLocationName('Sin ubicación');
            }
        };

        loadLocation();
    }, [item.latitude, item.longitude]);

    // Mover la función formatDate dentro del componente para evitar problemas de scope
    const formatDate = (date: string | null | undefined): string => {
        if (!date) return 'Fecha desconocida';
        
        try {
            return new Date(date).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return 'Fecha desconocida';
        }
    };

    const handleDelete = async (e: React.MouseEvent) => {
        e.stopPropagation(); // Evitar que el evento se propague al contenedor
        if (onDelete && window.confirm('¿Estás seguro de que quieres eliminar este archivo?')) {
            try {
                await onDelete(item.id);
            } catch (error) {
                console.error('Error al eliminar:', error);
            }
        }
    };

    // Obtener la URL de la miniatura o imagen original
    const imageUrl = getMediaUrl(item.thumbnail_path) || getMediaUrl(item.file_path) || '';

    return (
        <Grid item xs={12} sm={6} md={4} lg={3}>
            <Card sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                '&:hover': {
                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                }
            }}>
                <CardMedia
                    component="img"
                    height="200"
                    image={imageUrl}
                    alt={item.filename || 'Sin nombre'}
                    sx={{ cursor: 'pointer', objectFit: 'cover' }}
                    onClick={() => onSelect?.(item)}
                    onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                        e.currentTarget.src = '/placeholder-image.png'; // Asegúrate de tener una imagen placeholder
                    }}
                />
                <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                    <Typography
                        variant="subtitle1"
                        sx={{ 
                            mb: 1, 
                            fontWeight: 'medium',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}
                    >
                        {item.filename || 'Sin nombre'}
                    </Typography>

                    <Box sx={{ mt: 'auto' }}>
                        <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ display: 'flex', alignItems: 'center', mb: 1 }}
                        >
                            <LocationOnIcon sx={{ fontSize: 16, mr: 0.5 }} />
                            {isLoadingLocation ? (
                                <CircularProgress size={12} />
                            ) : (
                                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {locationName}
                                </span>
                            )}
                        </Typography>

                        <Typography variant="body2" color="text.secondary">
                            {formatDate(item.creation_date || item.uploaded_at || item.created_at)}
                        </Typography>

                        {item.event_type && (
                            <Typography
                                variant="body2"
                                sx={{
                                    mt: 1,
                                    py: 0.5,
                                    px: 1,
                                    bgcolor: 'rgba(0, 0, 0, 0.05)',
                                    borderRadius: 1,
                                    display: 'inline-block'
                                }}
                            >
                                {translateEventType(item.event_type)}
                                {item.event_confidence !== null && item.event_confidence !== undefined && 
                                    ` (${(item.event_confidence * 100).toFixed(1)}%)`
                                }
                            </Typography>
                        )}

                        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
                            {onSelect && (
                                <Button
                                    size="small"
                                    startIcon={<InfoIcon />}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onSelect(item);
                                    }}
                                >
                                    Ver detalles
                                </Button>
                            )}
                            {onDelete && (
                                <Button
                                    size="small"
                                    color="error"
                                    startIcon={<DeleteIcon />}
                                    onClick={handleDelete}
                                >
                                    Eliminar
                                </Button>
                            )}
                        </Box>
                    </Box>
                </CardContent>
            </Card>
        </Grid>
    );
};

const MediaGrid: React.FC<MediaGridProps> = ({
    media,
    onMediaSelect,
    onMediaDelete,
    isLoading
}) => {
    if (isLoading && media.length === 0) {
        return <LoadingSkeleton count={8} variant="card" />;
    }

    if (media.length === 0) {
        return (
            <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                p: 4,
                minHeight: '200px'
            }}>
                <Typography 
                    variant="body1"
                    sx={{ 
                        fontSize: '16px',
                        color: '#6b6b6b',
                        textAlign: 'center'
                    }}
                >
                    No hay archivos para mostrar
                </Typography>
            </Box>
        );
    }

    return (
        <Grid container spacing={3} sx={{ p: 3 }}>
            {media.map((item) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
                    <MediaCard
                        media={item}
                        onSelect={onMediaSelect}
                        onDelete={onMediaDelete}
                    />
                </Grid>
            ))}
        </Grid>
    );
};

export default MediaGrid;