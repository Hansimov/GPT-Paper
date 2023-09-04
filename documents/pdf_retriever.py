from pathlib import Path
from utils.logger import logger
from utils.calculator import get_int_digits


class MultiPDFRetriever:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self, project_dir):
        self.project_path = self.pdf_root / project_dir
        self.pdf_paths = sorted(list(self.project_path.glob("*.pdf")))

    def list_pdfs(self):
        logger.mesg(f"[{self.project_path}] has {len(self.pdf_paths)} PDFs:")
        pdf_count_digits = get_int_digits(len(self.pdf_paths))
        for idx, pdf_path in enumerate(self.pdf_paths):
            logger.file(f"{idx+1:>{pdf_count_digits}}. {pdf_path.name}", indent=2)


if __name__ == "__main__":
    multi_pdf_retriever = MultiPDFRetriever("cancer_review")
    multi_pdf_retriever.list_pdfs()
