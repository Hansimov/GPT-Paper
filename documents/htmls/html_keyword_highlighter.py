import re
from bs4 import BeautifulSoup
from documents.htmls.html_tag_masker import HTMLTagMasker


class HTMLKeywordHighlighter:
    def __init__(self, element, keyword):
        self.element = element
        self.keyword = keyword.strip()

        html_tag_mapper = HTMLTagMasker()
        hashed_element_str = html_tag_mapper.hash_tags(str(element))
        new_element_str = hashed_element_str

        for sub_keyword in keyword.split():
            new_element_str = re.sub(
                pattern=self.keyword_pattern_ignore_html_tags(sub_keyword),
                repl=self.highlight_keyword,
                string=new_element_str,
                flags=re.IGNORECASE,
            )
        # new_element_str = re.sub("(</searched>)(\s*?)(<searched>)", "", new_element_str)
        new_element_str = re.sub(
            pattern=r"(</searched>)([\s\n]*?)(<searched>)",
            repl=r"\2",
            string=new_element_str,
            flags=re.IGNORECASE,
        )

        new_element_str = html_tag_mapper.restore_tags(new_element_str)
        self.marked_element = BeautifulSoup(new_element_str, "lxml")

    def highlight_keyword(self, match):
        matched_text = match.group()
        if self.element.name in ["img"]:
            highlighted_text = matched_text
        else:
            highlighted_text = f"<searched>{matched_text}</searched>"
        return highlighted_text

    def keyword_pattern_ignore_html_tags(self, keyword):
        return "".join(f"{char}(<.+>)*" for char in keyword)
