import React from 'react';
import { 
    AppBar, 
    Toolbar, 
    Typography, 
    InputBase, 
    Avatar, 
    Box,
    Button
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';

// Logo mostrado en el encabezado
const Logo = () => (
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '16px', height: '16px' }}>
        <g clipPath="url(#clip0_6_535)">
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M47.2426 24L24 47.2426L0.757355 24L24 0.757355L47.2426 24ZM12.2426 21H35.7574L24 9.24264L12.2426 21Z"
                fill="currentColor"
            />
        </g>
        <defs>
            <clipPath id="clip0_6_535">
                <rect width="48" height="48" fill="white" />
            </clipPath>
        </defs>
    </svg>
);

interface HeaderProps {
    onSearch: (query: string) => void;
    searchValue: string;
}

const Header: React.FC<HeaderProps> = ({ onSearch, searchValue }) => {
    return (
        <AppBar position="static" color="default" elevation={0} sx={{ 
            borderBottom: '1px solid #ededed',
            backgroundColor: 'white',
            py: 3
        }}>
            <Toolbar sx={{ justifyContent: 'space-between', px: '40px' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: '16px', color: '#141414' }}>
                        <Box sx={{ width: '16px', height: '16px' }}>
                            <Logo />
                        </Box>
                        <Typography
                            variant="h6"
                            noWrap
                            component="div"
                            sx={{ 
                                fontSize: '18px',
                                fontWeight: 'bold', 
                                color: '#141414',
                                letterSpacing: '-0.015em',
                                lineHeight: 'tight'
                            }}
                        >
                            Media Organizer
                        </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: '36px' }}>
                        <Typography 
                            sx={{ 
                                color: '#141414', 
                                fontWeight: 500, 
                                fontSize: '14px',
                                cursor: 'pointer',
                                lineHeight: 'normal'
                            }}
                        >
                            Inicio
                        </Typography>
                        <Typography 
                            sx={{ 
                                color: '#141414', 
                                fontWeight: 500, 
                                fontSize: '14px',
                                cursor: 'pointer',
                                lineHeight: 'normal'
                            }}
                        >
                            Galería
                        </Typography>
                    </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                    <Box
                        component="form"
                        sx={{
                            position: 'relative',
                            backgroundColor: '#f5f5f5',
                            borderRadius: '6px',
                            marginLeft: 0,
                            width: '300px',
                            border: '1px solid #ededed',
                            '&:hover': {
                                backgroundColor: '#ededed',
                            },
                            '&:focus-within': {
                                backgroundColor: 'white',
                                borderColor: '#141414',
                            }
                        }}
                    >
                        <Box
                            sx={{
                                padding: '0 12px',
                                height: '100%',
                                position: 'absolute',
                                pointerEvents: 'none',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: '#6b6b6b'
                            }}
                        >
                            <SearchIcon fontSize="small" />
                        </Box>
                        <InputBase
                            placeholder="Buscar por tipo de evento..."
                            inputProps={{ 'aria-label': 'search' }}
                            value={searchValue}
                            onChange={(e) => onSearch(e.target.value)}
                            sx={{
                                color: '#141414',
                                fontSize: '14px',
                                width: '100%',
                                '& .MuiInputBase-input': {
                                    padding: '12px 12px 12px 48px',
                                    transition: 'width 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms',
                                },
                            }}
                        />
                    </Box>

                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        sx={{
                            backgroundColor: '#141414',
                            color: 'white',
                            fontSize: '14px',
                            fontWeight: 600,
                            textTransform: 'none',
                            borderRadius: '6px',
                            px: '20px',
                            py: '10px',
                            '&:hover': {
                                backgroundColor: '#2a2a2a',
                            }
                        }}
                    >
                        Subir Archivos
                    </Button>

                    <Avatar sx={{ width: 32, height: 32, bgcolor: '#141414', fontSize: '14px' }}>
                        U
                    </Avatar>
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
