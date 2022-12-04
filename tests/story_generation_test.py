from app.story_generator.generation import StoryGenerator, PromptGenerator
from tests.image_generation_test import get_segmented_story


def create_prompt(story_title=None):
    header = 'Exercise: Generate the beginning of the story for children based on a title given.'
    story_title_1, random_story_1 = get_segmented_story(sentences_per_page=3)
    random_story_2 = random_story_1
    while random_story_1[0] == random_story_2[0]:
        story_title_2, random_story_2 = get_segmented_story(sentences_per_page=3)
    examples = [random_story_1[0], random_story_2[0]]
    titles = [story_title_1, story_title_2]
    if story_title is None:
        story_title = 'The Dragon and prince penguin'
    MAX_TOKENS = 1000
    prompt_generator = PromptGenerator(header, examples, titles, max_tokens=MAX_TOKENS)
    return prompt_generator.generate_prompt_for_story_start(story_title=story_title)


def create_stories(story_title=None):
    sg = StoryGenerator(create_prompt(story_title))
    story = sg.generate()
    return story


def main():
    story_title = 'The princess and the Italy castle'
    result = create_stories(story_title)
    for story in result['generation']:
        title = story_title
        print(title + '\n' + story)
        print('----------------------------------------')

if __name__ == '__main__':
    main()