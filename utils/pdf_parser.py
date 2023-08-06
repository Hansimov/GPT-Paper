# pip install 'pdfminer.six[image]'
from pdfminer.layout import LTImage, LTContainer, LTPage
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.image import ImageWriter
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

    def run(self):
        pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        pdf_fullpath = self.pdf_root / pdf_filename
        # text = extract_text(pdf_fullpath)
        # print(text)
        pages = list(extract_pages(pdf_fullpath))
        print(f"Pages: {len(pages)}")
        for idx, page in enumerate(pages):
            print(f"Extracting images from page: {idx+1}")
            self.extract_image(page)


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
