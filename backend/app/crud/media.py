from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.media import Media
from app.schemas.media import MediaCreate, MediaUpdate

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
    
    db.delete(db_media)
    db.commit()
    return True
