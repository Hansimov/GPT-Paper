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

    def get_div_text(self):
        soup = BeautifulSoup(self.widget.value, "html.parser")
        div = soup.find("div")
        return div.text

    def switch_widget_mode(self, widget_mode="textarea"):
        if widget_mode == "html":
            self.widget = widgets.HTML(value=self.widget.value)
        elif widget_mode == "textarea":
            self.widget = widgets.Textarea(value=self.get_div_text())
        else:
            pass
        self.display()

    def apply_style(self, style):
        if self.display_mode == "markdown":
            soup = BeautifulSoup(self.widget.value, "html.parser")
            div = soup.find("div")
            if "style" in div.attrs:
                style_dict = dict(parseStyle(div["style"]))
            else:
                style_dict = {}

            style_dict.update(parseStyle(style))
            div["style"] = "; ".join(
                [f"{key}: {value}" for key, value in style_dict.items()]
            )

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
