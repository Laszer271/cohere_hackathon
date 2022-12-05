import cohere as co
from app.config import COHERE_CLIENT as co
from app.config import COHERE_ERROR, init_params, DISALLOWED_TOKENS, story_params
import pandas as pd
import time

import json

import numpy as np

# from app.story_generator.generation import PromptGenerator, StoryTextGenerator, add_newline_at_the_end
from app.story_generator.segmentation import StoryDivider
from app.config import init_params, DISALLOWED_TOKENS, story_params


def get_n_stories(n=3):
    import os
    stories_path = os.path.join(os.path.abspath(''), #os.pardir,
                                "data", "stories", "fairy_tales.json")
    with open(stories_path, "rb") as f:
        stories = json.load(f)
        assert n <= len(stories), f'Tried to get {n} stories while is only {len(stories)} stories in the database'
        example_stories = list(np.random.choice(stories, size=n, replace=False))

    return example_stories


def get_segment_of_stories(stories:list, segment_idx:int, handle_too_big_index=True,
                           n_pages=None, sentences_per_page=3):
    segmented_stories = []
    for s in stories:
        seg = StoryDivider(s["title"], s["text"])
        segmented = seg.divide_story_into_segments(n_pages=n_pages, sentences_per_page=sentences_per_page)
        if handle_too_big_index and segment_idx >= len(segmented):
            index = len(segmented) - 1

        result = s.copy()

        text = segmented[segment_idx]
        result.update({'text':text})
        segmented_stories.append(result)

    return segmented_stories


def get_segments_and_continuations(stories:list, n_pages=None, sentences_per_page=3):
    segmented_stories = []
    for s in stories:
        seg = StoryDivider(s["title"], s["text"])
        segmented = seg.divide_story_into_segments(n_pages=n_pages, sentences_per_page=sentences_per_page)

        segment_idx = np.random.randint(0, len(segmented) - 2)

        result = s.copy()
        prev_text = segmented[segment_idx]
        cont_text = segmented[segment_idx + 1]
        result.update({'Previous Part':prev_text, 'Continuation':cont_text})
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
    results['generation'] = results['generation'].str.replace('^\s+|\s+$', '',
                                                              regex=True)  # delete white characters at the end of string

    mask = (results['generation'].str[-1] != '.') & (results['generation'].str[-1] != '!') \
           & (results['generation'].str[-1] != '?') & (results['generation'].str[-1] != '"')
    results.loc[mask, 'generation'] += '.'  # ensure there is a dot at the end of the sentence
    return results


def print_result(result, parameters, keys_used, max_words=1500):
    starting_string = ''
    break_used = False
    for param, key in zip(parameters, keys_used[:-1]):
        starting_string += f'{key.title()}:'
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
                                 parameters=parameters, stop_token=init_params["STOP_SEQUENCES"][0])
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
        results = hard_filter_results(results, init_params["STOP_SEQUENCES"][0], story_params["DISALLOWED_STRINGS"])

    # postprocessing resutls
    results = postprocess_results(results, init_params["STOP_SEQUENCES"][0])

    # choosing best results
    result = choose_best_result(results)

    return result, prompt, results


class StoryGenerator:
    def __init__(self, n_pages, title, stories):
        self.n_pages = n_pages
        self.beginning = None
        self.summary = None
        self.title = title
        self.example_stories = stories
        self.continuations = []
        self.story_gen = None
        self.create_story_generator()

    def create_story_generator(self):
        gen = StoryTextGenerator(
            model=init_params["MODEL"], max_tokens=init_params["MAX_TOKENS"],
            stop_sequences=init_params["STOP_SEQUENCES"], temperature=init_params["TEMPERATURE"],
            min_p=init_params["MIN_P"], frequency_penalty=init_params["FREQ_PENALTY"],
            presence_penalty=init_params["PRESENCE_PENALTY"],
            disallowed_tokens=DISALLOWED_TOKENS.values())
        self.story_gen = gen

    def generate_story_description(self):
        if self.title:
            parameters = [self.title]
        else:
            parameters = []

        summary, summary_prompt, summary_results = generate_segment(self.example_stories,
                                                                    story_params["KEYS_TO_USE_FOR_SUMMARY"],
                                                                    story_params["SUMM_GEN_HEADER"],
                                                                    parameters, story_generator=self.story_gen)
        self.summary = summary
        return summary

    def generate_story_beginning(self):
        if self.title:
            parameters = [self.title, self.summary]
        else:
            parameters = [self.summary]

        story_beginnings = get_segment_of_stories(self.example_stories, 0)
        header = story_params["BEG_GEN_HEADER"].format(len(story_beginnings) + 1)

        beginning, beg_prompt, beg_results = generate_segment(story_beginnings,
                                                              story_params["KEYS_TO_USE_FOR_BEGINNING"], header,
                                                              parameters, story_generator=self.story_gen)
        self.beginning = beginning
        return beginning

    def generate_story_continuation(self):
        continuations_to_generate = self.n_pages - 2

        if len(self.continuations) == 0:
            prev_part = self.beginning
        else:
            prev_part = self.continuations[-1]

        if self.title:
            parameters = [self.title, self.summary, self.beginning]
        else:
            parameters = [self.summary, self.beginning]


        example_continuations = get_segments_and_continuations(self.example_stories)
        while True:
            header = story_params["CONT_GEN_HEADER"].format(len(example_continuations) + 1)
            try:
                continuation, cont_prompt, cont_results = generate_segment(example_continuations,
                                                                           story_params[
                                                                               "KEYS_TO_USE_FOR_CONTINUATION"],
                                                                           header,
                                                                           parameters,
                                                                           story_generator=self.story_gen)
            except AssertionError:
                example_continuations = example_continuations[:-1]
                continue
            break  # break if there was no error

        self.continuations.append(continuation)
        return continuation

    def generate_story_ending(self):
        if self.title:
            parameters = [self.title, self.summary, self.continuations[-1]]
        else:
            parameters = [self.summary, self.continuations[-1]]

        story_endings = [
            {'Previous Part':story_bef_end.pop('text'), 'Ending':story_end['text'], **story_bef_end} \
            for story_bef_end, story_end in
            zip(get_segment_of_stories(self.example_stories, -2), get_segment_of_stories(self.example_stories, -1))
        ]

        header = story_params["END_GEN_HEADER"].format(len(self.beginning) + 1)

        ending, end_prompt, end_results = generate_segment(story_endings, story_params["KEYS_TO_USE_FOR_ENDING"],
                                                           header, parameters,
                                                           story_generator=self.story_gen, check_n_tokens=False)
        self.ending = ending
        return ending

    def print_story(self):
        story = f'''
        Title:{self.title}
        Summary:{self.summary}

        Story:

        {self.beginning + ''.join(self.continuations) + self.ending}
        '''
        print(story)


class StoryTextGenerator:
    def __init__(self, prompt='', model='xlarge', max_tokens=1800, stop_sequences=None, disallowed_tokens=None,
                 temperature=0.8, min_p=0.75, frequency_penalty=0.0, presence_penalty=0.0):
        self.model = model
        self.temperature = temperature
        self.prompt = prompt
        self.max_tokens = max_tokens
        if stop_sequences is None:
            self.stop_sequences = ['<end>']
        else:
            self.stop_sequences = stop_sequences

        self.min_p = min_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.disallowed_tokens = {token:-10 for token in disallowed_tokens}

    def generate(self, prompt=None, num_generations=2, temperature=None, max_tokens=None):
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if prompt is None:
            prompt = self.prompt

        tries_number = 1
        response_code = 0
        while response_code != 200:
            try:
                prediction = co.generate(
                    model=self.model,
                    prompt=prompt,
                    return_likelihoods='GENERATION',
                    stop_sequences=self.stop_sequences,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    num_generations=num_generations,
                    p=self.min_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    logit_bias=self.disallowed_tokens,
                )

                # Get list of generations
                gens = []
                likelihoods = []
                for gen in prediction.generations:
                    gens.append(gen.text)

                    sum_likelihood = 0
                    for t in gen.token_likelihoods:
                        sum_likelihood += t.likelihood
                    # Get sum of likelihoods
                    likelihoods.append(sum_likelihood)

            except COHERE_ERROR:
                if tries_number == 3:
                    raise RuntimeError('Could not get a response from cohere generate endpoint')
                print('There was an error with Cohere server, retrying after 10 seconds')
                time.sleep(10)
                tries_number += 1
                continue
            break

        pd.options.display.max_colwidth = 200
        df = pd.DataFrame({'generation':gens, 'likelihood':likelihoods})
        df = df.drop_duplicates(subset=['generation'])
        df = df.sort_values('likelihood', ascending=False, ignore_index=True)
        return df


class PromptGenerator:
    def __init__(self, *, stories:list = None, keys_to_use:list = None, header:str = '', parameters:list = None,
                 stop_token:str = '--', max_tokens:int = 2048):
        self.stories = stories
        self.keys_to_use = keys_to_use
        self.header = header
        self.parameters = parameters
        if self.parameters is None:
            self.parameters = []

        self.stop_token = stop_token
        self.max_tokens = max_tokens

    def generate_prompt_for_story(self, stories:list = None, keys_to_use:list = None,
                                  header:str = None, parameters:list = None, check_n_tokens:bool = True):
        if stories is None:
            stories = self.stories
        assert stories is not None
        if keys_to_use is None:
            keys_to_use = self.keys_to_use
        assert keys_to_use is not None
        if header is None:
            header = self.header
        assert header is not None
        if parameters is None:
            parameters = self.parameters
        assert parameters is not None

        assert len(parameters) <= len(
            keys_to_use) - 1, f'Number of parameters should be equal or less to number of keys_to_use-1.\nGot {len(parameters)} parameters and {len(keys_to_use)} keys instead'

        if header:
            prompt = add_newline_at_the_end(header) + '\n'
        else:
            prompt = ''

        avg_story_length = 0
        for i, story in enumerate(stories):
            avg_story_length += len(story[keys_to_use[-1]])
            for key in keys_to_use:
                prompt += f'{key.title()}:{story[key]}'
                prompt = add_newline_at_the_end(prompt)
            prompt += add_newline_at_the_end(self.stop_token)
        avg_story_length //= len(stories)

        for key, param in zip(keys_to_use[:len(parameters)], parameters):
            prompt += f'{key.title()}:'
            if not param:
                break
            else:
                prompt += add_newline_at_the_end(param)

        if len(parameters) == 0 or param:
            prompt += f'{keys_to_use[len(parameters)].title()}:'

        estimated_tokens_number = len(prompt.split(' ')) + avg_story_length
        estimated_tokens_number *= 2  # let's assume word is on averate 2 tokens

        if check_n_tokens:
            assert estimated_tokens_number < self.max_tokens, \
                f'Estimated number of tokens was {estimated_tokens_number} which is more than specified max number of tokens ({self.max_tokens})'

        return prompt

    # def generate_prompt_for_story_start(self, story_title=None):
    #     prompt = add_newline_at_the_end(self.header)
    #
    #     for i, ex in enumerate(self.examples):
    #         if self.titles is not None:
    #             prompt += 'Title:' + add_newline_at_the_end(self.titles[i])
    #         prompt += self.pre_example_string
    #         prompt += add_newline_at_the_end(ex)
    #         prompt += add_newline_at_the_end(self.stop_token)
    #
    #     if self.titles is not None:
    #         prompt += 'Title:'
    #         if story_title is not None:
    #             prompt += add_newline_at_the_end(story_title)
    #             prompt += self.pre_example_string
    #     else:
    #         prompt += self.pre_example_string
    #
    #     estimated_tokens_number = len(prompt.split(' ')) + len(ex.split(' '))
    #     estimated_tokens_number *= 2  # let's assume word is on average 2 tokens
    #     assert estimated_tokens_number < self.max_tokens, f'Estimated number' \
    #                                                       f' of tokens was {estimated_tokens_number} which is more' \
    #                                                       f' than specified max number of tokens ({self.max_tokens})'
    #
    #     return prompt


def add_newline_at_the_end(text):
    if text[-1] != '\n':
        text += '\n'
    return text
