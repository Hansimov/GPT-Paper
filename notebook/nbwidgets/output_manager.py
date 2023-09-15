import ipywidgets as widgets


class BasicOutputNode:
    def __init__(self, output, content, prev=None, next=None):
        self.output = output
        self.content = content
        self.prev = None
        self.next = None


class BasicOutputNodeChain:
    def __init__(self):
        self.outputs = []
        self.active_idx = -1

    def append(self, output_node: BasicOutputNode):
        self.outputs.append(output_node)
        self.active_idx = len(self.outputs) - 1

    def increment_active_idx(self):
        if self.active_idx >= len(self.outputs) - 1:
            return
        else:
            self.active_idx += 1

    def decrement_active_idx(self):
        if self.active_idx <= 0:
            return
        else:
            self.active_idx -= 1

    def set_active_idx(self, idx):
        if idx < 0 or idx >= len(self.outputs):
            return

    def active_output(self):
        if len(self.outputs) == 0:
            return None
        return self.outputs[self.active_idx].output


class OutputNode:
    def __init__(self, request=None, response=None, parent=None):
        """
        Initialize OutputNode with agent messages and params.

        Args:
        - requests: [List] requests to agents
            - `request` is a dict with following keys:
              - ["model", "messages"(request_messages), "temperature", ...]
              - (alias of `request_payload` in agent)
              - # LINK agents/openai.py#agent-request-payload
            - `response` (str)
              - (alias of `reponse_content` in agent)
              - # LINK agents/openai.py#agent-response-content

        For each key in the requests:
            - `model`:
                - # LINK agents/openai.py#agent-available-models
                - ["gpt-3.5-turbo", "gpt-4", "poe-gpt-3.5-turbo-16k", "claude-2-100k", ...]
            - `temperature`: (float in [0,1])
                - # LINK agents/openai.py#agent-init
            - `messages`: [List] messages to agents
                - # LINK agents/openai.py#agent-request-messages
                - `role`:
                    - ["system", "user", "assistant"]
                - `content`
        """
        self.requests = requests
        self.parent = None
        self.children = []


class OutputCountWidget:
    def __init__(self, output_chain: BasicOutputNodeChain):
        self.html_widget = widgets.HTML()
        self.output_chain = output_chain
        self.update()

    def update(self):
        self.html_widget.value = (
            f"{self.output_chain.active_idx + 1}/{len(self.output_chain.outputs)}"
        )
