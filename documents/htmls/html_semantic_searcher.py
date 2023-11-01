import pandas as pd
from documents.embeddings.node_embedder import NodeEmbedder
from documents.embeddings.embedder import EmbeddingEncoder, Reranker
from documents.htmls.html_nodelizer import HTMLNodelizer
from documents.htmls.url_to_path_converter import UrlToPathConverter
from networks.html_fetcher import HTMLFetcher


class UrlToEmbeddingsDfConverter:
    def __init__(self, url, embedding_encoder=None):
        self.url = url
        url_converter = UrlToPathConverter(url)
        self.html_path = url_converter.output_path
        self.get_embeddings_df(embedding_encoder=embedding_encoder)

    def get_embeddings_df(self, embedding_encoder=None):
        self.embeddings_df_pkl_path = self.html_path.with_suffix(".embeddings.pkl")
        if self.embeddings_df_pkl_path.exists():
            print(f"> Load embeddings df from: {self.embeddings_df_pkl_path}")
            self.embeddings_df = pd.read_pickle(self.embeddings_df_pkl_path)
        else:
            self.html_fetcher = HTMLFetcher(self.url)
            self.html_fetcher.run()
            self.html_nodelizer = HTMLNodelizer(
                html_path=self.html_fetcher.output_path,
                url=self.html_fetcher.html_url,
                domain=self.html_fetcher.domain,
            )
            self.html_nodelizer.run()
            self.node_embedder = NodeEmbedder(
                self.html_nodelizer, embedding_encoder=embedding_encoder
            )
            self.node_embedder.compute_embeddings()
            self.embeddings_df = self.node_embedder.embeddings_df
        return self.embeddings_df


class HTMLSemanticSearcher:
    def __init__(
        self, url, embedding_encoder=None, reranker=None, document_entity=None
    ):
        self.url = url
        self.document_entity = document_entity
        self.load_models(embedding_encoder=embedding_encoder, reranker=reranker)
        self.get_embeddings_df()

    def load_models(self, embedding_encoder=None, reranker=None):
        if embedding_encoder:
            self.embeddings_encoder = embedding_encoder
        else:
            self.embeddings_encoder = EmbeddingEncoder()

        if reranker:
            self.reranker = reranker
        else:
            self.reranker = Reranker()

    def get_embeddings_df(self):
        if self.document_entity:
            self.embeddings_df = self.document_entity.embeddings_df
        else:
            self.url_to_embeddings_df_converter = UrlToEmbeddingsDfConverter(
                self.url, embedding_encoder=self.embeddings_encoder
            )
            self.embeddings_df = self.url_to_embeddings_df_converter.embeddings_df

    def search(self, query, retrieve_top_k=50, rerank_top_k=10):
        self.query = query
        self.retrieve(retrieve_top_k)
        self.rerank(rerank_top_k)
        return self.top_rerank_results

    def retrieve(self, top_k=50, display=False):
        query_embeddings = self.embeddings_encoder.calc_embedding(
            self.query, query_prefix=False, tolist=False
        )
        self.retrieve_results = []
        for row_idx, row in self.embeddings_df.iterrows():
            node_idx = row["idx"]
            embedding = row["embedding"]
            # full_text = row["full_text_with_description"]
            retrieve_score = (query_embeddings @ embedding.T).tolist()
            self.retrieve_results.append(
                {
                    "node_idx": node_idx,
                    "row_idx": row_idx,
                    "retrieve_score": retrieve_score,
                }
            )

        self.top_retrieve_results = sorted(
            self.retrieve_results, key=lambda x: x["retrieve_score"], reverse=True
        )[:top_k]

        if display:
            for retrieve_result in self.top_retrieve_results[:10]:
                row_idx = retrieve_result["row_idx"]
                node_idx = retrieve_result["node_idx"]
                retrieve_score = retrieve_result["retrieve_score"]
                full_text = self.embeddings_df.iloc[row_idx][
                    "full_text_with_description"
                ]
                print(retrieve_score, row_idx, node_idx)
                print(full_text)
            print("=" * 30)

        return self.top_retrieve_results

    def rerank(self, top_k=10, with_description=True, display=True):
        if with_description:
            full_text_column = "full_text"
        else:
            full_text_column = "full_text_with_description"

        rerank_pairs = [
            [
                self.query,
                self.embeddings_df.iloc[retrieve_result["row_idx"]][full_text_column],
            ]
            for retrieve_result in self.top_retrieve_results
        ]
        self.rerank_scores = self.reranker.compute_scores(rerank_pairs, tolist=True)

        self.rerank_results = [
            {
                **retrieve_resulst,
                "rerank_score": rerank_score,
            }
            for retrieve_resulst, rerank_score in zip(
                self.top_retrieve_results, self.rerank_scores
            )
        ]

        self.top_rerank_results = sorted(
            self.rerank_results, key=lambda x: x["rerank_score"], reverse=True
        )[:top_k]

        if display:
            for rerank_result in self.top_rerank_results[:10]:
                row_idx = rerank_result["row_idx"]
                node_idx = rerank_result["node_idx"]
                retrieve_score = rerank_result["retrieve_score"]
                rerank_score = rerank_result["rerank_score"]
                full_text = self.embeddings_df.iloc[row_idx][
                    "full_text_with_description"
                ]
                print(rerank_score)
                print(full_text)
            print("=" * 30)
        return self.top_rerank_results


if __name__ == "__main__":
    print(f"Query: {query}")
    html_semantic_searcher = HTMLSemanticSearcher(url)
    html_semantic_searcher.search(query)
    print(f"Query: {query}")
