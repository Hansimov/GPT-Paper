import camelot
import tabula
from utils.logger import Logger

logger = Logger().logger


class PDFTableExtractor:
    def __init__(self, pdf_fullpath):
        self.pdf_fullpath = str(pdf_fullpath)

    def extract_tables(self):
        logger.info(f"Extracting tables from: [{self.pdf_fullpath}]")
        # tables = camelot.read_pdf(
        #     self.pdf_fullpath,
        #     pages="7",
        #     flavor="lattice",
        # )
        tables = tabula.read_pdf(self.pdf_fullpath, pages="all")
        logger.info(f"{len(tables)} tables found.")
        for table in tables:
            print(table)

    def run(self):
        self.extract_tables()
