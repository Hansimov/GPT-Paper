from contextlib import contextmanager
import ipywidgets as widgets
import sys
from IPython.display import display
import markdown2


class OutputViewer:
    def __init__(self, output="", display_mode="markdown", editable=False):
        self.output = output
        self.display_mode = display_mode
        self.editable = editable
        self.create_widget()

    def create_widget(self):
        self.widget = widgets.HTML(value=self.output)

    def md2html(self, markdown_text):
        return markdown2.markdown(markdown_text)

    def use_style(self, style):
        if self.display_mode == "markdown":
            if self.editable:
                editable_style = "contenteditable='true'"
            else:
                editable_style = ""

            self.widget.value = (
                f"<div {editable_style} style='{style}'>{self.widget.value}</style>"
            )

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
            self.widget.value = self.md2html(self.output)
        else:
            self.widget.value = self.output

    def write(self, text):
        self.output += text

    def flush(self):
        pass

    def update(self, text):
        self.widget.value = self.md2html(text)
