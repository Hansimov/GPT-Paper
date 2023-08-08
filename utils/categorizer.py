from sklearn.cluster import KMeans, DBSCAN
import numpy as np


class PDFTextBlockCategorizer:
    def __init__(self, blocks):
        self.blocks = blocks

    def run(self):
        X = np.array(
            [(x0, y0, x1, y1, len(text)) for x0, y0, x1, y1, text in self.blocks]
        )

        # n_clusters = 3
        # kmeans = KMeans(n_clusters=n_clusters)
        # kmeans.fit(X)
        # self.labels = kmeans.labels_

        dbscan = DBSCAN()
        dbscan.fit(X)
        self.labels = dbscan.labels_
        self.n_clusters = len(np.unique(self.labels))
        print(f"Clusters num: {self.n_clusters}")
