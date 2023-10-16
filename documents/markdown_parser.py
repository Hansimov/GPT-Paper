import re
from pathlib import Path
import itertools
import hashlib


class TextNode:
    def __init__(self, text, idx):
        self.text = text
        self.idx = idx
        self.level = -1
        self.children = []

    def calc_level(self, mark="#"):
        header = re.match(r"^#+", self.text.strip())
        if header:
            self.level = len(list(itertools.takewhile(lambda x: x == mark, self.text)))

    def generate_uuid(self, salt="", id_set=None):
        self.uuid = hashlib.md5((self.text + salt).encode()).hexdigest()

    def get_json(self):
        self.json = {"uuid": self.uuid, "text": self.text, "idx": self.idx}
        return self.json


class MarkdownParser:
    def __init__(self, markdown_path):
        self.markdown_path = markdown_path
        self.headers = []
        self.nodes = []
        self.node_id_set = set()

    def get_most_recent_same_level_node(self, node):
        node_idx = node.idx
        for tmp_node in reversed(self.nodes[:node_idx]):
            if tmp_node.level == node.level:
                return tmp_node
        return None

    def get_direct_parent_node(self, node):
        node_idx = node.idx
        for tmp_node in reversed(self.nodes[:node_idx]):
            if node.level == -1:
                if tmp_node.level != -1:
                    return tmp_node
            else:
                if tmp_node.level == node.level - 1:
                    return tmp_node
        return None

    def structurize(self):
        with open(markdown_path, "r", encoding="utf-8") as rf:
            markdown_text = rf.read()
        lines = markdown_text.split("\n")

        node_idx = -1
        for line_idx, line in enumerate(lines):
            text = line.strip()
            if not text:
                continue
            node_idx += 1

            text_node = TextNode(text=text, idx=node_idx)
            text_node.calc_level()
            text_node.generate_uuid(salt=str(node_idx), id_set=self.node_id_set)
            text_node.prev = self.nodes[-1] if self.nodes else None
            if text_node.prev:
                text_node.prev.next = text_node
            else:
                text_node.prev = None

            parent_text_node = self.get_direct_parent_node(text_node)
            text_node.parent = parent_text_node
            if parent_text_node:
                parent_text_node.children.append(text_node)

            self.node_id_set.add(text_node.uuid)
            self.nodes.append(text_node)

            print(
                f"{node_idx}, {text_node.level}: "
                + f"{text_node.text}\n"
                + (f"  <{text_node.parent.text}>" if text_node.parent else "None")
            )

    def run(self):
        self.structurize()


if __name__ == "__main__":
    pdf_name = "2308.08155 - AutoGen - Enabling Next-Gen LLM Applications via Multi-Agent Conversation"
    markdown_path = (
        Path(__file__).parents[1] / "pdfs" / "llm_agents" / pdf_name / f"{pdf_name}.mmd"
    )
    markdown_parser = MarkdownParser(markdown_path)
    markdown_parser.run()
