import ipywidgets as widgets
from IPython.display import display


class SectionWidget:
    def __init__(self):
        self.create_widgets()

    def create_button(self):
        button = widgets.Button(
            description="Generate Details",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click and generate details for this section",
            icon="radiation",  # (FontAwesome names without the `fa-` prefix),
        )
        button.on_click = self.generate_section_details
        return button

    def generate_section_details(self):
        print("Generating ...")

    def create_tab(self):
        # self.button = self.create_button()

        tab = widgets.Tab()
        tab_titles = ["Section 1", "Section 2", "Section 3", "Section 4"]
        tab_contents = ["Content 1", "Content 2", "Content 3", "Content 4"]
        tab_children = [widgets.HTML(description=content) for content in tab_contents]
        tab.children = tab_children
        tab.titles = [title for title in tab_titles]
        return tab

    def create_widgets(self):
        self.widgets = []
        self.container = widgets.VBox()
        self.button = self.create_button()
        self.tab = self.create_tab()
        self.widgets.extend([self.button, self.tab])
        self.container.children = self.widgets

    def display(self):
        display(self.container)
