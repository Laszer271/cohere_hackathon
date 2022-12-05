import os
import dotenv
import cohere
from stability_sdk import client


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
