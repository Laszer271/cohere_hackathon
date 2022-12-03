import cohere

class StoryGenerator:
    def __init__(self, model, seed, length, temperature, top_p, top_k, prompt):
        self.model = model
        self.length = length
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.prompt = prompt

    def generate(self):
        # generate a story with cohere
        pass


class PromptGenerator:
    def __init__(self):
        # create a prompt with examples from dataset with other fairytales in similar category/parameters
        pass