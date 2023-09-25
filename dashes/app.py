from dash import Dash, html, dcc, Input, Output, State, callback
from dashes.themes.dark_theme import DarkTheme
from pathlib import Path


class ReferenceLayout:
    def __init__(self):
        self.create_layout()

    def create_layout(self):
        self.layout = html.Div("Reference Search")


class ReferenceSearchApp:
    app_root = Path(__file__).parent

    def __init__(self):
        pass

    def init_app_configs(self):
        self.app_configs = {
            "title": "Reference Search",
            "update_title": None,
        }
        self.app_attrs = {
            "_favicon": str(self.app_root / "assets" / "paper.png"),
        }
        self.server_configs = {
            "debug": True,
            "dev_tools_ui": False,
            "dev_tools_hot_reload_interval": 0.5,
            "dev_tools_hot_reload_watch_interval": 0.5,
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
        reference_layout = ReferenceLayout()
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
