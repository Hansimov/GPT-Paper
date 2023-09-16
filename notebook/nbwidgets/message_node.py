class MessageNode:
    def __init__(
        self,
        role="",
        content="",
        verbose_content="",
        editable=False,
        hidden=False,
        parent=None,
    ):
        self.role = role
        self.content = content
        if not verbose_content:
            self.verbose_content = content
        else:
            self.verbose_content = verbose_content
        self.editable = editable
        self.hidden = hidden
        self.parent = parent
        self.children = []
        self.message = self.to_dict()

    def get_compact_content(self, limit_width=200, shown_width=80):
        if len(self.content) > limit_width:
            return (
                self.content[:shown_width]
                + f" ... [{len(self.content)} chars in total]"
            )
        else:
            return self.content

    def to_dict(self):
        message_dict = {
            "role": self.role,
            "content": self.content,
            "editable": self.editable,
            "hidden": self.hidden,
            "compact_content": self.get_compact_content(),
            "verbose_content": self.verbose_content,
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
