/**
 * Definiciones de tipos para medios
 */

export interface Media {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  created_at: string;
  updated_at: string;
  creation_date?: string;
  uploaded_at?: string;
  thumbnail_path?: string | null;
  processed_file_path?: string | null;
  file_type: string;
  width?: number | null;
  height?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  event_type?: string | null;
  event_confidence?: number | null;
}

export interface MediaUpdate {
  event_type?: string;
  event_confidence?: number;
  [key: string]: any;
}

export interface MediaFilter {
  event_type?: string;
  file_type?: string;
  date_from?: string;
  date_to?: string;
  has_location?: boolean;
  search_term?: string;
}

export interface MediaStats {
  total_count: number;
  total_size: number;
  by_type: {
    [key: string]: {
      count: number;
      size: number;
    }
  };
  by_event: {
    [key: string]: number;
  };
}
