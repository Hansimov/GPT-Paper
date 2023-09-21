import ipywidgets as widgets
from nbwidgets.message_viewer import MessageViewer, MessageNode
from IPython.display import display
from utils.tokenizer import SentenceTokenizer


class ParagraphViewer:
    def __init__(self):
        self.create_widgets()

    def create_output_widget(self):
        self.output_widget = widgets.Output(layout=widgets.Layout())

    def create_text_viewer(self):
        self.text_viewer = MessageViewer(
            MessageNode(role="input"), placeholder="Paragraph"
        )

    def create_result_viewer(self):
        self.result_viewer = MessageViewer(MessageNode(role="other"))

    def create_buttons(self):
        self.split_to_sentences_button = widgets.Button(
            description="Split paragraph",
            layout=widgets.Layout(width="auto"),
        )
        self.split_to_sentences_button.on_click(self.split_to_sentences)

        self.buttons_box = widgets.HBox([self.split_to_sentences_button])

    def split_to_sentences(self, button=None):
        self.split_to_sentences_button.style.button_color = "orange"
        paragraph_text = self.text_viewer.text_widget.value
        if not paragraph_text.strip():
            self.split_to_sentences_button.style.button_color = None
            return
        self.sentence_tokenizer = SentenceTokenizer()
        sentences = self.sentence_tokenizer.text_to_sentences(paragraph_text)
        self.result_viewer.text_widget.value = "\n".join(
            [f"{idx+1}. {sentence}" for idx, sentence in enumerate(sentences)]
        )
        self.result_viewer.sync_text_to_html()
        self.split_to_sentences_button.style.button_color = "green"

    def send_to_query(self, button=None):
        pass

    def create_widgets(self):
        self.create_output_widget()
        self.create_text_viewer()
        self.create_result_viewer()
        self.create_buttons()

    def display(self):
        with self.output_widget:
            for viewer in [self.text_viewer, self.result_viewer]:
                display(viewer.output_widget)
                viewer.sync_text_to_html()
                viewer.display()
        display(self.buttons_box)
