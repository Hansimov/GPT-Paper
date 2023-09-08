import json
import re
import operator
import pprint
from pathlib import Path


class ReviewParser:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self, project_dir):
        self.project_path = self.pdf_root / project_dir
        self.result_root = self.project_path / "_results"
        self.review_outline_json_path = self.result_root / "review_outline.json"
        self.review_sections_json_path = self.result_root / "review_sections.json"
        self.outline = []
        self.sections = []

    def load_outline(self):
        with open(self.review_outline_json_path, "r", encoding="utf-8") as rf:
            self.outline = json.load(rf)
        print(self.outline)
        return self.outline

    def dump_outline(self):
        with open(self.review_outline_json_path, "w", encoding="utf-8") as rf:
            json.dump(self.outline, rf, indent=2, ensure_ascii=False)
        return self.review_outline_json_path

    def load_sections(self):
        """
        * Required keys: `[idx, level, title, intro]`
        * Optional Keys: `[summary, statements, translation]`

        ```json
        [
            { "idx": 0, "level": "0",   "title": "...", "intro": "..." },
            { "idx": 1, "level": "1",   "title": "...", "intro": "..." },
            { "idx": 2, "level": "1.1", "title": "...", "intro": "..." },
            { "idx": 3, "level": "1.2", "title": "...", "intro": "..." },
        ]
        ```
        """
        with open(self.review_sections_json_path, "r", encoding="utf-8") as rf:
            self.sections = json.load(rf)
        return self.sections

    def dump_sections(self):
        with open(self.review_sections_json_path, "w", encoding="utf-8") as rf:
            json.dump(self.sections, rf, indent=2, ensure_ascii=False)
        return self.review_sections_json_path

    def calc_level_depth(self, level):
        level = re.sub(r"\.$", "", level)
        level_depth = len(level.split("."))
        if str(level) == "0":
            level_depth = 0
        return level_depth

    def get_sections_at_depth(self, depth=1, op=operator.eq, contain_main_title=False):
        sections_at_depth = []
        for section in self.sections:
            section_level_depth = self.calc_level_depth(section["level"])
            if section_level_depth == 0 and not contain_main_title:
                continue
            if op(section_level_depth, depth):
                sections_at_depth.append(section)
        return sections_at_depth

    def get_sections_above_depth(
        self, depth=1, contain_current_depth=True, contain_main_title=False
    ):
        if contain_current_depth:
            op = operator.le
        else:
            op = operator.lt
        sections_at_depth = self.get_sections_at_depth(
            depth=depth, op=op, contain_main_title=contain_main_title
        )
        pprint.pprint(sections_at_depth)

    def get_sections_below_depth(
        self, depth=1, contain_current_depth=True, contain_main_title=False
    ):
        if contain_current_depth:
            op = operator.ge
        else:
            op = operator.gt
        sections_at_depth = self.get_sections_at_depth(
            depth=depth, op=op, contain_main_title=contain_main_title
        )
        pprint.pprint(sections_at_depth)


if __name__ == "__main__":
    parser = ReviewParser("cancer_review")
    parser.load_sections()
    # parser.get_sections_at_depth(1)
    parser.get_sections_below_depth(3, contain_current_depth=False)
