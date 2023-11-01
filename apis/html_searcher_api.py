import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from documents.htmls.html_nodelizer import HTMLNodelizer
from documents.embeddings.embedder import EmbeddingEncoder, Reranker
from documents.htmls.html_semantic_searcher import HTMLSemanticSearcher
from documents.embeddings.node_embedder import NodeEmbedder
from networks.html_fetcher import HTMLFetcher
from typing import Union


class DocumentEntity:
    def __init__(
        self,
        url: str = None,
        app=None,
    ):
        self.url = url
        self.app = app

        self.html_fetcher = HTMLFetcher(url)
        self.html_fetcher.run()
        self.html_nodelizer = HTMLNodelizer(
            html_path=self.html_fetcher.output_path,
            url=self.html_fetcher.html_url,
            domain=self.html_fetcher.domain,
        )
        self.html_nodelizer.run()
        self.node_embedder = NodeEmbedder(
            html_nodelizer=self.html_nodelizer,
            embedding_encoder=self.app.embedding_encoder,
        )
        self.node_embedder.run()

        self.init_paths()

    def init_paths(self):
        self.html_path = self.html_nodelizer.html_path
        self.nodes = self.html_nodelizer.nodes
        self.embeddings_df_pkl_path = self.node_embedder.embeddings_df_pkl_path
        self.embeddings_df = self.node_embedder.embeddings_df


class APIApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title="Documents Retriever API",
            version="1.0",
        )
        self.load_cache()
        self.setup_routes()

    def load_cache(self):
        self.embedding_encoder = EmbeddingEncoder()
        self.reranker = Reranker()
        self.html_nodelizer_cache = {}
        self.data_store = {}

    def fetch_html_from_url(self, url: str):
        html_fetcher = HTMLFetcher(url)
        html_fetcher.run()
        return {
            "url": url,
            "html_path": html_fetcher.output_path,
        }

    class EmbedHTMLFromUrlPostItem(BaseModel):
        url: str = Field(
            default=None,
            description="URL to fetch, nodelize and embed HTML",
        )

    def embed_html_from_url(self, item: EmbedHTMLFromUrlPostItem):
        url = item.url
        if url not in self.data_store:
            document_entity = DocumentEntity(url=url, app=self)
            self.data_store[url] = document_entity
        else:
            document_entity = self.data_store[url]

        return {
            "url": url,
            "html_path": document_entity.html_path,
            "embeddings_df_pkl_path": document_entity.embeddings_df_pkl_path,
            "nodes_count": len(document_entity.nodes),
        }

    class EmbeddingPostItem(BaseModel):
        text: Union[str, list[str]] = Field(
            default=None,
            description="`str` or `list[str]`: Text(s) to calculate embedding",
        )

    def calculate_embedding(self, item: EmbeddingPostItem):
        if isinstance(item.text, str):
            result = self.embedding_encoder.calc_embedding(text=item.text, tolist=True)
        else:
            result = [
                self.embedding_encoder.calc_embedding(text=text, tolist=True)
                for text in item.text
            ]
        return result

    class RerankPostItem(BaseModel):
        query: str = None
        passages: list[str] = Field(
            default=None,
            description="`list[str]`: Passages to rerank.",
        )

    def rerank_passages_with_query(self, item: RerankPostItem):
        pairs = [[item.query, passage] for passage in item.passages]
        rerank_scores = self.reranker.compute_scores(pairs)
        return rerank_scores

    class SearchPostItem(BaseModel):
        query: str = None
        url: str = None
        sort: bool = Field(
            default=True,
            description="Sort the returned passages by score",
        )
        max_tokens: int = Field(
            default=None,
            description="Max tokens for passages texts",
        )
        retrieve_top_k: int = Field(
            default=50,
            description="Max number of retrieved passages",
        )
        rerank_top_k: int = Field(
            default=10,
            description="Max number of reranked passages",
        )

    def search_passages_with_query(self, item: SearchPostItem):
        url = item.url
        query = item.query
        self.embed_html_from_url(item=APIApp.EmbedHTMLFromUrlPostItem(url=url))
        self.html_semantic_searcher = HTMLSemanticSearcher(
            url=url,
            embedding_encoder=self.embedding_encoder,
            reranker=self.reranker,
            document_entity=self.data_store[url],
        )
        search_results = self.html_semantic_searcher.search(
            query=query,
            retrieve_top_k=item.retrieve_top_k,
            rerank_top_k=item.rerank_top_k,
        )
        return {
            "url": url,
            "query": query,
            "results": search_results,
        }

    def setup_routes(self):
        # self.app.get(
        #     "/url",
        #     summary="Fetch HTML from URL",
        # )(self.fetch_html_from_url)

        # self.app.post(
        #     "/embed_url",
        #     summary="Fetch, nodelize and embed HTML from URL",
        # )(self.embed_html_from_url)

        self.app.post(
            "/embedding",
            summary="Calculate embedding for text",
        )(self.calculate_embedding)

        self.app.post(
            "/rerank",
            summary="Calculate rerank scores for list of passages with query",
        )(self.rerank_passages_with_query)

        self.app.post(
            "/search",
            summary="Search passages from url with query",
        )(self.search_passages_with_query)


app = APIApp().app

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=12344, reload=True)
