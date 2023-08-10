from collections import Counter
from sklearn.cluster import DBSCAN, KMeans, OPTICS
from termcolor import colored
from utils.calculator import flatten, flatten_len
from utils.logger import Logger
from utils.text_processor import TextBlock
import numpy as np

logger = Logger().logger


class BodyTextBlockCategorizer:
    def __init__(self, doc_blocks):
        self.doc_blocks = doc_blocks

    def generate_categorize_vectors(self):
        categorize_metrics = []
        for page_idx, page_blocks in enumerate(self.doc_blocks):
            for block in page_blocks:
                block_bbox = block["bbox"]
                block_text = ""  # Todo
                categorize_metrics.append((block_bbox, block_text))
        categorize_vectors = np.array(
            [(*bbox, len(text)) for bbox, text in categorize_metrics]
        )
        self.categorize_vectors = categorize_vectors
        logger.debug(self.categorize_vectors)
        return categorize_vectors

    def categorize(self):
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

        logger.info(
            f"{self.n_clusters} clusters for {flatten_len(self.doc_blocks)} blocks."
        )

    def get_most_common_category(self):
        categories_by_page = []
        start = 0
        for page_blocks in self.doc_blocks:
            end = start + len(page_blocks)
            categories_by_page.append(self.categories[start:end])
            start = end

        filtered_doc_blocks = []
        for i in range(len(self.doc_blocks)):
            page_blocks = self.doc_blocks[i]
            page_categories = categories_by_page[i]
            filtered_page_blocks = [
                block for j, block in enumerate(page_blocks) if page_categories[j] == 0
            ]
            filtered_doc_blocks.append(filtered_page_blocks)
            len_removed_blocks = len(page_blocks) - len(filtered_page_blocks)
            logger.info(
                f"  [-] {len_removed_blocks} headers/footers "
                f"({len(page_blocks):>2} -> {len(filtered_page_blocks):>2}) "
                f"removed in Page {i+1} "
            )

        len_filtered_doc_blocks = flatten_len(filtered_doc_blocks)
        len_doc_blocks = flatten_len(self.doc_blocks)
        logger.info(f"{len_filtered_doc_blocks} blocks remained of {len_doc_blocks}.")
        self.filtered_doc_blocks = filtered_doc_blocks
        return filtered_doc_blocks

    def run(self):
        self.categorize()
        self.get_most_common_category()


class FragmentedTextBlockCategorizer:
    def __init__(self, doc_blocks):
        self.doc_blocks = doc_blocks

    def generate_categorize_vectors(self):
        categorize_metrics = []
        for page_idx, page_blocks in enumerate(self.doc_blocks):
            for block in page_blocks:
                tblock = TextBlock(block)
                block_text = tblock.get_block_text()
                block_bbox = tblock.get_bbox()
                block_char_num = tblock.get_char_num()
                block_area = tblock.get_area()
                block_char_per_pixel = tblock.get_char_per_pixel()
                block_avg_line_width = tblock.get_avg_line_width()

                categorize_metrics.append(
                    (
                        block_char_num,
                        block_area,
                        # block_char_per_pixel,
                        block_avg_line_width,
                    )
                )
        categorize_vectors = np.array(categorize_metrics)

        self.categorize_metrics = categorize_metrics
        self.categorize_vectors = categorize_vectors
        logger.debug(self.categorize_vectors)
        return categorize_vectors

    def categorize(self):
        categorize_vectors = self.generate_categorize_vectors()

        dbscan = DBSCAN(eps=10)
        dbscan.fit(categorize_vectors)
        categories = dbscan.labels_
        self.n_clusters = len(np.unique(categories))

        # self.n_clusters = 2
        # kmeans = KMeans(n_clusters=self.n_clusters)
        # kmeans.fit(categorize_vectors)
        # categories = kmeans.labels_

        # category_counter = Counter(categories)
        # most_common_category = category_counter.most_common(1)[0][0]
        # categories = [
        #     0 if category == most_common_category else 1 for category in categories
        # ]

        self.categories = categories

        logger.info(
            f"{self.n_clusters} clusters for {flatten_len(self.doc_blocks)} text blocks."
        )

    def display_results(self):
        flatten_blocks = flatten(self.doc_blocks)
        for block, category, metric in zip(
            flatten_blocks, self.categories, self.categorize_metrics
        ):
            tblock = TextBlock(block)

            category_color = "light_green" if category % 2 == 0 else "light_red"
            logger.info(
                colored(f"Category: {category} ", category_color)
                + colored(f"{metric}", "light_cyan")
            )

            logger.info(tblock.get_block_text())

        logger.info(
            colored(
                f"{self.n_clusters} clusters for "
                f"{flatten_len(self.doc_blocks)} text blocks.",
                "green",
            )
        )

    def run(self):
        self.categorize()
        self.display_results()
