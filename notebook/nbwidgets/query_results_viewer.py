import html
import ipywidgets as widgets
from nbwidgets.styles import calc_font_color_by_background
from utils.tokenizer import WordTokenizer
from IPython.display import display


class QueryResultsViewer:
    def __init__(self, queries=None, query_results=None):
        self.queries = queries
        self.query_results = query_results
        self.create_widgets()
        self.query_results_to_html()

    def display(self):
        display(self.html_widget)

    def create_widgets(self):
        self.html_widget = widgets.HTML(value="")

    def query_results_to_html(self):
        word_tokenizer = WordTokenizer()
        if not self.query_results:
            self.html_str = ""
            return

        region_scores = [
            region["score"]
            for query_result in self.query_results
            for region in query_result["regions"]
        ]

        def normalize_score(score):
            return (score - min(region_scores)) / (
                max(region_scores) - min(region_scores)
            )

        html_str = ""
        for query_result in self.query_results:
            pdf_name = query_result["pdf_name"]
            pdf_name_html = f"<h3>{pdf_name}</h3>\n"

            region_texts_html = ""
            for region in query_result["regions"]:
                normalized_region_score = normalize_score(region["score"])
                page_idx = region["page_idx"]
                region_idx = region["region_idx"]
                region_text = region["text"]
                token_count = word_tokenizer.count_tokens(
                    region_text.replace("\n", " ")
                )
                region_background_color = (0, 150, 0, normalized_region_score)
                region_text_color = calc_font_color_by_background(
                    region_background_color
                )
                region_text_style = f"""
                background-color: rgba{region_background_color};
                color: {region_text_color}
                """
                region_text_html = f"""
                <li>
                    <details>
                        <summary style='{region_text_style}' title='{html.escape(region_text)}'>
                            Page {page_idx}, Region {region_idx},
                            Tokens {token_count}, Score {round(float(normalized_region_score),2)}
                        </summary>
                        {region_text}
                    </details>
                </li>\n
                """
                region_texts_html += region_text_html

            region_texts_html = f"<ol>\n{region_texts_html}\n</ol>"
            html_str += f"<li>{pdf_name_html}\n{region_texts_html}</li>"

        region_text_count = sum(
            [len(query_result["regions"]) for query_result in self.query_results]
        )
        queries_str = "<br>".join(
            [f"{idx+1}. {query}" for idx, query in enumerate(self.queries)]
        )
        html_str = f"""
        <details>
            <summary>
            Related {region_text_count} Paragraphs in {len(self.query_results)} References of Queries:<br>
            {queries_str}
            </summary>
            <div class='query_results'>
                <ol>
                    {html_str}
                </ol>
            </div>
        </details>
        """

        style_str = f"""
        <style>
            .query_results {{
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid gray;
            }}
        </style>
        """
        html_str += style_str
        self.html_str = html_str
        self.html_widget.value = html_str

    def update_query_results(self, queries, query_results):
        self.queries = queries
        self.query_results = query_results
        self.query_results_to_html()
