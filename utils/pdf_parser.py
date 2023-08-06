from pdfminer.high_level import extract_text
from pathlib import Path


class PDFExtractor:
    def __init__(self):
        pass

    def run(self):
        pdf_root = Path(__file__).parents[1] / "pdfs"
        pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        pdf_fullpath = pdf_root / pdf_filename
        text = extract_text(pdf_fullpath)
        print(text)


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
