from collections import Counter
from sklearn.cluster import DBSCAN
import numpy as np


class PDFTextBlockCategorizer:
    def __init__(self, blocks):
        self.blocks = blocks

    def run(self):
        X = np.array(
            [(x0, y0, x1, y1, len(text)) for x0, y0, x1, y1, text in self.blocks]
        )

        dbscan = DBSCAN()
        dbscan.fit(X)
        categories = dbscan.labels_
        self.n_clusters = len(np.unique(categories))
        category_counter = Counter(categories)
        most_common_category = category_counter.most_common(1)[0][0]
        categories = [
            0 if category == most_common_category else 1 for category in categories
        ]
        self.categories = categories

        print(f"{self.n_clusters} clusters for {len(self.blocks)} blocks")
