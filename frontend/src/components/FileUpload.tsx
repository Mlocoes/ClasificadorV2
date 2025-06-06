import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploadProps {
    onUpload: (files: File[]) => Promise<void>;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        setError(null);

        try {
            if (!acceptedFiles?.length) {
                setError('No se han seleccionado archivos');
                return;
            }

            const invalidFiles = acceptedFiles.filter(file => {
                const isImage = file.type.startsWith('image/');
                const isVideo = file.type.startsWith('video/');
                const isHeic = file.name.toLowerCase().endsWith('.heic') || 
                             file.name.toLowerCase().endsWith('.heif');
                return !(isImage || isVideo || isHeic);
            });

            if (invalidFiles.length > 0) {
                setError(`Archivos no soportados: ${invalidFiles.map(f => f.name).join(', ')}`);
                return;
            }

            setUploading(true);
            await onUpload(acceptedFiles);
            
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Error al subir los archivos';
            setError(errorMessage);
            console.error('Error en la carga de archivos:', err);
        } finally {
            setUploading(false);
        }
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png', '.heic', '.heif'],
            'video/*': ['.mp4', '.mov'],
            'image/heic': ['.heic', '.heif']
        },
        maxSize: 100 * 1024 * 1024, // 100MB
        multiple: true,
        disabled: uploading,
    });

    return (
        <div className="space-y-4">
            <div 
                {...getRootProps()} 
                className={`
                    relative overflow-hidden border-2 border-dashed transition-all duration-200
                    ${isDragActive ? 'border-[#141414] bg-[#f8f9fa]' : 'border-[#e5e7eb] hover:border-[#d1d5db] hover:bg-[#f8f9fa]'}
                    rounded-xl cursor-pointer
                `}
            >
                <input {...getInputProps()} />
                
                <div className="flex flex-col items-center justify-center px-6 py-10 text-center">
                    {/* Icono de subida */}
                    <div className={`
                        mb-4 flex h-12 w-12 items-center justify-center rounded-full
                        ${isDragActive ? 'bg-[#e8f4ff] text-[#0066cc]' : 'bg-[#f3f4f6] text-[#6b7280]'}
                    `}>
                        <svg 
                            className="h-6 w-6" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                        >
                            <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth={2} 
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>

                    {/* Texto principal */}
                    <div className="flex flex-col space-y-1">
                        <span className="text-sm font-medium text-[#141414]">
                            {isDragActive 
                                ? 'Suelta los archivos aquí...' 
                                : 'Arrastra y suelta archivos aquí'}
                        </span>
                        <span className="text-xs text-[#6b7280]">
                            o haz clic para seleccionar archivos
                        </span>
                    </div>

                    {/* Tipos de archivo aceptados */}
                    <div className="mt-4">
                        <p className="text-xs text-[#6b7280]">
                            JPG, PNG, HEIC/HEIF, MP4, MOV hasta 100 MB
                        </p>
                    </div>
                </div>

                {/* Barra de progreso */}
                {uploading && (
                    <div className="absolute bottom-0 left-0 right-0">
                        <div className="h-1 w-full bg-[#e5e7eb]">
                            <div className="h-1 animate-pulse bg-[#0066cc]"></div>
                        </div>
                    </div>
                )}
            </div>

            {/* Mensaje de error */}
            {error && (
                <div className="rounded-md bg-red-50 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
