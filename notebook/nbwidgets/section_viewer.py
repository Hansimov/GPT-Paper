from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
from agents.paper_reviewer import SectionSummarizer, documents_retriever
from documents.section_parser import SectionNode, SectionTree


class SectionViewer:
    def __init__(self, section_node, parent=None):
        self.section_node = section_node
        self.section_node.section_viewer = self
        self.parent = parent
        self.children = []
        self.extra_prompt = ""
        self.response_content = ""
        self.section_summarizer = SectionSummarizer()
        # self.create_widgets()

    def summarize_chat(self, button):
        self.summarize_button.style.button_color = "orange"
        self.output_widget.clear_output()
        queries = documents_retriever.query([self.intro])
        with self.output_widget:
            # print(f"Button clicked at {datetime.now()}")
            self.response_content = self.section_summarizer.chat(
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
            value=self.section_node.title,
            layout=widgets.Layout(width="90%", justify_content="flex-start"),
            style=text_style,
        )

        def update_title_text_value(title_text_widget):
            self.section_node.title = title_text_widget.value

        self.title_text_widget.on_submit(update_title_text_value)

        self.intro_text_widget = widgets.Text(
            description="Intro",
            value=self.section_node.intro,
            layout=widgets.Layout(width="90%", justify_content="flex-start"),
            style=text_style,
        )

        def update_intro_text_value(intro_text_widget):
            self.section_node.intro = intro_text_widget.value

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

    def create_widgets(self):
        self.create_output_widget()
        self.create_title_and_intro_text_widget()
        self.create_button()
        self.container = widgets.VBox()
        self.children = []
        self.widgets = [
            self.summarize_button,
            self.title_text_widget,
            self.intro_text_widget,
            self.extra_prompt_widget,
            self.output_widget,
        ]

        if len(self.children) == 0:
            pass
        else:
            pass
            # self.section_viewer_children = [
            #     child.container for child in self.section_node.
            # ]

        self.container.children = self.widgets

    def display(self):
        display(self.container)


class SectionViewerTree:
    def __init__(self, project_dir):
        self.section_tree = SectionTree(project_dir)
        self.construct_section_viewers_tree()

    def construct_section_viewers_tree(self):
        self.section_tree.construct_hierarchical_sections()

        section_root = self.section_tree.section_root
        section_viewer_root = SectionViewer(section_root)
        self.section_viewer = section_viewer_root

        section_viewer_stack = [section_viewer_root]
        while len(section_viewer_stack) > 0:
            section_viewer = section_viewer_stack.pop()
            section_node = section_viewer.section_node
            print(section_node.level)
            for child in section_node.children[::-1]:
                child_section_viewer = SectionViewer(child)
                child_section_viewer.parent = section_viewer
                section_viewer_stack.append(child_section_viewer)
                section_viewer.children.append(child_section_viewer)

        self.section_viewer_root = section_viewer_root


if __name__ == "__main__":
    section_viewer_tree = SectionViewerTree("cancer_review")
    # print(section_viewer_tree.section_viewer_root.level)
    # print(section_tree.section_root.children)
