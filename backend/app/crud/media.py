from sqlalchemy.orm import Session
from typing import List, Optional
import os
from pathlib import Path
from app.models.media import Media
from app.schemas.media import MediaCreate, MediaUpdate
from app.core.config import settings

def get_media(db: Session, media_id: int) -> Optional[Media]:
    return db.query(Media).filter(Media.id == media_id).first()

def get_all_media(db: Session, skip: int = 0, limit: int = 100) -> List[Media]:
    return db.query(Media).offset(skip).limit(limit).all()

def create_media(db: Session, media: MediaCreate, file_path: str) -> Media:
    db_media = Media(
        filename=media.filename,
        file_path=file_path,
        mime_type=media.mime_type,
        file_size=media.file_size
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def update_media(db: Session, media_id: int, media_update: MediaUpdate) -> Optional[Media]:
    db_media = get_media(db, media_id)
    if not db_media:
        return None
    
    update_data = media_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_media, key, value)
    
    db.commit()
    db.refresh(db_media)
    return db_media

def delete_media(db: Session, media_id: int) -> bool:
    db_media = get_media(db, media_id)
    if not db_media:
        return False
    
    # Eliminar archivo original
    if db_media.file_path:
        # Eliminar archivo en /app/storage/uploads/
        filename = db_media.file_path.replace('/uploads/', '')
        file_path = Path('/app/storage/uploads') / filename
        try:
            print(f"Intentando eliminar archivo original: {file_path}")
            if file_path.exists():
                os.chmod(str(file_path), 0o666)  # Asegurar permisos de escritura
                os.remove(str(file_path))
                print(f"Archivo original eliminado: {file_path}")
        except Exception as e:
            print(f"Error eliminando archivo original {file_path}: {e}")

    # Eliminar miniatura
    if db_media.thumbnail_path:
        # Eliminar miniatura en /app/storage/thumbnails/
        thumb_filename = db_media.thumbnail_path.replace('/thumbnails/', '')
        thumb_path = Path('/app/storage/thumbnails') / thumb_filename
        try:
            print(f"Intentando eliminar miniatura: {thumb_path}")
            if thumb_path.exists():
                os.chmod(str(thumb_path), 0o666)  # Asegurar permisos de escritura
                os.remove(str(thumb_path))
                print(f"Miniatura eliminada: {thumb_path}")
        except Exception as e:
            print(f"Error eliminando miniatura {thumb_path}: {e}")
    
    # Eliminar archivo procesado
    if db_media.processed_file_path:
        # Eliminar archivo en /app/storage/processed/
        processed_filename = db_media.processed_file_path.replace('/processed/', '')
        processed_path = Path('/app/storage/processed') / processed_filename
        try:
            print(f"Intentando eliminar archivo procesado: {processed_path}")
            if processed_path.exists():
                os.chmod(str(processed_path), 0o666)  # Asegurar permisos de escritura
                os.remove(str(processed_path))
                print(f"Archivo procesado eliminado: {processed_path}")
        except Exception as e:
            print(f"Error eliminando archivo procesado {processed_path}: {e}")
    
    # Eliminar registro de base de datos
    db.delete(db_media)
    db.commit()
    return True
