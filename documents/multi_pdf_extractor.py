from utils.file import rmtree_and_mkdir
from documents.pdf_visual_extractor import PDFVisualExtractor
from functools import reduce
from tqdm import tqdm
from typing import Union
from utils.logger import logger, Runtimer
from utils.calculator import get_int_digits
from utils.layout_analyzer import DITLayoutAnalyzer
from utils.tokenizer import BiEncoderX, CrossEncoderX, SentenceTokenizer

from documents.embeddings_querier import EmbeddingsQuerier
import pandas as pd
import operator
import pathlib
from pathlib import Path
import pickle
import platform

if platform.system() == "Windows":
    pathlib.PosixPath = pathlib.WindowsPath


class MultiPDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self, project_dir):
        self.project_path = self.pdf_root / project_dir
        self.result_root = self.project_path / "_results"
        self.pdf_paths = sorted(list(self.project_path.glob("*.pdf")))
        self.pdfs_count = len(self.pdf_paths)
        self.pdfs_count_digits = get_int_digits(len(self.pdf_paths))
        self.docs_embeddings_path = self.result_root / "docs_embeddings.pkl"
        self.queries_cache_path = self.result_root / "queries_cache.pkl"

    def list_pdfs(self):
        logger.mesg(f"[{self.project_path}] has {self.pdfs_count} PDFs:")
        for idx, pdf_path in enumerate(self.pdf_paths):
            logger.file(f"{idx+1:>{self.pdfs_count_digits}}. {pdf_path.name}", indent=2)

    def extract_pdfs(self):
        # layout_analyzer = DITLayoutAnalyzer(size="large")
        # layout_analyzer.setup_model(quiet=False)

        # bi_encoder = BiEncoderX()
        # bi_encoder.load_model()

        for pdf_idx, pdf_path in enumerate(tqdm(self.pdf_paths[:], colour="green")):
            logger.store_level()
            logger.note(
                f"[{pdf_idx+1:>{self.pdfs_count_digits}}/{self.pdfs_count}] {pdf_path.name}"
            )
            logger.store_indent()
            logger.indent(2)
            extractor = PDFVisualExtractor(pdf_path)
            logger.mesg("> Dump page images")
            extractor.dump_pdf_to_page_images()
            logger.mesg("> Annotate page images")
            extractor.annotate_page_images(layout_analyzer=None)
            logger.mesg("> Remove overlaps, order regions, and crop")
            extractor.remove_overlapped_layout_regions_from_pages()
            extractor.order_pages_regions()
            extractor.crop_page_images("ordered")
            logger.mesg("> Extract texts, and combine to doc")
            extractor.extract_texts_from_pages()
            extractor.combine_page_texts_to_doc()
            logger.mesg("> Text to embeddings")
            extractor.doc_texts_to_embeddings(bi_encoder=None)
            logger.restore_indent()
            # extractor.query_region_texts()
            logger.restore_level()

    def combine_docs_embeddings(self, overwrite=False):
        if not overwrite and self.docs_embeddings_path.exists():
            return
        rmtree_and_mkdir(self.result_root)

        df = pd.DataFrame()
        for idx, pdf_path in enumerate(self.pdf_paths):
            embedding_path = pdf_path.with_suffix("") / "texts" / "embeddings.pkl"
            doc_df = pd.read_pickle(embedding_path)
            # self.docs_embeddings_df = self.docs_embeddings_df.append(df)
            df = pd.concat([df, doc_df], ignore_index=True)

        self.docs_embeddings_df = df
        print(self.docs_embeddings_df)
        logger.note(f"> Dump embeddings of {self.pdfs_count} PDFs")
        logger.file(f"- {self.docs_embeddings_path}", indent=2)
        self.docs_embeddings_df.to_pickle(self.docs_embeddings_path)

    def query_docs(
        self,
        query,
        rerank_n=20,
        exclude_things=["list"],
        cache=True,
        quiet=False,
    ):
        # ANCHOR[id=query-docs]
        """
        Keys of queries item in returned list:
          * rank, score
          * pdf_name, page_idx, region_idx
          * region_thing, previous_title
          * text

        Columns of `quereis_cache.pkl`:
          * query (str)
          * results (list of dicts)
        """
        logger.enter_quiet(quiet)

        if cache:
            if self.queries_cache_path.exists():
                queries_cache_df = pd.read_pickle(self.queries_cache_path)

                cached_query_rows = queries_cache_df.loc[
                    queries_cache_df["query"] == query
                ]
                cached_query_rows_num = cached_query_rows.shape[0]
                # print(f"Cached query rows: {cached_query_rows_num}")
                if cached_query_rows_num >= 1:
                    cached_query_results_indexes = cached_query_rows["results"].iloc[0]

                    if len(cached_query_results_indexes) >= rerank_n:
                        query_results_indexes = cached_query_results_indexes[:rerank_n]

                        query_results = self.load_query_results_by_indexes(
                            query_results_indexes
                        )
                        return query_results
            else:
                queries_cache_df = pd.DataFrame()

        self.docs_embeddings_df = pd.read_pickle(self.docs_embeddings_path)
        df = self.docs_embeddings_df.copy()

        def is_thing_excluded(row):
            return row["thing"] in exclude_things

        df = df[~df.apply(is_thing_excluded, axis=1)]

        # print(df)
        df.reset_index(drop=True, inplace=True)
        # print(df)

        self.embeddings_querier = EmbeddingsQuerier(df=df)
        query_results_scores_and_indexes = self.embeddings_querier.search(
            query=query, rerank_n=20
        )
        query_results = []
        sentence_tokenizer = SentenceTokenizer()
        for rank_idx, (item_idx, score) in enumerate(query_results_scores_and_indexes):
            query_item = df.iloc[item_idx]
            pdf_name = query_item["pdf_name"]
            region_text = query_item["text"]
            page_idx = query_item["page_idx"]
            region_idx = query_item["region_idx"]
            region_thing = query_item["thing"]
            previous_title = query_item["previous_title"]
            sentences = sentence_tokenizer.text_to_sentences(region_text)
            sentences_str = "\n".join(sentences)
            query_results.append(
                {
                    "rank": rank_idx + 1,
                    "score": score,
                    "pdf_name": pdf_name,
                    "page_idx": page_idx,
                    "region_idx": region_idx,
                    "region_thing": region_thing,
                    "previous_title": previous_title,
                    "text": sentences_str,
                }
            )

            logger.store_indent()
            logger.indent(2)
            logger.line(
                f"{rank_idx+1}: ({score:.4f}) [Page {page_idx}, {region_thing.capitalize()} Region {region_idx}]"
            )
            logger.file(f"- {pdf_name}")
            logger.indent(2)
            logger.file(f"- {previous_title}")
            logger.indent(2)
            logger.success(sentences_str)
            logger.restore_indent()
        logger.exit_quiet(quiet)

        if cache:
            self.dump_query_results_indexes(query, query_results)

        print(query_results[0].keys())

        return query_results

    def dump_query_results_indexes(self, query, query_results):
        # ANCHOR[id=dump-query-results-indexes]
        if self.queries_cache_path.exists():
            queries_cache_df = pd.read_pickle(self.queries_cache_path)
        else:
            queries_cache_df = pd.DataFrame()

        query_results_indexes = []
        for query_result in query_results:
            query_result_without_text = {
                k: v for k, v in query_result.items() if k not in ["text"]
            }
            query_results_indexes.append(query_result_without_text)

        query_reults_indexes_df = pd.DataFrame(
            [{"query": query, "results": query_results_indexes}]
        )
        queries_cache_df = pd.concat(
            [queries_cache_df, query_reults_indexes_df], ignore_index=True
        )
        queries_cache_df.to_pickle(self.queries_cache_path)

    def load_query_results_by_indexes(self, indexes: Union[list, dict]):
        if type(indexes) == dict:
            indexes = [indexes]

        docs_embeddings_df = pd.read_pickle(self.docs_embeddings_path)

        query_results = []
        for index in indexes:
            df_mask = reduce(
                operator.and_,
                [
                    docs_embeddings_df[key] == index[key]
                    for key in ["pdf_name", "page_idx", "region_idx"]
                ],
            )
            row = docs_embeddings_df.loc[df_mask]
            text = row["text"].iloc[0]
            index["text"] = text
            query_results.append(index)

        return query_results


if __name__ == "__main__":
    with Runtimer():
        multi_pdf_extractor = MultiPDFExtractor("cancer_review")
        # multi_pdf_extractor.extract_pdfs()
        multi_pdf_extractor.combine_docs_embeddings()
        # query="Unraveling the “black-box” of artificial intelligence-based pathological analysis of liver cancer"
        # query = "Current advances of AI-based approaches for clinical management of liver cancer"
        # query_results = multi_pdf_extractor.query_docs(query=query, quiet=True)
        # print(query_results)
