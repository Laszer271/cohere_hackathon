import json

import numpy as np

from app.story_generator.generation import PromptGenerator, StoryTextGenerator, add_newline_at_the_end
from app.story_generator.segmentation import StoryDivider
from config import init_params, DISALLOWED_TOKENS, story_params


def get_n_stories(n=3):
    import os
    stories_path = os.path.join(os.path.abspath(''), os.pardir,
                                "data", "stories", "fairy_tales.json")
    with open(stories_path, "rb") as f:
        stories = json.load(f)
        assert n <= len(stories), f'Tried to get {n} stories while is only {len(stories)} stories in the database'
        example_stories = list(np.random.choice(stories, size=n, replace=False))

    return example_stories


def get_segment_of_stories(stories: list, segment_idx: int, handle_too_big_index=True,
                           n_pages=None, sentences_per_page=3):
    segmented_stories = []
    for s in stories:
        seg = StoryDivider(s["title"], s["text"])
        segmented = seg.divide_story_into_segments(n_pages=n_pages, sentences_per_page=sentences_per_page)
        if handle_too_big_index and segment_idx >= len(segmented):
            index = len(segmented) - 1

        result = s.copy()

        text = segmented[segment_idx]
        result.update({'text': text})
        segmented_stories.append(result)

    return segmented_stories


def get_segments_and_continuations(stories: list, n_pages=None, sentences_per_page=3):
    segmented_stories = []
    for s in stories:
        seg = StoryDivider(s["title"], s["text"])
        segmented = seg.divide_story_into_segments(n_pages=n_pages, sentences_per_page=sentences_per_page)

        segment_idx = np.random.randint(0, len(segmented) - 2)

        result = s.copy()
        prev_text = segmented[segment_idx]
        cont_text = segmented[segment_idx + 1]
        result.update({'Previous Part': prev_text, 'Continuation': cont_text})
        del result['text']
        segmented_stories.append(result)

    return segmented_stories


def hard_filter_results(results, stop_seq, disallowed_strings):
    # results = results.loc[results['generation'].str.contains(stop_seq)]

    mask = None
    for s in disallowed_strings:
        new_mask = ~results['generation'].str.contains(s, regex=False)
        if mask is None:
            mask = new_mask
        else:
            mask = mask & new_mask
    results = results.loc[mask]
    return results


def postprocess_results(results, stop_seq):
    results['generation'] = results['generation'].str.replace(stop_seq, '', regex=False)
    results['generation'] = results['generation'].str.replace('\s+$', '',
                                                              regex=True)  # delete white characters at the end of string

    mask = (results['generation'].str[-1] != '.') & (results['generation'].str[-1] != '!') \
           & (results['generation'].str[-1] != '?') & (results['generation'].str[-1] != '"')
    results.loc[mask, 'generation'] += '.'  # ensure there is a dot at the end of the sentence
    return results


def print_result(result, parameters, keys_used, max_words=1500):
    starting_string = ''
    break_used = False
    for param, key in zip(parameters, keys_used[:-1]):
        starting_string += f'{key.title()}: '
        if param:
            starting_string += param
        else:
            break_used = True
            break

        starting_string = add_newline_at_the_end(starting_string)

    if not break_used:
        starting_string += f'{keys_used[-1].title()}:'

    for i, row in result.iterrows():
        print('-' * 50)
        print('likelihood:', row['likelihood'])

        text = starting_string + row["generation"]
        if len(text.split(' ')) > max_words:
            print('Text too long')
            continue
        print(text)


def choose_best_result(results):
    return results.loc[((results['generation'].str.split('.').str.len() - 5).abs()).idxmin(), 'generation']


def generate_segment(example_stories, keys_to_use, header, parameters, story_generator=None, check_n_tokens=True):
    prompt_gen = PromptGenerator(stories=example_stories, keys_to_use=keys_to_use, header=header,
                                 parameters=parameters, stop_token=story_params["STOP_SEQUENCES"][0])
    prompt = prompt_gen.generate_prompt_for_story(check_n_tokens=check_n_tokens)

    if story_generator is None:
        story_generator = StoryTextGenerator(
            prompt=None, model=init_params["MODEL"], max_tokens=init_params["MAX_TOKENS"],
            stop_sequences=init_params["STOP_SEQUENCES"], temperature=init_params["TEMPERATURE"],
            min_p=init_params["MIN_P"], frequency_penalty=init_params["FREQ_PENALTY"],
            presence_penalty=init_params["PRESENCE_PENALTY"],
            disallowed_tokens=DISALLOWED_TOKENS.values())

    # Generate in a loop in order to always have at least one viable generated output
    results = []
    try_number = 1
    while len(results) == 0:
        if try_number > 1:
            print('Try:', try_number)

        # generating
        results = story_generator.generate(prompt=prompt, num_generations=5)
        try_number += 1

        # filtering
        results = hard_filter_results(results, story_params["STOP_SEQUENCES"][0], story_params["DISALLOWED_STRINGS"])

    # postprocessing resutls
    results = postprocess_results(results, story_params["STOP_SEQUENCES"][0])

    # choosing best results
    result = choose_best_result(results)

    return result, prompt, results
