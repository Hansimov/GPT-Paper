import html as pyhtml
import dash_mantine_components as dmc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML as danger_html
from dash import html
from documents.text_translator import TextTranslator
from utils.tokenizer import WordTokenizer
from notebook.nbwidgets.styles import calc_font_color_by_background


class QueryResultsViewer:
    def __init__(self, queries=None, query_results=None):
        self.queries = queries
        self.query_results = query_results
        self.create_layout()
        self.query_results_to_html()

    def create_layout(self):
        self.layout = html.Div(
            id="query-results",
            children=[danger_html("Here are the query results")],
        )

    def query_results_to_html(self, translate=False):
        if not self.query_results:
            self.html_str = ""
            return

        word_tokenizer = WordTokenizer()

        if translate:
            text_translator = TextTranslator(
                project_dir="cancer_review", engine="google"
            )

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
                if translate:
                    translated_region_text = text_translator.translate(region_text)
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
                if normalized_region_score >= 0.3:
                    details_open_str = "open"
                else:
                    details_open_str = ""

                if translate:
                    region_hover_text = pyhtml.escape(translated_region_text)
                else:
                    region_hover_text = pyhtml.escape(region_text)

                region_text_html = f"""
                <li>
                    <details {details_open_str}>
                        <summary style='{region_text_style}' title='{region_hover_text}'>
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
        <details open>
            <summary>
            Related {region_text_count} Paragraphs in {len(self.query_results)} References of {len(self.queries)} Queries:
            </summary>
            <div class='query_result_item'>
                <ol>
                    {html_str}
                </ol>
            </div>
        </details>
        """

        style_str = f"""
        <style>
            .query_result_item {{
                max-height: 85vh;
                overflow-y: auto;
                border: 1px solid gray;
                font-size: 18px;
            }}
        </style>
        """
        html_str += style_str
        self.html_str = html_str
        self.danger_html_str = danger_html(html_str)

    def update_query_results(self, queries, query_results):
        self.queries = queries
        self.query_results = query_results
        self.query_results_to_html()
