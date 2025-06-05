import React, { useState, useEffect } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    Typography,
    CircularProgress
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { format } from 'date-fns';
import type { Media, MediaUpdate } from '../services/mediaService';
import { getLocationNameFromCoords } from '../services/locationService';

interface MediaTableProps {
    media: Media[];
    onDelete: (id: number) => void;
    onUpdate: (id: number, data: MediaUpdate) => void;
}

const MediaTable: React.FC<MediaTableProps> = ({ media, onDelete, onUpdate }) => {
    const [editDialog, setEditDialog] = useState<{ open: boolean; media: Media | null }>({
        open: false,
        media: null,
    });
    const [editForm, setEditForm] = useState<MediaUpdate>({});
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

    const handleEdit = (item: Media) => {
        setEditDialog({ open: true, media: item });
        setEditForm({
            event_type: item.event_type || '',
            latitude: item.latitude || undefined,
            longitude: item.longitude || undefined,
        });
    };

    const handleSave = () => {
        if (editDialog.media) {
            onUpdate(editDialog.media.id, editForm);
            setEditDialog({ open: false, media: null });
        }
    };

    const formatDate = (dateString: string) => {
        return format(new Date(dateString), 'dd/MM/yyyy HH:mm');
    };

    return (
        <>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Miniatura</TableCell>
                            <TableCell>Nombre</TableCell>
                            <TableCell>Fecha</TableCell>
                            <TableCell>Ubicación</TableCell>
                            <TableCell>Evento</TableCell>
                            <TableCell>Eliminar</TableCell>
                            <TableCell>Actualizar</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {media.map((item) => (
                            <TableRow key={item.id}>
                                <TableCell>
                                    {item.thumbnail_path && (
                                        <img
                                            src={`http://localhost:8000${item.thumbnail_path.replace('../storage', '')}`}
                                            alt={item.filename}
                                            style={{ width: 100, height: 100, objectFit: 'cover' }}
                                        />
                                    )}
                                </TableCell>
                                <TableCell>{item.filename}</TableCell>
                                <TableCell>{formatDate(item.uploaded_at)}</TableCell>
                                <TableCell>
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <LocationOnIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                        {item.latitude && item.longitude ? (
                                            loadingLocations[item.id] ? (
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <CircularProgress size={16} />
                                                    <Typography variant="body2" color="text.secondary">
                                                        Cargando ubicación...
                                                    </Typography>
                                                </Box>
                                            ) : (
                                                <Typography variant="body2" color="text.secondary">
                                                    {locationNames[item.id] || `${item.latitude.toFixed(4)}, ${item.longitude.toFixed(4)}`}
                                                </Typography>
                                            )
                                        ) : (
                                            <Typography variant="body2" color="text.secondary">
                                                No disponible
                                            </Typography>
                                        )}
                                    </Box>
                                </TableCell>
                                <TableCell>
                                    {item.event_type}
                                    {item.event_confidence && ` (${(item.event_confidence * 100).toFixed(1)}%)`}
                                </TableCell>
                                <TableCell>
                                    <IconButton onClick={() => onDelete(item.id)}>
                                        <DeleteIcon />
                                    </IconButton>
                                </TableCell>
                                <TableCell>
                                    <IconButton onClick={() => handleEdit(item)}>
                                        <EditIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog open={editDialog.open} onClose={() => setEditDialog({ open: false, media: null })}>
                <DialogTitle>Editar medio</DialogTitle>
                <DialogContent>
                    <TextField
                        margin="dense"
                        label="Tipo de evento"
                        fullWidth
                        value={editForm.event_type || ''}
                        onChange={(e) => setEditForm({ ...editForm, event_type: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Latitud"
                        type="number"
                        fullWidth
                        value={editForm.latitude || ''}
                        onChange={(e) => setEditForm({ ...editForm, latitude: parseFloat(e.target.value) })}
                    />
                    <TextField
                        margin="dense"
                        label="Longitud"
                        type="number"
                        fullWidth
                        value={editForm.longitude || ''}
                        onChange={(e) => setEditForm({ ...editForm, longitude: parseFloat(e.target.value) })}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setEditDialog({ open: false, media: null })}>Cancelar</Button>
                    <Button onClick={handleSave} variant="contained">
                        Guardar
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default MediaTable;
