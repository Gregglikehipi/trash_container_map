from pydantic import BaseModel
from datetime import datetime

class Platform(BaseModel):
    id: int
    address: str
    longitude: float
    latitude: float
    status: str

class AllPlatforms(BaseModel):
    platforms: list[Platform]

class PlatformCommentBase(BaseModel):
    text: str

class PlatformCommentCreate(PlatformCommentBase):
    platform_id: int

class PlatformCommentResponse(PlatformCommentBase):
    id: int
    platform_id: int
    date: datetime

    class Config:
        from_attributes = True


