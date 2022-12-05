import cohere as co
from app.config import COHERE_CLIENT as co
from app.config import COHERE_ERROR
import pandas as pd
import time


class StoryGenerator:
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
        self.disallowed_tokens = {token: -10 for token in disallowed_tokens}

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
        df = pd.DataFrame({'generation': gens, 'likelihood': likelihoods})
        df = df.drop_duplicates(subset=['generation'])
        df = df.sort_values('likelihood', ascending=False, ignore_index=True)
        return df


class PromptGenerator:
    def __init__(self, *, stories: list = None, keys_to_use: list = None, header: str = '', parameters: list = None,
                 stop_token: str = '--', max_tokens: int = 2048):
        self.stories = stories
        self.keys_to_use = keys_to_use
        self.header = header
        self.parameters = parameters
        if self.parameters is None:
            self.parameters = []

        self.stop_token = stop_token
        self.max_tokens = max_tokens

    def generate_prompt_for_story(self, stories: list = None, keys_to_use: list = None,
                                  header: str = None, parameters: list = None, check_n_tokens: bool = True):
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

        assert len(parameters) <= len(keys_to_use) - 1, f'Number of parameters should be equal or less to number of keys_to_use-1.\nGot {len(parameters)} parameters and {len(keys_to_use)} keys instead'

        if header:
            prompt = add_newline_at_the_end(header) + '\n'
        else:
            prompt = ''

        avg_story_length = 0
        for i, story in enumerate(stories):
            avg_story_length += len(story[keys_to_use[-1]])
            for key in keys_to_use:
                prompt += f'{key.title()}: {story[key]}'
                prompt = add_newline_at_the_end(prompt)
            prompt += add_newline_at_the_end(self.stop_token)
        avg_story_length = avg_story_length // len(stories)

        for key, param in zip(keys_to_use[: len(parameters)], parameters):
            prompt += f'{key.title()}: '
            if not param:
                break
            else:
                prompt += add_newline_at_the_end(param)

        if len(parameters) == 0 or param:
            prompt += f'{keys_to_use[len(parameters)].title()}: '

        estimated_tokens_number = len(prompt.split(' ')) + avg_story_length
        estimated_tokens_number *= 2  # let's assume word is on averate 2 tokens

        if check_n_tokens:
            assert estimated_tokens_number < self.max_tokens,\
                f'Estimated number of tokens was {estimated_tokens_number} which is more than specified max number of tokens ({self.max_tokens})'

        return prompt

    # def generate_prompt_for_story_start(self, story_title=None):
    #     prompt = add_newline_at_the_end(self.header)
    #
    #     for i, ex in enumerate(self.examples):
    #         if self.titles is not None:
    #             prompt += 'Title: ' + add_newline_at_the_end(self.titles[i])
    #         prompt += self.pre_example_string
    #         prompt += add_newline_at_the_end(ex)
    #         prompt += add_newline_at_the_end(self.stop_token)
    #
    #     if self.titles is not None:
    #         prompt += 'Title: '
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
