import React, { useState, useEffect } from 'react';
import {
    Grid,
    Card,
    CardContent,
    CardMedia,
    Typography,
    IconButton,
    Box,
    CircularProgress
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { Media } from '../types/media';
import { format } from 'date-fns';
import { getLocationNameFromCoords } from '../services/locationService';

interface MediaGridProps {
    media: Media[];
    onDelete: (id: number) => void;
    onEdit: (media: Media) => void;
}

const MediaGrid: React.FC<MediaGridProps> = ({ media, onDelete, onEdit }) => {
    const [locationNames, setLocationNames] = useState<{[key: number]: string}>({});
    const [loadingLocations, setLoadingLocations] = useState<{[key: number]: boolean}>({});

    useEffect(() => {
        const loadLocationNames = async () => {
            const locationPromises = media
                .filter(item => item.latitude && item.longitude)
                .map(async (item) => {
                    try {
                        setLoadingLocations(prev => ({ ...prev, [item.id]: true }));
                        const locationName = await getLocationNameFromCoords(
                            item.latitude!,
                            item.longitude!
                        );
                        return { id: item.id, name: locationName };
                    } catch (error) {
                        console.error(`Error cargando ubicación para ID ${item.id}:`, error);
                        return { id: item.id, name: 'Error al cargar ubicación' };
                    } finally {
                        setLoadingLocations(prev => ({ ...prev, [item.id]: false }));
                    }
                });
            
            const results = await Promise.allSettled(locationPromises);
            const newLocationNames = results.reduce((acc, result) => {
                if (result.status === 'fulfilled') {
                    acc[result.value.id] = result.value.name;
                }
                return acc;
            }, {} as {[key: number]: string});
            
            setLocationNames(prev => ({ ...prev, ...newLocationNames }));
        };
        
        if (media.length > 0) {
            loadLocationNames();
        }
    }, [media]);

    const formatDate = (dateString: string) => {
        return format(new Date(dateString), 'dd/MM/yyyy HH:mm');
    };

    return (
        <Grid container spacing={3}>
            {media.map((item) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
                    <Card>
                        {item.thumbnail_path && (
                            <CardMedia
                                component="img"
                                height="200"
                                image={`http://localhost:8000${item.thumbnail_path.replace('../storage', '')}`}
                                alt={item.filename}
                                sx={{ objectFit: 'cover' }}
                            />
                        )}
                        <CardContent>
                            <Typography variant="subtitle1" noWrap>
                                {item.filename}
                            </Typography>
                            
                            <Box sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1, 
                                mt: 1, 
                                mb: 1 
                            }}>
                                <LocationOnIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                                {item.latitude && item.longitude ? (
                                    loadingLocations[item.id] ? (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <CircularProgress size={16} />
                                            <Typography variant="body2" color="text.secondary">
                                                Cargando ubicación...
                                            </Typography>
                                        </Box>
                                    ) : (
                                        <Typography variant="body2" color="text.secondary" noWrap>
                                            {locationNames[item.id] || `${item.latitude.toFixed(4)}, ${item.longitude.toFixed(4)}`}
                                        </Typography>
                                    )
                                ) : (
                                    <Typography variant="body2" color="text.secondary">
                                        No disponible
                                    </Typography>
                                )}
                            </Box>
                            
                            <Typography variant="body2" color="text.secondary">
                                {item.mime_type}
                            </Typography>
                            
                            {item.event_type && (
                                <Typography variant="body2" color="text.secondary">
                                    Evento: {item.event_type}
                                    {item.event_confidence && ` (${(item.event_confidence * 100).toFixed(1)}%)`}
                                </Typography>
                            )}
                            
                            <Typography variant="body2" color="text.secondary">
                                Fecha: {formatDate(item.uploaded_at)}
                            </Typography>
                            
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                                <IconButton size="small" onClick={() => onEdit(item)}>
                                    <EditIcon />
                                </IconButton>
                                <IconButton size="small" onClick={() => onDelete(item.id)}>
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};

export default MediaGrid;