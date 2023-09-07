from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
from agents.paper_reviewer import SectionSummarizer


class SectionViewer:
    def __init__(self, topic, intro, queries):
        self.topic = topic
        self.intro = intro
        self.queries = queries
        self.section_summarizer = SectionSummarizer()
        self.create_widgets()

    def create_button(self):
        self.summarize_button = widgets.Button(
            description="Summarize Section",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click and generate details for this section",
            icon="radiation",
        )
        self.summarize_button.on_click(self.summarize_chat)

    def summarize_chat(self, button):
        self.output_widget.clear_output()
        with self.output_widget:
            print(f"Button clicked at {datetime.now()}")

    def create_output_widget(self):
        self.output_widget = widgets.Output()
        for agent in self.section_summarizer.agents:
            agent.output_widget = self.output_widget

    def create_tab(self):
        self.tab = widgets.Tab()
        self.tab.titles = [title for title in [self.topic]]
        tab_children = [
            widgets.Text(
                value=content,
                layout=widgets.Layout(width="100%"),
            )
            for content in [self.intro]
        ]
        self.tab.children = tab_children

    def create_widgets(self):
        self.create_output_widget()
        self.create_button()
        self.create_tab()
        self.container = widgets.VBox()
        self.widgets = []
        self.widgets.extend([self.summarize_button, self.tab, self.output_widget])
        self.container.children = self.widgets

    def display(self):
        display(self.container)
