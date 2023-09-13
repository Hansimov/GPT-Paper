from contextlib import contextmanager
import ipywidgets as widgets
import sys
from IPython.display import display


class OutputWidget:
    def __init__(self):
        self.output = ""
        self.html_widget = widgets.HTML()

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
        self.html_widget.value = self.output

    def write(self, text):
        self.output += text.replace("\n", "<br/>")

    def flush(self):
        pass

    def update(self, text):
        self.html_widget.value = text
