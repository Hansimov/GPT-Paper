from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
from agents.paper_reviewer import SectionSummarizer, documents_retriever


class SectionViewer:
    def __init__(self, title, intro):
        self.title = title
        self.intro = intro
        self.extra_prompt = ""
        self.section_summarizer = SectionSummarizer()
        self.create_widgets()

    def create_button(self):
        self.summarize_button = widgets.Button(
            description="Summarize",
            disabled=False,
            button_style="",
            tooltip="Summarize this section based on the topic and intro",
            icon="radiation",
        )
        self.translate_button = widgets.Button(
            description="Translate",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click and translate the details for this section",
            icon="language",
        )
        self.summarize_button.on_click(self.summarize_chat)

    def summarize_chat(self, button):
        self.summarize_button.style.button_color = "orange"
        self.output_widget.clear_output()
        queries = documents_retriever.query([self.intro])
        with self.output_widget:
            # print(f"Button clicked at {datetime.now()}")
            self.section_summarizer.chat(
                topic=self.intro,
                queries=queries,
                extra_prompt=self.extra_prompt,
            )
            self.summarize_button.style.button_color = "darkgreen"

    def create_output_widget(self):
        self.output_widget = widgets.Output()
        for agent in self.section_summarizer.agents:
            agent.output_widget = self.output_widget

    def create_title_and_intro_text_widget(self):
        text_style = {"description_width": "50px"}
        self.title_text_widget = widgets.Text(
            description="Title",
            value=self.title,
            layout=widgets.Layout(width="90%", justify_content="flex-start"),
            style=text_style,
        )

        def update_title_text_value(title_text_widget):
            self.title = title_text_widget.value

        self.title_text_widget.on_submit(update_title_text_value)

        self.intro_text_widget = widgets.Text(
            description="Intro",
            value=self.intro,
            layout=widgets.Layout(width="90%", justify_content="flex-start"),
            style=text_style,
        )

        def update_intro_text_value(intro_text_widget):
            self.intro = intro_text_widget.value

        self.intro_text_widget.on_submit(update_intro_text_value)

        self.extra_prompt_widget = widgets.Text(
            description="Prompt",
            value=self.extra_prompt,
            placeholder="",
            layout=widgets.Layout(width="90%", justify_content="flex-start"),
            style=text_style,
        )

        def update_extra_promt_value(extra_prompt_widget):
            self.extra_prompt = extra_prompt_widget.value

        self.extra_prompt_widget.on_submit(update_extra_promt_value)

    def create_widgets(self):
        self.create_output_widget()
        self.create_title_and_intro_text_widget()
        self.create_button()
        self.container = widgets.VBox()
        self.widgets = []
        self.widgets.extend(
            [
                self.summarize_button,
                self.title_text_widget,
                self.intro_text_widget,
                self.extra_prompt_widget,
                self.output_widget,
            ]
        )
        self.container.children = self.widgets

    def display(self):
        display(self.container)
