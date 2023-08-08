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
        labels = dbscan.labels_
        self.n_clusters = len(np.unique(labels))
        label_counter = Counter(labels)
        most_common_label = label_counter.most_common(1)[0][0]
        labels = [0 if label == most_common_label else 1 for label in labels]
        self.labels = labels

        print(f"{self.n_clusters} clusters for {len(self.blocks)} blocks")
