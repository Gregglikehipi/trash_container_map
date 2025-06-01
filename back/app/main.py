from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Header
from fastapi.responses import FileResponse, JSONResponse
from typing import Union, Annotated, List
from sqlalchemy.orm import Session
from app.sqlModels import db_helper, PlatformDB, PlatformCommentDB, Base, PlatformRatingDB
from app.pydanticModels import (
    AllPlatforms,
    PlatformCommentBase,
    PlatformResponse,
    PlatformCommentResponse,
    RatingBase,
    RatingResponse,
    PlatformWithRatingResponse
)
import pandas as pd
import os
import uuid
from datetime import datetime
from collections import defaultdict
from app.crud import *
import shutil
import cv2
import numpy as np
from ultralytics import YOLO
import hashlib


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

@app.get("/platform_photo/{platform_id}")
def read_platform_photo(platform_id: str):
    photo_dir = "app/photo"
    photos = []
    
    for filename in os.listdir(photo_dir):
        if filename.startswith(f"{platform_id}_") and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(photo_dir, filename)
            photos.append({
                "filename": filename,
                "url": f"/platform_photo/file/{filename}", 
                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
            })
    
    photos.sort(key=lambda x: x["created_at"], reverse=True)
    
    if not photos:
        raise HTTPException(status_code=404, detail="No photos found for this platform")
    
    return JSONResponse(content={
        "platform_id": platform_id,
        "photo_count": len(photos),
        "photos": photos
    })

@app.get("/platform_photos/{filename}")
def get_platform_photo(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(file_path)

@app.post("/platform_photo/{platform_id}")
def save_platform_photo(session: Annotated[Session, Depends(db_helper.get_db)],
                        platform_id: str, 
                        file: UploadFile = File(...), ):
    
    unique_id = str(uuid.uuid4())[:8] 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{platform_id}_{timestamp}_{unique_id}{file_extension}"
    
    file_path = os.path.join(UPLOAD_DIR, filename)

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


@app.post("/ratings/{platform_id}", response_model=RatingResponse)
async def rate_platform(
    platform_id: int,
    rating_data: RatingBase,
    request: Request,
    x_user_token: str = Header(None),
    db: Session = Depends(db_helper.get_db)
):
    user_token = get_user_token(request, x_user_token)
    rating = set_platform_rating(db, platform_id, user_token, rating_data.rating)
    return rating

@app.get("/platform_info/{id}", response_model=PlatformWithRatingResponse)
async def read_platform_info(
    id: str,
    request: Request,
    x_user_token: str = Header(None),
    db: Session = Depends(db_helper.get_db)
):
    platform = db.get(PlatformDB, id)
    if not platform:
        raise HTTPException(status_code=404, detail="Площадка не найдена")
    
    user_token = get_user_token(request, x_user_token)
    user_rating = get_user_rating(db, id, user_token)
    avg_rating = get_average_rating(db, id)

    ratings = db.query(PlatformRatingDB).filter_by(platform_id=id).all()
    ratings_count = len(ratings)
    rating_distribution = get_rating_distribution(ratings) 
    
    return {
        **platform.__dict__,
        "average_rating": avg_rating,
        "user_rating": user_rating.rating if user_rating else None,
        "ratings_count": ratings_count,
        "rating_distribution": rating_distribution
    }

def get_user_token(request: Request, x_user_token: str = None) -> str:
    ip = request.client.host or "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    if x_user_token:  # Если есть токен из localStorage
        return f"user-{hashlib.sha256(f'{ip}-{user_agent}-{x_user_token}'.encode()).hexdigest()}"
    else:  # Fallback на IP + User-Agent
        return f"ip-{hashlib.sha256(f'{ip}-{user_agent}'.encode()).hexdigest()}"