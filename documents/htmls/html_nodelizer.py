import bs4
import hashlib
import itertools
import pandas as pd
import re

from abc import abstractmethod
from bs4 import BeautifulSoup
from pathlib import Path
from thefuzz import fuzz

from documents.keyword_searcher import KeywordSearcher
from documents.htmls.html_keyword_highlighter import HTMLKeywordHighlighter
from networks.html_fetcher import HTMLFetcher

"""
The key problem of structurazing HTML is not only how to represent the tree,
but also how to make it human-readable and understandable.

The idea in this script is to use Node and GroupNode,
which are organized in two data structures:
1. Tree: Represents the hierarchical structure, useful to get relationships among nodes.
2. List: Stores the sequential info, suitable for human reading and understanding,
    also more convinient to loop and process.

"""


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

    @abstractmethod
    def parse_element(self):
        self.type = "node"

    def get_parent_element(self):
        return self.element.parent

    def get_parent(self):
        return self.parent

    def get_parents(self, depth=0):
        parent = self.get_parent()
        for i in range(depth):
            parent = parent.get_parent()
        return parent

    def get_full_text(self):
        if self.get_description():
            self.full_text = f"{self.get_description()}: {self.get_text()}"
        else:
            self.full_text = self.get_text()
        return self.full_text

    def get_description(self):
        self.description = self.type
        return self.description()

    def get_section_group_node(self):
        node = self
        while node and node.type != "section_group":
            node = node.parent

        if node is None:
            print(self.element)
            raise NotImplementedError("get_section_group_node(): None!")
        elif node.type != "section_group":
            print(node.element)
            print(self.element)
            raise NotImplementedError("get_section_group_node(): No section group!")
        else:
            return node

    def get_most_recent_group_node(self):
        node = self
        while node and not node.type.endswith("group"):
            node = node.parent

        if node is None:
            print(self.element)
            raise NotImplementedError("get_most_recent_group_node(): None!")
        elif not node.type.endswith("group"):
            print(node.element)
            print(self.element)
            raise NotImplementedError(
                "get_most_recent_group_node(): No most recent group!"
            )
        else:
            return node

    def get_full_node(self, keyword=""):
        most_recent_group_node = self.get_most_recent_group_node()
        if (
            hasattr(self, "class_str")
            and self.class_str.endswith("caption")
            and self.parent.type.endswith("group")
        ):
            self.full_node = self.parent
        elif most_recent_group_node.type == "list_group":
            self.full_node = most_recent_group_node
        # elif most_recent_group_node.type == "figure_group":
        #     self.full_node = [
        #         node
        #         for node in [
        #             most_recent_group_node.prev,
        #             most_recent_group_node,
        #             most_recent_group_node.next,
        #         ]
        #         if node is not None
        #     ]
        # elif self.type == "image":
        #     self.full_node = [
        #         node
        #         for node in [
        #             self.prev,
        #             self,
        #             self.next,
        #         ]
        #         if node is not None
        #     ]
        else:
            self.full_node = self

        return self.full_node


class JavascriptNode(Node):
    def parse_element(self):
        self.type = "javascript"


class TableNode(Node):
    def parse_element(self):
        self.type = "table"

    def get_df(self):
        self.df = pd.read_html(str(self.element))[0]
        return self.df

    def get_markdown(self):
        self.markdown = self.get_df().to_markdown(index=False)
        return self.markdown

    def get_text(self):
        self.text = str(self.get_markdown())
        return self.text

    def get_columns(self):
        self.columns = self.get_df().columns.tolist()
        return self.columns

    def get_full_node(self, keyword=""):
        if self.parent.type == "table_group":
            self.full_node = self.parent
        else:
            self.full_node = self
        return self.full_node


class TextNode(Node):
    def parse_element(self):
        self.type = "text"

    def get_full_text(self):
        if self.tag not in ["p", "span"]:
            self.tagged_text = f"<{self.tag}>{self.get_text()}</{self.tag}>"
        else:
            self.tagged_text = self.get_text()

        if self.class_str:
            self.full_text = f"{self.get_description()}: {self.tagged_text}"
        else:
            self.full_text = self.tagged_text
        return self.full_text


class StringNode(Node):
    def parse_element(self):
        self.type = "string"

    def get_text(self):
        self.text = str(self.element)
        return self.text


class HyperlinkNode(Node):
    def parse_element(self):
        self.type = "hyperlink"

    def get_text(self):
        self.text = self.element.text.strip()
        return self.text

    def get_href(self):
        self.href = self.element.get("href", None)
        return self.href


class HeaderNode(Node):
    def parse_element(self):
        self.type = "header"

    def get_level(self):
        self.level = int(self.tag[-1])
        return self.level

    def get_text(self):
        for child in self.element.children:
            if isinstance(child, bs4.element.NavigableString):
                self.text = child.strip()
                break
        return self.text

    @abstractmethod
    def get_number(self):
        pass

    def get_full_text(self):
        self.full_text = (
            f"{self.get_description()}: {self.get_number()} {self.get_text()}"
        )
        return self.full_text

    def get_indented_full_text(self, indent=2, indent_char=" ", begin_char="-"):
        indent_str = indent_char * indent * (self.level - 1)
        self.indented_full_text = (
            f"{indent_str}{begin_char} {self.get_number()} {self.get_text()}"
        )
        return self.indented_full_text

    def get_full_node(self, keyword=""):
        if self.parent.type == "section_group" and (
            keyword == "" or self.get_text().lower() == keyword.lower()
        ):
            self.full_node = self.parent
        else:
            self.full_node = self
        return self.full_node


class CodeNode(Node):
    def parse_element(self):
        self.type = "code"


class SeparatorNode(Node):
    def parse_element(self):
        self.type = "sep"


class ImageNodeSourceReplacer:
    def __init__(self, html_url=""):
        self.html_url = html_url
        self.src_prefix = html_url[: html_url.rfind("/") + 1]

    def replace(self, node):
        node.src = node.element.get("src", "")
        if node.src and not node.src.startswith(("http", "https", "data", "file")):
            node.src = self.src_prefix + node.src
            node.element["src"] = node.src
            node.element["title"] = node.src
        return node


class ImageNode(Node):
    def parse_element(self):
        self.type = "image"

    def get_text(self):
        self.text = self.element.get("alt", "")
        if not self.text:
            self.text = self.element.get("src", "")
        return self.text

    def get_src(self):
        self.src = self.element.get("src", "")
        return self.src

    def get_full_text(self):
        self.full_text = f"{self.type}: ![{self.get_text()}]({self.get_src()})"
        return self.full_text


class StyleNode(Node):
    def parse_element(self):
        self.type = "style"


class IgnorableNode(Node):
    def parse_element(self):
        self.type = "ignorable"


class SVGNode(Node):
    def parse_element(self):
        self.type = "svg"


class CaptionNode(Node):
    def parse_element(self):
        self.type = "caption"


class GroupNode(Node):
    def parse_element(self):
        self.type = "group"

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
        self.header_node = None
        for child in self.children:
            if child.type == "header":
                self.header_node = child

        if self.header_node is None:
            # print(self.element)
            print("get_header_node(): No header node for SectionGroupNode")
            # raise NotImplementedError
            self.header_node = self.children[0]

        return self.header_node

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

    @abstractmethod
    def get_caption_node(self):
        pass


class ListGroupNode(GroupNode):
    def parse_element(self):
        self.type = "list_group"


class BlockquoteGroupNode(GroupNode):
    def parse_element(self):
        self.type = "blockquote_group"


class DivGroupNode(GroupNode):
    def parse_element(self):
        self.type = "div_group"


class DetailsGroupNode(GroupNode):
    def parse_element(self):
        self.type = "details_group"


class SpanGroupNode(GroupNode):
    def parse_element(self):
        self.type = "span_group"


class SpecElementNodelizer:
    def __init__(self, element):
        node = None
        if isinstance(element, bs4.element.NavigableString):
            node = StringNode(element)
        else:
            tag = element.name
            class_str = " ".join(element.get("class", []))
            children_cnt = len(list(element.children))

            if children_cnt == 1 and isinstance(
                list(element.children)[0], bs4.element.NavigableString
            ):
                node = TextNode(element)
            elif class_str and class_str.startswith("section"):
                node = SectionGroupNode(element)
            elif class_str == "figure":
                node = FigureGroupNode(element)
            elif class_str == "table":
                node = TableGroupNode(element)
            elif tag in ["ul", "ol", "li"]:
                node = ListGroupNode(element)
            elif tag in ["blockquote"]:
                node = BlockquoteGroupNode(element)
            elif tag in ["details"]:
                node = DetailsGroupNode(element)
            elif tag in ["style"]:
                node = StyleNode(element)
            elif tag in ["noscript"]:
                node = IgnorableNode(element)
            elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                node = HeaderNode(element)
            elif tag in ["img"]:
                node = ImageNode(element)
            elif tag in ["table"]:
                node = TableNode(element)
            elif tag in ["a"]:
                node = HyperlinkNode(element)
            elif class_str == "sourceCode" or tag == "pre":
                node = CodeNode(element)
            elif tag in ["script"]:
                node = JavascriptNode(element)
            elif tag in [
                "del",
                "em",
                "i",
                "mark",
                "p",
                "span",
                "strong",
                "sub",
                "sup",
                "strike",
                "summary",
                "u",
            ]:
                node = TextNode(element)
            elif tag in ["hr", "br"]:
                node = SeparatorNode(element)
            else:
                if node is None:
                    if tag in ["div"]:
                        node = DivGroupNode(element)
                    else:
                        print(element)
                        node = TextNode(element)
                        # raise NotImplementedError

        self.node = node


class Ar5ivElementNodelizer:
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
            if tag in ["blockquote"]:
                node = BlockquoteGroupNode(element)
            if tag in ["details"]:
                node = DetailsGroupNode(element)

            if tag in ["style"]:
                node = StyleNode(element)
            if tag in ["noscript"]:
                node = IgnorableNode(element)

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
            if tag in [
                "del",
                "em",
                "i",
                "mark",
                "p",
                "span",
                "strong",
                "sub",
                "sup",
                "strike",
                "summary",
                "u",
            ]:
                node = TextNode(element)
            if tag in ["hr", "br"]:
                node = SeparatorNode(element)

        if node is None:
            if tag in ["div"]:
                node = DivGroupNode(element)
            else:
                print(element)
                node = TextNode(element)
                # raise NotImplementedError

        self.node = node


class HTMLNodelizer:
    def __init__(self, html_path=None, url=None, domain=None):
        self.html_path = html_path
        self.url = url
        with open(self.html_path, "r", encoding="utf-8") as rf:
            html_string = rf.read()
        self.soup = BeautifulSoup(html_string, "lxml")
        self.nodes = []
        self.style_nodes = []
        self.section_node = None
        self.domain = domain

    def get_element_nodelizer_class(self):
        domain_nodelizers = {
            "ar5iv": Ar5ivElementNodelizer,
            "docs.com": SpecElementNodelizer,
        }
        if self.domain in domain_nodelizers.keys():
            element_nodelizer_class = domain_nodelizers[self.domain]
        else:
            raise NotImplementedError(f"Not supported domain: {self.domain}")
        return element_nodelizer_class

    def get_main_element(self):
        domain_main_element_patterns = {
            "ar5iv": {"name": "article"},
            "docs.com": {"id": "MAIN"},
        }
        if self.domain in domain_main_element_patterns.keys():
            self.main_element = self.soup.find(
                **domain_main_element_patterns[self.domain]
            )
        else:
            raise NotImplementedError(f"Not supported domain: {self.domain}")
        return self.main_element

    def extract_styles(self):
        # <head> stores <styles> and <script>, which are useful for rendering HTML as it is
        style_str = ""
        head_element = self.soup.find("head")
        for child in head_element.children:
            if child.name in ["style", "script"]:
                style_str += str(child)
        for style_node in self.style_nodes:
            style_str += str(style_node.element)
        return style_str

    def traverse_element(self, element, parent_node):
        for child in element.children:
            node = self.get_element_nodelizer_class()(child).node

            if node:
                if node.type in ["style", "script"]:
                    self.style_nodes.append(node)
                elif node.type in ["ignorable"]:
                    continue
                else:
                    if node.type in ["image"]:
                        node = ImageNodeSourceReplacer(self.url).replace(node)
                    self.nodes.append(node)

                if parent_node:
                    node.parent = parent_node
                    parent_node.children.append(node)

                if node.type.endswith("group"):
                    self.traverse_element(child, parent_node=node)

            else:
                print(child.name, child.id)
                print(child)
                raise NotImplementedError

    def parse_html_to_nodes(self):
        self.main_element = self.get_main_element()
        self.main_node = SectionGroupNode(self.main_element)
        self.traverse_element(element=self.main_element, parent_node=self.main_node)
        print(f"{len(self.nodes)} nodes parsed.")
        for idx, node in enumerate(self.nodes):
            node.idx = idx
            if idx > 0:
                self.prev = self.nodes[idx - 1]
            if idx < len(self.nodes) - 1:
                self.next = self.nodes[idx + 1]

    def run(self):
        self.parse_html_to_nodes()


if __name__ == "__main__":
    url = "https://ar5iv.labs.arxiv.org/html/1810.04805"
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
    html_nodelizer = HTMLNodelizer(
        html_path=html_fetcher.output_path,
        url=html_fetcher.url,
        domain=html_fetcher.domain,
    )
    html_nodelizer.run()
