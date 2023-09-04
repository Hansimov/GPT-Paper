import json
import pandas as pd
from collections import defaultdict
from pathlib import Path
from sentence_transformers.util import semantic_search
from termcolor import colored

from utils.calculator import get_int_digits
from utils.envs import init_os_envs
from utils.file import rmtree_and_mkdir
from utils.layout_analyzer import draw_regions_on_page
from utils.logger import logger, add_fillers, Runtimer
from utils.tokenizer import (
    SentenceTokenizer,
    BiEncoderX,
    CrossEncoderX,
    df_column_to_torch_tensor,
)

init_os_envs(cuda_device=0, huggingface=True)


def query_embeddings_df(query, df, retrieve_n=100, rerank_n=10, exclude_things=[]):
    def drop_exclude_things(row):
        return row["thing"] in exclude_things

    drop_mask = df.apply(drop_exclude_things, axis=1)
    df = df[~drop_mask]

    doc_embeddings_tensors = df_column_to_torch_tensor(df["embedding"])
    df_doc_texts = df["text"].values.tolist()
    df_pdf_names = df["pdf_name"].values.tolist()
    df_page_idxs = df["page_idx"].values.tolist()
    df_region_idxs = df["region_idx"].values.tolist()
    df_region_things = df["thing"].values.tolist()
    levels = df["level"].values.tolist()

    bi_encoder = BiEncoderX()
    bi_encoder.load_model()
    query_embedding_tensor = bi_encoder.model.encode(query, convert_to_tensor=True)

    # Retrieve
    retrieve_n = min(100, len(df_doc_texts))
    retrieve_results = semantic_search(
        query_embeddings=query_embedding_tensor,
        corpus_embeddings=doc_embeddings_tensors,
        top_k=retrieve_n,
    )[0]

    query_log = f"Query: {colored(query,'light_cyan')}"
    retrieve_statistics_str = (
        f"Top {retrieve_n} Retrieved in {len(df_doc_texts)} chunks:"
    )
    logger.note(query_log)
    logger.line(retrieve_statistics_str)

    logger.store_indent()
    logger.indent(2)
    for item_idx, item in enumerate(retrieve_results):
        score = item["score"]
        chunk_idx = item["corpus_id"]
        page_idx = df_page_idxs[chunk_idx]
        region_idx = df_region_idxs[chunk_idx]
        # logger.line(
        #     f"{item_idx+1}: ({score:.4f}) [Page {page_idx}, Region {region_idx}]\n"
        #     + f"{colored(df_doc_texts[chunk_idx],'light_green')}"
        # )
    logger.restore_indent()

    # Re-ranking
    cross_encoder = CrossEncoderX()
    cross_encoder.load_model()
    cross_encoder_model = cross_encoder.model
    cross_inp = [
        [query, df_doc_texts[retrieve_result["corpus_id"]]]
        for retrieve_result in retrieve_results
    ]
    cross_scores = cross_encoder_model.predict(cross_inp)
    for idx in range(len(cross_scores)):
        retrieve_results[idx]["cross_score"] = cross_scores[idx]
    rerank_results = sorted(
        retrieve_results, key=lambda x: x["cross_score"], reverse=True
    )

    sentence_tokenizer = SentenceTokenizer()
    logger.note(query_log)
    rerank_statistics_str = f"Top {rerank_n} Re-ranked in {len(df_doc_texts)} chunks"
    logger.line(rerank_statistics_str)

    rerank_results = rerank_results[:rerank_n]
    for item_idx, item in enumerate(rerank_results):
        score = item["cross_score"]
        chunk_idx = item["corpus_id"]
        page_idx = df_page_idxs[chunk_idx]
        region_idx = df_region_idxs[chunk_idx]
        region_thing = df_region_things[chunk_idx]
        chunk_level = levels[chunk_idx]
        chunk_text = df_doc_texts[chunk_idx]
        chunk_pdf_name = df_pdf_names[chunk_idx]
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

    return
    # Dump to query results page json
    query_results_page_region_idxs = defaultdict(list)
    for item_idx, item in enumerate(top_results[:10]):
        chunk_idx = item["corpus_id"]
        page_idx = df_page_idxs[chunk_idx]
        region_idx = df_region_idxs[chunk_idx]
        rank = item_idx + 1
        query_results_page_region_idxs[page_idx].append((region_idx, rank))
    query_results_page_region_idxs = {
        k: sorted(v, key=lambda x: x[0])
        for k, v in sorted(query_results_page_region_idxs.items())
    }
    query_results_path = self.queries_results_path / f"{query[:100]}"
    rmtree_and_mkdir(query_results_path)
    page_idx_digits = get_int_digits(len(self.pdf_doc))
    for page_idx, region_idxs_and_ranks in query_results_page_region_idxs.items():
        page_info_json_name = f"page_{page_idx:0>{page_idx_digits}}.json"
        query_results_page_info_json_path = query_results_path / page_info_json_name
        ordered_page_info_path = self.ordered_page_images_path / page_info_json_name
        with open(ordered_page_info_path, "r") as rf:
            page_infos = json.load(rf)

        query_results_page_infos = page_infos.copy()
        query_results_page_infos["page"]["current_image_path"] = str(
            query_results_path / Path(page_infos["page"]["original_image_path"]).name
        )
        query_results_page_infos["page"]["regions_num"] = len(region_idxs_and_ranks)
        query_results_page_infos["regions"] = []
        for item_idx, region_idx_and_rank in enumerate(region_idxs_and_ranks):
            region_idx, rank = region_idx_and_rank
            query_results_page_infos["regions"].append(
                page_infos["regions"][region_idx - 1]
            )
            query_results_page_infos["regions"][item_idx]["score"] = rank
        logger.store_indent()
        logger.indent(2)
        logger.success("> Dump query results page info json")
        logger.file(f"- {query_results_page_info_json_path}")
        with open(query_results_page_info_json_path, "w") as wf:
            json.dump(query_results_page_infos, wf, indent=4)
        draw_regions_on_page(
            query_results_page_info_json_path,
            query_results_path,
            show_region_idx=False,
            score_use_percent=False,
        )
        logger.restore_indent()
