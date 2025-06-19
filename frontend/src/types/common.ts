/**
 * Tipos para la configuración de la aplicación
 */

export interface ConfigState {
  aiModel: string;
  isLoading: boolean;
  error: string | null;
}

/**
 * Tipos para servicios
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

/**
 * Tipos para componentes UI
 */
export interface LoadingProps {
  isLoading: boolean;
  loadingText?: string;
  children: React.ReactNode;
}

/**
 * Constantes
 */
export const ViewMode = {
  GRID: 'grid',
  TABLE: 'table'
} as const;

export const AIModel = {
  CLIP: 'clip',
  OPENCV_DNN: 'opencv_dnn',
  OPENCV_YOLO: 'opencv_yolo'
} as const;

export const FileType = {
  IMAGE: 'image',
  VIDEO: 'video'
} as const;

// Tipos derivados de las constantes
export type ViewModeType = typeof ViewMode[keyof typeof ViewMode];
export type AIModelType = typeof AIModel[keyof typeof AIModel];
export type FileTypeType = typeof FileType[keyof typeof FileType];
