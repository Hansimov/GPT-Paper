import matplotlib.pyplot as plt

# python -m pip install --upgrade pymupdf
import fitz
import shutil
from itertools import islice
from matplotlib.patches import Rectangle
from pathlib import Path
from termcolor import colored
from utils.categorizer import PDFTextBlockCategorizer
from utils.logger import Logger, add_fillers

logger = Logger(prefix=False).logger


class PDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"
    image_root = pdf_root / "images"

    def __init__(self):
        pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        # pdf_filename = "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images.pdf"
        # pdf_filename = "HEP 2020 Predicting survival after hepatocellular carcinoma resection using.pdf"
        self.pdf_fullpath = self.pdf_root / pdf_filename
        self.pdf_doc = fitz.open(self.pdf_fullpath)

    def extract_all_texts(self):
        for idx, page in enumerate(self.pdf_doc):
            text = page.get_text("block")
            print(f"Page {idx+1}:")
            print(text)

    def calc_rect_center(self, rect, reverse_y=False):
        if reverse_y:
            x0, y0, x1, y1 = rect[0], -rect[1], rect[2], -rect[3]
        else:
            x0, y0, x1, y1 = rect

        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2
        return (x_center, y_center)

    def plot_text_block_rect(self, points, rects, categories, point_texts):
        fig, ax = plt.subplots()
        colors = ["b", "r", "g", "c", "m", "y", "k"]

        for i, rect_center in enumerate(points):
            category_idx = categories[i]
            color = colors[category_idx]
            x0, y0, x1, y1 = rects[i]
            rect = Rectangle((x0, -y0), x1 - x0, -y1 + y0, fill=False, edgecolor=color)
            ax.add_patch(rect)
            x, y = rect_center
            plt.scatter(x, y, color=color)
            plt.annotate(point_texts[i], rect_center)
        plt.show()

    def remove_no_body_text_blocks(self, doc_blocks, categories):
        categories_by_page = []
        start = 0
        for page_blocks in doc_blocks:
            end = start + len(page_blocks)
            categories_by_page.append(categories[start:end])
            start = end

        filtered_doc_blocks = []
        for i in range(len(doc_blocks)):
            page_blocks = doc_blocks[i]
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

        return filtered_doc_blocks

    def extract_all_text_blocks(self):
        # * https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractBLOCKS

        rect_centers = []
        rects = []
        point_texts = []
        categorize_vectors = []
        doc_blocks = []
        for page_idx, page in islice(enumerate(self.pdf_doc), len(self.pdf_doc)):
            page_blocks = page.get_text("blocks")
            doc_blocks.append(page_blocks)
            page_cnt = page_idx + 1
            logger.info(
                colored(
                    add_fillers(f"Start Page {page_cnt}: {len(page_blocks)} blocks"),
                    "light_yellow",
                )
            )
            block_cnt = 0
            for block in page_blocks:
                block_rect = block[:4]  # (x0,y0,x1,y1)
                x0, y0, x1, y1 = block_rect
                rects.append(block_rect)
                block_text = block[4]
                block_num = block[5]
                # block_cnt += 1
                block_cnt = block_num + 1

                rect_center = self.calc_rect_center(block_rect, reverse_y=True)
                rect_centers.append(rect_center)
                point_text = f"({page_cnt}.{block_cnt})"
                point_texts.append(point_text)

                block_type = "text" if block[6] == 0 else "image"
                logger.info(f"Block: {page_cnt}.{block_cnt}")
                logger.debug(f"<{block_type}> {rect_center} - {block_rect}")
                logger.debug(block_text)
                categorize_vectors.append((*block_rect, block_text))

            logger.info(
                colored(
                    add_fillers(f"End Page {page_cnt}: {len(page_blocks)} blocks"),
                    "green",
                )
            )

        categorizer = PDFTextBlockCategorizer(categorize_vectors)
        categorizer.run()

        self.remove_no_body_text_blocks(
            doc_blocks=doc_blocks, categories=categorizer.categories
        )

        # self.plot_text_block_rect(
        #     categories=categorizer.labels,
        #     points=rect_centers,
        #     rects=rects,
        #     point_texts=point_texts,
        # )

    def save_image(self, xref, basepath):
        ext_image = self.pdf_doc.extract_image(xref)
        ext = ext_image["ext"]
        fullpath = basepath.with_suffix(f".{ext}")
        print(f"  > Saving image to: {fullpath}")
        pix = fitz.Pixmap(self.pdf_doc, xref)
        pix.save(fullpath)

    def extract_images(self):
        img_idx = 0
        for page_idx, page in enumerate(self.pdf_doc):
            img_infos = page.get_images()
            print(f"Page {page_idx}: {img_infos}")
            for info in img_infos:
                xref = info[0]
                img_basepath = self.image_root / f"img_{img_idx+1}"
                self.save_image(xref, img_basepath)
                img_idx += 1

    def replace_html_entities(self, text):
        symbols = {
            "&nbsp;": " ",
            "&amp;": "&",
        }
        for k, v in symbols.items():
            text = text.replace(k, v)
        return text

    def format_toc(self):
        levels = [0] * 10
        lines = []
        for level, title, page, dest in self.pdf_toc:
            levels[level - 1] += 1
            for i in range(level, len(levels)):
                levels[i] = 0

            level_str = ".".join(map(str, levels[1:level]))
            trailing_level_str = " " if level > 1 else ""
            leading_level_str = " " * 2 * max(level - 2, 0)

            title_str = self.replace_html_entities(title)

            lines.append(
                f"{leading_level_str}{level_str}{trailing_level_str}{title_str}"
            )

        for line in lines:
            print(line)

    def extract_toc(self):
        self.pdf_toc = self.pdf_doc.get_toc(simple=False)
        self.format_toc()

    def run(self):
        # self.extract_all_texts()
        self.extract_all_text_blocks()
        # self.extract_toc()
        # self.extract_images()


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
