import ipywidgets as widgets
from nbwidgets.output_viewer import OutputViewer
from IPython.display import display


class ConversationViewer:
    def __init__(self, messages=None):
        self.messages = messages
        self.output_viewers = []

    def create_user_input_widget(self):
        self.user_input_widget = OutputViewer(output="Type something", editable=True)
        self.user_input_widget.use_style(
            f"""
                background-color: rgba(100, 0, 0, 0.5);
                padding: 10px;
            """
        )

    def construct_widgets_from_messages(self):
        for message in self.messages:
            role = message["role"]
            content = message["content"]
            output_viewer = OutputViewer(content)
            if role == "system":
                output_viewer_background_color = "rgba(100, 100, 0, 0.5)"
            elif role == "user":
                output_viewer_background_color = "rgba(0, 100, 0, 0.5)"
            else:  # role == "assistant"
                output_viewer_background_color = "rgba(0, 100, 100, 0.5)"

            output_viewer.use_style(
                f"""
                    background-color: {output_viewer_background_color};
                    padding: 10px;
                """
            )
            self.output_viewers.append(output_viewer)
        self.create_user_input_widget()
        self.output_viewers.append(self.user_input_widget)
        self.container = widgets.VBox(
            [output_viewer.widget for output_viewer in self.output_viewers]
        )

    def display(self):
        display(self.container)
