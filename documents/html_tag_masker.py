import hashlib
import re


class HTMLTagMasker:
    def __init__(self):
        self.tag_dict = {}
        self.hashed_html_string = ""
        self.restored_html_string = ""

    def hash_tags(self, html_string):
        # `/?`: Match closed tag starting with `/`, like `</div>`
        # `[^>]*`: Match any character except `>`, like `<p class='abc'>` or `<br/>`
        pattern = re.compile(r"<(/?\w+[^>]*?)>")

        def replacer(match):
            tag = match.group(1)
            hashed_tag = hashlib.md5(tag.encode("utf-8")).hexdigest()
            self.tag_dict[hashed_tag] = tag
            return "<" + hashed_tag + ">"

        self.hashed_html_string = pattern.sub(replacer, html_string)
        return self.hashed_html_string

    def restore_tags(self, html_str=""):
        pattern = re.compile(r"<([0-9a-f]{32})>")

        def replacer(match):
            hashed_tag = match.group(1)
            original_tag = self.tag_dict[hashed_tag]
            return "<" + original_tag + ">"

        if not html_str:
            html_str = self.hashed_html_string
        self.restored_html_string = pattern.sub(replacer, html_str)

        return self.restored_html_string
