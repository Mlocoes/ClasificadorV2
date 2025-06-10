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
    MenuItem,
    Autocomplete,
    InputAdornment
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import type { Media } from '../services/mediaService';
import { getMediaUrl } from '../services';
import { getLocationNameFromCoords } from '../services/locationService';
import { translateEventType } from '../services/translationService';
import { searchPlaces } from '../services/geocodingService';
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
    const [locationQuery, setLocationQuery] = React.useState('');
    const [locationOptions, setLocationOptions] = React.useState<{
        id: string;
        name: string;
        displayName: string;
        latitude: number;
        longitude: number;
    }[]>([]);
    const [isLoadingLocations, setIsLoadingLocations] = React.useState(false);
    
    const eventTypes = [
        'wedding', 'conference', 'sports', 'concert', 'party', 
        'reunion', 'travel', 'birthday', 'graduation', 'family'
    ];

    // Buscar lugares cuando cambia el texto de búsqueda
    React.useEffect(() => {
        const fetchPlaces = async () => {
            if (locationQuery.length >= 3) {
                setIsLoadingLocations(true);
                try {
                    const places = await searchPlaces(locationQuery);
                    setLocationOptions(places);
                } catch (error) {
                    console.error("Error buscando lugares:", error);
                    setLocationOptions([]);
                } finally {
                    setIsLoadingLocations(false);
                }
            } else {
                setLocationOptions([]);
            }
        };

        const debounceTimer = setTimeout(() => {
            fetchPlaces();
        }, 500);

        return () => clearTimeout(debounceTimer);
    }, [locationQuery]);

    const validateCoordinates = () => {
        const newErrors: {latitude?: string; longitude?: string} = {};            
        const lat = editedMedia.latitude;
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

    // Limpiar las coordenadas
    const handleClearCoordinates = () => {
        setEditedMedia({
            ...editedMedia,
            latitude: null,
            longitude: null
        });
        setLocationQuery('');
        setErrors({});
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

                    {/* Campo de búsqueda de ubicaciones */}
                    <Autocomplete
                        fullWidth
                        options={locationOptions}
                        loading={isLoadingLocations}
                        getOptionLabel={(option) => option.displayName || ''}
                        filterOptions={(x) => x} // No filtramos, ya que la API ya nos da los resultados filtrados
                        onInputChange={(_, value) => setLocationQuery(value)}
                        onChange={(_, option) => {
                            if (option) {
                                setEditedMedia({
                                    ...editedMedia,
                                    latitude: option.latitude,
                                    longitude: option.longitude
                                });
                                setErrors({});
                            }
                        }}
                        noOptionsText="Sin resultados"
                        loadingText="Buscando..."
                        renderInput={(params) => (
                            <TextField 
                                {...params} 
                                label="Buscar ubicación por nombre"
                                placeholder="Ej: Madrid, España"
                                helperText="Escribe nombre de ciudad, país o ubicación"
                                sx={{ mb: 3 }}
                                InputProps={{
                                    ...params.InputProps,
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            <LocationOnIcon color="action" />
                                        </InputAdornment>
                                    ),
                                    endAdornment: (
                                        <>
                                            {isLoadingLocations ? <CircularProgress color="inherit" size={20} /> : null}
                                            {params.InputProps.endAdornment}
                                        </>
                                    ),
                                }}
                            />
                        )}
                        renderOption={(props, option) => (
                            <Box component="li" {...props}>
                                <LocationOnIcon sx={{ mr: 1 }} />
                                <Typography variant="body2" noWrap>
                                    {option.displayName}
                                </Typography>
                            </Box>
                        )}
                    />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="textSecondary">
                            Coordenadas GPS
                        </Typography>
                        <Button 
                            size="small" 
                            onClick={handleClearCoordinates}
                            variant="text"
                            sx={{ minWidth: 'auto', fontSize: '0.75rem' }}
                        >
                            Limpiar coordenadas
                        </Button>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
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
    const [searchQuery, setSearchQuery] = React.useState<string>('');
    const [filteredMedia, setFilteredMedia] = React.useState<Media[]>(media);

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

    const handleSearch = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        setSearchQuery(value);

        if (value.trim() === '') {
            setFilteredMedia(media);
            return;
        }

        // Filtrar los medios basados en la búsqueda de texto
        const filtered = media.filter(item => 
            item.filename.toLowerCase().includes(value.toLowerCase()) ||
            (item.event_type && item.event_type.toLowerCase().includes(value.toLowerCase()))
        );
        setFilteredMedia(filtered);
    };

    React.useEffect(() => {
        setFilteredMedia(media);
    }, [media]);

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
            <TextField
                fullWidth
                label="Buscar ubicación"
                value={searchQuery}
                onChange={handleSearch}
                sx={{ mb: 2 }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <SearchIcon />
                        </InputAdornment>
                    ),
                }}
            />
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
                        {filteredMedia.map((item) => (
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
