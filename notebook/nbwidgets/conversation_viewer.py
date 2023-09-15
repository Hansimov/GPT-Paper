import ipywidgets as widgets
from nbwidgets.output_viewer import OutputViewer
from IPython.display import display


class ConversationViewer:
    def __init__(self, messages=None):
        self.messages = messages
        self.output_viewers = []

    def create_user_input_widget(self):
        self.user_input_viewer = OutputViewer(
            output="?", id="user_input", editable=True
        )
        self.user_input_viewer.use_style(
            f"""
                background-color: rgba(100, 100, 100, 0.5);
                padding: 8px;
            """
        )
        self.user_input_button = widgets.HTML(
            value=f"""
                <button
                    style='
                        background-color: rgba(100, 100, 100, 0.5);
                        padding: 8px;
                    '
                    onclick='
                        var user_input = document.getElementById("user_input");
                        console.log(user_input);
                        var user_input_content = user_input.innerHTML;
                        var kernel = IPython.notebook.kernel;
                        kernel.execute("user_input = " + "\\"" + user_input_content + "\\"");
                        kernel.execute("conversation_viewer.submit_user_input()");
                    '
                >
                    Chat
                </button>
            """
        )
        self.user_input_widget = widgets.VBox(
            [self.user_input_viewer.widget, self.user_input_button]
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
                    padding: 8px;
                """
            )
            self.output_viewers.append(output_viewer)

        self.create_user_input_widget()
        self.container = widgets.VBox(
            [output_viewer.widget for output_viewer in self.output_viewers]
            + [self.user_input_widget]
        )

    def submit_user_input(self):
        self.user_input_widget.set_editable(False)

    def display(self):
        display(self.container)
