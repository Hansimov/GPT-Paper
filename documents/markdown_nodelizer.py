import re
from pathlib import Path
import itertools
import hashlib


class TextNode:
    def __init__(self, text, idx):
        self.text = text
        self.idx = idx
        self.level = -1
        self.prev = None
        self.next = None
        self.parent = None
        self.children = []

    def calc_level(self, mark="#"):
        header = re.match(r"^#+", self.text.strip())
        if header:
            self.level = len(list(itertools.takewhile(lambda x: x == mark, self.text)))

        return self.level

    def generate_uuid(self, salt="", id_set=None):
        self.uuid = hashlib.md5((self.text).encode()).hexdigest()

        while self.uuid in id_set:
            self.uuid = hashlib.md5((self.text + salt).encode()).hexdigest()
            # print("Re-generate UUID")

        return self.uuid

    def get_json(self):
        self.json = {"uuid": self.uuid, "text": self.text, "idx": self.idx}
        return self.json


class MarkdownNodelizer:
    def __init__(self, markdown_path):
        self.markdown_path = markdown_path
        self.titles = []
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

    def get_titles(self):
        for node in self.nodes:
            if node.level != -1:
                self.titles.append(node)
                title = re.sub(r"^#+", "", node.text)
                title_str = (node.level - 1) * 2 * " " + "-" + title
                print(title_str)

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

            node = TextNode(text=text, idx=node_idx)
            node.calc_level()
            node.generate_uuid(salt=str(node_idx), id_set=self.node_id_set)
            self.node_id_set.add(node.uuid)

            node.prev = self.nodes[-1] if self.nodes else None
            if node.prev:
                node.prev.next = node

            node.parent = self.get_direct_parent_node(node)
            if node.parent:
                node.parent.children.append(node)

            self.nodes.append(node)

        # print(
        #     f"{node_idx}, {node.level}: "
        #     + f"{node.text}\n"
        #     + (f"  <{node.parent.text}>" if node.parent else "None")
        # )

    def run(self):
        self.structurize()
        self.get_titles()
        print(f"{len(self.nodes)} nodes, and {len(self.titles)} titles.")


if __name__ == "__main__":
    pdf_name = "2308.08155 - AutoGen - Enabling Next-Gen LLM Applications via Multi-Agent Conversation"
    markdown_path = (
        Path(__file__).parents[1] / "pdfs" / "llm_agents" / pdf_name / f"{pdf_name}.mmd"
    )
    markdown_nodelizer = MarkdownNodelizer(markdown_path)
    markdown_nodelizer.run()
