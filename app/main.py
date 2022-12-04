from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# to start app cd to project root directory and run:
# uvicorn app.main:app --reload
# reference: https://fastapi.tiangolo.com/#run-it

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/options")
def read_item():
    return {}

@app.post("/page")
def read_item():
    return {"text": "Some cool text"}

@app.post("/image")
def read_item():
    return {"Images": "Some cool pictures, based on story"}

