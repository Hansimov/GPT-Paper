# pip install 'pdfminer.six[image]'
from pdfminer.layout import LTImage, LTContainer, LTPage
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.image import ImageWriter
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pathlib import Path


class PDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self):
        pass

    def get_image(self, layout_object):
        if isinstance(layout_object, LTImage):
            return layout_object
        if isinstance(layout_object, LTContainer):
            for child in layout_object:
                return self.get_image(child)
        else:
            return None

    def extract_image(self, page: LTPage):
        images = list(filter(bool, map(self.get_image, page)))
        iw = ImageWriter(self.pdf_root / "images")
        for image in images:
            iw.export_image(image)

    def extract_images(self):
        pages = list(extract_pages(self.pdf_fullpath))
        print(f"Pages: {len(pages)}")
        for idx, page in enumerate(pages):
            print(f"Extracting images from page: {idx+1}")
            self.extract_image(page)

    def replace_html_entities(self, text):
        symbols = {
            "&nbsp;": " ",
            "&amp;": "&",
        }
        for k, v in symbols.items():
            text = text.replace(k, v)
        return text

    def format_outline(self, pdf_outlines):
        levels = [0] * 10
        lines = []
        for (level, title, dest, action, se) in pdf_outlines:
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
        with open(self.pdf_fullpath, "rb") as rf:
            pdf_parser = PDFParser(rf)
            pdf_doc = PDFDocument(pdf_parser)
            pdf_outlines = pdf_doc.get_outlines()
            # Introduction to PDF Destinations
            # * https://evermap.com/Tutorial_ABM_Destinations.asp
            self.format_outline(pdf_outlines)

    def run(self):
        pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        pdf_filename = "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images.pdf"
        pdf_filename = "HEP 2020 Predicting survival after hepatocellular carcinoma resection using.pdf"
        self.pdf_fullpath = self.pdf_root / pdf_filename
        # text = extract_text(pdf_fullpath)
        # print(text)
        self.extract_toc()


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
