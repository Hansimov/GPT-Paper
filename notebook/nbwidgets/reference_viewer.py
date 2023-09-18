from IPython.display import display
from agents.documents_retriever import DocumentsRetriever
from nbwidgets.query_results_viewer import QueryResultsViewer
from nbwidgets.conversation_viewer import ConversationViewer
import ipywidgets as widgets


class ReferenceViewer:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.documents_retriever = DocumentsRetriever(self.project_dir)
        self.create_widgets()

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
        self.create_conversation_viewer()
        self.create_query_results_viewer()
        self.left_container = widgets.VBox(layout=widgets.Layout(width="50%"))
        self.right_container = widgets.VBox(layout=widgets.Layout(width="50%"))
        self.left_container.children = [self.conversation_viewer.output_widget]
        self.right_container.children = [self.query_results_viewer.container]
        self.container = widgets.HBox([self.left_container, self.right_container])

    def display(self):
        display(self.container)
        self.conversation_viewer.display()
