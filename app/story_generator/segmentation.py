class StoryDivider:
    def __init__(self, story_id, story_text):
        self.story_id = story_id
        self.story_text = story_text
        self.story_segments = []

    def divide_story_into_segments(self, *, n_pages=None, sentences_per_page=3):
        if n_pages is None:
            n_sentences = len(self.story_text.split('.'))
            n_pages = n_sentences // sentences_per_page
        story_segments = []
        for i in range(n_pages):
            story_segment = self.story_text.split('.')[i * sentences_per_page:(i + 1) * sentences_per_page]
            story_segment = '.'.join(story_segment)
            story_segments.append(story_segment)
            if i == n_pages - 1:
                if len(story_segment.split('.')) < sentences_per_page:
                    story_segment = self.story_text.split('.')[(i + 1) * sentences_per_page:]
                    story_segment = '.'.join(story_segment)
                    story_segments.append(story_segment)
        self.story_segments = story_segments
        return story_segments

    def get_story_segments(self):
        return self.story_segments