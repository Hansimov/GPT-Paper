class MessageNode:
    def __init__(self, role="", content="", hidden=False, editable=False, parent=None):
        self.role = role
        self.content = content
        self.editable = editable
        self.hidden = hidden
        self.parent = parent
        self.children = []
        self.message = self.to_dict()

    def content_shown(self, limit_width=40, shown_width=40):
        if self.hidden and len(self.content) > limit_width:
            return self.content[:shown_width] + " ..."
        else:
            return self.content

    def to_dict(self):
        message_dict = {
            "role": self.role,
            "content": self.content,
            "editable": self.editable,
            "hidden": self.hidden,
            "content_shown": self.content_shown(),
        }
        return message_dict


class MessageChain:
    def __init__(self, messages=None):
        if messages is None:
            messages = []
        self.messages = []
        self.message_nodes = [
            MessageNode(
                role=message["role"],
                content=message["content"],
                editable=message["editable"],
            )
            for message in self.messages
        ]

    def append(self, message_node: MessageNode):
        self.message_nodes.append(message_node)

    def to_list(self):
        message_list = [message_node.to_dict() for message_node in self.message_nodes]
        return message_list


class MessageTree:
    def __init__(self, message_nodes):
        self.message_nodes = message_nodes
