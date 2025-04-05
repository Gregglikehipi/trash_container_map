from pydantic import BaseModel

class Platform(BaseModel):
    id: int
    address: str
    longitude: float
    latitude: float

class AllPlatforms(BaseModel):
    platforms: list[Platform]


