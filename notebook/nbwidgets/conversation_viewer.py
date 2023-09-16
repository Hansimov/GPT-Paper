import ipywidgets as widgets
from nbwidgets.output_viewer import OutputViewer, MessageViewer
from IPython.display import display
from nbwidgets.message_node import MessageNode, MessageChain, MessageTree


class ConversationViewer:
    def __init__(self, messages=None):
        if messages is None:
            messages = []
        self.messages = messages
        self.message_nodes = [
            MessageNode(
                role=message.get("role", "user"),
                content=message.get("content", ""),
                editable=message.get("editable", False),
                hidden=message.get("hidden", False),
            )
            for message in self.messages
        ]
        self.output_viewers = []
        self.create_output_widget()

    def create_output_widget(self):
        self.output_widget = widgets.Output()
        display(self.output_widget)

    def create_user_input_widget(self):
        message_node = MessageNode(role="input")
        self.user_input_viewer = MessageViewer(message_node)

    def create_buttons(self):
        self.buttons_box = widgets.HBox()
        self.submit_button = widgets.Button(
            description="Submit", layout=widgets.Layout(width="auto")
        )
        self.submit_button.on_click(self.submit_user_input)
        self.model_html_widget = widgets.HTML(value="<div>model: </div>")
        self.available_models = [
            "poe-gpt-3.5-turbo-16k",
            "poe-gpt-3.5-turbo",
            "poe-gpt-4",
        ]
        self.model_dropdown = widgets.Dropdown(
            options=self.available_models,
            value=self.available_models[0],
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
        if user_input_content.strip():
            self.submit_button.style.button_color = "darkgreen"
            new_message_node = MessageNode(
                role="user",
                content=user_input_content + " [Submitted]",
                editable=False,
                hidden=True,
            )
            self.message_nodes.append(new_message_node)
            self.update_display()
            # print(self.message_nodes)
            self.messages.append(new_message_node.to_dict())
        else:
            self.submit_button.style.button_color = None

    def update_display(self):
        self.construct_widgets_from_messages()
        self.output_widget.clear_output()
        self.display()

    def construct_widgets_from_messages(self):
        self.output_viewers = []
        for message_node in self.message_nodes:
            output_viewer = MessageViewer(message_node)

            self.output_viewers.append(output_viewer)

        self.create_user_input_widget()
        self.create_buttons()
        self.widgets = [
            output_viewer.widget for output_viewer in self.output_viewers
        ] + [self.user_input_viewer.output_widget, self.buttons_box]
        self.container = widgets.VBox(self.widgets)

    def display(self):
        with self.output_widget:
            display(self.container)
            self.user_input_viewer.display()
