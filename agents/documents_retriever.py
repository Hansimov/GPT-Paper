import json
from documents.multi_pdf_extractor import MultiPDFExtractor


class DocumentsRetriever:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.multi_pdf_extractor = MultiPDFExtractor(project_dir)

    def query(self, query: str, rerank_n=20, text_only=False) -> list:
        query_results = self.multi_pdf_extractor.query_docs(
            query, rerank_n=rerank_n, quiet=True
        )
        if text_only:
            query_results = [item["text"] for item in query_results]
        else:
            query_results = [
                {
                    "pdf_name": item["pdf_name"],
                    "page_idx": item["page_idx"],
                    "region_idx": item["region_idx"],
                    "text": item["text"],
                }
                for item in query_results
            ]
        # query_results = json.dumps(query_results, indent=2, ensure_ascii=False)
        return query_results

    def query_multi(self, queries: list, rerank_n=20, text_only=False) -> list:
        query_results = []
        for query in queries:
            query_results.append(
                self.query(query, rerank_n=rerank_n, text_only=text_only)
            )
        query_results = self.combine_query_results(query_results)
        return query_results

    def combine_query_results(self, query_results: list) -> list:
        combined_query_res = []
        for query_result in query_results:
            # if type(query_result) == str:
            #     query_result = json.loads(query_result)
            combined_query_res.extend(query_result)

        # Remove duplicates
        combined_query_res = [
            dict(t) for t in {tuple(d.items()) for d in combined_query_res}
        ]

        print(f"{len(combined_query_res)} queries after combined.")
        return combined_query_res
