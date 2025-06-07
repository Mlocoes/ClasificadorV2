import React from 'react';
import { 
    Table, 
    TableBody, 
    TableCell, 
    TableContainer, 
    TableHead, 
    TableRow, 
    Paper, 
    Button,
    Box,
    Typography,
    CircularProgress
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import type { Media } from '../services/mediaService';
import { getMediaUrl } from '../services/mediaService';
import { getLocationNameFromCoords } from '../services/locationService';
import { translateEventType } from '../services/translationService';
import { LoadingSkeleton } from './LoadingSkeleton';

const LocationDisplay: React.FC<{ latitude: number | null; longitude: number | null }> = ({ latitude, longitude }) => {
    const [locationName, setLocationName] = React.useState<string>('');
    const [isLoading, setIsLoading] = React.useState(false);

    React.useEffect(() => {
        const loadLocation = async () => {
            if (latitude !== null && longitude !== null) {
                setIsLoading(true);
                try {
                    const name = await getLocationNameFromCoords(latitude, longitude);
                    setLocationName(name);
                } catch (error) {
                    console.error('Error cargando ubicación:', error);
                    setLocationName(latitude && longitude ? `${latitude.toFixed(4)}, ${longitude.toFixed(4)}` : 'Sin ubicación');
                } finally {
                    setIsLoading(false);
                }
            } else {
                setLocationName('Sin ubicación');
            }
        };

        loadLocation();
    }, [latitude, longitude]);

    if (isLoading) {
        return <CircularProgress size={20} />;
    }

    return <span>{locationName}</span>;
};

interface MediaTableProps {
    media: Media[];
    onMediaSelect?: (media: Media) => void;
    onMediaDelete: (id: number) => Promise<void>;
    onMediaEdit?: (media: Media) => void;
    isLoading?: boolean;
}

const MediaTable: React.FC<MediaTableProps> = ({
    media,
    onMediaSelect,
    onMediaDelete,
    onMediaEdit,
    isLoading
}) => {
    const formatDate = (dateString: string | null | undefined) => {
        if (!dateString) return 'Fecha desconocida';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return 'Fecha desconocida';
        }
    };

    const handleDelete = async (id: number) => {
        if (window.confirm('¿Estás seguro de que quieres eliminar este archivo?')) {
            await onMediaDelete(id);
        }
    };

    if (isLoading) {
        return <LoadingSkeleton count={5} variant="table" />;
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
                <Typography variant="body1" color="textSecondary">
                    No hay archivos para mostrar
                </Typography>
            </Box>
        );
    }

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Vista previa</TableCell>
                        <TableCell>Nombre</TableCell>
                        <TableCell>Fecha</TableCell>
                        <TableCell>Ubicación</TableCell>
                        <TableCell>Tipo de Evento</TableCell>
                        <TableCell>Acciones</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {media.map((item) => (
                        <TableRow key={item.id}>
                            <TableCell>
                                <img 
                                    src={getMediaUrl(item.thumbnail_path) || getMediaUrl(item.file_path)} 
                                    alt={item.filename}
                                    style={{ width: '100px', height: '100px', objectFit: 'cover', cursor: 'pointer' }}
                                    onClick={() => onMediaSelect?.(item)}
                                />
                            </TableCell>
                            <TableCell>{item.filename}</TableCell>
                            <TableCell>{formatDate(item.creation_date || item.uploaded_at || item.created_at)}</TableCell>
                            <TableCell>
                                <LocationDisplay 
                                    latitude={item.latitude || null} 
                                    longitude={item.longitude || null}
                                />
                            </TableCell>
                            <TableCell>{translateEventType(item.event_type)}</TableCell>
                            <TableCell>
                                <Box display="flex" gap={1}>
                                    {onMediaEdit && (
                                        <Button 
                                            startIcon={<EditIcon />}
                                            onClick={() => onMediaEdit(item)}
                                            size="small"
                                        >
                                            Editar
                                        </Button>
                                    )}
                                    <Button
                                        startIcon={<DeleteIcon />}
                                        onClick={() => handleDelete(item.id)}
                                        color="error"
                                        size="small"
                                    >
                                        Eliminar
                                    </Button>
                                </Box>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default MediaTable;
