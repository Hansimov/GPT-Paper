from IPython.display import display
from agents.documents_retriever import DocumentsRetriever
from nbwidgets.message_viewer import MessageViewer, MessageNode
from nbwidgets.query_results_viewer import QueryResultsViewer
from nbwidgets.conversation_viewer import ConversationViewer
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
        if self.layout_mode == "both":
            self.left_container.layout.width = "100%"
            self.right_container.layout.width = "0%"
            self.layout_mode = "left"
        elif self.layout_mode == "left":
            self.left_container.layout.width = "0%"
            self.right_container.layout.width = "100%"
            self.layout_mode = "right"
        elif self.layout_mode == "right":
            self.left_container.layout.width = "50%"
            self.right_container.layout.width = "50%"
            self.layout_mode = "both"
        else:
            pass
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
        self.create_buttons()
        self.container = widgets.VBox(
            [
                self.toggle_layout_button,
                widgets.HBox([self.left_container, self.right_container]),
            ]
        )

    def display(self):
        display(self.container)
        self.paragraph_viewer.display()
        self.conversation_viewer.display()
