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

    def create_split_sentence_button(self):
        self.split_sentences_button = widgets.Button(
            description="Split to sentences",
            layout=widgets.Layout(width="auto"),
        )
        self.split_sentences_button.on_click(self.tokenize_sentences)

    def create_conversation_viewer(self):
        self.conversation_viewer = ConversationViewer()

    def create_query_results_viewer(self):
        queries = self.documents_retriever.query(
            [
                "The AI-based diagnosis was the first implementation of computer vision in pathology."
            ],
        )
        self.query_results_viewer = QueryResultsViewer(queries)

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
        self.container = widgets.HBox([self.left_container, self.right_container])

    def display(self):
        display(self.container)
        self.paragraph_viewer.display()
        self.conversation_viewer.display()
