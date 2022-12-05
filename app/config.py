import os
import dotenv
import cohere
from stability_sdk import client
import re


def _get_elem(env_var):
    if isinstance(env_var, tuple):
        env_var = env_var[0]
    return env_var


project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, '.env')
dotenv.load_dotenv(dotenv_path)
COHERE_KEY = _get_elem(os.getenv('COHERE_KEY'))
STABILITY_KEY = _get_elem(os.getenv('STABILITY_KEY'))
COHERE_CLIENT = cohere.Client(COHERE_KEY)
STABILITY_API = client.StabilityInference(
    key=STABILITY_KEY,
    verbose=False)

COHERE_ERROR = cohere.CohereError

init_params = {
    "MAX_TOKENS": 150,
    "STOP_SEQUENCES": ['--'],
    "TEMPERATURE": 0.75,
    "MODEL": 'xlarge',
    "MIN_P": 0.8,
    "FREQ_PENALTY": 0.0,
    "PRESENCE_PENALTY": 1.0,
    "N_EXAMPLE_STORIES": 5}

DISALLOWED_TOKENS = {
    'https': 1099,
    ' https': 1595,
    '://': 695,
    '::': 5280,
    ' ::': 13361,
    '/': 48,
    ' /': 1040,
    'http': 2676,
    ' http': 2930,
    '#': 36,
    ' #': 1462,
    '(': 41,
    ' (': 367,
    ')': 42,
    ' )': 3479,
}
story_params = {
    "DISALLOWED_STRINGS": set([re.sub('^\s|\s$', '', key) for key in DISALLOWED_TOKENS.keys()]),
    "SUMM_GEN_HEADER": f'Assignment: Write a short summary of {init_params["N_EXAMPLE_STORIES"] + 1} stories for children based on titles given. Your stories should be in a old-school book format.',
    "KEYS_TO_USE_FOR_SUMMARY": ['title', 'summary'],
    "BEG_GEN_HEADER": 'Assignment: Write a beginning of {} stories for children based on titles and summary of the story given. Your stories should be in a old-school book format.',
    "KEYS_TO_USE_FOR_BEGINNING": ['title', 'summary', 'text'],
    "KEYS_TO_USE_FOR_CONTINUATION": ['title', 'summary', 'Previous Part', 'Continuation'],
    "CONT_GEN_HEADER": 'Assignment: Write a continuations of {} stories for children based on titles, summary and the previous part given the story given. Your stories should be in a old-school book format.',
    "KEYS_TO_USE_FOR_ENDING": ['title', 'summary', 'Previous Part', 'Ending'],
    "END_GEN_HEADER": 'Assignment: Write an ending of {} stories for children based on titles, summary and the previous part given the story given. Your stories should be in a old-school book format.',
}
