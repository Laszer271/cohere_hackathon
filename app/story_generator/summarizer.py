from app.config import COHERE_CLIENT as co


class StorySummarizer:
    def __init__(self, story, max_tokens=None):
        self.story = story
        if max_tokens is None:
            self.max_tokens = 300
        else:
            self.max_tokens = max_tokens
        self.stop_sequences = ["--"]

    def summarize(self, focus_on='main characters'):
        prompt = f'''
        Exercise: Summarize part of the story in one sentence focusing on {focus_on}.
        Story: Once upon a time, a king ruled over a distant land. He lived with his daughter, the princess and her stepmother, the queen. The little princess was called Snow White. Her stepmother owned a magic mirror, and everyday she would daily ask, Mirror on the wall, who’s the fairest of them all? And every time she asked, the mirror would give the same answer, “Thou, O Queen, art the fairest of all.”  This made the queen very happy because she knew that her magical mirror does not lie. One morning when the queen asked, she was shocked when it answered: “You, my queen, are fair; it is true. But Snow White is even fairer than you” The Queen became jealous. She  ordered her huntsman to hurt Snow White but The poor huntsman was unable to hurt the girl. The huntsman took her to the great forest instead and let her go. He told her to run away and never return.  
        TLDR: Snow White's evil stepmother wanted to be the fairest in the land and was jealous of Snow White's beauty so the stepmother ordered a huntsman to kill Snow White, but the huntsman spared her life. 
        {self.stop_sequences[0]}
        Exercise: Summarize part of the story in one sentences focusing on {focus_on}.
        Story:She ran as far as her feet could carry her until she saw a little house and went inside in order to rest. Later, Snow White lay down on one of the little beds and fell fast asleep. That night, the owners of the house returned home. They were the seven dwarves. The next morning Snow White woke up, and when she saw the seven dwarves she was frightened.  But they were friendly. “How did you find your way to our house?” the dwarves asked. Then she told them that her stepmother had tried to hurt her butt the huntsman told her to run away and that she had run through the forest, finally stumbling upon their house. The dwarves said, “If you will keep the house for us, and cook, make beds, wash, sew, and knit, and keep everything clean and orderly, then you can stay with us, and you shall have everything that you want.” “Yes,” said Snow White, “with all my heart.”  Snow White greatly enjoyed keeping a tidy home. The dwarves were her new family.
        TLDR: Snow White came upon a cottage that belonged to seven dwarfs, who let her stay. 
        {self.stop_sequences[0]}
        Exercise: Summarize part of the story in one sentence focusing on {focus_on}.
        Story: {self.story}
        TLDR:'''

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
        if len(summary) != 0 and summary[-1] not in ['.', '!', '?']:
            summary = '.'.join(summary.split('.')[:-1]) + '.'
        return summary
