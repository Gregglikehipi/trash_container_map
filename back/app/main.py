from typing import Union, Annotated

from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.responses import FileResponse
from ultralytics import YOLO

from sqlalchemy.orm import Session

from app.pydanticModels import AllPlatforms
from app.crud import create_platform
from app.sqlModels import db_helper

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

info = {"platforms": [ {"id": 1, "address": "Ленина", "longitude": 55.148707, "latitude": 61.433685}, {"id": 2, "address": "Ленина", "longitude": 55.148707, "latitude": 61.333685}]}

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("app/my_model.pt")

@app.get("/platforms")
def get_platforms():
    text = AllPlatforms(**info)
    return text


@app.get("/platform_photo/{platform_id}")
def read_platform_photo(platform_id: int):
    result = model(f"app/photo/{platform_id}.jpg")
    return result


@app.get("/platform_info/{id}")
def read_platform_info(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/platform_info/{id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/test")
def read_item(session: Annotated[Session, Depends(db_helper.get_db)]):
    create_platform(session, "Челябинск", 90.808, 10.1010)
    return {"item_id": 1, "q": 1}
