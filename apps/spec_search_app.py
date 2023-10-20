from apps.themes.dark_theme import DarkTheme
from bs4 import BeautifulSoup
from dash import Dash, html, dcc, Input, Output, State, callback
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML as danger_html
from pathlib import Path
import dash_mantine_components as dmc


class ComponentStyler:
    def __init__(self):
        self.style = {"width": "100%", "padding": "10px 0 10px 0"}


class KeywordInputer:
    def __init__(self, app):
        self.app = app
        self.create_layout()

    def create_title(self, title="Search Spec"):
        self.title = html.Div(title)

    def create_input(self):
        self.input = dmc.Textarea(
            id="spec-keyword-input-textarea",
            placeholder="Type Keywords here",
            value="",
            minRows=1,
            autosize=True,
        )

    def create_button(self):
        self.search_button = dmc.Button(
            id="spec-keyword-search-button",
            children="Search",
        )

    def apply_style_to_components(self):
        component_style = ComponentStyler().style
        for component in [self.title, self.input, self.search_button]:
            component.style = component_style

    def create_layout(self):
        self.create_title()
        self.create_input()
        self.create_button()
        self.apply_style_to_components()
        self.layout = html.Div(
            [self.title, self.input, self.search_button],
        )

    # def add_callbacks(self):
    #     @self.app.callback(
    #         Output("query-results", "children"),
    #         Input("query-search-button", "n_clicks"),
    #         State("query-input-textarea", "value"),
    #     )
    #     def send_query(n_clicks, query):
    #         if n_clicks is None:
    #             return ["Here is the query results."]
    #         print(f"Query: {query}")
    #         # query_results = self.documents_retriever.query(query)
    #         # self.query_results_viewer.update_query_results(
    #         #     queries=[query], query_results=query_results
    #         # )
    #         # return [self.query_results_viewer.danger_html_str]
    #         return [f"Query: {query}"]


class HTMLAccordionItemer:
    def __init__(self, element):
        self.element = element
        self.html_to_accordion()

    def html_to_accordion(self):
        element = self.element
        self.accordion_control = dmc.AccordionControl(element.name)
        self.accordion_panel = dmc.AccordionPanel(danger_html(str(element)))
        self.accordion_item = dmc.AccordionItem(
            [self.accordion_control, self.accordion_panel], value=element.name
        )


class SpecHTMLViewer:
    def __init__(self, app):
        self.app = app
        self.create_layout()

    def create_accordions(self):
        element_html = """<ul>
        </ul>
        """
        soup = BeautifulSoup(element_html, "html.parser")
        element = soup.find("ul")
        self.accordion_item = HTMLAccordionItemer(element).accordion_item
        self.accordions = dmc.Accordion(
            children=[self.accordion_item],
        )

    def create_layout(self):
        self.create_accordions()
        self.layout = html.Div([self.accordions])


class SpecSearchApp:
    app_root = Path(__file__).parent

    def __init__(self):
        pass

    def init_app_configs(self):
        self.app_configs = {
            "title": "Spec Search",
            "update_title": None,
            "assets_ignore": ".*\.(md|pkl|docx)$",
        }
        self.app_attrs = {}
        self.server_configs = {
            "debug": True,
            "dev_tools_ui": False,
            "dev_tools_hot_reload_interval": 0.5,
            "dev_tools_hot_reload_watch_interval": 0.5,
            "host": "0.0.0.0",
            "port": 12346,
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
        keyword_inputer = KeywordInputer(self.app)
        spec_html_viewer = SpecHTMLViewer(self.app)
        self.app.layout = html.Div([keyword_inputer.layout, spec_html_viewer.layout])
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
    app = SpecSearchApp()
    app.run()
