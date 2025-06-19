import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { ViewModeType } from '../types/common';

// Definir el tipo para el estado de la aplicación
interface AppState {
  viewMode: ViewModeType;
  setViewMode: (mode: ViewModeType) => void;
  isUploading: boolean;
  setIsUploading: (isUploading: boolean) => void;
  lastRefreshTime: number;
  refreshData: () => void;
  notificationMessage: string | null;
  showNotification: (message: string) => void;
  clearNotification: () => void;
}

// Crear el contexto con un valor inicial
const AppContext = createContext<AppState | undefined>(undefined);

// Props para el proveedor del contexto
interface AppProviderProps {
  children: ReactNode;
}

// Proveedor del contexto que contiene el estado
export function AppProvider({ children }: AppProviderProps) {
  // Estado para el modo de visualización (grid o table)
  const [viewMode, setViewMode] = useState<ViewModeType>('grid');
  
  // Estado para indicar si hay una carga en proceso
  const [isUploading, setIsUploading] = useState(false);
  
  // Estado para controlar cuándo se refrescaron los datos por última vez
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());
  
  // Estado para mensajes de notificación
  const [notificationMessage, setNotificationMessage] = useState<string | null>(null);
  
  // Función para forzar un refresco de datos
  const refreshData = () => setLastRefreshTime(Date.now());
  
  // Función para mostrar una notificación
  const showNotification = (message: string) => {
    setNotificationMessage(message);
    // Limpiar automáticamente la notificación después de 5 segundos
    setTimeout(() => {
      setNotificationMessage(null);
    }, 5000);
  };
  
  // Función para limpiar una notificación
  const clearNotification = () => setNotificationMessage(null);
  
  // El valor que se proporcionará a través del contexto
  const value: AppState = {
    viewMode,
    setViewMode,
    isUploading,
    setIsUploading,
    lastRefreshTime,
    refreshData,
    notificationMessage,
    showNotification,
    clearNotification
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Hook personalizado para facilitar el uso del contexto
export function useAppContext() {
  const context = useContext(AppContext);
  
  if (context === undefined) {
    throw new Error('useAppContext debe ser utilizado dentro de un AppProvider');
  }
  
  return context;
}
