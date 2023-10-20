import hashlib
import itertools
import pandas as pd
import re

import bs4
from bs4 import BeautifulSoup
from pathlib import Path


class Node:
    def __init__(self, element):
        self.element = element
        self.tag = element.name
        self.prev = None
        self.next = None
        self.parent = None
        self.children = []

        if isinstance(element, bs4.element.NavigableString):
            pass
        else:
            self.id = element.get("id", None)
            self.classes = element.get("class", [])
            self.class_str = " ".join(self.classes)

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
        if self.tag not in ["p", "span"]:
            self.tagged_text = f"<{self.tag}>{self.text}</{self.tag}>"
        else:
            self.tagged_text = self.text

        if self.class_str:
            self.full_text = f"{self.class_str}: {self.tagged_text}"
        else:
            self.full_text = self.tagged_text
        return self.full_text


class StringNode(Node):
    def parse_element(self):
        self.type = "string"
        self.get_text()

    def get_text(self):
        self.text = str(self.element)
        return self.text


class HyperlinkNode(Node):
    def parse_element(self):
        self.type = "hyperlink"
        self.get_text()
        self.get_href()

    def get_text(self):
        self.text = self.element.text.strip()
        return self.text

    def get_href(self):
        self.href = self.element.get("href", None)
        return self.href


class HeaderNode(Node):
    def parse_element(self):
        self.type = "header"
        self.get_level()
        self.get_number()
        self.get_text()
        self.get_full_text()
        self.get_indented_full_text()

    def get_level(self):
        self.level = int(self.tag[-1])
        return self.level

    def get_text(self):
        for content in self.element.contents:
            if isinstance(content, bs4.element.NavigableString):
                self.text = content.strip()
                break
        return self.text

    def get_number(self):
        span_element = self.element.find("span")

        if span_element:
            self.header_number = span_element.text.strip()
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


class CodeNode(Node):
    def parse_element(self):
        self.type = "code"
        self.get_text()


class SeparatorNode(Node):
    def parse_element(self):
        self.type = "sep"
        self.get_text()


class ImageNode(Node):
    def parse_element(self):
        self.type = "img"
        self.get_text()

    def get_text(self):
        self.text = self.element.get("alt", "")
        return self.text

    def get_src(self):
        self.src = self.element.get("src", "")
        return self.src

    def get_full_text(self):
        self.full_text = f"![{self.text}]({self.src})"


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


class FigureGroupNode(GroupNode):
    def parse_element(self):
        self.type = "figure_group"

    def get_caption_node(self):
        for child in self.children:
            if child.class_str == "caption":
                return child


class TableGroupNode(GroupNode):
    def parse_element(self):
        self.type = "table_group"

    def get_caption_node(self):
        for child in self.children:
            if child.class_str == "table_caption":
                return child


class ListGroupNode(GroupNode):
    def parse_element(self):
        self.type = "list_group"


class ElementNodelizer:
    def __init__(self, element):
        if isinstance(element, bs4.element.NavigableString):
            node = StringNode(element)
        else:
            node = None
            tag = element.name
            class_str = " ".join(element.get("class", []))

            if class_str and class_str.startswith("section"):
                node = SectionGroupNode(element)
            if class_str == "figure":
                node = FigureGroupNode(element)
            if class_str == "table":
                node = TableGroupNode(element)
            if tag in ["ul", "ol", "li"]:
                node = ListGroupNode(element)

            if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                node = HeaderNode(element)
            if tag in ["img"]:
                node = ImageNode(element)
            if tag in ["table"]:
                node = TableNode(element)
            if tag in ["a"]:
                node = HyperlinkNode(element)
            if class_str == "sourceCode" or tag == "pre":
                node = CodeNode(element)
            if tag in ["script"]:
                node = JavascriptNode(element)
            if tag in ["p", "em", "strong", "sub", "sup", "mark"]:
                node = TextNode(element)
            if tag in ["hr", "br"]:
                node = SeparatorNode(element)

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
        for child in element.children:
            node = ElementNodelizer(child).node

            if node:
                self.nodes.append(node)
                if parent_node:
                    node.parent = parent_node
                    parent_node.children.append(node)
                if node.type.endswith("group"):
                    self.traverse_element(child, parent_node=node)
            else:
                if child.name in ["div", "blockquote"]:
                    self.traverse_element(child)
                else:
                    print(child.name, child.id)
                    print(child)
                    raise NotImplementedError

    def extract_styles(self):
        # <head> stores styles, which are useful for better rendering
        style_str = ""
        head_element = self.soup.find("head")
        for child in head_element.children:
            if child.name in ["style", "script"]:
                style_str += str(child)
        return style_str

    def parse_html_to_nodes(self):
        self.main_element = self.soup.find(id="MAIN")
        self.main_node = SectionGroupNode(self.main_element)
        self.traverse_element(element=self.main_element, parent_node=self.main_node)
        print(f"{len(self.nodes)} nodes parsed.")
        for idx, node in enumerate(self.nodes):
            node.idx = idx
            if idx > 0:
                self.prev = self.nodes[idx - 1]
            if idx < len(self.nodes) - 1:
                self.next = self.nodes[idx + 1]

    def remove_duplated_nodes(self, nodes):
        return sorted(
            list({node.idx: node for node in nodes}.values()), key=lambda x: x.idx
        )

    def search_by_keyword(self, keyword):
        searched_nodes = []
        for node in self.nodes:
            if not node.type.endswith("group"):
                # if node.get_text() is None:
                #     print(node.element)
                if keyword.strip().lower() in node.get_text().lower():
                    # print(node.type)
                    # print(node.get_parent().type)
                    # parent_node = node.get_parent()
                    # searched_nodes.append(parent_node)
                    searched_nodes.append(node)

        searched_nodes = self.remove_duplated_nodes(searched_nodes)

        for idx, node in enumerate(searched_nodes):
            print(f"{idx}: {node.type}\n{node.get_full_text()}")
        return searched_nodes

    def run(self):
        self.parse_html_to_nodes()
        self.extract_styles()
        # self.search_by_text("Traffic Generator Training Use Cases")
        # self.search_by_text("Training Step Order")
        # self.search_by_text("EnableDqDqsTrainEn")
        # self.search_by_keyword("Results Aggregation Feature")
        # self.search_by_keyword("Ddrio Feature")


if __name__ == "__main__":
    html_name = "Server DDR5 DMR MRC Training"
    html_path = (
        Path(__file__).parents[1] / "files" / "htmls" / "mrc" / f"{html_name}.html"
    )
    spec_html_nodelizer = SpecHTMLNodelizer(html_path)
    spec_html_nodelizer.run()
