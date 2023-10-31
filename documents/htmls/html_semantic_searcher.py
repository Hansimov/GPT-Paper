import pandas as pd
from documents.embeddings.embedder import EmbeddingEncoder, Reranker
from documents.htmls.url_to_path_converter import UrlToPathConverter


class UrlToEmbeddingsDfConverter:
    def __init__(self, url):
        self.url = url
        url_converter = UrlToPathConverter(url)
        self.html_path = url_converter.output_path

    def get_embeddings_df(self):
        self.embeddings_df_pkl_path = self.html_path.with_suffix(".embeddings.pkl")
        self.embeddings_df = pd.read_pickle(self.embeddings_df_pkl_path)
        return self.embeddings_df


class EmbeddingSearcher:
    def __init__(self, query, embedding_df):
        pass


class HTMLSemanticSearcher:
    def __init__(self, url):
        self.get_embeddings_df()
        self.load_embeddings_encoder()

    def get_embeddings_df(self):
        self.embeddings_df = UrlToEmbeddingsDfConverter(url).get_embeddings_df()
        self.embedings_list = self.embeddings_df["embedding"].tolist()

    def load_embeddings_encoder(self):
        self.embeddings_encoder = EmbeddingEncoder()

    def search(self, query, retrieve_top_k=50, rerank_top_k=10):
        self.query = query
        self.retrieve(retrieve_top_k)
        self.rerank(rerank_top_k)
        self.output_search_results()

    def retrieve(self, top_k=50):
        query_embeddings = self.embeddings_encoder.calc_embedding(
            query, query_prefix=False
        )
        self.retrieve_score_tuples = []
        for i, embedding in enumerate(self.embedings_list):
            retrieve_score = query_embeddings @ embedding.T
            self.retrieve_score_tuples.append((i, retrieve_score))

        self.top_retrieve_results = sorted(
            self.retrieve_score_tuples, key=lambda x: x[1], reverse=True
        )[:top_k]

        for i, score in self.top_retrieve_results[:10]:
            print(score)
            full_text = self.embeddings_df.iloc[i]["full_text_with_description"]
            print(full_text)
        print("=" * 30)

    def rerank(self, top_k=10):
        self.reranker = Reranker()
        self.reranker.load_model(quiet=False)
        rerank_pairs = [
            [
                self.query,
                self.embeddings_df.iloc[i]["full_text_with_description"],
            ]
            for i, retrieve_score in self.top_retrieve_results
        ]
        self.rerank_scores = self.reranker.compute_score(rerank_pairs)
        self.rerank_score_tuples = [
            (self.top_retrieve_results[j][0], score)
            for j, score in enumerate(self.rerank_scores)
        ]
        self.top_rerank_results = sorted(
            self.rerank_score_tuples, key=lambda x: x[1], reverse=True
        )[:top_k]

    def output_search_results(self):
        self.search_results = [
            (i, self.embeddings_df.iloc[i]["full_text_with_description"], score)
            for i, score in self.top_rerank_results
        ]
        for i, full_text, score in self.search_results:
            print(score)
            print(full_text)


if __name__ == "__main__":
    query = "author team of this document"
    html_semantic_searcher = HTMLSemanticSearcher(url)
    html_semantic_searcher.search(query)
