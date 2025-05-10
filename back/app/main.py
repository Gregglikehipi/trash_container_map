from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import Union, Annotated
from sqlalchemy.orm import Session
from app.sqlModels import db_helper, PlatformDB, PlatformCommentDB, Base
from app.pydanticModels import (
    AllPlatforms,
    PlatformCommentBase,
    PlatformResponse,
    PlatformCommentResponse
)
import pandas as pd
import os
from datetime import datetime
from collections import defaultdict
from app.crud import *
import shutil

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

UPLOAD_DIR = "app/photo"
os.makedirs(UPLOAD_DIR, exist_ok=True)

info = {"platforms": [ {"id": 1, "address": "Ленина", "longitude": 55.148707, "latitude": 61.433685, "status": "red"}, {"id": 2, "address": "Ленина", "longitude": 55.148707, "latitude": 61.333685, "status": "yellow"}, {"id": 3, "address": "Ленина", "longitude": 55.148707, "latitude": 61.533685, "status": "green"}]}

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# model = YOLO("app/my_model.pt")

"""
@app.on_event("startup")
async def load_platforms():
    try:
        Base.metadata.create_all(bind=db_helper.engine)
        
        file_path = "app/data/Выгрузка.xlsx"
        df = pd.read_excel(file_path, engine='openpyxl', dtype={'НомерПлощадки': str})
        
        df['Долгота'] = df['Долгота'].astype(str).str.replace(',', '.').astype(float)
        df['Широта'] = df['Широта'].astype(str).str.replace(',', '.').astype(float)
        df['НомерПлощадки'] = df['НомерПлощадки'].astype(str)
        
        db = db_helper.SessionLocal()
        try:
            count = db.query(PlatformDB).count()
            if count == 0:
                for _, row in df.iterrows():
                    platform = PlatformDB(
                        id=row['НомерПлощадки'],
                        address=row['Наименование'],
                        longitude=row['Долгота'],
                        latitude=row['Широта'],
                        status="green"
                    )
                    db.add(platform)
                db.commit()
        finally:
            db.close()
            
    except Exception as e:
        raise RuntimeError(f"Ошибка инициализации данных: {str(e)}")
"""

@app.get("/platforms", response_model=AllPlatforms)
def get_platforms(session: Session = Depends(db_helper.get_db)):
    platforms = read_platforms(session)
    return AllPlatforms(platforms = platforms)

@app.get("/platform_info/{id}", response_model=PlatformResponse)
def read_platform_info(id: str, session: Session = Depends(db_helper.get_db)):
    platform = session.get(PlatformDB, id)
    if not platform:
        raise HTTPException(status_code=404, detail="Площадка не найдена")
    return platform




@app.get("/platform_photo/{platform_id}")
def read_platform_photo(platform_id: str):
    photo_dir = "app/photo"
    platform_prefix = platform_id

    for filename in os.listdir(photo_dir):
        if filename.startswith(f"{platform_prefix}") and filename.endswith(".jpg"):
            file_path = os.path.join(photo_dir, filename)
            return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="Photo not found")

@app.post("/platform_photo/{platform_id}")
def save_platform_photo(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "saved_to": file_path}


@app.post("/platform_info/{id}")
def post_comment(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/test")
def read_item(session: Annotated[Session, Depends(db_helper.get_db)]):
    create_platform(session, "Челябинск", 90.808, 10.1010)
    return {"item_id": 1, "q": 1}


@app.post("/comments/{platform_id}", response_model=PlatformCommentResponse)
def post_create_comment(
    platform_id: str,
    comment_data: PlatformCommentBase,
    session: Session = Depends(db_helper.get_db)
):
    new_comment = create_comment(session, platform_id, comment_data.text)
    return new_comment

@app.get("/comments/{platform_id}", response_model=list[PlatformCommentResponse])
def get_read_comments(platform_id: str, session: Session = Depends(db_helper.get_db)):
    return get_comments(session, platform_id)

@app.get("/platforms/filter/", response_model=AllPlatforms)
def filter_platforms(
    status: str = None,
    db: Session = Depends(db_helper.get_db)
):
    platforms = filter_platforms_by_status(db, status)
    return AllPlatforms(platforms=platforms)

@app.get("/platforms/stats")
def get_platform_stats(db: Session = Depends(db_helper.get_db)):
    return get_platforms_stats(db)