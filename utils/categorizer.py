from sklearn.cluster import KMeans
import numpy as np


class PDFTextBlockCategorizer:
    def __init__(self, blocks):
        self.blocks = blocks
        self.labels = None

    def run(self):
        X = np.array(
            [(x0, y0, x1, y1, len(text)) for x0, y0, x1, y1, text in self.blocks]
        )
        n_clusters = 3
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(X)

        self.labels = kmeans.labels_

        # # group the text blocks by their cluster labels
        # clusters = {i: [] for i in range(n_clusters)}
        # for i, label in enumerate(self.labels):
        #     clusters[label].append(self.blocks[i])
