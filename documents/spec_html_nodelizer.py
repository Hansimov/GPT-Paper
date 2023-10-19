import hashlib
import itertools
import pandas as pd
import re

from bs4 import BeautifulSoup
from pathlib import Path


class Node:
    def __init__(self, element, idx=-1):
        self.element = element
        self.id = element.get("id", None)
        self.idx = idx
        self.classes = element.get("class", [])
        self.class_str = " ".join(self.classes)
        self.tag = element.name
        self.prev = None
        self.next = None
        self.parent = None
        self.children = []
        self.parse_element()

    def parse_element(self):
        """Implemented in subclasses."""
        self.get_text()

    def get_parent_element(self):
        self.parent_element = self.element.parent
        return self.parent_element

    def get_parent(self):
        return self.parent

    def get_parents(self, depth=0):
        parent = self.get_parent()
        for i in range(depth):
            parent = parent.get_parent()
        return parent

    def get_text(self):
        self.text = self.element.text.strip()
        return self.text

    def get_full_text(self):
        self.full_text = self.text
        return self.full_text


class JavascriptNode(Node):
    def parse_element(self):
        self.type = "javascript"
        self.get_text()


class TableNode(Node):
    def parse_element(self):
        self.type = "table"
        self.get_df()
        self.get_markdown()
        self.get_text()
        self.get_columns()

    def get_df(self):
        self.df = pd.read_html(str(self.element))[0]
        return self.df

    def get_markdown(self):
        self.markdown = self.df.to_markdown(index=False)
        return self.markdown

    def get_text(self):
        self.text = str(self.markdown)
        return self.text

    def get_columns(self):
        self.columns = self.df.columns.tolist()
        return self.columns


class TextNode(Node):
    def parse_element(self):
        self.type = "text"
        self.get_text()
        self.get_full_text()

    def get_full_text(self):
        if self.class_str:
            self.full_text = f"{self.class_str}: {self.text}"
        else:
            self.full_text = self.text
        return self.full_text


class HeaderNode(Node):
    def parse_element(self):
        self.type = "header"
        self.get_level()
        self.get_number()
        self.get_text()
        self.get_full_text()
        self.get_indented_full_text()

        # print(self.indented_full_text)

    def get_level(self):
        self.level = int(self.tag[-1])
        return self.level

    def get_number(self):
        span_element = self.element.find("span")

        if span_element:
            self.header_number = span_element.text.strip()
            span_element.extract()
        else:
            self.header_number = ""

        return self.header_number

    def get_full_text(self):
        self.full_text = f"{self.header_number} {self.text}"
        return self.full_text

    def get_indented_full_text(self, indent=2, indent_char=" ", begin_char="-"):
        indent_str = indent_char * indent * (self.level - 1)
        self.indented_full_text = (
            f"{indent_str}{begin_char} {self.header_number} {self.text}"
        )
        return self.indented_full_text


class FigureNode(Node):
    def parse_element(self):
        self.type = "figure"
        self.get_text()
        # img_tag = self.element.find("img")
        # if img_tag:
        #     self.image_source = img_tag["src"]
        #     img_tag.extract()
        # else:
        #     self.image_source = ""


class ListNode(Node):
    def parse_element(self):
        self.type = "list"


class CodeNode(Node):
    def parse_element(self):
        self.type = "code"


class SepNode(Node):
    def parse_element(self):
        self.type = "sep"


class GroupNode(Node):
    def get_text(self):
        texts = []
        for child in self.children:
            texts.append(child.get_text())
        self.text = "\n".join(texts)
        return self.text

    def get_full_text(self):
        full_texts = []
        for child in self.children:
            full_texts.append(child.get_full_text())
        self.full_text = "\n".join(full_texts)
        return self.full_text


class SectionGroupNode(GroupNode):
    def parse_element(self):
        self.type = "section_group"

    def get_header_node(self):
        for child in self.children:
            if child.type == "header":
                return child

    def get_section_level(self):
        pass

    def get_children(self):
        pass


class TableGroupNode(GroupNode):
    def parse_element(self):
        self.type = "table_group"

    def get_caption_node(self):
        for child in self.children:
            if child.class_str == "table_caption":
                return child


class ElementNodelizer:
    def __init__(self, element):
        node = None
        tag = element.name
        class_str = " ".join(element.get("class", []))

        if tag in ["script"]:
            node = JavascriptNode(element)
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            node = HeaderNode(element)
        if class_str == "figure":
            node = FigureNode(element)
        if class_str == "sourceCode" or tag == "pre":
            node = CodeNode(element)
        if tag in ["p"]:
            node = TextNode(element)
        if tag in ["ul", "ol"]:
            node = ListNode(element)
        if tag in ["hr"]:
            node = SepNode(element)
        if tag in ["table"]:
            node = TableNode(element)
        if class_str and class_str.startswith("section"):
            node = SectionGroupNode(element)
        if class_str == "table":
            node = TableGroupNode(element)

        self.node = node


class SpecHTMLNodelizer:
    def __init__(self, html_path):
        self.html_path = html_path
        with open(self.html_path, "r") as rf:
            html_string = rf.read()
        self.soup = BeautifulSoup(html_string, "html.parser")
        self.nodes = []
        self.section_node = None

    def traverse_element(self, element, parent_node=None):
        children_l1 = element.find_all(recursive=False)
        for child in children_l1:
            node = ElementNodelizer(child).node

            if node:
                self.nodes.append(node)
                if parent_node:
                    node.parent = parent_node
                    parent_node.children.append(node)
                if node.type in ["section_group", "table_group"]:
                    self.traverse_element(child, parent_node=node)
            else:
                if child.name in ["div", "blockquote"]:
                    self.traverse_element(child)
                else:
                    raise NotImplementedError

    def parse_html_to_nodes(self):
        main_element = self.soup.find(id="MAIN")
        main_node = SectionGroupNode(main_element)
        self.traverse_element(element=main_element, parent_node=main_node)
        print(f"{len(self.nodes)} nodes parsed.")
        for idx, node in enumerate(self.nodes):
            node.idx = idx
            if idx > 0:
                self.prev = self.nodes[idx - 1]
            if idx < len(self.nodes) - 1:
                self.next = self.nodes[idx + 1]

            # if node.type == "table_group":
            #     print(node.get_caption_node().full_text)

    def search_by_text(self, text):
        search_text = text
        for node in self.nodes:
            if not node.type.endswith("group"):
                if search_text.strip().lower() in node.get_text().lower():
                    print(node.type)
                    print(node.get_parents(1).type)
                    print(node.get_parents(1).get_full_text())

    def get_node_parent(self):
        pass

    def run(self):
        self.parse_html_to_nodes()
        # self.search_by_text("Traffic Generator Training Use Cases")
        # self.search_by_text("Training Step Order")
        # self.search_by_text("EnableDqDqsTrainEn")
        self.search_by_text("auto-sweep hardware")


if __name__ == "__main__":
    html_name = "Server DDR5 DMR MRC Training"
    html_path = (
        Path(__file__).parents[1] / "files" / "htmls" / "mrc" / f"{html_name}.html"
    )
    spec_html_nodelizer = SpecHTMLNodelizer(html_path)
    spec_html_nodelizer.run()
