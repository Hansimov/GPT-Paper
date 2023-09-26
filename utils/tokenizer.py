import os
import requests
import tiktoken
import torch
from nltk.tokenize import sent_tokenize
from utils.envs import enver
from utils.logger import logger, Runtimer
from sentence_transformers import SentenceTransformer, CrossEncoder
from sentence_transformers import util as st_util
from termcolor import colored
from utils.envs import enver


def df_column_to_torch_tensor(df_column):
    torch_tensor = torch.stack([torch.Tensor(i) for i in df_column])
    return torch_tensor


def remove_newline_seps_from_text(text):
    chars_map = {
        "-\n": "",
        "\n": " ",
        "\f": "",
    }
    for k, v in chars_map.items():
        text = text.replace(k, v)
    return text


class WordTokenizer:
    """
    * How to count tokens with tiktoken · openai-cookbook
        * https://github.com/openai/openai-cookbook/blob/main/examples/
          How_to_count_tokens_with_tiktoken.ipynb


    Encoding name	    | OpenAI models
    :-------------------|:-------------------------------------------------
    cl100k_base	        | gpt-4, gpt-3.5-turbo, text-embedding-ada-002
    p50k_base	        | Codex models, text-davinci-002, text-davinci-003
    r50k_base (or gpt2)	| GPT-3 models like davinci
    -----------------------------------------------------------------------
    """

    def __init__(self, model="text-embedding-ada-002"):
        self.model = model
        self.encoding_name = None
        self.get_encoder_by_model()

    def get_encoder_by_model(self):
        self.encoding_model_map = {
            "cl100k_base": ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"],
            "p50k_base": ["Codex models", "text-davinci-002", "text-davinci-003"],
        }

        enver.set_envs(set_proxy=True)
        os.environ = enver.envs
        for encoding, models in self.encoding_model_map.items():
            if self.model in models:
                self.encoding_name = encoding
                self.encoder = tiktoken.get_encoding(self.encoding_name)
                break
        enver.restore_envs()
        os.environ = enver.envs

        if not self.encoding_name:
            raise ValueError(f"No valid encoding for model: {self.model}")

    def count_tokens(self, text):
        self.tokens = self.encoder.encode(text)
        self.token_cnt = len(self.tokens)
        logger.debug(f"{self.token_cnt} tokens of text: [{text}]")
        return self.token_cnt


class SentenceTokenizer:
    def text_to_sentences(self, text):
        text = remove_newline_seps_from_text(text)
        sentences = sent_tokenize(text)
        return sentences


def get_embedding_with_api(
    text,
    endpoint="openai",
    model="text-embedding-ada-002",
):
    enver.set_envs(set_proxy=True, openai=True)
    os.environ = enver.envs

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

    enver.restore_envs()
    os.environ = enver.envs

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


class BiEncoderX:
    def __init__(self, model_name=None):
        if model_name:
            self.model_name = model_name
        else:
            # self.model_name = "all-MiniLM-L6-v2"
            # self.model_name = (
            #     "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            # )
            # self.model_name = "moka-ai/m3e-base"
            # self.model_name = "BAAI/bge-large-en"
            # self.model_name = "multi-qa-MiniLM-L6-cos-v1"
            self.model_name = "msmarco-bert-base-dot-v5"
        self.is_load_model = False

    def load_model(self, quiet=True):
        logger.enter_quiet(quiet)
        logger.note(f"> Using embedding model: [{self.model_name}]")
        enver.set_envs(set_proxy=True, cuda_device=True, huggingface=True)
        os.environ = enver.envs
        self.model = SentenceTransformer(self.model_name)
        enver.restore_envs()
        os.environ = enver.envs
        self.is_load_model = True
        logger.exit_quiet(quiet)

    def calc_embedding(self, text, normalize_embeddings=True):
        text = remove_newline_seps_from_text(text)
        embeddings = self.model.encode(text, normalize_embeddings=normalize_embeddings)
        return embeddings

    def test_paraphrase_mining(self):
        sentences = [
            "你好",
            "我很好",
            "今天天气怎么样",
            "今晚的晚饭真好吃",
            "猫咪坐在外面",
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
            logger.indent(2)
            logger.line(f"1. {sentences[i]}\n2. {sentences[j]}")
            logger.indent(-2)


class CrossEncoderX:
    """
    MS MARCO Cross-Encoders — Sentence-Transformers documentation
    * https://www.sbert.net/docs/pretrained-models/ce-msmarco.html
    """

    def __init__(self, model_name=None):
        if model_name:
            self.model_name = model_name
        else:
            # self.model_name = "cross-encoder/ms-marco-TinyBERT-L-2-v2"
            # self.model_name = "cross-encoder/ms-marco-MiniLM-L-2-v2"
            self.model_name = "cross-encoder/ms-marco-MiniLM-L-4-v2"
            # self.model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
            # self.model_name = "cross-encoder/ms-marco-MiniLM-L-12-v2"
        self.is_load_model = False

    def load_model(self, quiet=True):
        logger.enter_quiet(quiet)
        logger.note(f"> Using CrossEncoder model: [{self.model_name}]")
        enver.set_envs(set_proxy=True, cuda_device=True, huggingface=True)
        os.environ = enver.envs
        self.model = CrossEncoder(self.model_name)
        enver.restore_envs()
        os.environ = enver.envs
        self.is_load_model = True
        logger.exit_quiet(quiet)

    def predict(self, cross_inp):
        cross_scores = self.model.predict(cross_inp)
        return cross_scores


if __name__ == "__main__":
    with Runtimer():
        word_tokenizer = WordTokenizer()
        word_tokenizer.count_tokens("你好吗？我的朋友。")
        # get_embedding_with_api("hello world!")
        # embedder = Embedder()
        # embedder.test_paraphrase_mining()
