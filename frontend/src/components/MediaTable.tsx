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
    CircularProgress,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    MenuItem
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

interface EditDialogProps {
    open: boolean;
    media: Media;
    onClose: () => void;
    onSave: (media: Media) => void;
}

const EditDialog: React.FC<EditDialogProps> = ({ open, media, onClose, onSave }) => {
    const [editedMedia, setEditedMedia] = React.useState<Media>(media);
    const [errors, setErrors] = React.useState<{
        latitude?: string;
        longitude?: string;
    }>({});
    
    const eventTypes = [
        'wedding', 'conference', 'sports', 'concert', 'party', 
        'reunion', 'travel', 'birthday', 'graduation', 'family'
    ];

    const validateCoordinates = () => {
        const newErrors: {latitude?: string; longitude?: string} = {};            const lat = editedMedia.latitude;
            const lon = editedMedia.longitude;

            if (lat !== undefined && lat !== null && (lat < -90 || lat > 90)) {
                newErrors.latitude = 'La latitud debe estar entre -90 y 90';
            }
            
            if (lon !== undefined && lon !== null && (lon < -180 || lon > 180)) {
                newErrors.longitude = 'La longitud debe estar entre -180 y 180';
            }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSave = () => {
        if (validateCoordinates()) {
            onSave(editedMedia);
            onClose();
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Editar Archivo</DialogTitle>
            <DialogContent>
                <Box sx={{ mt: 2 }}>
                    <TextField
                        select
                        fullWidth
                        label="Tipo de Evento"
                        value={editedMedia.event_type || ''}
                        onChange={(e) => setEditedMedia({
                            ...editedMedia,
                            event_type: e.target.value
                        })}
                        sx={{ mb: 2 }}
                    >
                        {eventTypes.map((type) => (
                            <MenuItem key={type} value={type}>
                                {translateEventType(type)}
                            </MenuItem>
                        ))}
                    </TextField>

                    <TextField
                        fullWidth
                        label="Latitud"
                        type="number"
                        value={editedMedia.latitude || ''}
                        onChange={(e) => {
                            const value = e.target.value === '' ? null : parseFloat(e.target.value);
                            setEditedMedia({
                                ...editedMedia,
                                latitude: value
                            });
                            setErrors({...errors, latitude: undefined});
                        }}
                        error={Boolean(errors.latitude)}
                        helperText={errors.latitude}
                        sx={{ mb: 2 }}
                        InputProps={{
                            inputProps: { 
                                min: -90, 
                                max: 90,
                                step: "any"
                            }
                        }}
                    />

                    <TextField
                        fullWidth
                        label="Longitud"
                        type="number"
                        value={editedMedia.longitude || ''}
                        onChange={(e) => {
                            const value = e.target.value === '' ? null : parseFloat(e.target.value);
                            setEditedMedia({
                                ...editedMedia,
                                longitude: value
                            });
                            setErrors({...errors, longitude: undefined});
                        }}
                        error={Boolean(errors.longitude)}
                        helperText={errors.longitude}
                        InputProps={{
                            inputProps: { 
                                min: -180, 
                                max: 180,
                                step: "any"
                            }
                        }}
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="inherit">
                    Cancelar
                </Button>
                <Button 
                    onClick={handleSave} 
                    color="primary" 
                    variant="contained"
                    disabled={Object.keys(errors).length > 0}
                >
                    Guardar
                </Button>
            </DialogActions>
        </Dialog>
    );
}

const MediaTable: React.FC<MediaTableProps> = ({
    media,
    onMediaSelect,
    onMediaDelete,
    onMediaEdit,
    isLoading
}) => {
    const [editingMedia, setEditingMedia] = React.useState<Media | null>(null);

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
        await onMediaDelete(id);
    };

    const handleEditClick = (item: Media) => {
        setEditingMedia(item);
    };

    const handleEditSave = (editedMedia: Media) => {
        if (onMediaEdit) {
            onMediaEdit(editedMedia);
        }
        setEditingMedia(null);
    };

    if (isLoading && media.length === 0) {
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
        <>
            <TableContainer component={Paper}>
                {isLoading && media.length > 0 && (
                    <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        p: 1,
                        position: 'relative'
                    }}>
                        <Box sx={{ 
                            display: 'flex',
                            alignItems: 'center',
                            bgcolor: 'background.paper', 
                            boxShadow: 1, 
                            borderRadius: 1,
                            px: 2,
                            py: 0.5
                        }}>
                            <CircularProgress size={20} sx={{ mr: 1 }} />
                            <Typography variant="body2">Actualizando...</Typography>
                        </Box>
                    </Box>
                )}
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
                                                onClick={() => handleEditClick(item)}
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
            {editingMedia && (
                <EditDialog 
                    open={Boolean(editingMedia)} 
                    media={editingMedia} 
                    onClose={() => setEditingMedia(null)} 
                    onSave={handleEditSave}
                />
            )}
        </>
    );
};

export default MediaTable;
