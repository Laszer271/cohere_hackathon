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
count = 1
last_text = ''

@app.post("/settings")
async def read_item(info: Request):
    data = await info.json()
    global data_generator
    global count

    count = 1
    stories = get_n_stories(3)
    data_generator = StoryGenerator(data['settings']['pages'], data['settings']['summary'], stories)
    return {}


@app.post("/page")
async def read_item(info: Request):
    data = await info.json()  # Data from post
    print(data)
    global count
    global data_generator
    global last_text

    if count == 1:
        summary = data_generator.generate_story_description()
        print('Summary:', summary)
        text = data_generator.generate_story_beginning()
        print('Beginning:', text)
    elif count < data_generator.n_pages:
        if count == 2:
            data_generator.beginning = data['text']
        else:
            data_generator.continuations[-1] = data['text']
        text = data_generator.generate_story_continuation()
        print('Continuation:', text)
    else:
        data_generator.continuations[-1] = data['text']
        text = data_generator.generate_story_ending()
        print('Ending:', text)

    if data['text'] != text:
        last_text = text
        count += 1

    return {"text": text}  # Use this format


@app.post("/image")
async def read_item(info: Request):
    data = await info.json()
    return {"image": encoded_string_example}


@app.post("/pdf")
async def read_item(info: Request):
    data = await info.json()
    return {"source": "../data/pdf/sample_string.pdf"}
