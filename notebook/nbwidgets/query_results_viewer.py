import ipywidgets as widgets


class QueryResultsViewer:
    def __init__(self, queries):
        self.queries = queries
        self.queries_to_html()
        self.create_widgets()

    def queries_to_html(self):
        html_str = ""
        for query_result in self.queries:
            pdf_name = query_result["pdf_name"]
            pdf_name_html = f"<h3>{pdf_name}</h3>\n"
            text_list_html = "\n".join(
                [f"<li>{region['text']}</li>" for region in query_result["regions"]]
            )
            texts_html = f"<ol>\n{text_list_html}\n</ol>"
            html_str += f"{pdf_name_html}\n{texts_html}"
        html_str = f"<div class='query_results'>{html_str}</div>"
        style_str = f"""
        <style>
            .query_results {{
                height: 400px;
                overflow-y:auto
            }}
        </style>
        """
        html_str += style_str
        self.html_str = html_str

    def create_widgets(self):
        self.container = widgets.VBox()
        self.widgets = [widgets.HTML(self.html_str)]
        self.container.children = self.widgets
