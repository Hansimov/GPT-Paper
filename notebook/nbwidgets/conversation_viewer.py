import ipywidgets as widgets
from nbwidgets.output_viewer import OutputViewer, UserInputViewer
from IPython.display import display


class ConversationViewer:
    def __init__(self, messages=None):
        self.messages = messages
        self.output_viewers = []

    def create_user_input_widget(self):
        self.user_input_viewer = UserInputViewer()

    def create_buttons(self):
        self.buttons_box = widgets.HBox()
        self.submit_button = widgets.Button(
            description="Submit", layout=widgets.Layout(width="auto")
        )
        self.submit_button.on_click(self.submit_user_input)
        self.model_html_widget = widgets.HTML(value="<div>model: </div>")
        self.model_dropdown = widgets.Dropdown(
            options=["poe-gpt-3.5-turbo", "poe-gpt-3.5-turbo-16k", "poe-gpt-4"],
            value="poe-gpt-3.5-turbo-16k",
            layout=widgets.Layout(width="auto"),
        )
        self.buttons_box.children = [
            self.submit_button,
            self.model_html_widget,
            self.model_dropdown,
        ]

    def submit_user_input(self, button=None):
        self.submit_button.style.button_color = "orange"
        user_input_content = self.user_input_viewer.on_submit()
        if user_input_content:
            self.submit_button.style.button_color = "darkgreen"
        else:
            self.submit_button.style.button_color = None

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

            output_viewer.apply_style(
                f"""
                    background-color: {output_viewer_background_color};
                    padding: 8px;
                """
            )
            self.output_viewers.append(output_viewer)

        self.create_user_input_widget()
        self.create_buttons()
        self.widgets = [
            output_viewer.widget for output_viewer in self.output_viewers
        ] + [self.user_input_viewer.output_widget, self.buttons_box]
        self.container = widgets.VBox(self.widgets)

    def display(self):
        display(self.container)
        self.user_input_viewer.display()
