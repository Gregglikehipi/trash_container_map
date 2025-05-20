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
import cv2
import numpy as np
from ultralytics import YOLO


from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

UPLOAD_DIR = "app/photo"
os.makedirs(UPLOAD_DIR, exist_ok=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("app/my_model.pt")


@app.get("/platforms", response_model=AllPlatforms)
def get_platforms(session: Session = Depends(db_helper.get_db)):
    platforms = read_platforms(session)
    return AllPlatforms(platforms = platforms)


@app.get("/platform", response_model=AllPlatforms)
def get_platform(session: Session = Depends(db_helper.get_db)):
    platforms = session.query(PlatformDB).limit(10).all()
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
def save_platform_photo(session: Annotated[Session, Depends(db_helper.get_db)],
                        platform_id: str, file: UploadFile = File(...), ):
    file_path = os.path.join(UPLOAD_DIR, f"{platform_id}.jpg")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = model(file_path)

    result = results[0]

    result.save(filename=file_path)

    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    empty_count = np.sum(class_ids == 0)
    full_count = np.sum(class_ids == 1)

    print(f"Empty trash containers: {empty_count}")
    print(f"Full trash containers: {full_count}")


    if full_count > 0 and empty_count == 0:
        update_platform(session, int(platform_id), "red", datetime.today().strftime('%d-%m-%Y'))
        print("red")

    if full_count > 0 and empty_count > 0:
        update_platform(session, int(platform_id), "yellow", datetime.today().strftime('%d-%m-%Y'))
        print("yellow")

    if full_count == 0 and empty_count == 0:
        print("huh?")

    if full_count == 0 and empty_count > 0:
        update_platform(session, int(platform_id), "green", datetime.today().strftime('%d-%m-%Y'))
        print("green")



    return {"filename": file.filename, "saved_to": file_path}


@app.post("/comments/{platform_id}", response_model=PlatformCommentResponse)
def post_create_comment(
    platform_id: int,
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