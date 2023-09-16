import ipywidgets as widgets
from nbwidgets.output_viewer import MessageViewer
from IPython.display import display
from nbwidgets.message_node import MessageNode, MessageChain, MessageTree


class ConversationViewer:
    def __init__(self, messages=None):
        self.message_viewers = []
        self.create_widgets()
        self.append_messages(messages)
        self.display()

    def append_messages(self, messages):
        if messages is None:
            self.message_viewers = []
            return

        if type(messages) != list:
            messages = [messages]

        for message in messages:
            message_node = MessageNode(
                role=message.get("role", "user"),
                content=message.get("content", ""),
                editable=message.get("editable", False),
                hidden=message.get("hidden", False),
            )
            message_viewer = MessageViewer(message_node)
            self.message_viewers.append(message_viewer)

    def create_widgets(self):
        self.create_output_widget()
        self.create_user_input_widget()
        self.create_buttons()

    def display(self):
        self.output_widget.clear_output()
        with self.output_widget:
            for message_viewer in self.message_viewers:
                display(message_viewer.widget)
            display(self.user_input_viewer.widget)
            display(self.buttons_box)

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
        # user_input_content = self.user_input_viewer.on_submit()
        user_input_content = self.user_input_viewer.text_widget.value
        if user_input_content.strip():
            self.submit_button.style.button_color = "darkgreen"
            new_message = {
                "role": "user",
                "content": user_input_content,
                "editable": False,
                "hidden": False,
            }
            self.append_messages(new_message)
            self.user_input_viewer.text_widget.value = ""
            self.display()
            self.post_chat()
        else:
            self.submit_button.style.button_color = None

    def get_messages(self):
        messages = [
            message_viewer.message_node.to_dict()
            for message_viewer in self.message_viewers
        ]
        return messages

    def post_chat(self):
        print(self.get_messages())
