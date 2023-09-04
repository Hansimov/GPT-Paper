from utils.file import rmtree_and_mkdir
from documents.pdf_visual_extractor import PDFVisualExtractor
from pathlib import Path
from tqdm import tqdm
from utils.logger import logger, Runtimer
from utils.calculator import get_int_digits
from utils.layout_analyzer import DITLayoutAnalyzer
from utils.tokenizer import BiEncoderX, CrossEncoderX
import pandas as pd
import pickle


class MultiPDFExtractor:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self, project_dir):
        self.project_path = self.pdf_root / project_dir
        self.result_root = self.project_path / "_results"
        self.pdf_paths = sorted(list(self.project_path.glob("*.pdf")))
        self.pdfs_count = len(self.pdf_paths)
        self.pdfs_count_digits = get_int_digits(len(self.pdf_paths))
        self.docs_embeddings_path = self.result_root / "docs_embeddings.pkl"

    def list_pdfs(self):
        logger.mesg(f"[{self.project_path}] has {self.pdfs_count} PDFs:")
        for idx, pdf_path in enumerate(self.pdf_paths):
            logger.file(f"{idx+1:>{self.pdfs_count_digits}}. {pdf_path.name}", indent=2)

    def extract_pdfs(self):
        # layout_analyzer = DITLayoutAnalyzer(size="large")
        # layout_analyzer.setup_model(quiet=False)

        # bi_encoder = BiEncoderX()
        # bi_encoder.load_model()

        for pdf_idx, pdf_path in enumerate(tqdm(self.pdf_paths[:], colour="green")):
            logger.store_level()
            logger.note(
                f"[{pdf_idx+1:>{self.pdfs_count_digits}}/{self.pdfs_count}] {pdf_path.name}"
            )
            logger.store_indent()
            logger.indent(2)
            extractor = PDFVisualExtractor(pdf_path)
            logger.mesg("> Dump page images")
            extractor.dump_pdf_to_page_images()
            logger.mesg("> Annotate page images")
            extractor.annotate_page_images(layout_analyzer=None)
            logger.mesg("> Remove overlaps, order regions, and crop")
            extractor.remove_overlapped_layout_regions_from_pages()
            extractor.order_pages_regions()
            extractor.crop_page_images("ordered")
            logger.mesg("> Extract texts, and combine to doc")
            extractor.extract_texts_from_pages()
            extractor.combine_page_texts_to_doc()
            logger.mesg("> Text to embeddings")
            extractor.doc_texts_to_embeddings(bi_encoder=None)
            logger.restore_indent()
            # extractor.query_region_texts()
            logger.restore_level()

    def combine_docs_embeddings(self, overwrite=False):
        if not overwrite and self.docs_embeddings_path.exists():
            return
        rmtree_and_mkdir(self.result_root)

        self.docs_embeddings_df = pd.DataFrame()
        for idx, pdf_path in enumerate(self.pdf_paths):
            embedding_path = pdf_path.with_suffix("") / "texts" / "embeddings.pkl"
            df = pd.read_pickle(embedding_path)
            self.docs_embeddings_df = self.docs_embeddings_df.append(df)

        print(self.docs_embeddings_df)
        logger.note(f"> Dump embeddings of {self.pdfs_count} PDFs")
        logger.file(f"- {self.docs_embeddings_path}", indent=2)
        self.docs_embeddings_df.to_pickle(self.docs_embeddings_path)

    def query(self):
        pass


if __name__ == "__main__":
    with Runtimer():
        multi_pdf_extractor = MultiPDFExtractor("cancer_review")
        # multi_pdf_retriever.list_pdfs()
        # multi_pdf_retriever.extract_pdfs()
        multi_pdf_extractor.combine_docs_embeddings()
