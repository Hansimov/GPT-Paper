import ipywidgets as widgets
from nbwidgets.message_viewer import MessageViewer, MessageNode
from IPython.display import display


class ParagraphViewer:
    def __init__(self):
        self.create_widgets()

    def create_text_editor(self):
        self.text_viewer = MessageViewer(
            MessageNode(role="input"), placeholder="Paragraph"
        )

    def create_widgets(self):
        self.create_text_editor()
        self.output_widget = self.text_viewer.output_widget
        self.widget = self.text_viewer.widget

    def display(self):
        self.text_viewer.display()
