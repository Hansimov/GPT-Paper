# pip install 'pdfminer.six[image]'
# python -m pip install --upgrade pymupdf
import fitz
from pathlib import Path


class PDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"
    image_root = pdf_root / "images"

    def __init__(self):
        pass

    def extract_text(self, pdf_doc):
        for idx, page in enumerate(pdf_doc):
            text = page.get_text()
            print(f"Page {idx+1}:")
            print(text)

    def save_image(self, pdf_doc, xref, basepath):
        ext_image = pdf_doc.extract_image(xref)
        ext = ext_image["ext"]
        fullpath = basepath.with_suffix(f".{ext}")
        print(f"  > Saving image to: {fullpath}")
        # bytes = ext_image["image"]
        # with open(fullpath, "wb") as wf:
        #     wf.write(bytes)
        pix = fitz.Pixmap(pdf_doc, xref)
        pix.save(fullpath)

    def extract_images(self, pdf_doc):
        for idx, page in enumerate(pdf_doc):
            img_infos = page.get_images()
            print(f"Page {idx}: {img_infos}")
            for info in img_infos:
                xref = info[0]
                img_basepath = self.image_root / f"img_{idx+1}"
                self.save_image(pdf_doc, xref, img_basepath)

    def replace_html_entities(self, text):
        symbols = {
            "&nbsp;": " ",
            "&amp;": "&",
        }
        for k, v in symbols.items():
            text = text.replace(k, v)
        return text

    def format_toc(self, pdf_toc):
        levels = [0] * 10
        lines = []
        for level, title, page, dest in pdf_toc:
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

    def extract_toc(self, pdf_doc):
        pdf_toc = pdf_doc.get_toc(simple=False)
        print(pdf_toc)
        self.format_toc(pdf_toc)

    def run(self):
        pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        # pdf_filename = "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images.pdf"
        # pdf_filename = "HEP 2020 Predicting survival after hepatocellular carcinoma resection using.pdf"
        self.pdf_fullpath = self.pdf_root / pdf_filename
        pdf_doc = fitz.open(self.pdf_fullpath)
        # self.extract_text(pdf_doc)
        # self.extract_toc(pdf_doc)
        self.extract_images(pdf_doc)


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_extractor.run()
