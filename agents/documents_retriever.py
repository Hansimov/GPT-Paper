import json
from documents.multi_pdf_extractor import MultiPDFExtractor
from collections import defaultdict
from operator import itemgetter


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
                    "score": item["score"],
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

    def group_query_results_by_pdf_name(self, query_results: list) -> dict:
        # Group query results by pdf_name
        grouped_queries = defaultdict(list)
        for item in query_results:
            pdf_name = item["pdf_name"]
            page_idx = item["page_idx"]
            region_idx = item["region_idx"]
            text = item["text"]
            grouped_queries[pdf_name].append(
                {
                    "text": text,
                    "page_idx": page_idx,
                    "region_idx": region_idx,
                }
            )
        # Sort grouped query results by pdf_name
        grouped_queries = dict(sorted(grouped_queries.items(), key=itemgetter(0)))

        sorted_grouped_queries = []
        # ref_idx = 1
        for pdf_name, regions in grouped_queries.items():
            # Sort regions by page_idx and region_idx
            regions = sorted(regions, key=itemgetter("page_idx", "region_idx"))
            # # Add ref_sub_idx to regions
            # ref_sub_idx = 1
            # for i in range(len(regions)):
            #     regions[i]["ref_sub_idx"] = ref_sub_idx
            #     ref_sub_idx += 1
            # Combine page_idx, region_idx and text to region
            sorted_grouped_queries.append(
                {
                    "pdf_name": pdf_name,
                    # "ref_idx": ref_idx,
                    "regions": regions,
                }
            )
            # ref_idx += 1
        return sorted_grouped_queries

    def combine_query_results(self, query_results: list) -> list:
        combined_query_res = []
        for query_result in query_results:
            # if type(query_result) == str:
            #     query_result = json.loads(query_result)
            combined_query_res.extend(query_result)

        # Sort by score
        combined_query_res = sorted(
            combined_query_res, key=lambda x: x["score"], reverse=True
        )

        # drop score items
        combined_query_res = [
            {
                "pdf_name": item["pdf_name"],
                "page_idx": item["page_idx"],
                "region_idx": item["region_idx"],
                "text": item["text"],
            }
            for item in combined_query_res
        ]
        # remove duplicates
        combined_query_res = [
            dict(t) for t in {tuple(d.items()) for d in combined_query_res}
        ]

        print(f"{len(combined_query_res)} queries after combined.")

        combined_query_res = self.group_query_results_by_pdf_name(combined_query_res)

        return combined_query_res