from typing import Union

from fastapi import FastAPI

from pydantic import BaseModel

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