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
    const formatDate = (dateString: string) => {
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
        <TableContainer component={Paper} sx={{ m: 3, borderRadius: '12px', border: '1px solid #dbdbdb' }}>
            <Table sx={{ minWidth: 650 }} aria-label="tabla de archivos multimedia">
                <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        <TableCell sx={{ fontWeight: 'bold', color: '#141414' }}>Vista previa</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', color: '#141414' }}>Nombre del archivo</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', color: '#141414' }}>Fecha de creación</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', color: '#141414' }}>Localización</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', color: '#141414' }}>Evento predicho</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', color: '#141414' }} align="right">Acciones</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {media.map((item) => (
                        <TableRow 
                            key={item.id}
                            sx={{ 
                                '&:last-child td, &:last-child th': { border: 0 },
                                '&:hover': { backgroundColor: '#f9f9f9' }
                            }}
                        >
                            <TableCell component="th" scope="row">
                                <Box
                                    component="img"
                                    src={`http://localhost:8000${item.thumbnail_path}`}
                                    alt={item.filename}
                                    sx={{
                                        width: 60,
                                        height: 60,
                                        objectFit: 'cover',
                                        borderRadius: '8px',
                                        cursor: 'pointer'
                                    }}
                                    onClick={() => onMediaSelect && onMediaSelect(item)}
                                />
                            </TableCell>
                            <TableCell>
                                <Typography sx={{ fontSize: '14px', fontWeight: 500 }}>
                                    {item.filename}
                                </Typography>
                            </TableCell>
                            <TableCell>
                                <Typography sx={{ fontSize: '14px', color: '#6b6b6b' }}>
                                    {formatDate(item.uploaded_at)}
                                </Typography>
                            </TableCell>
                            <TableCell>
                                {(item.latitude !== null && item.longitude !== null) ? (
                                    <Box
                                        sx={{
                                            backgroundColor: '#e8f4fd',
                                            color: '#6b6b6b',
                                            px: 1,
                                            py: 0.5,
                                            borderRadius: '4px',
                                            fontSize: '12px',
                                            fontWeight: 'medium',
                                            display: 'inline-block',
                                            maxWidth: '150px'
                                        }}
                                    >
                                        📍 {item.latitude.toFixed(4)}, {item.longitude.toFixed(4)}
                                    </Box>
                                ) : (
                                    <Typography sx={{ fontSize: '14px', color: '#9e9e9e' }}>
                                        Sin ubicación
                                    </Typography>
                                )}
                            </TableCell>
                            <TableCell>
                                {item.event_type ? (
                                    <Box
                                        sx={{
                                            backgroundColor: '#f5f5f5',
                                            color: '#6b6b6b',
                                            px: 1,
                                            py: 0.5,
                                            borderRadius: '4px',
                                            fontSize: '12px',
                                            fontWeight: 'medium',
                                            display: 'inline-block'
                                        }}
                                    >
                                        {item.event_type}
                                    </Box>
                                ) : (
                                    <Typography sx={{ fontSize: '14px', color: '#9e9e9e' }}>
                                        Sin clasificar
                                    </Typography>
                                )}
                            </TableCell>
                            <TableCell align="right">
                                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                                    {onMediaEdit && (
                                        <Button
                                            size="small"
                                            startIcon={<EditIcon />}
                                            onClick={() => onMediaEdit(item)}
                                            sx={{
                                                fontSize: '12px',
                                                textTransform: 'none',
                                                color: '#6b6b6b',
                                                minWidth: 'auto',
                                                '&:hover': {
                                                    backgroundColor: '#f5f5f5',
                                                }
                                            }}
                                        >
                                            Editar
                                        </Button>
                                    )}
                                    <Button
                                        size="small"
                                        startIcon={<DeleteIcon />}
                                        onClick={() => handleDelete(item.id)}
                                        sx={{
                                            fontSize: '12px',
                                            textTransform: 'none',
                                            color: '#d32f2f',
                                            minWidth: 'auto',
                                            '&:hover': {
                                                backgroundColor: '#ffebee',
                                            }
                                        }}
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
