import html
import ipywidgets as widgets
from nbwidgets.styles import calc_font_color_by_background


class QueryResultsViewer:
    def __init__(self, queries=None):
        self.queries = queries
        self.display()

    def display(self):
        self.queries_to_html()
        self.create_widgets()

    def create_widgets(self):
        self.container = widgets.VBox([widgets.HTML(self.html_str)])

    def queries_to_html(self):
        if not self.queries:
            self.html_str = ""
            return

        region_scores = [
            region["score"]
            for query_result in self.queries
            for region in query_result["regions"]
        ]

        def normalize_score(score):
            return (score - min(region_scores)) / (
                max(region_scores) - min(region_scores)
            )

        html_str = ""
        for query_result in self.queries:
            pdf_name = query_result["pdf_name"]
            pdf_name_html = f"<h3>{pdf_name}</h3>\n"

            region_texts_html = ""
            for region in query_result["regions"]:
                normalized_region_score = normalize_score(region["score"])
                page_idx = region["page_idx"]
                region_idx = region["region_idx"]
                region_text = region["text"]
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
                            Score {round(float(normalized_region_score),2)}
                        </summary>
                        {region_text}
                    </details>
                </li>\n
                """
                region_texts_html += region_text_html

            region_texts_html = f"<ol>\n{region_texts_html}\n</ol>"
            html_str += f"<li>{pdf_name_html}\n{region_texts_html}</li>"

        html_str = f"""
        <details>
            <summary>
                Related References
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
