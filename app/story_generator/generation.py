import cohere as co
from app.config import COHERE_CLIENT as co
import pandas as pd


class StoryGenerator:
    def __init__(self, prompt, model='xlarge', max_tokens=1800, stop_sequences=None, temperature=0.8):
        self.model = model
        self.temperature = temperature
        self.prompt = prompt
        self.max_tokens = max_tokens
        if stop_sequences is None:
            self.stop_sequences = ['<end>']
        else:
            self.stop_sequences = stop_sequences

    def generate(self, prompt=None, num_generations=2, temperature=None, max_tokens=None):
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if prompt is None:
            prompt = self.prompt
        prediction = co.generate(
            model=self.model,
            prompt=prompt,
            return_likelihoods='GENERATION',
            stop_sequences=self.stop_sequences,
            max_tokens=max_tokens,
            temperature=temperature,
            num_generations=num_generations)

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

        pd.options.display.max_colwidth = 200
        df = pd.DataFrame({'generation': gens, 'likelihood': likelihoods})
        df = df.drop_duplicates(subset=['generation'])
        df = df.sort_values('likelihood', ascending=False, ignore_index=True)
        return df


class PromptGenerator:
    def __init__(self, header, examples, titles=None, pre_example_string='Answer: ', stop_token='<end>',
                 max_tokens=1000):
        self.header = header
        self.examples = examples
        self.titles = titles
        self.pre_example_string = pre_example_string
        self.stop_token = stop_token
        self.max_tokens = max_tokens

    def generate_prompt_for_story_start(self, story_title=None):
        prompt = add_newline_at_the_end(self.header)

        for i, ex in enumerate(self.examples):
            if self.titles is not None:
                prompt += 'Title: ' + add_newline_at_the_end(self.titles[i])
            prompt += self.pre_example_string
            prompt += add_newline_at_the_end(ex)
            prompt += add_newline_at_the_end(self.stop_token)

        if self.titles is not None:
            prompt += 'Title: '
            if story_title is not None:
                prompt += add_newline_at_the_end(story_title)
                prompt += self.pre_example_string
        else:
            prompt += self.pre_example_string

        estimated_tokens_number = len(prompt.split(' ')) + len(ex.split(' '))
        estimated_tokens_number *= 2  # let's assume word is on average 2 tokens
        assert estimated_tokens_number < self.max_tokens, f'Estimated number' \
                                                          f' of tokens was {estimated_tokens_number} which is more' \
                                                          f' than specified max number of tokens ({self.max_tokens})'

        return prompt


def add_newline_at_the_end(text):
    if text[-1] != '\n':
        text += '\n'
    return text
