from datetime import datetime
import ipywidgets as widgets
from IPython.display import display


class SectionEditor:
    def __init__(self):
        self.create_widgets()

    def create_button(self):
        button = widgets.Button(
            description="Generate Details",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click and generate details for this section",
            icon="radiation",
        )
        button.on_click(self.button_output)
        self.button = button

    def button_output(self, button):
        self.output.clear_output()
        with self.output:
            print(f"Button clicked at {datetime.now()}")

    def create_output(self):
        self.output = widgets.Output()

    def create_tab(self):
        tab = widgets.Tab()
        tab_titles = ["Section 1", "Section 2", "Section 3", "Section 4"]
        tab_contents = ["Content 1", "Content 2", "Content 3", "Content 4"]
        tab_children = [widgets.HTML(description=content) for content in tab_contents]
        tab.children = tab_children
        tab.titles = [title for title in tab_titles]
        self.tab = tab

    def create_widgets(self):
        self.create_output()
        self.create_button()
        self.create_tab()
        self.container = widgets.VBox()
        self.widgets = []
        self.widgets.extend([self.button, self.tab, self.output])
        self.container.children = self.widgets

    def display(self):
        display(self.container)
