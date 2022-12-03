from typing import Union
from fastapi import FastAPI

# to start app cd to project root directory and run:
# uvicorn app.main:app --reload
# reference: https://fastapi.tiangolo.com/#run-it


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/story")
def get_story():
    return {"Story": "Lorem ipsum dolor sit amet"}


@app.get("/images")
def read_item():
    return {"Images": "Some cool pictures, based on story"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

