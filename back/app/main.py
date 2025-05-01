from typing import Union, Annotated, List

from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.responses import FileResponse
# from ultralytics import YOLO

from sqlalchemy.orm import Session

<<<<<<< HEAD
from fastapi import HTTPException
=======
from app.pydanticModels import AllPlatforms
from app.crud import create_platform
from app.crud import *
from app.sqlModels import db_helper
import pandas as pd

from app.pydanticModels import (
    AllPlatforms,
    PlatformCommentCreate,
    PlatformCommentResponse
)
>>>>>>> temp-branch

from fastapi.middleware.cors import CORSMiddleware

from back.app.crud import create_platform, import_excel_to_db
from back.app.pydanticModels import AllPlatforms
from back.app.sqlModels import PlatformComment, db_helper, Platform

app = FastAPI()

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

<<<<<<< HEAD
"""@app.get("/platforms")
=======
"""
@app.get("/platforms")
>>>>>>> temp-branch
def get_platforms():
    text = AllPlatforms(**info)
    return text
"""

@app.get("/platforms", response_model=AllPlatforms)
def get_platforms(session: Session = Depends(db_helper.get_db)):
    db_platforms = session.query(Platform).all()

    return AllPlatforms(
        platforms=[
            Platform(
                id=p.platform_id,
                address=p.address,
                longitude=p.longitude,
                latitude=p.latitude,
                status=p.status
            ) for p in db_platforms
        ]
    )

@app.get("/platform_photo/{platform_id}")
def read_platform_photo(platform_id: int):
    image_path = f"app/photo/{platform_id}.jpg"
    results = model(image_path)

    result_img_path = f"app/photo/annotated_{platform_id}.jpg"
    results[0].save(filename=result_img_path)

    return FileResponse(result_img_path, media_type="image/jpeg")
"""


@app.get("/platform_photo/{platform_id}")
def read_platform_photo(platform_id: int):
    return FileResponse(path=f"app/photo/{platform_id}.jpg")


@app.get("/platform_info/{id}")
def read_platform_info(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/platform_info/{id}")
def post_comment(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/test")
def read_item(session: Annotated[Session, Depends(db_helper.get_db)]):
    create_platform(session, "Челябинск", 90.808, 10.1010)
    return {"item_id": 1, "q": 1}

<<<<<<< HEAD
@app.post("/comments/{platform_id}", response_model=PlatformComment)
def create_comment(platform_id: int, text: str, session: Session = Depends(db_helper.get_db)):
    return create_comment(session, platform_id, text)

@app.get("/comments/{platform_id}", response_model=List[PlatformComment])
def read_comments(platform_id: int, session: Session = Depends(db_helper.get_db)):
    comments = read_comments(session, platform_id)
    return comments

@app.get("/comments/detail/{comment_id}", response_model=PlatformComment)
def read_comment(comment_id: int, session: Session = Depends(db_helper.get_db)):
    comment = read_comment(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment

@app.put("/comments/{comment_id}", response_model=PlatformComment)
def update_comment(comment_id: int, new_text: str, session: Session = Depends(db_helper.get_db)):
    try:
        return update_comment(session, comment_id, new_text)
=======

@app.get("/platforms", response_model=AllPlatforms)
def get_platforms_from_excel():
    file_path = "app/data/Выгрузка.xlsx"
    
    df = pd.read_excel(file_path, engine='openpyxl')
    
    df['Долгота'] = df['Долгота'].astype(str).str.replace(',', '.').astype(float)
    df['Широта'] = df['Широта'].astype(str).str.replace(',', '.').astype(float)
    
    df['НомерПлощадки'] = df['НомерПлощадки'].astype(int)
    
    platforms = []
    for _, row in df.iterrows():
        platform = {
            "id": row['НомерПлощадки'],
            "address": row['Наименование'],
            "longitude": row['Долгота'],
            "latitude": row['Широта'],
            "status": "green"
        }
        
        platforms.append(platform)

    return {"platforms": platforms}


@app.post("/comments/{platform_id}", response_model=PlatformCommentResponse)
def post_create_comment(
    platform_id: int,
    comment_data: PlatformCommentCreate,
    session: Session = Depends(db_helper.get_db)
):
    new_comment = create_comment(session, platform_id, comment_data.text)
    return PlatformCommentResponse.model_validate(new_comment)

@app.get("/comments/{platform_id}", response_model=list[PlatformCommentResponse])
def get_read_comments(platform_id: int, session: Session = Depends(db_helper.get_db)):
    comments = read_comments(session, platform_id)
    return [PlatformCommentResponse.model_validate(c) for c in comments]

@app.get("/comments/detail/{comment_id}", response_model=PlatformCommentResponse)
def get_read_comment(comment_id: int, session: Session = Depends(db_helper.get_db)):
    comment = read_comment(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return PlatformCommentResponse.model_validate(comment)

@app.put("/comments/{comment_id}", response_model=PlatformCommentResponse)
def put_update_comment(
    comment_id: int,
    comment_data: PlatformCommentCreate,
    session: Session = Depends(db_helper.get_db)
):
    try:
        updated_comment = update_comment(session, comment_id, comment_data.text)
        return PlatformCommentResponse.model_validate(updated_comment)
>>>>>>> temp-branch
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/comments/{comment_id}", response_model=dict)
<<<<<<< HEAD
def delete_comment(comment_id: int, session: Session = Depends(db_helper.get_db)):
=======
def delete_delete_comment(comment_id: int, session: Session = Depends(db_helper.get_db)):
>>>>>>> temp-branch
    try:
        delete_comment(session, comment_id)
        return {"detail": "Комментарий удален"}
    except ValueError as e:
<<<<<<< HEAD
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/import-excel")
def import_excel_data():
    try:
        import_excel_to_db()
        return {"status": "success", "message": "Data imported successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
=======
        raise HTTPException(status_code=404, detail=str(e))
>>>>>>> temp-branch
