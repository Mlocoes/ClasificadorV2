import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Paper, Typography, Box } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface FileUploadProps {
    onUpload: (files: File[]) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        onUpload(acceptedFiles);
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png', '.heic'],
            'video/*': ['.mp4', '.mov'],
        },
    });

    return (
        <Paper
            {...getRootProps()}
            sx={{
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: isDragActive ? '#f0f8ff' : '#fff',
                border: '2px dashed #ccc',
                '&:hover': {
                    backgroundColor: '#f0f8ff',
                },
            }}
        >
            <input {...getInputProps()} />
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <CloudUploadIcon sx={{ fontSize: 48, color: '#666', mb: 2 }} />
                <Typography variant="h6" color="textSecondary">
                    {isDragActive
                        ? 'Suelta los archivos aquí'
                        : 'Arrastra fotos o videos aquí, o haz clic para seleccionar'}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Formatos soportados: JPG, PNG, HEIC, MP4, MOV
                </Typography>
            </Box>
        </Paper>
    );
};

export default FileUpload;
