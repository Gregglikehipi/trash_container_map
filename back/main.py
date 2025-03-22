from typing import Union, Annotated

from fastapi import FastAPI, Depends

from pydantic import BaseModel
from sqlalchemy.orm import Session

from crud import create_platform
from sqlModels import db_helper

app = FastAPI()


@app.get("/platforms")
def read_root():
    return {"Hello": "World"}


@app.get("/platform_photo/{id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/platform_info/{id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/platform_info/{id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/test")
def read_item(session: Annotated[Session, Depends(db_helper.get_db)]):
    create_platform(session, "Челябинск", 90, 90)
    return {"item_id": 1, "q": 1}