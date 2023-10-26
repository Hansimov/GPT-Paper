from apps.themes.dark_theme import DarkTheme
from bs4 import BeautifulSoup
from dash import Dash, html, dcc, Input, Output, State, callback
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML as danger_html
from pathlib import Path
from documents.spec_html_nodelizer import SpecHTMLNodelizer
from networks.html_fetcher import HTMLFetcher
import dash_mantine_components as dmc


class ComponentStyler:
    def __init__(self):
        self.style = {"width": "100%", "padding": "10px 0 10px 0"}

    def stylize(self, components):
        for component in components:
            component.style = self.style


class URLInputer:
    def __init__(self, app, value=""):
        self.app = app
        self.value = value
        self.create_layout()

    def create_input(self):
        self.input = dmc.TextInput(
            id="spec-url-input-textarea",
            placeholder="Type url here",
            value=self.value,
        )

    def create_button(self):
        self.submit_button = dmc.Button(
            id="spec-url-submit-button",
            children="Submit",
        )

    def apply_style_to_components(self):
        ComponentStyler().stylize([self.input, self.submit_button])

    def create_layout(self):
        self.create_input()
        self.create_button()
        self.apply_style_to_components()
        self.layout = html.Div(
            [self.input, self.submit_button],
        )


class KeywordInputer:
    def __init__(self, app, spec_url=""):
        self.app = app
        self.spec_url = spec_url
        self.create_layout()

    def create_title(self):
        self.title = html.Div(
            danger_html(
                f'Search in Spec: <a href="{self.spec_url}">{self.spec_url}</a>'
            )
        )

    def create_input(self):
        self.input = dmc.TextInput(
            id="spec-keyword-input-textarea",
            placeholder="Type Keywords here",
            value="",
        )

    def create_button(self):
        self.search_button = dmc.Button(
            id="spec-keyword-search-button",
            children="Search",
        )

    def apply_style_to_components(self):
        ComponentStyler().stylize([self.title, self.input, self.search_button])

    def create_layout(self):
        self.create_title()
        self.create_input()
        self.create_button()
        self.apply_style_to_components()
        self.layout = html.Div(
            [self.title, self.input, self.search_button],
        )

    def add_callbacks(self):
        @self.app.app.callback(
            Output("keyword-search-accordion", "children"),
            [
                Input("spec-keyword-search-button", "n_clicks"),
                Input("spec-keyword-input-textarea", "n_submit"),
            ],
            State("spec-keyword-input-textarea", "value"),
        )
        def send_query(n_clicks, n_submit, query):
            if not query or (n_clicks is None and n_submit is None):
                return ["(Here will display the searched results.)"]

            print(f"Keyword: {query}")

            accordion_items = self.app.search_by_keyword(query)

            if len(accordion_items) == 0:
                return ["No results found."]
            else:
                return accordion_items


class HTMLAccordionItemer:
    def __init__(self, elements, title="accordion"):
        self.elements = elements
        self.title = title
        self.html_to_accordion()

    def html_to_accordion(self):
        elements = self.elements
        self.accordion_control = dmc.AccordionControl(danger_html(self.title))
        self.accordion_panel = dmc.AccordionPanel(
            danger_html("<hr>".join([str(element) for element in elements]))
        )
        self.accordion_item = dmc.AccordionItem(
            children=[self.accordion_control, self.accordion_panel], value=self.title
        )


class SpecHTMLViewer:
    def __init__(self, app):
        self.app = app
        self.create_layout()

    def extract_styles(self):
        self.styles = self.app.spec_html_nodelizer.extract_styles()
        self.search_highlight_styles = """
        <style>
            searched {
                background-color: PaleGreen;
            }
            ref-index {
                font-weight: bold;
                color: magenta;
            }
            ref-title {
                color: blue;
            }
        </style>
        """
        self.styles += self.search_highlight_styles

    def create_accordion(self):
        self.accordion = dmc.AccordionMultiple(
            id="keyword-search-accordion",
            children=[],
            variant="contained",
            transitionDuration="200",
            chevronPosition="left",
        )

    def create_layout(self):
        self.extract_styles()
        self.create_accordion()
        self.layout = html.Div([danger_html(self.styles), self.accordion])


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
        self.url_inputer = URLInputer(self)
        self.layout_children = [self.url_inputer.layout]
        self.app.layout = html.Div(
            id="spec-search-app",
            children=self.layout_children,
        )
        self.app.layout.style = self.layout_styles

    def update_layout(self):
        self.url_inputer = URLInputer(self, value=self.url)
        self.keyword_inputer = KeywordInputer(self, spec_url=self.url)
        self.keyword_inputer.add_callbacks()
        self.spec_html_viewer = SpecHTMLViewer(self)
        self.layout_children = [
            self.url_inputer.layout,
            self.keyword_inputer.layout,
            self.spec_html_viewer.layout,
        ]
        return self.layout_children

    def run_server(self):
        self.app.run_server(**self.server_configs)

    def nodelize_html_with_url(self, url):
        self.url = url
        html_fetcher = HTMLFetcher(url)
        html_fetcher.run()
        self.spec_html_nodelizer = SpecHTMLNodelizer(html_fetcher.output_path)
        self.spec_html_nodelizer.parse_html_to_nodes()

    def add_callbacks(self):
        @self.app.callback(
            [
                Output("spec-url-input-textarea", "value"),
                Output("spec-search-app", "children"),
            ],
            Input("spec-url-submit-button", "n_clicks"),
            State("spec-url-input-textarea", "value"),
        )
        def submit_url(n_clicks, url=""):
            if not url or n_clicks is None:
                pass
            else:
                self.nodelize_html_with_url(url)
                self.update_layout()
            return url, self.layout_children

    def group_searched_node_elements_by_header_title(self, searched_nodes):
        grouped_elements = []

        def get_header_title(node):
            return node.get_section_group_node().get_header_node().get_full_text()

        for node in searched_nodes:
            header_title = get_header_title(node)
            if len(grouped_elements) > 0 and header_title == grouped_elements[-1][0]:
                grouped_elements[-1][1].append(node.marked_element)
            else:
                grouped_elements.append([header_title, [node.marked_element]])

        return grouped_elements

    def search_by_keyword(self, keyword):
        searched_nodes = self.spec_html_nodelizer.search_by_keyword(keyword)
        grouped_searched_node_elements = (
            self.group_searched_node_elements_by_header_title(searched_nodes)
        )
        accordion_items = []
        for idx, grouped_title_and_elements in enumerate(
            grouped_searched_node_elements
        ):
            grouped_title, grouped_elements = grouped_title_and_elements
            accordion_item = HTMLAccordionItemer(
                elements=grouped_elements,
                title=f"<ref-index>[{idx+1}]</ref-index> <ref-title>{grouped_title}</ref-title>",
            ).accordion_item
            accordion_items.append(accordion_item)
        return accordion_items

    def run(self):
        self.init_app_configs()
        self.init_layout_configs()
        self.create_app()
        self.create_layout()
        self.add_callbacks()
        self.run_server()


if __name__ == "__main__":
    app = SpecSearchApp()
    app.run()
