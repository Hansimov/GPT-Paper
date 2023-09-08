import ipywidgets as widgets
from IPython.display import display
from documents.review_parser import ReviewParser


class ArticleViewer:
    def __init__(self):
        self.review_parser = ReviewParser("cancer_review")
        self.review_parser.load_sections()
        self.create_widgets()

    def create_output_widget(self):
        self.output_widget = widgets.Output()

    def create_sidebar(self):
        self.review_parser.load_sections()
        depth_1_section = self.review_parser.get_sections_at_depth(1)
        self.section_selector = widgets.ToggleButtons(
            options=[section["title"] for section in depth_1_section],
            value=depth_1_section[0]["title"],
            description="Sections: ",
            disabled=False,
            layout=widgets.Layout(width="90%"),
        )

    def create_widgets(self):
        self.create_output_widget()
        self.create_sidebar()
        self.container = widgets.HBox()
        self.widgets = []
        self.widgets.extend(
            [
                self.output_widget,
                self.section_selector,
            ]
        )
        self.container.children = self.widgets

    def display(self):
        display(self.container)
