import os
import random
import json

from app.image_generator.image_generator import ImageGenerator
from app.story_generator.segmentation import StoryDivider
from app.story_generator.summarizer import StorySummarizer


def get_random_story():
    stories_path = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir,
                                "data", "stories", "fairy_tales.json")
    with open(stories_path, "rb") as f:
        stories = json.load(f)
        example_story = random.choice(stories)
    return example_story


def get_segmented_story(story=None, sentences_per_page=3):
    if story is None:
        story = get_random_story()
    if len(story) > 2048:
        story = story[:2000]
    seg = StoryDivider(story["title"], story["text"])
    segmented = seg.divide_story_into_segments(sentences_per_page=sentences_per_page)
    return story["title"], segmented


def summarize_story(story=None):
    story = get_segmented_story(story, sentences_per_page=3)
    for part in story[1]:
        summarized_part = StorySummarizer(part, max_tokens=200).summarize()
        if summarized_part != "":
            get_image_to_story_segment(summarized_part)
        print(part)


def get_image_to_story_segment(segment_summarized):
    ig = ImageGenerator(segment_summarized)
    return ig.generate()


def create_the_story_object():
    # waiting for guys to implement this
    # prob loop over the segmented story plus some object to hold it in consistent format for API
    pass


def main():
    summarize_story()


if __name__ == "__main__":
    main()
