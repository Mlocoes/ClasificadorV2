import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, CircularProgress, Button } from '@mui/material';

interface UploadAreaProps {
    onUpload: (files: File[]) => Promise<void>;
    isLoading: boolean;
}

export const UploadArea: React.FC<UploadAreaProps> = ({ onUpload, isLoading }) => {
    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            onUpload(acceptedFiles);
        },
        [onUpload]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif'],
            'video/*': ['.mp4', '.mov', '.avi', '.mkv'],
        },
    });

    return (
        <Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: '12px', p: 2 }}>
                <Typography sx={{ 
                    color: '#141414', 
                    fontSize: '24px',
                    fontWeight: 'bold', 
                    lineHeight: 'tight',
                    minWidth: '240px'
                }}>
                    Arrastra y suelta archivos aquí
                </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', p: 4 }}>
                <Box
                    {...getRootProps()}
                    sx={{
                        display: 'flex', 
                        flexDirection: 'column', 
                        alignItems: 'center', 
                        gap: '16px',
                        borderRadius: '12px',
                        border: '2px dashed #dbdbdb',
                        px: 6,
                        py: '30px',
                        cursor: 'pointer',
                        backgroundColor: isDragActive ? '#f0f8ff' : 'transparent',
                        '&:hover': {
                            backgroundColor: '#f5f5f5'
                        }
                    }}
                >
                    <input {...getInputProps()} />
                    {isLoading ? (
                        <CircularProgress />
                    ) : (
                        <>
                            <Box sx={{ 
                                display: 'flex', 
                                maxWidth: '480px', 
                                flexDirection: 'column', 
                                alignItems: 'center',
                                gap: 2
                            }}>
                                <Typography sx={{ 
                                    color: '#141414',
                                    fontSize: '18px',
                                    fontWeight: 'bold',
                                    lineHeight: 'tight',
                                    letterSpacing: '-0.015em',
                                    maxWidth: '480px',
                                    textAlign: 'center'
                                }}>
                                    {isDragActive
                                        ? 'Suelta los archivos aquí...'
                                        : 'Arrastra y suelta fotos aquí'}
                                </Typography>
                                <Typography sx={{ 
                                    color: '#141414',
                                    fontSize: '14px',
                                    fontWeight: 'normal',
                                    lineHeight: 'normal',
                                    maxWidth: '480px',
                                    textAlign: 'center'
                                }}>
                                    O selecciona desde tu computadora
                                </Typography>
                            </Box>
                            <Button
                                variant="contained"
                                disableElevation
                                sx={{
                                    minWidth: '84px',
                                    maxWidth: '480px',
                                    height: '40px',
                                    px: 4,
                                    backgroundColor: '#ededed',
                                    color: '#141414',
                                    borderRadius: '50px',
                                    fontSize: '14px',
                                    fontWeight: 'medium',
                                    textTransform: 'none',
                                    '&:hover': {
                                        backgroundColor: '#dbdbdb',
                                    }
                                }}
                            >
                                Seleccionar Archivos
                            </Button>
                        </>
                    )}
                </Box>
            </Box>
        </Box>
    );
};

export default UploadArea;
