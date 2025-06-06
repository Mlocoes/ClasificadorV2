import { useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import GridViewIcon from '@mui/icons-material/GridView';
import TableRowsIcon from '@mui/icons-material/TableRows';
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Importar componentes
import { Header, UploadArea, MediaGrid, MediaTable } from './components';
import mediaService from './services/mediaService';
import type { Media } from './services/mediaService';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: true,
            retry: 1,
            staleTime: 0,
            gcTime: 30000,
            refetchInterval: 10000,
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
    const [notification, setNotification] = useState<{
        message: string;
        type: 'success' | 'error';
        open: boolean;
    }>({ message: '', type: 'success', open: false });

    const { 
        data: mediaList = [], 
        refetch 
    } = useQuery({
        queryKey: ['mediaList'],
        queryFn: () => mediaService.getAllMedia(),
        refetchInterval: 5000,
        refetchIntervalInBackground: true
    });

    const showNotification = (message: string, type: 'success' | 'error') => {
        setNotification({ message, type, open: true });
    };

    const handleUpload = async (files: File[]) => {
        setIsUploading(true);
        try {
            for (const file of files) {
                await mediaService.uploadFile(file);
            }
            
            await queryClient.invalidateQueries({ queryKey: ['mediaList'] });
            await refetch();
            
            showNotification('Archivos subidos exitosamente', 'success');
        } catch (error) {
            console.error('Error uploading files:', error);
            showNotification('Error al subir los archivos', 'error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleMediaDelete = async (id: number) => {
        try {
            await mediaService.deleteMedia(id);
            
            await queryClient.invalidateQueries({ queryKey: ['mediaList'] });
            await refetch();
            
            showNotification('Archivo eliminado exitosamente', 'success');
        } catch (error) {
            console.error('Error deleting media:', error);
            showNotification('Error al eliminar el archivo', 'error');
        }
    };
    
    const handleMediaEdit = (media: Media) => {
        // Implementar lógica de edición si es necesaria
        console.log('Editing media:', media);
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

                {/* View Mode Toggle */}
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    my: 3 
                }}>
                    <ToggleButtonGroup
                        value={viewMode}
                        exclusive
                        onChange={(_, newViewMode) => {
                            if (newViewMode !== null) {
                                setViewMode(newViewMode);
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
                {viewMode === 'grid' ? (
                    <MediaGrid
                        media={filteredMedia}
                        onMediaDelete={handleMediaDelete}
                    />
                ) : (
                    <MediaTable
                        media={filteredMedia}
                        onMediaDelete={handleMediaDelete}
                        onMediaEdit={handleMediaEdit}
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
