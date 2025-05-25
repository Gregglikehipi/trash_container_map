from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict
from pydantic import Field

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
    platform_id: int
    date: datetime

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    rating: int = Field(ge=1, le=5)  

class RatingResponse(RatingBase):
    platform_id: int
    user_token: str
    timestamp: datetime

class PlatformWithRatingResponse(PlatformResponse):
    average_rating: Optional[float]
    user_rating: Optional[int]
    ratings_count: int
    rating_distribution: Dict[int, int]