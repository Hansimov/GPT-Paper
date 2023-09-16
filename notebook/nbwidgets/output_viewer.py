from contextlib import contextmanager
import ipywidgets as widgets
import sys
from IPython.display import display
import markdown2
from bs4 import BeautifulSoup
from cssutils import parseStyle
from nbwidgets.message_node import MessageNode


def apply_style(html_text, style, tag="div"):
    soup = BeautifulSoup(html_text, "html.parser")
    element = soup.find(tag)
    if "style" in element.attrs:
        style_dict = dict(parseStyle(element["style"]))
    else:
        style_dict = {}

    style_dict.update(parseStyle(style))
    element["style"] = "; ".join(
        [f"{key}: {value}" for key, value in style_dict.items()]
    )

    return str(soup)


class MessageViewer:
    def __init__(self, message_node: MessageNode = None):
        self.message_node = message_node
        self.create_widgets()

    def create_widgets(self):
        message = self.message_node.to_dict()

        self.text_widget = widgets.Textarea(
            value=f"{message['content']}",
            placeholder="Type something",
            layout=widgets.Layout(width="auto"),
        )
        self.output_widget = widgets.Output()
        self.html_widget = widgets.HTML(
            value=f"<div>{message['content']}</div>",
            layout=widgets.Layout(
                width="auto",
            ),
        )
        self.init_style()
        if message["role"] == "input":
            self.widget = widgets.VBox([self.text_widget])
        else:
            self.widget = widgets.VBox([self.html_widget])

    def sync_text_to_html(self):
        soup = BeautifulSoup(self.html_widget.value, "html.parser")
        div = soup.find("div")
        div.string = self.text_widget.value
        self.html_widget.value = str(soup)

    def sync_html_to_text(self):
        soup = BeautifulSoup(self.html_widget.value, "html.parser")
        div = soup.find("div")
        self.text_widget.value = div.text

    # def on_submit(self, callback=None):
    #     self.sync_text_to_html()
    #     if self.text_widget.value.strip() == "":
    #         return ""

    #     self.html_widget.value = apply_style(
    #         self.html_widget.value,
    #         "background: rgba(0, 100, 0, 0.5); padding: 8px; margin: 0px;",
    #     )
    #     self.widget = widgets.VBox(
    #         [self.html_widget],
    #         layout=widgets.Layout(width="auto"),
    #     )
    #     self.output_widget.clear_output()
    #     self.display()
    #     return self.text_widget.value

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
            display(self.widget)


class OutputViewer:
    def __init__(self, output="", id=None, display_mode="markdown", editable=False):
        self.id = id
        self.output = output
        self.display_mode = display_mode
        self.editable = editable
        self.create_widget()

    def create_widget(self):
        if self.display_mode == "markdown":
            html_text = f"<div>{self.output}</div>"
            self.widget = widgets.HTML(value=html_text)

            soup = BeautifulSoup(self.widget.value, "html.parser")
            for tag in soup.find_all("div"):
                if self.editable:
                    tag["contenteditable"] = "true"
                if self.id:
                    tag["id"] = self.id
            self.widget.value = str(soup)
        else:
            self.widget = widgets.HTML(value=self.output)

    def md2html(self, markdown_text):
        return markdown2.markdown(markdown_text)

    def use_style(self, style):
        if self.display_mode == "markdown":
            soup = BeautifulSoup(self.widget.value, "html.parser")
            for tag in soup.find_all("div"):
                tag["style"] = style

            self.widget.value = str(soup)

    def set_editable(self, editable=False):
        self.editable = editable
        soup = BeautifulSoup(self.widget.value, "html.parser")
        for tag in soup.find_all("div"):
            if self.editable:
                tag["contenteditable"] = "true"
            else:
                tag["contenteditable"] = "false"
        self.widget.value = str(soup)

    def display(self):
        display(self.widget)

    def clear_output(self):
        self.output = ""
        self.widget.value = self.output

    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.stdout = self.original_stdout

        if self.display_mode == "markdown":
            if self.id:
                id_str = f"id='{self.id}'"
            else:
                id_str = ""
            self.widget.value = f"""
                <div {id_str}>
                    {self.md2html(self.output)}
                </div>
            """
        else:
            self.widget.value = self.output

    def write(self, text):
        self.output += text

    def flush(self):
        pass

    def update(self, text):
        self.widget.value = self.md2html(text)
