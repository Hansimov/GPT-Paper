import uvicorn
from fastapi import FastAPI
from typing import Union
from documents.htmls.html_nodelizer import HTMLNodelizer
from networks.html_fetcher import HTMLFetcher
from documents.embeddings.embedder import EmbeddingEncoder, Reranker

from pydantic import BaseModel

app = FastAPI(docs_url="/")


@app.get(
    "/url",
    summary="Fetch HTML from URL",
)
def fetch_html_from_url(url: str):
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()

    return {
        "url": url,
        "html_path": html_fetcher.output_path,
    }


embedding_encoder = EmbeddingEncoder()


class EmbeddingPostItem(BaseModel):
    text: str = None


@app.post(
    "/embedding",
    summary="Encode text to embedding",
)
def encode_embedding(item: EmbeddingPostItem):
    text = item.text
    embedding = embedding_encoder.calc_embedding(text)
    return {
        "text": text,
        "embedding": embedding.tolist(),
    }


reranker = Reranker()


class RerankPostItem(BaseModel):
    query: str = None
    passages: list[str] = None
    sort: bool = True


@app.post(
    "/rerank",
    summary="Calculate rerank scores for list of passages with query",
)
def rerank(item: RerankPostItem):
    pairs = [[item.query, passage] for passage in item.passages]
    rerank_scores = reranker.compute_score(pairs).tolist()
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


if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=12344, reload=True)
