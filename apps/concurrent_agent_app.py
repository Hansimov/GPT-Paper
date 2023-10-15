from dash import Dash, html, dcc, Input, Output, State, callback
from apps.themes.dark_theme import DarkTheme
from pathlib import Path
import dash_mantine_components as dmc


class UserInput:
    def __init__(self, app):
        self.app = app
        self.create_layout()
        self.add_callbacks()

    def create_layout(self):
        self.user_input_textarea = dmc.Textarea(
            id="user-input",
            label="User Input",
            minRows=1,
            autosize=True,
        )
        self.text_display = html.P(id="user-input-display")
        self.components = [self.user_input_textarea, self.text_display]

    def add_callbacks(self):
        @self.app.callback(
            Output("user-input-display", "children"), Input("user-input", "value")
        )
        def update_output(value):
            return value


class ConcurrentAgentsApp:
    app_root = Path(__file__).parent

    def __init__(self):
        pass

    def init_app_configs(self):
        self.app_configs = {
            "title": "Chat with Multi Concurrent Agents",
            "update_title": None,
            "assets_ignore": ".*\.(md|pkl|docx)$",
        }
        self.app_attrs = {
            # "_favicon": "assets/connection.png",
        }
        self.server_configs = {
            "debug": True,
            "dev_tools_ui": False,
            "dev_tools_hot_reload_interval": 2,
            "dev_tools_hot_reload_watch_interval": 2,
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
        user_input = UserInput(self.app)
        self.app.layout = dmc.Stack(children=user_input.components, id="app")
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
    app = ConcurrentAgentsApp()
    app.run()
