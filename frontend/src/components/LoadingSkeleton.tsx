import React from 'react';
import { Box, Skeleton, Grid } from '@mui/material';

interface LoadingSkeletonProps {
    count?: number;
    variant?: 'card' | 'table' | 'list';
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ count = 8, variant = 'card' }) => {
    if (variant === 'card') {
        return (
            <Grid container spacing={2}>
                {[...Array(count)].map((_, index) => (
                    <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                        <Box sx={{ 
                            border: '1px solid #e0e0e0', 
                            borderRadius: 1, 
                            p: 1,
                            height: '300px'
                        }}>
                            <Skeleton variant="rounded" width="100%" height="200px" />
                            <Box sx={{ pt: 1 }}>
                                <Skeleton variant="text" height={24} />
                                <Skeleton variant="text" height={20} width="70%" />
                                <Skeleton variant="text" height={20} width="50%" />
                            </Box>
                        </Box>
                    </Grid>
                ))}
            </Grid>
        );
    }

    if (variant === 'table') {
        return (
            <Box>
                {[...Array(count)].map((_, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', p: 2, borderBottom: '1px solid #e0e0e0' }}>
                        <Skeleton variant="rounded" width={60} height={60} sx={{ mr: 2 }} />
                        <Box sx={{ flex: 1 }}>
                            <Skeleton variant="text" width="80%" />
                            <Skeleton variant="text" width="50%" />
                        </Box>
                        <Skeleton variant="circular" width={30} height={30} />
                    </Box>
                ))}
            </Box>
        );
    }

    // variant === 'list'
    return (
        <Box>
            {[...Array(count)].map((_, index) => (
                <Box key={index} sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                    <Skeleton variant="text" width="60%" />
                    <Skeleton variant="text" width="40%" />
                </Box>
            ))}
        </Box>
    );
};
