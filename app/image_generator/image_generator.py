import io
import warnings

import cohere
from PIL import Image
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from app.config import STABILITY_API as stability_api


class ImageGenerator:
    def __init__(self, story_segment, width=512, height=512):
        self.story_segment = story_segment
        self.width = width
        self.height = height

    def generate(self):
        image_prompt = f"children's tale style; {self.story_segment}"
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
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.show()
