from IPython.display import display
from agents.documents_retriever import DocumentsRetriever
from nbwidgets.message_viewer import MessageViewer, MessageNode
from nbwidgets.query_results_viewer import QueryResultsViewer
from nbwidgets.conversation_viewer import ConversationViewer
from nbwidgets.paragraph_viewer import ParagraphViewer
from utils.tokenizer import SentenceTokenizer
import ipywidgets as widgets
import re


class ReferenceViewer:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.documents_retriever = DocumentsRetriever(self.project_dir)
        self.sentence_tokenizer = SentenceTokenizer()
        self.create_widgets()

    def create_paragraph_viewer(self):
        self.paragraph_viewer = ParagraphViewer()

    def update_toggle_button_description(self):
        self.layout_descriptions = {
            "both": "Chat + References",
            "left": "Chat",
            "right": "References",
        }

        self.layout_widths = {
            "both": ("50%", "50%"),
            "left": ("100%", "0%"),
            "right": ("0%", "100%"),
        }

        for container, width in zip(
            [self.left_container, self.right_container],
            self.layout_widths[self.layout_mode],
        ):
            container.layout.width = width

        self.toggle_layout_button.description = (
            f"Toggle Layout ({self.layout_descriptions[self.layout_mode]})"
        )

    def create_toggle_layout_button(self):
        self.toggle_layout_button = widgets.Button(
            description="Toggle Layout",
            layout=widgets.Layout(width="auto"),
        )
        self.layout_mode = "both"
        self.toggle_layout_button.on_click(self.toggle_layout)
        self.update_toggle_button_description()

    def create_sent_query_button(self):
        self.send_query_button = widgets.Button(
            description="Send Query",
            layout=widgets.Layout(width="auto"),
        )
        self.send_query_button.on_click(self.send_query)

    def send_query(self, button=None):
        self.send_query_button.style.button_color = "orange"
        queries_str = self.paragraph_viewer.result_viewer.text_widget.value
        queries = re.sub(r"^\d+\.\s*", "", queries_str, flags=re.MULTILINE).split("\n")
        query_results = self.documents_retriever.query(queries)
        self.query_results_viewer.update_query_results(queries, query_results)
        self.send_query_button.style.button_color = "green"

    def toggle_layout(self, button=None):
        self.layout_modes = ["both", "left", "right"]
        next_layout_mode_index = self.layout_modes.index(self.layout_mode) + 1
        self.layout_mode = self.layout_modes[
            next_layout_mode_index % len(self.layout_modes)
        ]
        self.update_toggle_button_description()

    def create_buttons(self):
        self.create_toggle_layout_button()
        self.create_sent_query_button()
        self.buttons_box = widgets.HBox(
            [self.toggle_layout_button, self.send_query_button]
        )

    def create_conversation_viewer(self):
        self.conversation_viewer = ConversationViewer()

    def create_query_results_viewer(self):
        queries = [
            "The AI-based diagnosis was the first implementation of computer vision in pathology.",
            "Visual explanation (saliency mapping, pathologist-in-the-loop)",
        ]
        query_results = self.documents_retriever.query(queries)
        self.query_results_viewer = QueryResultsViewer(
            queries=queries, query_results=query_results
        )

    def create_widgets(self):
        self.create_paragraph_viewer()
        self.create_conversation_viewer()
        self.create_query_results_viewer()
        self.left_container = widgets.VBox(layout=widgets.Layout(width="50%"))
        self.right_container = widgets.VBox(layout=widgets.Layout(width="50%"))
        self.left_container.children = [
            self.paragraph_viewer.output_widget,
            self.conversation_viewer.output_widget,
        ]
        self.right_container.children = [self.query_results_viewer.html_widget]
        self.container_hbox = widgets.HBox([self.left_container, self.right_container])
        self.create_buttons()
        self.container = widgets.VBox([self.buttons_box, self.container_hbox])

    def display(self):
        display(self.container)
        self.paragraph_viewer.display()
        self.conversation_viewer.display()
