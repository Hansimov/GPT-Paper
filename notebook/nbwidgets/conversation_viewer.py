import ipywidgets as widgets
from nbwidgets.message_viewer import MessageViewer
from IPython.display import display
from nbwidgets.message_node import MessageNode, MessageChain, MessageTree
from nbwidgets.styles import enable_textarea_auto_expand, enable_scroll_to_chat_bottom
from time import sleep
from datetime import datetime
from agents.openai import OpenAIAgent
from functools import partial
from pprint import pprint


class ConversationViewer:
    def __init__(self, messages=None):
        self.message_viewers = []
        self.create_widgets()
        self.append_messages(messages)
        # self.display()

    def create_output_widget(self):
        self.output_widget = widgets.Output(layout=widgets.Layout(max_height="700px"))
        # display(self.output_widget)

    def create_anchor_widget(self):
        self.anchor_widget = widgets.HTML(value="<chat-anchor></chat-anchor>")

    def create_user_input_widget(self):
        message_node = MessageNode(role="input")
        self.user_input_viewer = MessageViewer(message_node)

    def create_buttons(self):
        self.buttons_box = widgets.HBox()
        self.submit_button = widgets.Button(
            description="Submit", layout=widgets.Layout(width="auto")
        )
        self.submit_button.on_click(self.submit_user_input)

        self.regenerate_button = widgets.Button(
            description="Regenerate", layout=widgets.Layout(width="auto")
        )
        self.regenerate_button.on_click(self.regenerate_message)

        self.pop_message_button = widgets.Button(
            description="Pop", layout=widgets.Layout(width="auto")
        )
        self.pop_message_button.on_click(
            partial(self.pop_message, is_display=True, pop_count=2)
        )

        self.stop_button = widgets.Button(
            description="Stop", layout=widgets.Layout(width="auto")
        )
        self.stop_button.on_click(self.stop_chat)

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
            self.regenerate_button,
            self.stop_button,
            self.pop_message_button,
            self.model_html_widget,
            self.model_dropdown,
        ]

    def create_widgets(self):
        self.create_output_widget()
        self.create_anchor_widget()
        self.create_user_input_widget()
        self.create_buttons()

    def display(self):
        self.display_times = getattr(self, "display_times", 0) + 1

        self.output_widget.clear_output()
        with self.output_widget:
            display(self.anchor_widget)
            for message_viewer in self.message_viewers:
                display(message_viewer.output_widget)
                message_viewer.sync_text_to_html()
                message_viewer.display()
        display(self.user_input_viewer.widget)
        display(self.buttons_box)

        if self.display_times <= 1:
            enable_textarea_auto_expand()
            enable_scroll_to_chat_bottom()

    def display_new_message(self, message_count=1):
        with self.output_widget:
            for message_viewer in self.message_viewers[-message_count:]:
                display(message_viewer.output_widget)
                message_viewer.sync_text_to_html()
                message_viewer.display()

    def submit_user_input(self, button=None):
        self.submit_button.style.button_color = "orange"
        user_input_content = self.user_input_viewer.text_widget.value
        if user_input_content.strip():
            new_user_input_message = {
                "role": "user",
                "content": user_input_content,
                "editable": False,
                "hidden": False,
            }
            self.append_messages(new_user_input_message)
            self.user_input_viewer.text_widget.value = ""
            self.display_new_message(1)
            # self.display()
            self.post_chat()
            self.submit_button.style.button_color = "darkgreen"
        else:
            self.submit_button.style.button_color = None

    def pop_message(self, button=None, is_display=False, pop_count=1):
        popped_messages = []
        for _ in range(pop_count):
            if len(self.message_viewers) == 0:
                break
            popped_message = self.message_viewers.pop()
            pprint(popped_message.message_node.to_dict())
            popped_messages.append(popped_message)
        if is_display:
            self.display()
        return popped_messages

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
                verbose_content=message.get("verbose_content", ""),
                editable=message.get("editable", False),
                hidden=message.get("hidden", False),
            )
            message_viewer = MessageViewer(message_node)
            self.message_viewers.append(message_viewer)

    def regenerate_message(self, button=None):
        self.regenerate_button.style.button_color = "orange"
        self.pop_message()
        self.post_chat()
        self.regenerate_button.style.button_color = "darkgreen"

    def get_messages(self):
        messages = [
            message_viewer.message_node.to_dict()
            for message_viewer in self.message_viewers
        ]
        return messages

    def get_last_message_viewer(self):
        return self.message_viewers[-1]

    def post_chat(self):
        new_assistant_message = {
            "role": "assistant",
            "content": "",
            "editable": False,
            "hidden": False,
        }
        self.append_messages(new_assistant_message)
        self.display_new_message(1)

        agent = OpenAIAgent(
            model=self.model_dropdown.value,
            memory=True,
            history_messages=self.get_messages()[:-1],
            update_widget=self.get_last_message_viewer(),
        )

        response_content = agent.chat(prompt="")
        last_message_viewer = self.get_last_message_viewer()
        last_message_viewer.message_node.verbose_content = (
            last_message_viewer.text_widget.value
        )
        last_message_viewer.message_node.content = response_content
        last_message_viewer.sync_text_to_html()

    def stop_chat(self, button=None):
        self.stop_button.style.button_color = "orange"
        # self.pop_message()
        self.stop_button.style.button_color = "darkgreen"
