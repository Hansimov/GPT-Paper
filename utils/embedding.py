import json
import openai
import os
import requests
from pathlib import Path


def init_os_envs(apis=[], set_proxy=True):
    with open(Path(__file__).parents[1] / "secrets.json", "r") as rf:
        secrets = json.load(rf)

    if type(apis) == str:
        apis = [apis]
    apis = [api.lower() for api in apis]

    if set_proxy:
        for proxy_env in ["http_proxy", "https_proxy"]:
            os.environ[proxy_env] = secrets["http_proxy"]

    if "openai" in apis:
        os.environ["OPENAI_API_KEY"] = secrets["openai_api_key"]


def get_embedding(text):
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
        proxies={
            "http": "http://localhost:11111",
            "https": "http://localhost:11111",
        },
        json={
            "input": text,
            "model": "text-embedding-ada-002",
        },
    )

    return response.json()["data"]


if __name__ == "__main__":
    init_os_envs(apis=["openai"])
    print(get_embedding("hello world"))
