from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Metadatos
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # Para videos
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    creation_date = Column(DateTime, nullable=True)
    
    # Archivo procesado con formato fecha-evento
    processed_file_path = Column(String, nullable=True)
    
    # Datos CLIP
    event_type = Column(String, nullable=True)
    event_confidence = Column(Float, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())