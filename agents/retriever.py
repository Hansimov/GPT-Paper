from documents.multi_pdf_extractor import MultiPDFExtractor


class DocumentsRetriever:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.multi_pdf_extractor = MultiPDFExtractor(project_dir)

    def query(self, query, rerank_n=20, text_only=True):
        query_results = self.multi_pdf_extractor.query_docs(
            query, rerank_n=rerank_n, quiet=True
        )
        if text_only:
            query_results = [item["text"] for item in query_results]
        return query_results
