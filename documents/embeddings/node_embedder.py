from documents.embeddings.embedder import EmbeddingEncoder
from documents.htmls.html_nodelizer import HTMLNodelizer
from networks.html_fetcher import HTMLFetcher
import pandas as pd


class NodeEmbedder:
    def __init__(self, html_nodelizer):
        self.html_nodelizer = html_nodelizer
        self.html_path = html_nodelizer.html_path
        self.embeddings_df_pkl_path = self.html_path.with_suffix(".embeddings.pkl")
        self.embedding_encoder = EmbeddingEncoder()
        self.load_embedding_cache()

    def load_embedding_cache(self):
        if self.embeddings_df_pkl_path.exists():
            print(f"> Load embeddings df from: {self.embeddings_df_pkl_path}")
            self.embeddings_df = pd.read_pickle(self.embeddings_df_pkl_path)
        else:
            self.embeddings_df = pd.DataFrame()

    def dump_embeddings_to_pickle(self):
        self.embeddings_df = pd.concat(
            [self.embeddings_df, pd.DataFrame(self.embedding_items)],
            ignore_index=True,
        )
        print(self.embeddings_df)
        self.embeddings_df_pkl_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"> Dump embeddings df to: {self.embeddings_df_pkl_path}")
        self.embeddings_df.to_pickle(self.embeddings_df_pkl_path)

    def compute_embeddings(self):
        self.embedding_items = []
        for node in self.html_nodelizer.nodes[:]:
            if not node.type.endswith("group"):
                if node.type in ["string", "paragraph", "text"]:
                    add_description = False
                else:
                    add_description = True
                node_full_text = node.get_full_text(add_description=add_description)
                if (not self.embeddings_df.empty) and (
                    self.embeddings_df["full_text_with_description"]
                    .isin([node_full_text])
                    .any()
                ):
                    continue
                else:
                    node_embedding = self.embedding_encoder.calc_embedding(
                        node_full_text
                    )
                    print(node_embedding)
                    embedding_item = {
                        "idx": node.idx,
                        "type": node.type,
                        "text": node.get_text(),
                        "full_text": node.get_full_text(add_description=False),
                        "full_text_with_description": node_full_text,
                        "embedding": node_embedding,
                    }
                    self.embedding_items.append(embedding_item)
        self.dump_embeddings_to_pickle()


if __name__ == "__main__":
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
    html_nodelizer = HTMLNodelizer(
        html_path=html_fetcher.output_path,
        url=html_fetcher.html_url,
        domain=html_fetcher.domain,
    )
    html_nodelizer.run()
    node_embedder = NodeEmbedder(html_nodelizer)
    node_embedder.compute_embeddings()
