import re
import itertools
import hashlib
from bs4 import BeautifulSoup
from pathlib import Path


class Node:
    def __init__(self, ele, description=None):
        self.ele = ele
        self.description = description

        self.prev = None
        self.next = None
        self.parent = None
        self.children = []

        self.parse_element()

    def parse_element(self):
        self.text = ele.text.strip()


class HeaderNode:
    def __init__(self, ele):
        self.prev = None
        self.next = None
        self.parent = None
        self.children = []
        self.ele = ele

    def parse(self):
        span = self.ele.find("span")
        if span:
            self.section = span.text.strip()
            span.extract()
        else:
            self.section = ""
        self.tag = self.ele.name
        self.text = self.ele.text.strip()
        self.level = int(self.tag[-1])
        print(f"{self.tag}: <{self.section}> {self.text}")


class SpecHTMLNodelizer:
    def __init__(self, html_path):
        self.html_path = html_path
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
        with open(self.html_path, "r", encoding="utf-8") as rf:
            html_str = rf.read()
        soup = BeautifulSoup(html_str, "html.parser")

        # headers = soup.find_all(re.compile(r"^h[1-6]$"))
        # for header in headers:
        #     header_node = HeaderNode(header)
        #     header_node.parse()

        root = soup.find(id="MAIN")

        level1_children = root.find_all(recursive=False)
        for child in level1_children:
            if "class" in child.attrs:
                class_name = child["class"]
            else:
                class_name = None
            print(child.name, class_name)

        # # Element [id="header"]: title, author, date
        # head_ele = root.find(id="header")

        # title_ele = head_ele.find("p", {"class": "title"})
        # title_node = Node(ele=title_ele, description="title")
        # self.nodes.append(title_node)

        # author_ele = head_ele.find("p", {"class": "author"})
        # author_node = Node(ele=author_ele, description="author")
        # self.nodes.append(author_node)

        # date_ele = head_ele.find("p", {"class": "date"})
        # date_node = Node(ele=date_ele, description="date")
        # self.nodes.append(date_node)

        # node_idx = -1
        # for line_idx, line in enumerate(lines):
        #     text = line.strip()
        #     if not text:
        #         continue
        #     node_idx += 1

        #     node = ElementNode(text=text, idx=node_idx, tag=tag)
        #     node.calc_level()
        #     node.generate_uuid(salt=str(node_idx), id_set=self.node_id_set)
        #     self.node_id_set.add(node.uuid)

        #     node.prev = self.nodes[-1] if self.nodes else None
        #     if node.prev:
        #         node.prev.next = node

        #     node.parent = self.get_direct_parent_node(node)
        #     if node.parent:
        #         node.parent.children.append(node)

        #     self.nodes.append(node)

        # print(
        #     f"{node_idx}, {node.level}: "
        #     + f"{node.text}\n"
        #     + (f"  <{node.parent.text}>" if node.parent else "None")
        # )

    def run(self):
        self.structurize()
        # self.get_headers()
        # print(f"{len(self.nodes)} nodes, and {len(self.headers)} headers.")


if __name__ == "__main__":
    html_name = "Server DDR5 DMR MRC Training"
    html_path = (
        Path(__file__).parents[1] / "files" / "htmls" / "mrc" / f"{html_name}.html"
    )
    spec_html_nodelizer = SpecHTMLNodelizer(html_path)
    spec_html_nodelizer.run()
