from contextlib import contextmanager
import ipywidgets as widgets
import sys
from IPython.display import display
import markdown2


class OutputWidget:
    def __init__(self):
        self.output = ""
        self.html = ""
        self.html_widget = widgets.HTML()

    def md2html(self, markdown_text):
        return markdown2.markdown(markdown_text)

    def display(self):
        display(self.html_widget)

    def clear_output(self):
        self.output = ""
        self.html_widget.value = self.output

    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.stdout = self.original_stdout
        self.html_widget.value = self.md2html(self.output)
        # self.html_widget.value = self.output

    def write(self, text):
        self.output += text

    def flush(self):
        pass

    def update(self, text):
        self.html_widget.value = self.md2html(text)
