import fitz
import matplotlib.pyplot as plt
import shutil
from collections import Counter
from itertools import islice, chain
from matplotlib.patches import Rectangle
from pathlib import Path
from termcolor import colored
from utils.categorizer import PDFTextBlockCategorizer
from utils.logger import Logger, add_fillers
from utils.tokenizer import Tokenizer
from utils.calculator import flatten_len, kilo_count, font_flags_to_list
from utils.table import PDFTableParser

logger = Logger().logger


class PDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"
    image_root = pdf_root / "images"

    def __init__(self):
        # pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        pdf_filename = "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images.pdf"
        # pdf_filename = "HEP 2020 Predicting survival after hepatocellular carcinoma resection using.pdf"
        # pdf_filename = "Nature Cancer 2020 Pan-cancer computational histopathology reveals.pdf"
        self.pdf_fullpath = self.pdf_root / pdf_filename
        self.pdf_doc = fitz.open(self.pdf_fullpath)

    def extract_all_texts(self):
        for idx, page in enumerate(self.pdf_doc):
            text = page.get_text("block")
            logger.info(f"Page {idx+1}:")
            logger.debug(text)

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
            logger.debug(
                f"  [-] {len_removed_blocks} headers/footers "
                f"({len(page_blocks):>2} -> {len(filtered_page_blocks):>2}) "
                f"removed in Page {i+1} "
            )

        len_filtered_doc_blocks = flatten_len(filtered_doc_blocks)
        len_doc_blocks = flatten_len(doc_blocks)
        logger.info(f"{len_filtered_doc_blocks} blocks remained of {len_doc_blocks}.")

        return filtered_doc_blocks

    def extract_all_text_blocks(self):
        # * https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractBLOCKS

        rect_centers = []
        rects = []
        point_texts = []
        categorize_vectors = []
        doc_blocks = []
        tokenizer = Tokenizer()
        doc_token_cnt = 0
        for page_idx, page in islice(enumerate(self.pdf_doc), len(self.pdf_doc)):
            page_blocks = page.get_text("blocks")
            doc_blocks.append(page_blocks)
            page_cnt = page_idx + 1
            logger.info(
                colored(
                    add_fillers(f"Start [Page {page_cnt}] [{len(page_blocks)} blocks]"),
                    "light_yellow",
                )
            )
            block_cnt = 0
            page_token_cnt = 0
            for block in page_blocks:
                # Process block values
                block_rect = block[:4]  # (x0,y0,x1,y1)
                block_text = block[4]
                block_num = block[5]
                block_cnt = block_num + 1
                # block_cnt += 1
                block_type = "text" if block[6] == 0 else "image"

                if block_type == "text":
                    token_cnt = tokenizer.count_tokens(block_text.replace("\n", " "))
                    page_token_cnt += token_cnt
                else:
                    token_cnt = 0

                categorize_vectors.append((*block_rect, block_text))

                # Prepare for plot categorization of text blocks
                rects.append(block_rect)
                rect_center = self.calc_rect_center(block_rect, reverse_y=True)
                rect_centers.append(rect_center)
                point_text = f"({page_cnt}.{block_cnt})"
                point_texts.append(point_text)

                # Logging
                token_cnt_str = ""
                if block_type == "text":
                    token_cnt_str = f"| (tokens: {token_cnt})"
                logger.info(
                    f"<{block_type}> Block: {page_cnt}.{block_cnt} {token_cnt_str}"
                )

                logger.debug(f"{rect_center} - {block_rect}")
                logger.debug(block_text)

            doc_token_cnt += page_token_cnt

            logger.info(f"{page_token_cnt} tokens in Page {page_cnt}.")
            logger.info(
                colored(
                    add_fillers(f"End [Page {page_cnt}] [{len(page_blocks)} blocks]"),
                    "light_magenta",
                )
            )

        doc_token_cnt_kilo = kilo_count(doc_token_cnt)
        logger.info(
            colored(
                f"{doc_token_cnt_kilo}k ({doc_token_cnt}) tokens in whole document.\n",
                "light_green",
            )
        )

        categorizer = PDFTextBlockCategorizer(categorize_vectors)
        categorizer.run()

        # self.plot_text_block_rect(
        #     categories=categorizer.categories,
        #     points=rect_centers,
        #     rects=rects,
        #     point_texts=point_texts,
        # )

        filtered_doc_blocks = self.remove_no_body_text_blocks(
            doc_blocks=doc_blocks, categories=categorizer.categories
        )

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

    def extract_all_text_block_dicts(self):
        """
        * https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractDICT
        * https://pymupdf.readthedocs.io/en/latest/textpage.html#structure-of-dictionary-outputs
        * https://pymupdf.readthedocs.io/en/latest/_images/img-textpage.png
        * https://pymupdf.readthedocs.io/en/latest/textpage.html#block-dictionaries

        Data Structure of a Text/Image Block Dict in Page Blocks:

        ```json
        {
            "width": <float>,
            "height": <float>,
            "blocks": [
                {
                    "type": <int> (0),
                    "bbox": <tuple> (4 floats),
                    "number": <int> (start from 0),
                    "lines": [
                        {
                            "bbox": <tuple> (4 floats),
                            "wmode": <int> (0),
                            "dir": <tuple> (2 floats),
                            "spans": [
                                {
                                    "bbox": <tuple> (4 floats),
                                    "origin": <tuple> (2 floats),
                                    "flags": <int>,
                                    "size": <float>,
                                    "font" <str>,
                                    "color": <int>,
                                    "ascender": <float>,
                                    "descender": <float>,
                                    "text": <str>
                                },
                                ...
                            ]
                        },
                        ...
                    ]
                },
                {
                    "type": <int> (1),
                    "bbox": <tuple> (4 floats),
                    "number": <int>,
                    "width": <float>,
                    "height": <float>,
                    "ext": <str> ("jpeg"),
                    "colorspace": <int>,
                    "xres": <int>,
                    "yres": <int>,
                    "bpc": <int>,
                    "transform": <tuple> (6 floats),
                    "size": <int>,
                    "image": <bytes>
                },
                ...
            ]
        }
        ```
        """
        for page_idx, page in islice(enumerate(self.pdf_doc), len(self.pdf_doc)):
            page_dict = page.get_text("dict")
            page_blocks = page_dict["blocks"]
            logger.info(f"{len(page_blocks)} blocks")
            block_cnt = 0
            for block in page_blocks:
                block_type = "text" if block["type"] == 0 else "image"
                block_num = block["number"]
                block_cnt = block_num + 1
                block_bbox = block["bbox"]
                logger.info(f"<{block_type}> Block {block_cnt}")

                if block_type == "text":
                    lines = block["lines"]
                    logger.debug(f"{len(lines)} lines")
                    block_text = ""
                    fontsize_list = []
                    font_properties = []
                    for line in lines:
                        line_bbox = line["bbox"]
                        spans = line["spans"]
                        # logger.info(f"{len(spans)} spans")
                        line_text = ""
                        for span in spans:
                            span_bbox = span["bbox"]
                            span_origin = span["origin"]
                            span_text = span["text"]
                            span_font = span["font"]
                            span_fontsize = round(span["size"], 1)
                            span_flags = span["flags"]
                            fontsize_list.append(span_fontsize)
                            font_properties = font_flags_to_list(span_flags)
                            logger.debug(
                                f"<font: {span_font}> <fontsize: {span_fontsize}>"
                            )
                            logger.debug(colored(f"{span_text}", "light_cyan"))
                            line_text += f"{span_text}"
                        block_text += f"{line_text}\n"

                    # block = block_text.replace("\n", " ")
                    block_text = block_text.replace(" ﬁ ", "fi")
                    most_common_fontsize = Counter(fontsize_list).most_common(1)[0][0]
                    logger.info(f"<{most_common_fontsize}>")
                    logger.info(colored(f"{block_text}", "light_cyan"))

                elif block_type == "image":
                    img_width = block["width"]
                    img_height = block["height"]
                    img_ext = block["ext"]
                    img_size = block["size"]
                    img_size_mb = round(img_size / (1024 * 1024), 1)
                    img_bytes = block["image"]
                    logger.info(
                        colored(
                            f"<{img_ext.upper()}> <{img_width}x{img_height}> ({img_size_mb} MB)",
                            "light_magenta",
                        )
                    )
                else:
                    raise ValueError(f"Unknown block type: {block_type}")

    def extract_all_text_htmls(self):
        html_str = ""
        for page_idx, page in islice(enumerate(self.pdf_doc), len(self.pdf_doc)):
            html_str += page.get_text("html")
        with open("output.html", "w") as wf:
            wf.write(html_str)

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

    def extract_tables(self):
        table_parser = PDFTableParser(self.pdf_fullpath)
        table_parser.run()

    def run(self):
        # self.extract_all_texts()
        # self.extract_all_text_blocks()
        # self.extract_toc()
        # self.extract_images()
        # self.extract_all_text_htmls()
        # self.extract_all_text_block_dicts()
        self.extract_tables()


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
