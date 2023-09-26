import os
import pandas as pd
import pathlib
import platform
from datetime import datetime
from pathlib import Path
from sentence_transformers.util import semantic_search
from termcolor import colored
from utils.envs import enver
from utils.logger import logger, Runtimer
from utils.tokenizer import (
    SentenceTokenizer,
    BiEncoderX,
    CrossEncoderX,
    df_column_to_torch_tensor,
)

if platform.system() == "Windows":
    pathlib.PosixPath = pathlib.WindowsPath


class EmbeddingsQuerier:
    def __init__(self, df):
        self.df = df
        self.df_values_to_list()
        self.setup_model()

    def setup_model(self):
        logger.note(f"Setup: {datetime.now()}")
        enver.set_envs(cuda_device=True, huggingface=True)
        os.environ = enver.envs

        self.df_embeddings_tensors = df_column_to_torch_tensor(self.df["embedding"])

        self.bi_encoder = BiEncoderX()
        self.bi_encoder.load_model()

        self.cross_encoder = CrossEncoderX()
        self.cross_encoder.load_model()

        enver.restore_envs()
        os.environ = enver.envs

    def df_values_to_list(self):
        logger.note(f"df_values_to_list: {datetime.now()}")
        df = self.df
        self.df_texts = df["text"].values.tolist()
        self.df_pdf_names = df["pdf_name"].values.tolist()
        self.df_page_idxs = df["page_idx"].values.tolist()
        self.df_region_idxs = df["region_idx"].values.tolist()
        self.df_things = df["thing"].values.tolist()
        self.df_levels = df["level"].values.tolist()

    def retrieve(self, query, retrieve_n=64):
        logger.note(f"retrieve: {datetime.now()}")
        self.query = query
        self.query_embedding_tensor = self.bi_encoder.model.encode(
            self.query, convert_to_tensor=True
        )
        retrieve_n = min(retrieve_n, len(self.df_texts))
        self.retrieve_results = semantic_search(
            query_embeddings=self.query_embedding_tensor,
            corpus_embeddings=self.df_embeddings_tensors,
            top_k=retrieve_n,
        )[0]

        self.query_log = f"Query: {colored(query,'light_cyan')}"
        retrieve_statistics_str = (
            f"Top {retrieve_n} Retrieved in {len(self.df_texts)} chunks:"
        )
        logger.note(self.query_log)
        logger.line(retrieve_statistics_str)
        logger.store_indent()
        logger.indent(2)
        for item_idx, item in enumerate(self.retrieve_results):
            score = item["score"]
            chunk_idx = item["corpus_id"]
            page_idx = self.df_page_idxs[chunk_idx]
            region_idx = self.df_region_idxs[chunk_idx]
        logger.restore_indent()

    def rerank(self, rerank_n=20):
        logger.note(f"rerank: {datetime.now()}")
        logger.enter_quiet(False)
        cross_inp = [
            [self.query, self.df_texts[retrieve_result["corpus_id"]]]
            for retrieve_result in self.retrieve_results
        ]
        cross_scores = self.cross_encoder.predict(cross_inp)
        for idx in range(len(cross_scores)):
            self.retrieve_results[idx]["cross_score"] = cross_scores[idx]
        rerank_results = sorted(
            self.retrieve_results, key=lambda x: x["cross_score"], reverse=True
        )

        rerank_statistics_str = (
            f"Top {rerank_n} Re-ranked in {len(self.df_texts)} chunks"
        )
        logger.line(rerank_statistics_str)

        rerank_results = rerank_results[:rerank_n]
        rerank_results_df_scores_and_idxs = []
        sentence_tokenizer = SentenceTokenizer()
        for item_idx, item in enumerate(rerank_results):
            score = item["cross_score"]
            chunk_idx = item["corpus_id"]
            rerank_results_df_scores_and_idxs.append((chunk_idx, score))
            page_idx = self.df_page_idxs[chunk_idx]
            region_idx = self.df_region_idxs[chunk_idx]
            region_thing = self.df_things[chunk_idx]
            chunk_level = self.df_levels[chunk_idx]
            chunk_text = self.df_texts[chunk_idx]
            chunk_pdf_name = self.df_pdf_names[chunk_idx]
            sentences = sentence_tokenizer.text_to_sentences(chunk_text)
            sentences_str = "\n".join(sentences)
            logger.store_indent()
            logger.indent(2)
            logger.line(
                f"{item_idx+1}: ({score:.4f}) [Page {page_idx}, {region_thing.capitalize()} Region {region_idx}, Level {chunk_level}]"
            )
            logger.file(f"- {chunk_pdf_name}")
            logger.indent(2)
            logger.success(sentences_str)
            logger.restore_indent()

        logger.exit_quiet()

        return rerank_results_df_scores_and_idxs

    def search(self, query, retrieve_n=64, rerank_n=20):
        self.retrieve(query, retrieve_n=retrieve_n)
        rerank_results_df_scores_and_idxs = self.rerank(rerank_n=rerank_n)
        return rerank_results_df_scores_and_idxs


if __name__ == "__main__":
    with Runtimer():
        docs_embeddings_pickle = (
            Path(__file__).parents[1]
            / "pdfs"
            / "cancer_review"
            / "_results"
            / "docs_embeddings.pkl"
        )
        embeddings_df = pd.read_pickle(docs_embeddings_pickle)
        embeddings_querier = EmbeddingsQuerier(embeddings_df)

        query = "Textual explanation"
        embeddings_querier.search(query, retrieve_n=64, rerank_n=20)
        query = "Example-based explanation"
        embeddings_querier.search(query, retrieve_n=64, rerank_n=20)
