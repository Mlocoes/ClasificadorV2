from fastapi import APIRouter
from app.api.v1 import media, config

router = APIRouter()

router.include_router(media.router, prefix="/media", tags=["media"])
router.include_router(config.router, prefix="/config", tags=["config"])