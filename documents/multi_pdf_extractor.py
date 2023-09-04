from pathlib import Path
from utils.logger import logger, Runtimer
from utils.calculator import get_int_digits
from documents.pdf_visual_extractor import PDFVisualExtractor
from utils.layout_analyzer import DITLayoutAnalyzer
from tqdm import tqdm


class MultiPDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self, project_dir):
        self.project_path = self.pdf_root / project_dir
        self.pdf_paths = sorted(list(self.project_path.glob("*.pdf")))
        self.pdfs_count = len(self.pdf_paths)
        self.pdfs_count_digits = get_int_digits(len(self.pdf_paths))

    def list_pdfs(self):
        logger.mesg(f"[{self.project_path}] has {self.pdfs_count} PDFs:")
        for idx, pdf_path in enumerate(self.pdf_paths):
            logger.file(f"{idx+1:>{self.pdfs_count_digits}}. {pdf_path.name}", indent=2)

    def extract_pdfs(self):
        layout_analyzer = DITLayoutAnalyzer(size="large")
        logger.store_level()
        for pdf_idx, pdf_path in enumerate(tqdm(self.pdf_paths[2:8], colour="green")):
            logger.note(
                f"[{pdf_idx+1:>{self.pdfs_count_digits}}/{self.pdfs_count}] {pdf_path.name}"
            )
            logger.store_indent()
            logger.indent(2)
            extractor = PDFVisualExtractor(pdf_path)
            logger.note("> Dump page images")
            extractor.dump_pdf_to_page_images()
            logger.note("> Annotate page images")
            extractor.annotate_page_images(layout_analyzer=layout_analyzer)
            logger.note("> Remove overlaps, order regions, and crop")
            extractor.remove_overlapped_layout_regions_from_pages()
            extractor.order_pages_regions()
            extractor.crop_page_images("ordered")
            logger.restore_indent()
            # extractor.extract_texts_from_pages()
            # extractor.combine_page_texts_to_doc()
            # extractor.doc_texts_to_embeddings()
            # extractor.query_region_texts()
        logger.restore_level()


if __name__ == "__main__":
    with Runtimer():
        multi_pdf_retriever = MultiPDFExtractor("cancer_review")
        # multi_pdf_retriever.list_pdfs()
        multi_pdf_retriever.extract_pdfs()
