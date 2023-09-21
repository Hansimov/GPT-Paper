from IPython.display import display
from agents.documents_retriever import DocumentsRetriever
from nbwidgets.message_viewer import MessageViewer, MessageNode
from nbwidgets.query_results_viewer import QueryResultsViewer
from nbwidgets.conversation_viewer import ConversationViewer
from nbwidgets.paragraph_viewer import ParagraphViewer
from utils.tokenizer import SentenceTokenizer
import ipywidgets as widgets


class ReferenceViewer:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.documents_retriever = DocumentsRetriever(self.project_dir)
        self.sentence_tokenizer = SentenceTokenizer()
        self.create_widgets()

    def tokenize_sentences(self, button=None):
        sentences = self.sentence_tokenizer.text_to_sentences(text)
        print(sentences)

    def create_paragraph_viewer(self):
        self.paragraph_viewer = MessageViewer(
            MessageNode(role="input"), placeholder="Paragraph"
        )

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

    def toggle_layout(self, button=None):
        self.layout_modes = ["both", "left", "right"]
        next_layout_mode_index = self.layout_modes.index(self.layout_mode) + 1
        self.layout_mode = self.layout_modes[
            next_layout_mode_index % len(self.layout_modes)
        ]
        self.update_toggle_button_description()

    def create_buttons(self):
        self.create_toggle_layout_button()

    def create_split_sentence_button(self):
        self.split_sentences_button = widgets.Button(
            description="Split to sentences",
            layout=widgets.Layout(width="auto"),
        )
        self.split_sentences_button.on_click(self.tokenize_sentences)

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
            # self.paragraph_viewer.output_widget,
            self.conversation_viewer.output_widget,
        ]
        self.right_container.children = [self.query_results_viewer.container]
        self.container_hbox = widgets.HBox([self.left_container, self.right_container])
        self.create_buttons()
        self.container = widgets.VBox([self.toggle_layout_button, self.container_hbox])

    def display(self):
        display(self.container)
        self.paragraph_viewer.display()
        self.conversation_viewer.display()
