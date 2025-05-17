from datetime import datetime
from pydantic import BaseModel
from typing import List

class PlatformBase(BaseModel):
    class Config:
        from_attributes = True

class PlatformCreate(PlatformBase):
    address: str
    longitude: float
    latitude: float
    status: str

class PlatformResponse(PlatformBase):
    id: int
    address: str
    longitude: float
    latitude: float
    status: str
    change: str

class AllPlatforms(BaseModel):
    platforms: List[PlatformResponse]

class PlatformCommentBase(BaseModel):
    text: str

class PlatformCommentResponse(PlatformCommentBase):
    id: int
    platform_id: str
    date: datetime

    class Config:
        from_attributes = True