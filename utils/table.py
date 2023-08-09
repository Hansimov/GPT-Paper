import camelot
from utils.logger import Logger

logger = Logger().logger


class PDFTableParser:
    def __init__(self, pdf_fullpath):
        self.pdf_fullpath = str(pdf_fullpath)

    def extract_tables(self):
        logger.info(f"Extracting tables from: [{self.pdf_fullpath}]")
        tables = camelot.read_pdf(
            self.pdf_fullpath,
            pages="7",
            flavor="lattice",
        )
        logger.info(f"{len(tables)} tables found.")
        for table in tables:
            print(table.df)

    def run(self):
        self.extract_tables()
