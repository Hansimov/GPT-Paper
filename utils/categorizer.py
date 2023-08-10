from collections import Counter
from sklearn.cluster import DBSCAN
from utils.logger import Logger
import numpy as np

logger = Logger().logger


class PDFTextBlockCategorizer:
    def __init__(self, blocks):
        self.blocks = blocks

    def generate_categorize_vectors(self, block_format="dicts"):
        if block_format == "dicts":
            categorize_metrics = []
            for page_idx, page_blocks in enumerate(self.blocks):
                for block in page_blocks:
                    block_bbox = block["bbox"]
                    block_text = ""  # Todo
                    categorize_metrics.append((block_bbox, block_text))
            categorize_vectors = np.array(
                [(*bbox, len(text)) for bbox, text in categorize_metrics]
            )
            return categorize_vectors

    def run(self):
        categorize_vectors = self.generate_categorize_vectors()

        dbscan = DBSCAN()
        dbscan.fit(categorize_vectors)
        categories = dbscan.labels_
        self.n_clusters = len(np.unique(categories))
        category_counter = Counter(categories)
        most_common_category = category_counter.most_common(1)[0][0]
        categories = [
            0 if category == most_common_category else 1 for category in categories
        ]
        self.categories = categories

        logger.info(f"{self.n_clusters} clusters for {len(self.blocks)} blocks.")
