import re
import itertools
import hashlib
from bs4 import BeautifulSoup
from pathlib import Path

from bs4 import BeautifulSoup


class Node:
    def __init__(self, element):
        self.element = element
        self.id = element.get("id", None)
        self.prev = None
        self.next = None
        self.parent = None
        self.children = []


class TextNode(Node):
    def parse_element(self):
        self.type = "text"
        self.text = self.element.text.strip()


class HeaderNode(Node):
    def parse_element(self):
        self.type = "header"
        span_element = self.element.find("span")
        if span_element:
            self.header_number = span_element.text.strip()
            span_element.extract()
        else:
            self.header_number = ""
        self.tag_name = self.element.name
        self.header_text = self.element.text.strip()
        self.header_level = int(self.tag_name[-1])


class TableNode(Node):
    def parse_element(self):
        self.type = "table"
        caption_tag = self.element.find("p", class_="table_caption")
        if caption_tag:
            self.caption = caption_tag.text.strip()
            caption_tag.extract()
        else:
            self.caption = ""


class FigureNode(Node):
    def parse_element(self):
        self.type = "figure"
        img_tag = self.element.find("img")
        if img_tag:
            self.image_source = img_tag["src"]
            img_tag.extract()
        else:
            self.image_source = ""


class ListNode(Node):
    def parse_element(self):
        self.type = "list"


class CodeNode(Node):
    def parse_element(self):
        self.type = "code"


class SepNode(Node):
    def parse_element(self):
        self.type = "sep"


class SpecHTMLNodelizer:
    def __init__(self, html_path):
        self.html_path = html_path
        with open(self.html_path, "r") as rf:
            html_string = rf.read()
        self.soup = BeautifulSoup(html_string, "html.parser")
        self.nodes = []

    def traverse_element(self, element):
        children_l1 = element.find_all(recursive=False)
        for child in children_l1:
            tag = child.name
            class_str = " ".join(child.get("class", []))
            element_id = child.get("id", None)
            print(f"{tag}, class={class_str}, id={element_id}")

            node = None
            if tag == "script":
                continue
            if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                node = HeaderNode(child)
            if class_str == "table" or tag == "table":
                node = TableNode(child)
            if class_str == "figure":
                node = FigureNode(child)
            if class_str == "sourceCode" or tag == "pre":
                node = CodeNode(child)
            if tag in ["p"]:
                node = TextNode(child)
            if tag in ["ul", "ol"]:
                node = ListNode(child)
            if tag in ["hr"]:
                node = SepNode(child)

            if node:
                self.nodes.append(node)
            else:
                if tag in ["div", "blockquote"]:
                    self.traverse_element(child)
                elif class_str and class_str.startswith("section"):
                    self.traverse_element(child)
                else:
                    raise NotImplementedError

    def parse_html_to_nodes(self):
        root_element = self.soup.find(id="MAIN")
        self.traverse_element(root_element)

    def run(self):
        self.parse_html_to_nodes()


if __name__ == "__main__":
    html_name = "Server DDR5 DMR MRC Training"
    html_path = (
        Path(__file__).parents[1] / "files" / "htmls" / "mrc" / f"{html_name}.html"
    )
    spec_html_nodelizer = SpecHTMLNodelizer(html_path)
    spec_html_nodelizer.run()
