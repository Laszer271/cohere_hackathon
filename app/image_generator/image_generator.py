import io
import warnings
import base64

from PIL import Image
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from app.config import STABILITY_API as stability_api


class ImageGenerator:
    def __init__(self, story_segment, width=512, height=512):
        self.story_segment = story_segment
        self.width = width
        self.height = height

    def generate(self):
        image_prompt = f"Description: {self.story_segment}; fairy tale; book for children; lovely story; cartoon style; by Ernest Shepard; by John Tenniel; Beatrix Potter"
        print('IMAGE_PROMPT:', image_prompt)
        answers = stability_api.generate(
            prompt=image_prompt,
            width=self.width,
            height=self.height
        )
        # iterating over the generator produces the api response
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                    return None
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = io.BytesIO(artifact.binary)
                    img_str = base64.b64encode(img.getvalue())
                    return img_str
