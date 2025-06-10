from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MediaBase(BaseModel):
    filename: str
    mime_type: str
    file_size: int
    
class MediaCreate(MediaBase):
    pass

class MediaUpdate(BaseModel):
    event_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Media(MediaBase):
    id: int
    file_path: str
    thumbnail_path: Optional[str] = None
    processed_file_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    creation_date: Optional[datetime] = None
    event_type: Optional[str] = None
    event_confidence: Optional[float] = None
    uploaded_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True