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
import type { Media } from '../services/mediaService';

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
    // Función para formatear la fecha
    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return date.toISOString().split('T')[0]; // Formato YYYY-MM-DD
        } catch (e) {
            return 'Fecha desconocida';
        }
    };

    const handleDelete = async () => {
        if (onDelete && window.confirm('¿Estás seguro de que quieres eliminar este archivo?')) {
            await onDelete(item.id);
        }
    };

    return (
        <Grid item xs={12} sm={6} md={4} lg={3}>
            <Card
                sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    border: '1px solid #dbdbdb',
                    boxShadow: 'none',
                    '&:hover': {
                        borderColor: '#b0b0b0',
                    }
                }}
            >
                <CardMedia
                    component="img"
                    height="180"
                    image={`http://localhost:8000${item.thumbnail_path}`}
                    alt={item.filename}
                    sx={{ cursor: 'pointer', objectFit: 'cover' }}
                    onClick={() => onSelect && onSelect(item)}
                />
                <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                    <Typography 
                        noWrap 
                        sx={{
                            fontSize: '14px',
                            fontWeight: 'bold',
                            color: '#141414',
                            lineHeight: 'normal'
                        }}
                    >
                        {item.filename}
                    </Typography>
                    <Typography 
                        sx={{ 
                            mt: 0.5, 
                            fontSize: '14px',
                            fontWeight: 'normal',
                            lineHeight: 'normal',
                            color: '#141414'
                        }}
                    >
                        {formatDate(item.uploaded_at)}
                    </Typography>
                    
                    {item.event_type && (
                        <Typography 
                            sx={{ 
                                mt: 1, 
                                fontSize: '12px',
                                fontWeight: 'medium',
                                color: '#6b6b6b',
                                backgroundColor: '#f5f5f5',
                                px: 1,
                                py: 0.5,
                                borderRadius: '4px',
                                display: 'inline-block',
                                width: 'fit-content'
                            }}
                        >
                            {item.event_type}
                            {item.event_confidence && ` (${(item.event_confidence * 100).toFixed(1)}%)`}
                        </Typography>
                    )}

                    {(item.latitude !== null && item.longitude !== null) && (
                        <Typography 
                            sx={{ 
                                mt: 1, 
                                fontSize: '12px',
                                fontWeight: 'medium',
                                color: '#6b6b6b',
                                backgroundColor: '#e8f4fd',
                                px: 1,
                                py: 0.5,
                                borderRadius: '4px',
                                display: 'inline-block',
                                width: 'fit-content'
                            }}
                        >
                            📍 {item.latitude.toFixed(6)}, {item.longitude.toFixed(6)}
                        </Typography>
                    )}

                    <Box sx={{ mt: 'auto', pt: 2, display: 'flex', gap: 1 }}>
                        {onSelect && (
                            <Button
                                size="small"
                                startIcon={<InfoIcon />}
                                onClick={() => onSelect(item)}
                                sx={{
                                    fontSize: '12px',
                                    textTransform: 'none',
                                    color: '#6b6b6b',
                                    '&:hover': {
                                        backgroundColor: '#f5f5f5',
                                    }
                                }}
                            >
                                Ver
                            </Button>
                        )}
                        {onDelete && (
                            <Button
                                size="small"
                                startIcon={<DeleteIcon />}
                                onClick={handleDelete}
                                sx={{
                                    fontSize: '12px',
                                    textTransform: 'none',
                                    color: '#d32f2f',
                                    '&:hover': {
                                        backgroundColor: '#ffebee',
                                    }
                                }}
                            >
                                Eliminar
                            </Button>
                        )}
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
    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
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
                <Typography sx={{ 
                    fontSize: '16px',
                    color: '#6b6b6b',
                    textAlign: 'center'
                }}>
                    No hay archivos para mostrar
                </Typography>
            </Box>
        );
    }

    return (
        <Grid container spacing={3} sx={{ p: 3 }}>
            {media.map((item) => (
                <MediaCard
                    key={item.id}
                    media={item}
                    onSelect={onMediaSelect}
                    onDelete={onMediaDelete}
                />
            ))}
        </Grid>
    );
};

export default MediaGrid;