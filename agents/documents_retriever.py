import json
from documents.multi_pdf_extractor import MultiPDFExtractor
from collections import defaultdict
from operator import itemgetter
from typing import Union


class DocumentsRetriever:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.multi_pdf_extractor = MultiPDFExtractor(project_dir)

    def query(self, queries: Union[list, str], rerank_n=20) -> list:
        if type(queries) == str:
            queries = [queries]

        queries_results = []
        for query in queries:
            query_results = self.multi_pdf_extractor.query_docs(
                query, rerank_n=rerank_n, quiet=True
            )
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
            queries_results.append(query_results)

        queries_results = self.combine_query_results(queries_results)
        return queries_results

    def group_query_results_by_pdf_name(self, query_results: list) -> dict:
        # Group query results by pdf_name
        grouped_queries = defaultdict(list)
        for item in query_results:
            pdf_name = item["pdf_name"]
            grouped_queries[pdf_name].append(
                {
                    "text": item["text"],
                    "page_idx": item["page_idx"],
                    "region_idx": item["region_idx"],
                    "score": item["score"],
                }
            )
        # Sort grouped query results by pdf_name
        # grouped_queries = dict(sorted(grouped_queries.items(), key=itemgetter(0)))

        # Sort grouped query results by average score
        grouped_queries = dict(
            sorted(
                grouped_queries.items(),
                key=lambda x: sum(item["score"] for item in x[1]) / len(x[1]),
                reverse=True,
            )
        )

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

        # remove duplicates
        unique_keys = ("pdf_name", "page_idx", "region_idx")

        combined_query_res = list(
            {tuple(d[k] for k in unique_keys): d for d in combined_query_res}.values()
        )

        print(f"{len(combined_query_res)} queries after combined.")

        combined_query_res = self.group_query_results_by_pdf_name(combined_query_res)

        return combined_query_res
