from termcolor import colored
import logging
import os
import requests
from utils.envs import init_os_envs
from utils.logger import Logger

init_os_envs(apis=["openai"])


def calc_embedding(
    text,
    endpoint="openai",
    model="text-embedding-ada-002",
):
    """
    Response Example:

    ```json
    {
        'object': 'list',
        'data': [{
            'object': 'embedding',
            'index': 0,
            'embedding': [...]
        }],
        'model': 'text-embedding-ada-002-v2',
        'usage': {
            'prompt_tokens': 5,
            'total_tokens': 5
        }
    }
    ```
    """
    logger = Logger().logger

    endpoint_url_map = {
        "openai": "https://api.openai.com/v1/embeddings",
    }

    if endpoint in endpoint_url_map:
        endpoint_url = endpoint_url_map[endpoint]
    else:
        endpoint_url = endpoint

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    }

    logger.info(
        f"{colored('Calculate embedding of:','light_magenta')}\n"
        f"{colored(text,'light_cyan')}"
    )

    response = requests.post(
        url=endpoint_url,
        headers=headers,
        json={
            "input": text.replace("\n", " "),
            "model": model,
        },
    )
    data = response.json()["data"]
    embedding = data[0]["embedding"]
    token_count = response.json()["usage"]["prompt_tokens"]

    logger.info(
        f"{colored('Token count: ','light_magenta')}"
        f"{colored(token_count,'light_cyan')}\n"
        f"{colored('Dimension of embedding: ','light_magenta')}"
        f"{colored(len(embedding),'light_cyan')}"
    )

    return embedding


if __name__ == "__main__":
    calc_embedding("hello world!")
