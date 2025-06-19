import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { Media, MediaFilter } from '../types/media';
import { mediaService } from '../services';

/**
 * Hook personalizado para manejar la carga y filtrado de medios
 */
export function useMediaList(initialFilter: MediaFilter = {}) {
  const [filter, setFilter] = useState<MediaFilter>(initialFilter);
  
  // Query para obtener los medios con React Query
  const { 
    data: media, 
    isLoading, 
    error, 
    refetch 
  } = useQuery<Media[]>({
    queryKey: ['media', filter],
    queryFn: () => mediaService.getAllMedia()
  });

  // Función para actualizar filtros
  const updateFilter = (newFilter: Partial<MediaFilter>) => {
    setFilter(prev => ({ ...prev, ...newFilter }));
  };

  // Función para limpiar filtros
  const clearFilters = () => {
    setFilter({});
  };

  return {
    media: media || [],
    isLoading,
    error,
    filter,
    updateFilter,
    clearFilters,
    refetchMedia: refetch
  };
}

/**
 * Hook para manejar las operaciones de un medio seleccionado
 */
export function useMediaOperations() {
  const [selectedMedia, setSelectedMedia] = useState<Media | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const queryClient = useQueryClient(); // Para invalidar la caché después de operaciones

  // Función para seleccionar un medio
  const selectMedia = (media: Media | null) => {
    setSelectedMedia(media);
  };

  // Función para eliminar un medio
  const deleteMedia = async (id: number) => {
    if (!id) return;
    
    setIsDeleting(true);
    setDeleteError(null);
    
    try {
      await mediaService.deleteMedia(id);
      // Invalidar la caché para refrescar la lista
      queryClient.invalidateQueries({ queryKey: ['media'] });
      // Si el medio eliminado era el seleccionado, deseleccionarlo
      if (selectedMedia?.id === id) {
        setSelectedMedia(null);
      }
    } catch (error) {
      setDeleteError(`Error al eliminar el medio: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return {
    selectedMedia,
    isDeleting,
    deleteError,
    selectMedia,
    deleteMedia
  };
}

// Necesario para useMediaOperations
import { useQueryClient } from '@tanstack/react-query';
