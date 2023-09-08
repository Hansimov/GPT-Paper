import ipywidgets as widgets
from IPython.display import display
from documents.review_parser import ReviewParser
from nbwidgets.section_viewer import SectionViewer


class ArticleViewer:
    def __init__(self):
        self.review_parser = ReviewParser("cancer_review")
        self.review_parser.load_sections()
        self.create_widgets()

    def create_output_widget(self):
        self.output_widget = widgets.Output()

    def create_accordion(self):
        self.review_parser.load_sections()
        depth_1_sections = self.review_parser.get_sections_at_depth(1)

        self.accordion = widgets.Accordion(
            children=[
                # widgets.Text(value=section["intro"]) for section in depth_1_sections
                SectionViewer(title=section["title"], intro=section["intro"]).container
                for section in depth_1_sections
            ],
            titles=[
                f"{section['level']} {section['title']}" for section in depth_1_sections
            ],
        )

    def create_widgets(self):
        self.create_output_widget()
        self.create_accordion()
        self.container = widgets.HBox()
        self.widgets = []
        self.widgets.extend(
            [
                self.accordion,
                self.output_widget,
            ]
        )
        self.container.children = self.widgets

    def display(self):
        display(self.container)
