import React from 'react';
import { Box, Container, Paper } from '@mui/material';
import Header from '../Header';

interface MainLayoutProps {
  children: React.ReactNode;
}

/**
 * Layout principal para la aplicación
 * Contiene el encabezado y el contenedor principal para el contenido
 */
export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [searchValue, setSearchValue] = React.useState('');
  
  // Manejador de búsqueda
  const handleSearch = (query: string) => {
    setSearchValue(query);
    // Aquí podría implementarse lógica adicional de búsqueda
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header 
        onSearch={handleSearch} 
        searchValue={searchValue} 
        onRefreshMedia={() => {}}
      />
      
      <Container component="main" maxWidth="xl" sx={{ mt: 3, mb: 3, flex: 1 }}>
        <Paper 
          elevation={3} 
          sx={{ 
            p: 3, 
            borderRadius: 2,
            minHeight: 'calc(100vh - 160px)'
          }}
        >
          {children}
        </Paper>
      </Container>
      
      <Box 
        component="footer" 
        sx={{ 
          py: 2, 
          textAlign: 'center',
          borderTop: '1px solid rgba(0,0,0,0.1)',
          backgroundColor: 'background.paper'
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary">
            ClasificadorV2 © {new Date().getFullYear()}
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

// Importación necesaria para Typography
import { Typography } from '@mui/material';
