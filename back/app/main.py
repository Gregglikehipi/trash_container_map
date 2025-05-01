from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Union, Annotated
from sqlalchemy.orm import Session
from app.sqlModels import db_helper, PlatformDB, PlatformCommentDB, Base
from app.pydanticModels import (
    AllPlatforms,
    PlatformResponse,
    PlatformCommentCreate,
    PlatformCommentResponse
)
import pandas as pd
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware

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


@app.on_event("startup")
async def load_platforms():
    try:
        # Создаем таблицы, если они еще не существуют
        Base.metadata.create_all(bind=db_helper.engine)
        
        file_path = "app/data/Выгрузка.xlsx"
        df = pd.read_excel(file_path, engine='openpyxl')
        
        df['Долгота'] = df['Долгота'].astype(str).str.replace(',', '.').astype(float)
        df['Широта'] = df['Широта'].astype(str).str.replace(',', '.').astype(float)
        df['НомерПлощадки'] = df['НомерПлощадки'].astype(int)
        
        db = db_helper.SessionLocal()
        try:
            # Проверяем, есть ли уже данные в таблице
            count = db.query(PlatformDB).count()
            if count == 0:  # Добавляем данные только если таблица пуста
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

@app.get("/platforms", response_model=AllPlatforms)
def get_platforms(session: Session = Depends(db_helper.get_db)):
    platforms = session.query(PlatformDB).all()
    return AllPlatforms(platforms=platforms)

@app.get("/platform_info/{id}", response_model=PlatformResponse)
def read_platform_info(id: int, session: Session = Depends(db_helper.get_db)):
    platform = session.get(PlatformDB, id)
    if not platform:
        raise HTTPException(status_code=404, detail="Площадка не найдена")
    return platform


@app.get("/platform_photo/{platform_id}")
def read_platform_photo(platform_id: int):
    return FileResponse(path=f"app/photo/{platform_id}.jpg")


@app.post("/platform_info/{id}")
def post_comment(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/test")
def read_item(session: Annotated[Session, Depends(db_helper.get_db)]):
    create_platform(session, "Челябинск", 90.808, 10.1010)
    return {"item_id": 1, "q": 1}


@app.post("/comments/{platform_id}", response_model=PlatformCommentResponse)
def post_create_comment(
    platform_id: int,
    comment_data: PlatformCommentCreate,
    session: Session = Depends(db_helper.get_db)
):
    new_comment = create_comment(session, platform_id, comment_data.text)
    return new_comment

@app.get("/comments/{platform_id}", response_model=list[PlatformCommentResponse])
def get_read_comments(platform_id: int, session: Session = Depends(db_helper.get_db)):
    return get_comments(session, platform_id)