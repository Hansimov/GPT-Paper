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
        self.query_count = 20
        self.response_content = ""
        self.section_summarizer = SectionSummarizer(content_type="refinement")

        self.editable_widgets_visibility = True
        if len(self.section_node.children) > 0:
            self.editable_widgets_visibility = False

        # self.create_widgets()

    def retrieve_queries(self, button=None):
        self.retrieve_button.style.button_color = "orange"
        queries = documents_retriever.query(
            [self.section_node.intro], rerank_n=self.query_count
        )
        self.retrieve_button.style.button_color = "darkgreen"
        query_results_viewer = QueryResultsViewer(queries)
        self.right_container.children = [
            self.intro_text_widget,
            query_results_viewer.container,
        ]
        return queries

    def summarize_chat(self, button=None):
        self.summarize_button.style.button_color = "orange"
        self.output_widget.clear_output()
        queries = self.retrieve_queries()
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

    def create_title_and_intro_text_widgets(self):
        text_style = {"description_width": "50px"}
        self.title_text_widget = widgets.Text(
            # description="Title",
            description="",
            value=f"{self.section_node.level}: {self.section_node.title}",
            layout=widgets.Layout(
                width="99%",
                justify_content="flex-start",
                border="1px solid purple",
            ),
            style={**text_style, "background": "#000000"},
        )

        def update_title_text_value(title_text_widget):
            self.section_node.title = title_text_widget.value

        self.title_text_widget.on_submit(update_title_text_value)

        self.intro_text_widget = widgets.Text(
            # description="Intro",
            description="",
            value=self.section_node.intro,
            layout=widgets.Layout(
                width="99%",
                justify_content="flex-start",
                border="1px solid transparent",
            ),
            style={**text_style, "background": "transparent"},
        )

        def update_intro_text_value(intro_text_widget):
            self.section_node.intro = intro_text_widget.value
            print(self.retrieve_button.style.button_color)
            self.retrieve_button.style.button_color = None

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

        self.query_count_text_widget = widgets.Text(
            description="",
            value=str(self.query_count),
            placeholder=str(self.query_count),
            layout=widgets.Layout(width="40px", justify_content="flex-start"),
        )
        self.query_count_widget = widgets.HBox(
            children=[
                self.query_count_text_widget,
                widgets.HTML("queries,"),
            ]
        )

        def update_query_count_value(query_count_widget):
            self.query_count = int(query_count_widget.value)

        self.query_count_text_widget.on_submit(update_query_count_value)

        self.word_count_text_widget = widgets.Text(
            description="",
            value=str(self.word_count),
            placeholder="",
            layout=widgets.Layout(width="60px", justify_content="flex-start"),
        )
        self.word_count_widget = widgets.HBox(
            children=[
                widgets.HTML(" to "),
                self.word_count_text_widget,
                widgets.HTML("words:"),
            ]
        )

        def update_word_count_value(word_count_widget):
            self.word_count = int(word_count_widget.value)

        self.word_count_text_widget.on_submit(update_word_count_value)

        self.query_results_widget = widgets.HTML("")

    def create_buttons(self):
        button_layout = widgets.Layout(width="auto")
        self.retrieve_button = widgets.Button(
            description="Retrieve",
            disabled=False,
            button_style="",
            tooltip="Retrieve related references",
            icon="list",
            layout=button_layout,
        )

        self.retrieve_button.on_click(self.retrieve_queries)

        self.summarize_button = widgets.Button(
            description="Summarize",
            disabled=False,
            button_style="",
            tooltip="Summarize this section based on the topic and intro",
            icon="rocket",
            layout=button_layout,
        )
        self.summarize_button.on_click(self.summarize_chat)

        self.translate_button = widgets.Button(
            description="Translate",
            disabled=False,
            button_style="",
            tooltip="Click and translate the details for this section",
            icon="language",
            layout=button_layout,
        )

    def create_widgets(self, create_children=True):
        self.create_output_widget()
        self.create_title_and_intro_text_widgets()
        self.create_buttons()

        self.container = widgets.HBox(layout=widgets.Layout(border="solid 1px gray"))
        self.left_container = widgets.VBox(layout=widgets.Layout(width="50%"))
        self.right_container = widgets.VBox(
            layout=widgets.Layout(width="50%", height="50%", overflow_y="auto"),
        )

        self.editable_widgets = widgets.VBox(
            children=[
                # self.extra_prompt_widget,
                widgets.HBox(
                    children=[
                        widgets.HBox(
                            children=[
                                self.retrieve_button,
                                self.query_count_widget,
                            ],
                            layout=widgets.Layout(justify_content="flex-start"),
                        ),
                        widgets.HBox(
                            children=[
                                self.summarize_button,
                                self.word_count_widget,
                            ],
                            layout=widgets.Layout(
                                justify_content="flex-start",
                            ),
                        ),
                    ],
                    layout=widgets.Layout(justify_content="flex-start"),
                ),
                self.output_widget,
            ],
        )

        hidden_widgets = [self.intro_text_widget, self.editable_widgets]
        if not self.editable_widgets_visibility:
            for widget in hidden_widgets:
                widget.layout.display = "none"

        self.left_widgets = [self.title_text_widget, self.editable_widgets]
        self.right_widgets = [self.intro_text_widget, self.query_results_widget]

        if len(self.children) == 0:
            pass
        else:
            if create_children:
                for child in self.children:
                    child.create_widgets()

        self.left_container.children = self.left_widgets
        self.right_container.children = self.right_widgets
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

    def summarize_all_sections(self, button=None):
        self.summarize_all_button.style.button_color = "orange"
        section_viewer_stack = [self.section_viewer_root]
        while len(section_viewer_stack) > 0:
            section_viewer = section_viewer_stack.pop()
            if section_viewer.editable_widgets_visibility:
                section_viewer.summarize_chat(None)
                # section_viewer.retrieve_queries()
            for child_section_viewer in section_viewer.children:
                section_viewer_stack.append(child_section_viewer)
        self.summarize_all_button.style.button_color = "darkgreen"

    def retrieve_all_sections(self, button=None):
        self.retrieve_all_button.style.button_color = "orange"
        section_viewer_stack = [self.section_viewer_root]
        while len(section_viewer_stack) > 0:
            section_viewer = section_viewer_stack.pop()
            if section_viewer.editable_widgets_visibility:
                # section_viewer.summarize_chat(None)
                section_viewer.retrieve_queries()
                # print(section_viewer.section_node.title)
            for child_section_viewer in section_viewer.children:
                section_viewer_stack.append(child_section_viewer)
        self.retrieve_all_button.style.button_color = "darkgreen"

    def create_buttons(self):
        button_layout = widgets.Layout(width="auto")
        self.summarize_all_button = widgets.Button(
            description="Summarize All",
            disabled=False,
            button_style="",
            tooltip="Summarize all sections with one click",
            icon="radiation",
            layout=button_layout,
        )
        self.summarize_all_button.on_click(self.summarize_all_sections)

        self.retrieve_all_button = widgets.Button(
            description="Retrieve All",
            disabled=False,
            button_style="",
            tooltip="Retrieve references for all sections with one click",
            icon="wikipedia-w",
            layout=button_layout,
        )
        self.retrieve_all_button.on_click(self.retrieve_all_sections)

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
        self.create_buttons()
        self.container = widgets.VBox()
        self.button_widgets = widgets.HBox(
            children=[self.retrieve_all_button, self.summarize_all_button]
        )
        self.container.children = [self.button_widgets]
        self.section_viewer_root.create_widgets()

    def display(self):
        display(self.container)
        self.section_viewer_root.display()


if __name__ == "__main__":
    section_viewer_tree = SectionViewerTree("cancer_review")
