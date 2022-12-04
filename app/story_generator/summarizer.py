from app.config import COHERE_CLIENT as co


class StorySummarizer:
    def __init__(self, story, max_tokens=None):
        self.story = story
        if max_tokens is None:
            self.max_tokens = 300
        else:
            self.max_tokens = max_tokens
        self.stop_sequences = ["--"]

    def summarize(self, ):
        prompt = f"""
        Exercise: Summarize part of the story.
        Story: Is Wordle getting tougher to solve? Players seem to be convinced that the game has gotten harder in recent weeks ever since The New York Times bought it from developer Josh Wardle in late January. The Times has come forward and shared that this likely isn't the case. That said, the NYT did mess with the back end code a bit, removing some offensive and sexual language, as well as some obscure words There is a viral thread claiming that a confirmation bias was at play. One Twitter user went so far as to claim the game has gone to "the dusty section of the dictionary" to find its latest words.
        TLDR: Wordle has not gotten more difficult to solve.
        --
        Exercise: Summarize part of the story.
        Story: ArtificialIvan, a seven-year-old, London-based payment and expense management software company, has raised $190 million in Series C funding led by ARG Global, with participation from D9 Capital Group and Boulder Capital. Earlier backers also joined the round, including Hilton Group, Roxanne Capital, Paved Roads Ventures, Brook Partners, and Plato Capital.
        TLDR: ArtificialIvan has raised $190 million in Series C funding.
        --
        Exercise: Summarize part of the story.
        Story: {self.story} 
        TLDR:"""

        response = co.generate(
            model='xlarge',
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=0.8,
            stop_sequences=self.stop_sequences)

        summary = response.generations[0].text
        summary = summary.strip()
        if len(summary) < 1:
            return ""
        for stop_sequence in self.stop_sequences:
            summary = summary.replace(stop_sequence, '')
        if summary[-1] not in ['.', '!', '?']:
            summary = '.'.join(summary.split('.')[:-1]) + '.'
        return summary
