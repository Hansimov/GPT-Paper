from contextlib import contextmanager
import ipywidgets as widgets
import sys
from IPython.display import display
import markdown2
from bs4 import BeautifulSoup
from cssutils import parseStyle
from nbwidgets.message_node import MessageNode


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
