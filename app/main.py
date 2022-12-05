from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import base64

from app.story_generator.generation import StoryTextGenerator, PromptGenerator
from tests.image_generation_test import get_segmented_story, summarize_story

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

with open("../data/img/sample_image.png", "rb") as image_file:
    encoded_string_example = base64.b64encode(image_file.read())


def create_story(story_title: str, n_pages: int):
    pass


@app.post("/settings")
async def read_item(info: Request):
    data = await info.json()
    return {}


@app.post("/page")
async def read_item(info: Request):
    data = await info.json()  # Data from post
    return {"text": "Generated New Story or Next page of existing one"}  # Use this format


@app.post("/image")
async def read_item(info: Request):
    data = await info.json()
    return {"image": encoded_string_example}


@app.post("/pdf")
async def read_item(info: Request):
    data = await info.json()
    return {"source": "../data/pdf/sample_string.pdf"}
