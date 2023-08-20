import fitz
import json
import matplotlib.pyplot as plt
import os
import shutil
from categorizers.body_text_block_categorizer import BodyTextBlockCategorizer
from categorizers.fragmented_block_categorizer import FragmentedTextBlockCategorizer
from collections import Counter
from itertools import islice, chain
from matplotlib.patches import Rectangle
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from termcolor import colored
from utils.calculator import (
    flatten_len,
    kilo_count,
    font_flags_to_list,
    rect_area,
    char_per_pixel,
    avg_line_width,
    rect_contain,
    rect_overlap,
)
from utils.logger import logger, add_fillers
from utils.tokenizer import Tokenizer
from utils.text_processor import TextBlock
from utils.layout_analyzer import (
    DITLayoutAnalyzer,
    calc_regions_overlaps,
    remove_regions_overlaps,
    draw_regions_on_page,
)


class PDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"
    image_root = pdf_root / "images"

    def __init__(self):
        # pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        self.pdf_filename = "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images.pdf"
        # pdf_filename = "HEP 2020 Predicting survival after hepatocellular carcinoma resection using.pdf"
        # pdf_filename = "Nature Cancer 2020 Pan-cancer computational histopathology reveals.pdf"
        # pdf_filename = "Deep learning for evaluation of microvascular invasion in hepatocellular carcinoma from tumor areas of histology images.pdf"
        self.pdf_fullpath = self.pdf_root / self.pdf_filename
        self.pdf_doc = fitz.open(self.pdf_fullpath)
        self.init_paths()

    def init_paths(self):
        self.assets_path = self.pdf_root / Path(self.pdf_filename).stem

        self.page_images_path = self.assets_path / "pages"
        self.annotated_page_images_path = self.assets_path / "pages_annotated"
        self.cropped_page_images_path = self.assets_path / "crops"
        self.no_overlap_page_images_path = self.assets_path / "pages_no_overlap"

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

        categorizer = BodyTextBlockCategorizer(categorize_vectors)
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
                    "type": <int> (0), // "text"
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
                    "type": <int> (1), // "image"
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
        doc_blocks = [
            page.get_text("dict")["blocks"]
            for page_idx, page in islice(enumerate(self.pdf_doc), len(self.pdf_doc))
        ]
        body_text_block_categorizer = BodyTextBlockCategorizer(doc_blocks)
        body_text_block_categorizer.run()
        self.filtered_doc_blocks = body_text_block_categorizer.filtered_doc_blocks

        filtered_doc_text_blocks = [
            [block for block in page_blocks if block["type"] == 0]
            for page_blocks in self.filtered_doc_blocks
        ]
        logger.info(
            f"{flatten_len(filtered_doc_text_blocks)} text blocks in {flatten_len(self.filtered_doc_blocks)} blocks."
        )

        fragmented_text_block_categorizer = FragmentedTextBlockCategorizer(
            filtered_doc_text_blocks
        )
        fragmented_text_block_categorizer.run()

        return

        for page_idx, page_blocks in enumerate(self.filtered_doc_blocks[:9]):
            doc_blocks.append(page_blocks)
            logger.info(
                colored(
                    f"{len(page_blocks)} blocks in Page {page_idx+1}", "light_magenta"
                )
            )
            block_cnt = 0
            for block in page_blocks:
                block_type = "text" if block["type"] == 0 else "image"
                block_num = block["number"]
                block_cnt += 1
                block_bbox = block["bbox"]
                block_area = rect_area(*block_bbox)

                logger.info(
                    colored(
                        f"<{block_type}> Block {block_num}/{len(page_blocks)} "
                        f"in Page {page_idx+1}/{len(self.filtered_doc_blocks)}",
                        "light_yellow",
                    )
                )

                if block_type == "text":
                    tblock = TextBlock(block)
                    block_text = tblock.get_block_text()
                    block_bbox = tblock.get_bbox()
                    block_font, block_fontsize = tblock.get_block_main_font()
                    block_tokens_num = tblock.get_block_tokens_num()
                    block_density = char_per_pixel(len(block_text), block_area)
                    logger.info(
                        colored(
                            f"<{block_font}> <{block_fontsize}> "
                            f"({len(block_text)}/{block_area}) ({block_density}) "
                            f"({avg_line_width(block_text)})",
                            "light_magenta",
                        )
                    )
                    logger.info(colored(f"{block_tokens_num} tokens.", "light_green"))
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
        table_parser = PDFTableExtractor(self.pdf_fullpath)
        table_parser.run()

    def dump_pdf_to_page_images(self, dpi=300):
        shutil.rmtree(self.page_images_path, ignore_errors=True)
        self.page_images_path.mkdir(parents=True, exist_ok=True)
        # transform_matrix = fitz.Matrix(dpi / 72, dpi / 72)
        logger.note(f"> Dumping PDF to image pages [dpi={dpi}]")
        logger.file(f"  - {self.page_images_path}")
        for page_idx, page in enumerate(self.pdf_doc):
            logger.msg(f"    - Page {page_idx+1}")
            image_path = self.page_images_path / f"page_{page_idx+1}.png"
            pix = page.get_pixmap(dpi=dpi)
            pix.save(image_path)
            # pix = page.get_pixmap(matrix=transform_matrix)
            # pix.pil_save(image_path, dpi=(dpi, dpi))

    def annotate_page_images(self):
        shutil.rmtree(self.annotated_page_images_path, ignore_errors=True)
        self.annotated_page_images_path.mkdir(parents=True, exist_ok=True)

        logger.note(f"> Annotating page images")
        # logger.file(f"  * {self.annotated_page_images_path}")

        logger.set_indent(2)

        layout_analyzer = DITLayoutAnalyzer(size="large")
        layout_analyzer.setup_model()

        page_image_paths = sorted(
            [
                self.page_images_path / p
                for p in os.listdir(self.page_images_path)
                if Path(p).suffix.lower() in [".jpg", ".png", "jpeg"]
                and not Path(p).stem.endswith("_annotated")
            ],
            key=lambda x: int(x.stem.split("_")[-1]),
        )

        for page_image_path in page_image_paths:
            output_image_path = self.annotated_page_images_path / page_image_path.name
            # output_image_path = self.page_images_path / (
            #     page_image_path.stem + "_annotated" + page_image_path.suffix
            # )
            logger.set_indent(2)
            logger.file(f"- {page_image_path.name}")
            logger.set_indent(4)
            pred_output, annotate_info_json_path = layout_analyzer.annotate_image(
                input_image_path=page_image_path,
                output_image_path=output_image_path,
            )
            draw_regions_on_page(
                annotate_info_json_path,
                output_parent_path=self.annotated_page_images_path,
            )
        logger.reset_indent()

    def crop_page_image(self, annotate_info_json_path, padding=2):
        with open(annotate_info_json_path, "r") as rf:
            annotate_infos = json.load(rf)
        page_image_path = Path(annotate_infos["page"]["original_image_path"])
        page_num = int(page_image_path.stem.split("_")[-1])
        page_image = Image.open(page_image_path)
        page_image_width, page_image_height = page_image.size
        regions = annotate_infos["regions"]
        region_image_page_path = self.cropped_page_images_path / f"page_{page_num}"
        region_image_page_path.mkdir(parents=True, exist_ok=True)

        logger.msg(f"- Crop Page {page_num} to {len(regions)} regions")

        for region in regions:
            region_idx = region["idx"]
            region_box = region["box"]
            region_thing = region["thing"]
            region_score = region["score"]
            region_box = [round(x) for x in region_box]
            crop_region_box = [
                max(0, region_box[0] - padding),
                max(0, region_box[1] - padding),
                min(page_image_width, region_box[2] + padding),
                min(page_image_height, region_box[3] + padding),
            ]
            region_image = page_image.crop(crop_region_box)
            region_image_path = region_image_page_path / (
                f"region_{region_idx}_{region_thing}_{region_score}"
                + page_image_path.suffix
            )
            region_image.save(region_image_path)

    def draw_regions_on_pages(self, output_parent_path):
        shutil.rmtree(output_parent_path, ignore_errors=True)
        output_parent_path.mkdir(parents=True, exist_ok=True)

        annotate_json_paths = self.get_annotate_json_paths()
        logger.note(f"> Draw on page images")
        for page_idx, annotate_json_path in enumerate(annotate_json_paths):
            logger.store_indent()
            logger.indent(2)
            draw_regions_on_page(annotate_json_path, output_parent_path)
            logger.restore_indent()

    def get_annotate_json_paths(self):
        annotate_json_paths = sorted(
            [
                self.annotated_page_images_path / p
                for p in os.listdir(self.annotated_page_images_path)
                if Path(p).suffix.lower() == ".json"
            ],
            key=lambda x: int(x.stem.split("_")[-1]),
        )
        return annotate_json_paths

    def crop_page_images(self):
        shutil.rmtree(self.cropped_page_images_path, ignore_errors=True)
        self.cropped_page_images_path.mkdir(parents=True, exist_ok=True)
        annotate_json_paths = self.get_annotate_json_paths()

        logger.note(f"> Croping page images")
        logger.set_indent(2)
        for annotate_json_path in annotate_json_paths:
            self.crop_page_image(annotate_json_path)
        logger.reset_indent()

    def remove_overlapped_layout_regions_from_page(self, annotate_info_json_path):
        with open(annotate_info_json_path, "r") as rf:
            annotate_infos = json.load(rf)
        regions = annotate_infos["regions"]

        logger.store_indent()
        logger.indent(2)
        logger.note(f"- Detect overlaps of {len(annotate_infos['regions'])} regions")
        regions_overlaps = calc_regions_overlaps(regions)
        logger.restore_indent()

        no_overlap_regions_infos = annotate_infos.copy()
        no_overlap_regions_infos["regions"] = remove_regions_overlaps(
            regions, regions_overlaps
        )
        no_overlap_regions_infos["page"]["original_image_path"] = annotate_infos[
            "page"
        ]["original_image_path"]
        no_overlap_regions_infos["page"]["current_image_path"] = str(
            self.no_overlap_page_images_path
            / Path(annotate_infos["page"]["original_image_path"]).name
        )
        no_overlap_regions_info_json_path = str(
            self.no_overlap_page_images_path
            / (Path(annotate_infos["page"]["current_image_path"]).stem + ".json")
        )

        logger.note("> Dump no-overlap regions info json")
        logger.file(f"  - {no_overlap_regions_info_json_path}")
        with open(no_overlap_regions_info_json_path, "w") as wf:
            json.dump(no_overlap_regions_infos, wf, indent=4)

        draw_regions_on_page(
            no_overlap_regions_info_json_path, self.no_overlap_page_images_path
        )

    def remove_overlapped_layout_regions_from_pages(self):
        annotate_json_paths = self.get_annotate_json_paths()
        shutil.rmtree(self.no_overlap_page_images_path, ignore_errors=True)
        self.no_overlap_page_images_path.mkdir(parents=True, exist_ok=True)
        for page_idx, annotate_json_path in enumerate(annotate_json_paths):
            with open(annotate_json_path, "r") as rf:
                annotate_infos = json.load(rf)
            logger.store_indent()
            logger.note(f"- Remove overlaps on Page {page_idx+1}")
            self.remove_overlapped_layout_regions_from_page(annotate_json_path)
            logger.restore_indent()

    def run(self):
        # self.extract_all_texts()
        # self.extract_all_text_blocks()
        # self.extract_toc()
        # self.extract_images()
        # self.extract_all_text_htmls()
        # self.extract_all_text_block_dicts()
        # self.extract_tables()
        # self.dump_pdf_to_page_images()
        # self.annotate_page_images()
        # self.crop_page_images()
        self.remove_overlapped_layout_regions_from_pages()


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
