from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.story_generator.generation import StoryGenerator, get_n_stories
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

with open("./data/img/sample_image.png", "rb") as image_file:
    encoded_string_example = base64.b64encode(image_file.read())


def create_story(story_title: str, n_pages: int):
    pass

data_generator = None
count = 0

@app.post("/settings")
async def read_item(info: Request):
    data = await info.json()
    global data_generator

    stories = get_n_stories(3)
    data_generator = StoryGenerator(data['settings']['pages'], data['settings']['summary'], stories)
    return {}


@app.post("/page")
async def read_item(info: Request):
    data = await info.json()  # Data from post
    print(data)
    global count
    global data_generator
    if count == 0:
        text = data_generator.generate_story_description()
    elif count == 1:
        data_generator.summary = data['text']
        text = data_generator.generate_story_beginning()
    # elif count < data_generator.n_pages -1:
    #     data_generator.beginning = data['text']
    #     text = data_generator.generate_story_continuation()
    else:
        data_generator.continuation = data['text']
        text = data_generator.generate_story_ending()
    count += 1
    # data_generator.generate_story_description()
    return {"text": text}  # Use this format


@app.post("/image")
async def read_item(info: Request):
    data = await info.json()
    return {"image": encoded_string_example}


@app.post("/pdf")
async def read_item(info: Request):
    data = await info.json()
    return {"source": "../data/pdf/sample_string.pdf"}
