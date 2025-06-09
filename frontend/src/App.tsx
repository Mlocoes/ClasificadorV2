import { useState, useEffect } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import GridViewIcon from '@mui/icons-material/GridView';
import TableRowsIcon from '@mui/icons-material/TableRows';
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Importar componentes
import { Header, UploadArea, MediaGrid, MediaTable } from './components';
import mediaService from './services/mediaService';
import type { Media, MediaUpdate } from './services/mediaService';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: 'always', // Recargar siempre al volver a la ventana
            retry: 1,
            staleTime: 0, // Los datos se consideran obsoletos inmediatamente
            gcTime: 5 * 60 * 1000, // Garbage collection después de 5 minutos
            refetchOnMount: 'always', // Recargar siempre al montar el componente
            refetchOnReconnect: 'always', // Recargar siempre al reconectar
        },
    },
});

// Tema personalizado Material-UI
const theme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#141414',
        },
        secondary: {
            main: '#6b6b6b',
        },
        background: {
            default: '#fafafa',
            paper: '#ffffff',
        },
        text: {
            primary: '#141414',
            secondary: '#6b6b6b',
        },
        divider: '#dbdbdb',
        action: {
            hover: '#f5f5f5',
            selected: '#ededed'
        }
    },
    typography: {
        fontFamily: '"Plus Jakarta Sans", "Noto Sans", sans-serif',
        h6: {
            fontSize: '18px',
            fontWeight: 'bold',
            letterSpacing: '-0.015em',
        },
        body1: {
            fontSize: '14px',
            lineHeight: 'normal',
        },
        body2: {
            fontSize: '14px',
            lineHeight: 'normal',
            color: '#6b6b6b',
        },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    borderRadius: '50px',
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    borderRadius: '12px',
                },
            },
        },
    },
});

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <AppContent />
                <ReactQueryDevtools />
            </ThemeProvider>
        </QueryClientProvider>
    );
}

function AppContent() {
    const queryClient = useQueryClient();
    const [isUploading, setIsUploading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [notification, setNotification] = useState<{
        message: string;
        type: 'success' | 'error';
        open: boolean;
    }>({ message: '', type: 'success', open: false });

    const { 
        data: mediaList = [], 
        isLoading,
        refetch,
        isRefetching,
        dataUpdatedAt
    } = useQuery<Media[]>({
        queryKey: ['mediaList'],
        queryFn: () => mediaService.getAllMedia(),
        staleTime: 0,
        refetchOnMount: 'always',
        refetchOnWindowFocus: 'always',
        refetchIntervalInBackground: false,
        retry: 1
    });
    
    // Actualizar la marca de tiempo cuando cambian los datos
    useEffect(() => {
        setLastUpdate(new Date());
    }, [dataUpdatedAt]);

    const showNotification = (message: string, type: 'success' | 'error') => {
        setNotification({ message, type, open: true });
    };

    const handleUpload = async (files: File[]) => {
        setIsUploading(true);
        try {
            // Subir archivos uno por uno y manejar errores individualmente
            for (const file of files) {
                try {
                    await mediaService.uploadFile(file);
                } catch (error) {
                    console.error(`Error uploading file ${file.name}:`, error);
                    showNotification(`Error al subir el archivo ${file.name}`, 'error');
                }
            }
            
            // Recargar la lista después de subir todos los archivos
            queryClient.removeQueries({ queryKey: ['mediaList'] });
            await refetch();
            
            showNotification('Archivos procesados exitosamente', 'success');
        } catch (error) {
            console.error('Error general en la subida:', error);
            showNotification('Error al procesar los archivos', 'error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleMediaDelete = async (id: number) => {
        if (!window.confirm('¿Estás seguro de que quieres eliminar este archivo?')) {
            return;
        }

        try {
            await mediaService.deleteMedia(id);
            queryClient.removeQueries({ queryKey: ['mediaList'] });
            await refetch();
            showNotification('Archivo eliminado exitosamente', 'success');
        } catch (error) {
            console.error('Error al eliminar archivo:', error);
            showNotification('Error al eliminar el archivo', 'error');
            await refetch();
        }
    };
    
    const handleMediaEdit = async (media: Media) => {
        try {
            const updateData: MediaUpdate = {
                event_type: media.event_type ?? null,
                latitude: media.latitude ?? null,
                longitude: media.longitude ?? null
            };
            
            await mediaService.updateMedia(media.id, updateData);
            queryClient.removeQueries({ queryKey: ['mediaList'] });
            await refetch();
            showNotification('Archivo actualizado exitosamente', 'success');
        } catch (error) {
            console.error('Error al actualizar archivo:', error);
            showNotification('Error al actualizar el archivo', 'error');
            await refetch();
        }
    };

    const handleSearch = (query: string) => {
        setSearchQuery(query);
    };

    // Filtrar medios basado en la búsqueda
    const filteredMedia = (mediaList as Media[]).filter(media => 
        !searchQuery || 
        media.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (media.event_type && media.event_type.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    // Mostrar estado de carga inicial
    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
            {/* Header */}
            <Header 
                onSearch={handleSearch}
                searchValue={searchQuery}
            />

            {/* Main Content */}
            <Box sx={{ p: 3 }}>
                {/* Upload Area */}
                <UploadArea 
                    onUpload={handleUpload}
                    isLoading={isUploading}
                />

                {/* View Mode Toggle and Last Update */}
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    my: 3 
                }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mr: 1 }}>
                            Última actualización: {lastUpdate.toLocaleTimeString()}
                        </Typography>
                        <Button 
                            size="small" 
                            onClick={() => refetch()} 
                            disabled={isRefetching}
                            sx={{ minWidth: 'auto', p: 0.5, ml: 1 }}
                        >
                            {isRefetching ? (
                                <CircularProgress size={16} />
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                    <path fillRule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                                    <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                                </svg>
                            )}
                        </Button>
                    </Box>
                    <ToggleButtonGroup
                        value={viewMode}
                        exclusive
                        onChange={(_, newViewMode) => {
                            if (newViewMode !== null) {
                                setViewMode(newViewMode);
                                // Recargar datos al cambiar el modo de vista
                                refetch();
                            }
                        }}
                        size="small"
                        sx={{
                            bgcolor: 'background.paper',
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: '50px',
                            '& .MuiToggleButton-root': {
                                border: 'none',
                                borderRadius: '50px',
                                px: 3,
                                py: 1,
                                '&.Mui-selected': {
                                    bgcolor: 'primary.main',
                                    color: 'white',
                                    '&:hover': {
                                        bgcolor: 'primary.dark',
                                    }
                                }
                            }
                        }}
                    >
                        <ToggleButton value="list" aria-label="vista de lista">
                            <TableRowsIcon sx={{ mr: 1, fontSize: 18 }} />
                            Lista
                        </ToggleButton>
                        <ToggleButton value="grid" aria-label="vista de cuadrícula">
                            <GridViewIcon sx={{ mr: 1, fontSize: 18 }} />
                            Cuadrícula
                        </ToggleButton>
                    </ToggleButtonGroup>
                </Box>

                {/* Media Content */}
                {isRefetching && (
                    <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        alignItems: 'center',
                        position: 'fixed',
                        bottom: '20px',
                        right: '20px',
                        zIndex: 1000,
                        bgcolor: 'background.paper',
                        boxShadow: 3,
                        borderRadius: '50%',
                        p: 1
                    }}>
                        <CircularProgress size={24} />
                    </Box>
                )}
                
                {viewMode === 'grid' ? (
                    <MediaGrid
                        media={filteredMedia}
                        onMediaDelete={handleMediaDelete}
                        isLoading={isRefetching}
                    />
                ) : (
                    <MediaTable
                        media={filteredMedia}
                        onMediaDelete={handleMediaDelete}
                        onMediaEdit={handleMediaEdit}
                        isLoading={isRefetching}
                    />
                )}
            </Box>

            {/* Notification Snackbar */}
            <Snackbar
                open={notification.open}
                autoHideDuration={6000}
                onClose={() => setNotification({ ...notification, open: false })}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert 
                    severity={notification.type} 
                    onClose={() => setNotification({ ...notification, open: false })}
                    sx={{ borderRadius: '12px' }}
                >
                    {notification.message}
                </Alert>
            </Snackbar>
        </Box>
    );
}

export default App;
