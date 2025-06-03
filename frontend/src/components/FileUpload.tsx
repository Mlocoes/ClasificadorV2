import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Paper, Typography, Box, LinearProgress, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface FileUploadProps {
    onUpload: (files: File[]) => Promise<void>;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        // Limpiar error previo
        setError(null);

        try {
            // Validar que hay archivos
            if (!acceptedFiles?.length) {
                setError('No se han seleccionado archivos');
                return;
            }

            // Validar tipos de archivo
            const invalidFiles = acceptedFiles.filter(file => {
                const isImage = file.type.startsWith('image/');
                const isVideo = file.type.startsWith('video/');
                return !(isImage || isVideo);
            });

            if (invalidFiles.length > 0) {
                setError(`Archivos no soportados: ${invalidFiles.map(f => f.name).join(', ')}`);
                return;
            }

            setUploading(true);

            // Procesar los archivos
            await onUpload(acceptedFiles);
            
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Error al subir los archivos';
            setError(errorMessage);
            console.error('Error en la carga de archivos:', err);
        } finally {
            setUploading(false);
        }
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png', '.heic'],
            'video/*': ['.mp4', '.mov']
        },
        maxSize: 100 * 1024 * 1024, // 100MB
        multiple: true,
        disabled: uploading,
    });

    return (
        <>
            <Paper
                {...getRootProps()}
                sx={{
                    p: 3,
                    textAlign: 'center',
                    cursor: uploading ? 'not-allowed' : 'pointer',
                    backgroundColor: isDragActive ? '#f0f8ff' : '#fff',
                    border: '2px dashed #ccc',
                    '&:hover': {
                        backgroundColor: uploading ? '#fff' : '#f0f8ff',
                    },
                }}
            >
                <input {...getInputProps()} />
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <CloudUploadIcon sx={{ fontSize: 48, color: '#666', mb: 2 }} />
                    <Typography variant="h6" color="textSecondary">
                        {uploading
                            ? 'Subiendo archivos...'
                            : isDragActive
                            ? 'Suelta los archivos aquí'
                            : 'Arrastra fotos o videos aquí, o haz clic para seleccionar'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                        Formatos soportados: JPG, PNG, HEIC, MP4, MOV
                    </Typography>
                </Box>
                {uploading && (
                    <Box sx={{ width: '100%', mt: 2 }}>
                        <LinearProgress />
                    </Box>
                )}
            </Paper>
            {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                </Alert>
            )}
        </>
    );
};

export default FileUpload;
