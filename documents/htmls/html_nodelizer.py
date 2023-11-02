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
The key problem of structuring HTML is not only how to represent the tree,
but also how to make it human-readable and understandable.

The idea in this script is to use Node and GroupNode,
which are organized in two data structures:
1. Tree: Represents the hierarchical structure, useful to get relationships among nodes.
2. List: Stores the sequential info, suitable for human reading and understanding,
    also more convenient to loop and process.

    
Then another problem appears:
how to determine whether the element should be grouped,
or treated as a complete single node.

Of course we could use specific rules for each domain,
but a better idea is to categorize the elements into several main types.
Then which types could be treated as "main types"?

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

    def get_text(self):
        self.text = self.element.text.strip()
        return self.text

    def get_full_text(self, add_description=True):
        if add_description and self.get_description():
            self.full_text = f"{self.get_description()}: {self.get_text()}"
        else:
            self.full_text = self.get_text()
        return self.full_text

    def get_description(self):
        if hasattr(self, "description") and self.description:
            return self.description
        self.description = self.type
        return self.description

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


class ScriptNode(Node):
    def parse_element(self):
        self.type = "script"


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

    def get_full_text(self, add_description=True):
        if add_description:
            self.full_text = f"{self.get_description()}:\n{self.get_text()}"
        else:
            self.full_text = self.get_text()
        return self.full_text

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

    def get_full_text(self, add_description=True):
        if self.tag in ["p", "span"]:
            self.tagged_text = self.get_text()
        else:
            self.tagged_text = f"<{self.tag}>{self.get_text()}</{self.tag}>"

        if add_description and self.get_description() not in [
            "text",
            "paragraph",
            "string",
        ]:
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

    def get_full_text(self, add_description=True):
        self.full_text = self.get_text()
        return self.full_text


class HyperlinkNode(Node):
    def parse_element(self):
        self.type = "hyperlink"

    def get_text(self):
        self.text = self.get_href()
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

    def get_description(self):
        self.description = "section"
        return self.description

    def get_text(self):
        self.text = ""
        for child in self.element.children:
            if isinstance(child, bs4.element.NavigableString):
                self.text += child.strip()
        return self.text

    @abstractmethod
    def get_number(self):
        pass

    def get_full_text(self, add_description=True):
        if add_description:
            self.full_text = (
                f"{self.get_description()} {self.get_number()}: {self.get_text()}"
            )
        else:
            self.full_text = f"[{self.get_number()}] {self.get_text()}"
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


class ArxivHeaderNode(HeaderNode):
    def get_number(self):
        self.number = ""
        span_element = self.element.find("span")
        # <span class="ltx_tag ltx_tag_section">2 </span>
        # <span class="ltx_tag ltx_tag_subsection">2.1 </span>
        # <h1 class="ltx_title ltx_title_document">A Survey of Large Language Models</h1>
        if span_element is not None:
            span_element_class_str = " ".join(span_element.get("class", []))
            if re.search("ltx_tag_(sub)*section", span_element_class_str):
                self.number = span_element.text.strip()

        return self.number


class SpecHeaderNode(HeaderNode):
    def get_number(self):
        # <span class="header-section-number">1.1</span>
        span_element = self.element.find("span", class_="header-section-number")
        if span_element:
            self.header_number = span_element.text.strip()
        else:
            self.header_number = ""

        return self.header_number


class CodeNode(Node):
    def parse_element(self):
        self.type = "code"


class SeparatorNode(Node):
    def parse_element(self):
        self.type = "sep"


class LinkableNodeSourceReplacer:
    def __init__(self, html_url=""):
        self.html_url = html_url
        self.src_prefix = html_url[: html_url.rfind("/") + 1]

    def replace(self, node):
        node.src = node.element.get("src", "")
        node.href = node.element.get("href", "")

        if node.src:
            node.link = node.src
            node.link_attr = "src"
        elif node.href:
            node.link = node.href
            node.link_attr = "href"
        else:
            node.link = None

        if node.link and not node.link.startswith(("http", "https", "data", "file")):
            node.link = self.src_prefix + node.link
            node.element[node.link_attr] = node.link
            node.element["title"] = node.link
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

    def get_full_text(self, add_description=True):
        if add_description:
            self.full_text = (
                f"{self.get_description()}: ![{self.get_text()}]({self.get_src()})"
            )
        else:
            self.full_text = f"![{self.get_text()}]({self.get_src()})"
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


class ParagraphNode(Node):
    def parse_element(self):
        self.type = "paragraph"

    def get_full_text(self, add_description=True):
        self.full_text = self.get_text()
        return self.full_text


class AuthorNode(Node):
    def parse_element(self):
        self.type = "author"

    def get_person_name(self):
        self.person_name = self.element.find(
            "span", class_="ltx_person_name"
        ).text.strip()
        return self.person_name

    def get_author_notes(self):
        self.author_notes = self.element.find(
            "span", class_="ltx_author_notes"
        ).text.strip()
        return self.author_notes


class GroupNode(Node):
    def parse_element(self):
        self.type = "group"

    def get_text(self):
        texts = []
        for child in self.children:
            texts.append(child.get_text())
        self.text = "\n".join(texts)
        return self.text

    def get_full_text(self, add_description=True):
        full_texts = []
        for child in self.children:
            full_texts.append(child.get_full_text(add_description=add_description))
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


class HyperlinkGroupNode(GroupNode):
    def parse_element(self):
        self.type = "hyperlink_group"


class SingleTextNodeChecker:
    def __init__(self, element):
        self.element = element

    def check(self):
        element_children = list(self.element.children)
        if len(element_children) == 1 and isinstance(
            element_children[0], bs4.element.NavigableString
        ):
            return True
        else:
            return False


class SpecElementNodelizer:
    def __init__(self, element):
        node = None
        if isinstance(element, bs4.element.NavigableString):
            node = StringNode(element)
            node_text = node.get_text().strip()
            if not node_text:
                node = IgnorableNode(element)
        else:
            tag = element.name
            class_str = " ".join(element.get("class", []))

            if tag in ["style"]:
                node = StyleNode(element)
            elif tag in ["script"]:
                node = ScriptNode(element)
            elif tag in ["noscript"]:
                node = IgnorableNode(element)
            elif tag in ["div"]:
                if re.search("^section", class_str):
                    node = SectionGroupNode(element)
                elif class_str == "figure":
                    node = FigureGroupNode(element)
                elif class_str == "table":
                    node = TableGroupNode(element)
                elif re.search("sourceCode", class_str):
                    node = CodeNode(element)
                else:
                    node = DivGroupNode(element)
            elif tag in ["ul", "ol", "li"]:
                if SingleTextNodeChecker(element).check():
                    node = TextNode(element)
                else:
                    node = ListGroupNode(element)
            elif tag in ["blockquote", "details"]:
                node = GroupNode(element)
                node.type = f"{tag}_group"
            elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                node = SpecHeaderNode(element)
            elif tag in ["img"]:
                node = ImageNode(element)
            elif tag in ["table"]:
                node = TableNode(element)
            elif tag in ["a"]:
                if SingleTextNodeChecker(element).check():
                    node = HyperlinkNode(element)
                else:
                    node = HyperlinkGroupNode(element)
            elif tag in ["pre", "code"]:
                node = CodeNode(element)
            elif tag in ["p"]:
                if re.search("caption", class_str):
                    node = CaptionNode(element)
                elif class_str in ["title", "author", "date"]:
                    node = TextNode(element)
                    node.type = class_str
                else:
                    node = ParagraphNode(element)
            elif tag in [
                "b",
                "del",
                "em",
                "i",
                "mark",
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
                pass

        if node is None:
            print(element)
            raise NotImplementedError("Can not categorize element!")

        self.node = node


class ArxivElementNodelizer:
    def __init__(self, element):
        node = None
        if isinstance(element, bs4.element.NavigableString):
            node = StringNode(element)
            if not node.get_text().strip():
                node = IgnorableNode(element)
        else:
            tag = element.name
            class_str = " ".join(element.get("class", []))

            if tag in ["section"]:
                node = SectionGroupNode(element)
            elif tag in ["figure"]:
                if re.search("ltx_table", class_str):
                    node = TableGroupNode(element)
                elif re.search("ltx_figure", class_str):
                    node = FigureGroupNode(element)
                else:
                    pass
            elif tag in ["ul", "ol", "li"]:
                if re.search("ltx_bibitem", class_str):
                    node = TextNode(element)
                    node.description = "bib_item"
                else:
                    node = ListGroupNode(element)
            elif tag in ["style"]:
                node = StyleNode(element)
            elif tag in ["script"]:
                node = ScriptNode(element)
            elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                node = ArxivHeaderNode(element)
            elif tag in ["img"]:
                node = ImageNode(element)
            elif tag in ["svg"]:
                node = SVGNode(element)
            elif tag in ["table"]:
                node = TableNode(element)
            elif tag in ["figcaption"]:
                node = CaptionNode(element)
            elif tag in ["div", "p", "span"]:
                if re.search("ltx_p(ara)?", class_str):
                    node = ParagraphNode(element)
                elif re.search("ltx_authors", class_str):
                    node = AuthorNode(element)
                elif re.search("ltx_abstract", class_str):
                    node = SectionGroupNode(element)
                    node.description = "abstract"
                elif re.search("ltx_keywords", class_str):
                    node = SectionGroupNode(element)
                    node.description = "keywords"
                elif re.search("ltx_role_footnotetext", class_str):
                    node = TextNode(element)
                elif re.search("ltx_(tag_bibitem|bibblock)", class_str):
                    node = TextNode(element)
                elif re.search("ltx_transformed_(outer|inner)", class_str):
                    node = SectionGroupNode(element)
                elif re.search("ltx_ERROR", class_str):
                    node = IgnorableNode(element)
                else:
                    pass
            else:
                pass

        if node is None:
            print(element)
            raise NotImplementedError("Can not categorize element!")

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
            "arxiv": ArxivElementNodelizer,
            "docs.com": SpecElementNodelizer,
        }
        if self.domain in domain_nodelizers.keys():
            self.element_nodelizer_class = domain_nodelizers[self.domain]
        else:
            raise NotImplementedError(f"Not supported domain: {self.domain}")
        return self.element_nodelizer_class

    def get_main_element(self):
        domain_main_element_patterns = {
            "arxiv": {"name": "article"},
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
                    if node.type in ["image", "hyperlink"]:
                        node = LinkableNodeSourceReplacer(self.url).replace(node)
                    self.nodes.append(node)

                if parent_node:
                    node.parent = parent_node
                    parent_node.children.append(node)

                if node.type.endswith("group"):
                    self.traverse_element(child, parent_node=node)
            else:
                print(child)
                raise NotImplementedError("Node is None!")

    def parse_html_to_nodes(self):
        self.main_element = self.get_main_element()
        self.main_node = SectionGroupNode(self.main_element)
        self.traverse_element(element=self.main_element, parent_node=self.main_node)

        for idx, node in enumerate(self.nodes):
            # print(f"{idx+1}: {node.type}")
            node.idx = idx
            if idx > 0:
                self.prev = self.nodes[idx - 1]
            if idx < len(self.nodes) - 1:
                self.next = self.nodes[idx + 1]
        self.groups = [node for node in self.nodes if node.type.endswith("group")]
        print(
            f"=== {len(self.groups)} groups, {len(self.nodes)-len(self.groups)} nodes. ==="
        )

        for idx, node in enumerate(self.nodes):
            if node.type.endswith("group"):
                print(f"[{node.type}]")
            elif node.type in ["table"]:
                print(node.type)
            else:
                print(node.get_full_text())

        print(
            f"=== {len(self.groups)} groups, {len(self.nodes)-len(self.groups)} nodes. ==="
        )

    def run(self):
        self.parse_html_to_nodes()


if __name__ == "__main__":
    # url = "https://ar5iv.labs.arxiv.org/html/1810.04805"
    # url = "https://arxiv.org/abs/1810.04805"
    url = "https://arxiv.org/abs/2303.08774"
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
    html_nodelizer = HTMLNodelizer(
        html_path=html_fetcher.output_path,
        url=html_fetcher.html_url,
        domain=html_fetcher.domain,
    )
    html_nodelizer.run()
