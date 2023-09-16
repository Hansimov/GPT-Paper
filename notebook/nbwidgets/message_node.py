class MessageNode:
    def __init__(self, role="", content="", editable=False, parent=None):
        self.role = role
        self.content = content
        self.editable = editable
        self.parent = parent
        self.children = []

    def to_dict(self):
        message_dict = {
            "role": self.role,
            "content": self.content,
            "editable": False,
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
