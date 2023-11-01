import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from documents.htmls.html_nodelizer import HTMLNodelizer
from documents.embeddings.embedder import EmbeddingEncoder, Reranker
from documents.embeddings.node_embedder import NodeEmbedder
from networks.html_fetcher import HTMLFetcher
from typing import Union


class DocumentEntity:
    def __init__(
        self,
        url: str = None,
        html_fetcher: HTMLFetcher = None,
        html_nodelizer: HTMLNodelizer = None,
        node_embedder: NodeEmbedder = None,
    ):
        self.url = url
        self.html_fetcher = html_fetcher
        self.html_nodelizer = html_nodelizer
        self.node_embedder = node_embedder


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

    class EmbedFromUrlPostItem(BaseModel):
        url: str = Field(
            default=None,
            description="URL to fetch, nodelize and embed HTML",
        )

    def embed_html_from_url(self, item: EmbedFromUrlPostItem):
        url = item.url
        if url not in self.data_store:
            html_fetcher = HTMLFetcher(url)
            html_fetcher.run()
            html_nodelizer = HTMLNodelizer(
                html_path=html_fetcher.output_path,
                url=html_fetcher.html_url,
                domain=html_fetcher.domain,
            )
            html_nodelizer.run()
            node_embedder = NodeEmbedder(
                html_nodelizer=html_nodelizer,
                embedding_encoder=self.embedding_encoder,
            )
            node_embedder.run()
            self.data_store[url] = DocumentEntity(
                url=url,
                html_fetcher=html_fetcher,
                html_nodelizer=html_nodelizer,
                node_embedder=node_embedder,
            )
        else:
            pass

        return {
            "url": url,
            "html_path": self.data_store[url].html_fetcher.output_path,
            "embeddings_df_pkl_path": self.data_store[
                url
            ].node_embedder.embeddings_df_pkl_path,
            "nodes_count": len(self.data_store[url].html_nodelizer.nodes),
        }

    class EmbeddingPostItem(BaseModel):
        text: Union[str, list[str]] = Field(
            default=None,
            description="`str` or `list[str]`: Text(s) to calculate embedding",
        )

    def calculate_embedding(self, item: EmbeddingPostItem):
        if isinstance(item.text, str):
            result = self.embedding_encoder.calc_embedding(item.text)
        else:
            result = [self.embedding_encoder.calc_embedding(text) for text in item.text]

        return result

    class RerankPostItem(BaseModel):
        query: str = None
        passages: list[str] = Field(
            default=None,
            description="`list[str]`: Passages to rerank.",
        )
        sort: bool = Field(
            default=False,
            description="Sort the reranked passages by rerank score",
        )
        include_query: bool = Field(
            default=False, description="Include the query in the response"
        )
        include_passages: bool = Field(
            default=False,
            description="Include the passages in the response, will return `list[dict]`"
            'Each dict item: `{"passage": ..., "score": ...}`',
        )
        max_tokens: int = Field(
            default=None,
            description="Max tokens of returned reranked passages texts",
        )
        top_k: int = Field(
            default=None,
            description="Max count of returned reranked passages",
        )

    class RerankPostResponseDictItem(BaseModel):
        query: str = None
        rerank_results: list[dict] = Field(
            default=None,
            description="`list[dict]`: Reranked results of the passages"
            'Each dict item: `{"passage": ..., "score": ...}`',
        )

    class RerankPostResponseListItem(BaseModel):
        query: str = None
        rerank_results: list[float] = Field(
            default=None,
            description="`list[float]`: Rerank scores of the passages."
            "'sort' must be `false`",
        )

    def rerank_passages_with_query(self, item: RerankPostItem):
        if item.sort and not item.include_passages:
            raise HTTPException(
                "'include_passages' must be `true` when 'sort' is `true`"
            )
        pairs = [[item.query, passage] for passage in item.passages]
        rerank_scores = self.reranker.compute_scores(pairs)

        if item.include_passages:
            rerank_results = [
                {
                    "passage": passage,
                    "score": score,
                }
                for passage, score in zip(item.passages, rerank_scores)
            ]
        else:
            rerank_results = rerank_scores

        if item.sort:
            rerank_results = sorted(
                rerank_results, key=lambda x: x["score"], reverse=True
            )

        return {
            "query": item.query,
            "rerank_results": rerank_results,
        }

    class SearchPostItem(BaseModel):
        query: str = None
        url: str = None
        sort: bool = Field(
            default=True,
            description="Sort the returned passages by score",
        )
        rerank: bool = Field(
            default=True,
            description="Better results with more time consumption",
        )
        tokens_limit: int = Field(
            default=None,
            description="Max tokens for passages texts",
        )
        passages_limit: int = Field(
            default=None,
            description="Max number of passages",
        )

    def search_passages_with_query(self, item: SearchPostItem):
        pass

    def setup_routes(self):
        self.app.get(
            "/url",
            summary="Fetch HTML from URL",
        )(self.fetch_html_from_url)

        self.app.post(
            "/embedding",
            summary="Calculate embedding for text",
        )(self.calculate_embedding)

        self.app.post(
            "/rerank",
            summary="Calculate rerank scores for list of passages with query",
            response_model=Union[
                self.RerankPostResponseDictItem,
                self.RerankPostResponseListItem,
            ],
        )(self.rerank_passages_with_query)

        self.app.post(
            "/search",
            summary="Search passages from url with query",
        )(self.search_passages_with_query)


app = APIApp().app

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=12344, reload=True)
