import os
import torch
from nltk.tokenize import sent_tokenize
from utils.envs import enver
from utils.logger import logger, Runtimer

from FlagEmbedding import FlagReranker
from sentence_transformers import SentenceTransformer
from sentence_transformers import util as st_util
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class SeparatorRemover:
    def __init__(self, text):
        self.text = text
        chars_map = {
            "-\n": "",
            "\n": " ",
            "\f": "",
        }
        for k, v in chars_map.items():
            self.text = text.replace(k, v)


class EmbeddingEncoder:
    def __init__(self, model_name=None):
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = "BAAI/bge-large-en-v1.5"
            self.query_prefix = (
                "Represent this sentence for searching relevant passages: "
            )
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

    def calc_embedding(self, text, normalize_embeddings=True, query_prefix=False):
        text = SeparatorRemover(text).text
        if query_prefix:
            text = self.query_prefix + text
        embeddings = self.model.encode(text, normalize_embeddings=normalize_embeddings)
        return embeddings


class Reranker:
    def __init__(self, model_name=None):
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = "BAAI/bge-reranker-base"
        self.is_load_model = False

    def load_model(self, quiet=True):
        logger.enter_quiet(quiet)
        logger.note(f"> Using CrossEncoder model: [{self.model_name}]")
        enver.set_envs(
            set_proxy=True, cuda_device=True, huggingface=True, huggingface_offline=True
        )
        os.environ = enver.envs
        # self.model = CrossEncoder(self.model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()

        # Setting use_fp16 to True speeds up computation with a slight performance degradation
        # self.reranker = FlagReranker(self.model_name, use_fp16=True)

        enver.restore_envs()
        os.environ = enver.envs
        self.is_load_model = True
        logger.exit_quiet(quiet)

    def compute_score(self, pairs):
        # ['query', 'passage']
        # [['query1', 'passage1'], ['query2', 'passage2']]

        with torch.no_grad():
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512,
            )
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float()

        # scores = self.reranker.compute_score(pairs)
        return scores


if __name__ == "__main__":
    with Runtimer():
        # embedding_encoder = EmbeddingEncoder()
        # embedding_encoder.load_model(quiet=False)
        # text = "Hello world!"
        # embedding = embedding_encoder.calc_embedding(text)
        # print(embedding)

        reranker = Reranker()
        reranker.load_model(quiet=False)
        scores = reranker.compute_score(
            [
                [
                    "What is the capital of France?",
                    "The capital of France is Paris.",
                ],
                [
                    "What is the capital of China?",
                    "The capital of England is San Francisco.",
                ],
            ]
        )
        print(scores)
