import ipywidgets as widgets
import markdown2
from bs4 import BeautifulSoup
from IPython.display import display
from nbwidgets.styles import apply_style
from nbwidgets.message_node import MessageNode


class MessageViewer:
    def __init__(self, message_node: MessageNode = None, compact_display=False):
        self.message_node = message_node
        self.compact_display = compact_display
        self.create_widgets()

    def create_widgets(self):
        message = self.message_node.to_dict()

        self.text_widget = widgets.Textarea(
            value=f"{message['verbose_content']}",
            placeholder="Type something",
            layout=widgets.Layout(width="auto"),
        )
        self.output_widget = widgets.Output()
        self.html_widget = widgets.HTML(
            value=f"<div>{message['verbose_content']}</div>",
            layout=widgets.Layout(width="auto"),
        )
        self.init_style()
        if message["role"] == "input":
            self.widget = self.text_widget
        else:
            self.widget = self.html_widget

    def sync_text_to_html(self, render=True):
        soup = BeautifulSoup(self.html_widget.value, "html.parser")
        div = soup.find("div")

        div.clear()
        if render:
            div_content = BeautifulSoup(
                markdown2.markdown(self.text_widget.value), "html.parser"
            )

        else:
            div_content = self.text_widget.value
        div.append(div_content)

        self.html_widget.value = str(soup)

    def sync_html_to_text(self):
        soup = BeautifulSoup(self.html_widget.value, "html.parser")
        div = soup.find("div")
        self.text_widget.value = div.text

    def update_text(self, text, update_type="append"):
        if update_type == "append":
            self.text_widget.value += text
        else:
            self.text_widget.value = text
        self.message_node.verbose_content = self.text_widget.value
        self.sync_text_to_html()

    def get_text(self):
        return self.text_widget.value

    def on_edit(self, callback=None):
        self.sync_html_to_text()
        self.widget = widgets.VBox([self.text_widget])
        self.output_widget.clear_output()
        self.display()

    def init_style(self, style=None):
        ROLE_BACKGROUND_COLORS = {
            "system": (100, 100, 0, 0.5),
            "user": (0, 100, 0, 0.5),
            "assistant": (0, 100, 100, 0.5),
            "input": (100, 100, 100, 0.5),
        }
        bg_color = ROLE_BACKGROUND_COLORS[self.message_node.role]

        self.html_widget.value = apply_style(
            self.html_widget.value,
            f"background-color: rgba{bg_color}; padding: 8px;",
        )

    def display(self):
        with self.output_widget:
            if self.compact_display:
                self.text_widget.value = self.message_node.get_compact_content()
                self.sync_text_to_html()
                display(self.widget)
            else:
                display(self.widget)
