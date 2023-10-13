from apps.themes.constants import COLORS


class DarkTheme:
    def __init__(self):
        self.create_layout_styles()
        self.create_text_styles()

    def create_layout_styles(self):
        self.layout_styles = {
            "backgroundColor": COLORS["deep-grey"],
            "color": COLORS["deep-white"],
        }

    def create_text_styles(self):
        self.text_styles = {
            # "fontFamily": "Consolas",
            # "whiteSpace": "pre",
            # "display": "inline-block",
        }
