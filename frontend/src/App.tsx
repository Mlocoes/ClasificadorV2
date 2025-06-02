import { useState, useEffect } from 'react';
import { Container, Typography, Box, Alert, Snackbar } from '@mui/material';
import FileUpload from './components/FileUpload';
import MediaTable from './components/MediaTable';
import mediaService from './services/mediaService';
import type { Media, MediaUpdate } from './services/mediaService';
import './App.css';

function App() {
    const [media, setMedia] = useState<Media[]>([]);
    const [alert, setAlert] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
        open: false,
        message: '',
        severity: 'success',
    });

    const loadMedia = async () => {
        try {
            const data = await mediaService.getAllMedia();
            setMedia(data);
        } catch (error) {
            showAlert('Error al cargar los medios', 'error');
        }
    };

    useEffect(() => {
        loadMedia();
    }, []);

    const showAlert = (message: string, severity: 'success' | 'error') => {
        setAlert({ open: true, message, severity });
    };

    const handleUpload = async (files: File[]) => {
        try {
            for (const file of files) {
                await mediaService.uploadFile(file);
            }
            showAlert('Archivos subidos correctamente', 'success');
            loadMedia();
        } catch (error) {
            showAlert('Error al subir los archivos', 'error');
        }
    };

    const handleDelete = async (id: number) => {
        try {
            await mediaService.deleteMedia(id);
            showAlert('Archivo eliminado correctamente', 'success');
            loadMedia();
        } catch (error) {
            showAlert('Error al eliminar el archivo', 'error');
        }
    };

    const handleUpdate = async (id: number, data: MediaUpdate) => {
        try {
            await mediaService.updateMedia(id, data);
            showAlert('Archivo actualizado correctamente', 'success');
            loadMedia();
        } catch (error) {
            showAlert('Error al actualizar el archivo', 'error');
        }
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Organizador de Medios
            </Typography>

            <Box sx={{ mb: 4 }}>
                <FileUpload onUpload={handleUpload} />
            </Box>

            <MediaTable media={media} onDelete={handleDelete} onUpdate={handleUpdate} />

            <Snackbar
                open={alert.open}
                autoHideDuration={6000}
                onClose={() => setAlert({ ...alert, open: false })}
            >
                <Alert severity={alert.severity} onClose={() => setAlert({ ...alert, open: false })}>
                    {alert.message}
                </Alert>
            </Snackbar>
        </Container>
    );
}

export default App;
