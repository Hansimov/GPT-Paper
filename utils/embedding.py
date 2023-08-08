import os
import requests
from utils.envs import init_os_envs

init_os_envs()


def calc_embedding(text):
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    }
    response = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers=headers,
        json={
            "input": text,
            "model": "text-embedding-ada-002",
        },
    )

    return response.json()["data"]


if __name__ == "__main__":
    init_os_envs(apis=["openai"])
    print(calc_embedding("hello world"))
