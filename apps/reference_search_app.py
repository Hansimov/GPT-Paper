from agents.documents_retriever import DocumentsRetriever
from dash import Dash, html, dcc, Input, Output, State, callback
from apps.themes.dark_theme import DarkTheme
from apps.components.query_results_viewer import QueryResultsViewer
from pathlib import Path
import dash_mantine_components as dmc


class ReferenceLayout:
    def __init__(self, app):
        self.app = app
        self.create_layout()

    def create_input(self):
        self.input = dmc.Textarea(
            id="query-input-textarea",
            placeholder="Type query here",
            value="",
            style={
                "width": "50%",
            },
            minRows=1,
            autosize=True,
        )

    def create_button(self):
        self.search_button = dmc.Button(
            id="query-search-button",
            children="Search",
            style={
                "width": "50%",
            },
        )

    def create_results_viewer(self):
        self.documents_retriever = DocumentsRetriever("cancer_review")
        self.query_results_viewer = QueryResultsViewer()

    def create_layout(self):
        self.create_input()
        self.create_button()
        self.create_results_viewer()
        self.layout = html.Div(
            [
                html.Div("Reference Search"),
                self.input,
                self.search_button,
                self.query_results_viewer.layout,
            ]
        )

    def add_callbacks(self):
        @self.app.callback(
            Output("query-results", "children"),
            Input("query-search-button", "n_clicks"),
            State("query-input-textarea", "value"),
        )
        def send_query(n_clicks, query):
            if n_clicks is None:
                return ["Here is the query results."]
            print(f"Query: {query}")
            query_results = self.documents_retriever.query(query)
            self.query_results_viewer.update_query_results(
                queries=[query], query_results=query_results
            )
            return [self.query_results_viewer.danger_html_str]


class ReferenceSearchApp:
    app_root = Path(__file__).parent

    def __init__(self):
        pass

    def init_app_configs(self):
        self.app_configs = {
            "title": "Reference Search",
            "update_title": None,
            "assets_ignore": ".*\.(md|pkl|docx)$",
        }
        self.app_attrs = {
            "_favicon": str(self.app_root / "assets" / "paper.png"),
        }
        self.server_configs = {
            "debug": True,
            "dev_tools_ui": False,
            "dev_tools_hot_reload_interval": 0.5,
            "dev_tools_hot_reload_watch_interval": 0.5,
            "host": "0.0.0.0",
            "port": 12345,
        }

    def init_layout_configs(self):
        dark_theme = DarkTheme()
        self.layout_styles = dark_theme.layout_styles
        self.text_styles = dark_theme.text_styles

    def create_app(self):
        self.app = Dash(__name__, **self.app_configs)
        for attr_key, attr_val in self.app_attrs.items():
            setattr(self.app, attr_key, attr_val)

    def create_layout(self):
        reference_layout = ReferenceLayout(self.app)
        reference_layout.add_callbacks()
        self.app.layout = reference_layout.layout
        self.app.layout.style = self.layout_styles

    def run_server(self):
        self.app.run_server(**self.server_configs)

    def run(self):
        self.init_app_configs()
        self.init_layout_configs()
        self.create_app()
        self.create_layout()
        self.run_server()


if __name__ == "__main__":
    app = ReferenceSearchApp()
    app.run()
