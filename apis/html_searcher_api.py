import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from documents.htmls.html_nodelizer import HTMLNodelizer
from documents.embeddings.embedder import EmbeddingEncoder, Reranker
from networks.html_fetcher import HTMLFetcher


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

    def fetch_html_from_url(self, url: str):
        html_fetcher = HTMLFetcher(url)
        html_fetcher.run()
        return {
            "url": url,
            "html_path": html_fetcher.output_path,
        }

    class EmbeddingPostItem(BaseModel):
        text: str = None

    class EmbeddingPostResponseItem(BaseModel):
        text: str = None
        embedding: list[float] = Field(
            default=None,
            description="`list[float]`: Embeddings of the text",
        )

    def calculate_embedding(self, item: EmbeddingPostItem):
        text = item.text
        embedding = self.embedding_encoder.calc_embedding(text)
        return {
            "text": text,
            "embedding": embedding.tolist(),
        }

    class RerankPostItem(BaseModel):
        query: str = None
        passages: list[str] = Field(
            default=None,
            description="`list[str]`: Passages to rerank.",
        )
        sort: bool = Field(
            default=True,
            description="Sort the reranked passages by score",
        )

    class RerankPostResponseItem(BaseModel):
        query: str = None
        rerank_scores: list[dict] = Field(
            default=None,
            description="`list[dict]`: Rerank scores of the passages. "
            'Each dict item: `{"passage": ..., "score": ...}`',
        )

    def rerank_passages_with_query(self, item: RerankPostItem):
        pairs = [[item.query, passage] for passage in item.passages]
        rerank_scores = self.reranker.compute_score(pairs).tolist()
        rerank_scores_with_passages = [
            {
                "passage": passage,
                "score": score,
            }
            for passage, score in zip(item.passages, rerank_scores)
        ]
        if item.sort:
            rerank_scores_with_passages = sorted(
                rerank_scores_with_passages, key=lambda x: x["score"], reverse=True
            )
        return {
            "query": item.query,
            "rerank_scores": rerank_scores_with_passages,
        }

    class RetrievePostItem(BaseModel):
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

    def retrieve_passages_with_query(self, item: RetrievePostItem):
        pass

    def setup_routes(self):
        self.app.get(
            "/url",
            summary="Fetch HTML from URL",
        )(self.fetch_html_from_url)
        self.app.post(
            "/embedding",
            summary="Calculate embedding for text",
            response_model=self.EmbeddingPostResponseItem,
        )(self.calculate_embedding)
        self.app.post(
            "/rerank",
            summary="Calculate rerank scores for list of passages with query",
            response_model=self.RerankPostResponseItem,
        )(self.rerank_passages_with_query)
        self.app.post(
            "/retrieve",
            summary="Retrieve passages from url with query",
        )(self.retrieve_passages_with_query)


app = APIApp().app

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=12344, reload=True)
