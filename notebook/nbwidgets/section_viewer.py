from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
from agents.paper_reviewer import SectionSummarizer, documents_retriever
from documents.section_parser import SectionNode, SectionTree
from nbwidgets.query_results_viewer import QueryResultsViewer


class SectionViewer:
    def __init__(self, section_node, parent=None):
        self.section_node = section_node
        self.section_node.section_viewer = self
        self.parent = parent
        self.children = []
        self.extra_prompt = ""
        self.word_count = 500
        self.response_content = ""
        self.section_summarizer = SectionSummarizer(content_type="refinement")
        # self.create_widgets()

    def summarize_chat(self, button):
        self.summarize_button.style.button_color = "orange"
        self.output_widget.clear_output()
        queries = documents_retriever.query([self.section_node.intro])
        # print(f"Button clicked at {datetime.now()}")
        query_results_viewer = QueryResultsViewer(queries)
        self.right_container.children = [query_results_viewer.container]
        self.response_content = self.section_summarizer.chat(
            topic=self.section_node.intro,
            queries=queries,
            extra_prompt=self.extra_prompt,
            word_count=self.word_count,
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
            value=f"{self.section_node.level}: {self.section_node.title}",
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

        self.word_count_widget = widgets.Text(
            description="Words",
            value=str(self.word_count),
            placeholder="",
            layout=widgets.Layout(width="90%", justify_content="flex-start"),
            style=text_style,
        )

        def update_word_count_value(word_count_widget):
            self.word_count = int(word_count_widget.value)

        self.word_count_widget.on_submit(update_word_count_value)

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

    def create_widgets(self, create_children=True):
        self.create_output_widget()
        self.create_title_and_intro_text_widget()
        self.create_button()
        self.container = widgets.HBox()
        self.left_container = widgets.VBox(layout=widgets.Layout(width="50%"))
        self.right_container = widgets.VBox(
            layout=widgets.Layout(width="50%", height="50%", overflow_y="auto"),
        )
        self.widgets = [
            self.summarize_button,
            self.title_text_widget,
            self.intro_text_widget,
            # self.extra_prompt_widget,
            self.word_count_widget,
            self.output_widget,
        ]

        if len(self.children) == 0:
            pass
        else:
            if create_children:
                for child in self.children:
                    child.create_widgets()

        self.left_container.children = self.widgets
        self.right_container.children = [
            widgets.HTML(value=str(self.section_node.intro))
        ]
        self.container.children = [self.left_container, self.right_container]

    def display(self, display_children=True):
        if display_children:
            section_viewer_stack = [self]
            while len(section_viewer_stack) > 0:
                section_viewer = section_viewer_stack.pop()
                display(section_viewer.container)
                for child_section_viewer in section_viewer.children:
                    section_viewer_stack.append(child_section_viewer)
        else:
            display(self.container)


class SectionViewerTree:
    def __init__(self, project_dir):
        self.section_tree = SectionTree(project_dir)
        self.construct_section_viewers_tree()
        self.create_widgets()
        self.display()

    def construct_section_viewers_tree(self):
        self.section_tree.construct_hierarchical_sections()

        section_root = self.section_tree.section_root
        section_viewer_root = SectionViewer(section_root)

        section_viewer_stack = [section_viewer_root]
        while len(section_viewer_stack) > 0:
            section_viewer = section_viewer_stack.pop()
            section_node = section_viewer.section_node
            # print(section_node.level)
            for child_section_node in section_node.children[::-1]:
                child_section_viewer = SectionViewer(child_section_node)
                child_section_viewer.parent = section_viewer
                section_viewer.children.append(child_section_viewer)
                section_viewer_stack.append(child_section_viewer)

        self.section_viewer_root = section_viewer_root

    def create_widgets(self):
        self.section_viewer_root.create_widgets()

    def display(self):
        self.section_viewer_root.display()


if __name__ == "__main__":
    section_viewer_tree = SectionViewerTree("cancer_review")
