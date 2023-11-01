import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from documents.htmls.html_nodelizer import HTMLNodelizer
from documents.embeddings.embedder import EmbeddingEncoder, Reranker
from networks.html_fetcher import HTMLFetcher


class APIApp:
    def __init__(self):
        self.app = FastAPI(docs_url="/")
        self.load_models()
        self.setup_routes()

    def load_models(self):
        self.embedding_encoder = EmbeddingEncoder()
        self.reranker = Reranker()

    class EmbeddingPostItem(BaseModel):
        text: str = None

    class RerankPostItem(BaseModel):
        query: str = None
        passages: list[str] = None
        sort: bool = True

    def fetch_html_from_url(self, url: str):
        html_fetcher = HTMLFetcher(url)
        html_fetcher.run()
        return {
            "url": url,
            "html_path": html_fetcher.output_path,
        }

    def calculate_embedding(self, item: EmbeddingPostItem):
        text = item.text
        embedding = self.embedding_encoder.calc_embedding(text)
        return {
            "text": text,
            "embedding": embedding.tolist(),
        }

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
        )(self.rerank_passages_with_query)


app = APIApp().app

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=12344, reload=True)
