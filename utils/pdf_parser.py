# pip install 'pdfminer.six[image]'
# python -m pip install --upgrade pymupdf
import fitz
from pathlib import Path
from itertools import islice


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

    def extract_all_text_blocks(self):
        # * https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractBLOCKS
        for idx, page in islice(enumerate(self.pdf_doc), 2):
            blocks = page.get_text("blocks")
            print(f"=== Start Page {idx+1}: {len(blocks)} blocks ===")
            block_cnt = 0
            for block in blocks:
                block_cnt += 1
                block_rect = block[:4]
                block_text = block[4]
                block_num = block[5]
                block_type = "text" if block[6] == 0 else "image"
                print(f"Block: {block_num+1}")
                print(f"<{block_type}> {block_rect}")
                print(block_text)

            print(f"=== End Page {idx+1}: {len(blocks)} blocks ===\n")

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
