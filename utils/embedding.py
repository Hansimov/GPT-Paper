from termcolor import colored
import logging
import os
import requests
from utils.envs import init_os_envs
from utils.logger import logger, Runtimer
from sentence_transformers import SentenceTransformer
from sentence_transformers import util as st_util


def get_embedding_with_api(
    text,
    endpoint="openai",
    model="text-embedding-ada-002",
):
    init_os_envs(apis=["openai"])

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


class Embedder:
    def __init__(self, model_name=None):
        init_os_envs(cuda_device=3)
        if model_name:
            self.model_name = model_name
        else:
            # self.model_name = "all-MiniLM-L6-v2"
            self.model_name = (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

    def load_model(self):
        self.model = SentenceTransformer(self.model_name)

    def test_paraphrase_mining(self):
        self.load_model()
        sentences = [
            "你好",
            "我很好",
            "今天天气怎么样",
            "今晚的晚饭真好吃",
            "The cat sits outside",
            "A man is playing guitar",
            "I love pasta",
            "Hello",
            "Today's weather is so good!",
            "what about Today's weather",
            "How about today evening's dinner?",
            "The new movie is awesome",
            "The cat plays in the garden",
            "A woman watches TV",
            "The new movie is so great",
            "Do you like pizza?",
        ]
        paraphrases = st_util.paraphrase_mining(self.model, sentences)
        for paraphrase in paraphrases[0:10]:
            score, i, j = paraphrase
            logger.mesg(f"Score: {score:.4f}")
            logger.line(f"{sentences[i]}\n{sentences[j]}")


if __name__ == "__main__":
    with Runtimer():
        # get_embedding_with_api("hello world!")
        embedder = Embedder()
        embedder.test_run()
