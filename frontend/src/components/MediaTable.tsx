import React, { useState } from 'react';
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
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import type { Media, MediaUpdate } from '../services/mediaService';
import { format } from 'date-fns';

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
                            <TableCell>Tipo</TableCell>
                            <TableCell>Evento</TableCell>
                            <TableCell>Fecha</TableCell>
                            <TableCell>Acciones</TableCell>
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
                                <TableCell>{item.mime_type}</TableCell>
                                <TableCell>
                                    {item.event_type}
                                    {item.event_confidence && ` (${(item.event_confidence * 100).toFixed(1)}%)`}
                                </TableCell>
                                <TableCell>{formatDate(item.uploaded_at)}</TableCell>
                                <TableCell>
                                    <IconButton onClick={() => handleEdit(item)}>
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton onClick={() => onDelete(item.id)}>
                                        <DeleteIcon />
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
