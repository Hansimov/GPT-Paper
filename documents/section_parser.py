import json
import re
import operator
import pprint
from pathlib import Path


def calc_level_depth(level, level_0_depth=0):
    level = re.sub(r"\.$", "", level)
    level_depth = len(level.split("."))
    if str(level) == "0":
        level_depth = level_0_depth
    return level_depth


class SectionsJsonParser:
    pdf_root = Path(__file__).parents[1] / "pdfs"

    def __init__(self, project_dir):
        self.project_path = self.pdf_root / project_dir
        self.result_root = self.project_path / "_results"
        self.review_outline_json_path = self.result_root / "review_outline.json"
        self.review_sections_json_path = self.result_root / "review_sections.json"
        self.review_sections_hierarchical_json_path = (
            self.result_root / "review_sections_hierarchical.json"
        )
        self.outline = []
        self.sections = []

    def load_outline(self):
        with open(self.review_outline_json_path, "r", encoding="utf-8") as rf:
            self.outline = json.load(rf)
        print(self.outline)
        return self.outline

    def dump_outline(self):
        with open(self.review_outline_json_path, "w", encoding="utf-8") as wf:
            json.dump(self.outline, wf, indent=2, ensure_ascii=False)
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
            { "idx": 3, "level": "1.1.1", "title": "...", "intro": "..." },
            { "idx": 4, "level": "1.1.2", "title": "...", "intro": "..." },
            { "idx": 5, "level": "1.2", "title": "...", "intro": "..." },
            ...
        ]
        ```
        """
        with open(self.review_sections_json_path, "r", encoding="utf-8") as rf:
            self.sections = json.load(rf)
        return self.sections

    def dump_sections(self):
        with open(self.review_sections_json_path, "w", encoding="utf-8") as wf:
            json.dump(self.sections, wf, indent=2, ensure_ascii=False)
        return self.review_sections_json_path

    def calc_section_level_depth(self, section, level_0_depth=0):
        return calc_level_depth(section["level"], level_0_depth=level_0_depth)

    def get_sections_at_depth(self, depth=1, op=operator.eq, contain_main_title=False):
        sections_at_depth = []
        for section in self.sections:
            section_level_depth = self.calc_section_level_depth(section)
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

    def reorder_sections_idxs(self):
        self.sections.sort(key=lambda x: x["idx"])
        section_idx = self.sections[0]["idx"]
        for section in self.sections:
            section["idx"] = section_idx
            section_idx += 1


class SectionNode:
    def __init__(self, section=None, parent=None):
        self.section = section
        self.parent = parent
        self.children = []

        self.idx = section["idx"]
        self.level = section["level"]
        self.title = section["title"]
        self.intro = section["intro"]

        self.depth = calc_level_depth(section["level"])

    def get_latest_node_with_depth(self, depth):
        latest_node = self
        while latest_node.depth > depth:
            latest_node = latest_node.parent
        return latest_node

    def get_common_parent(self, another_node):
        max_depth = max(self.depth, another_node.depth)
        common_parent = self.get_latest_node_with_depth(max_depth).parent
        return common_parent

    def dump_to_hierarchical_sections_dict(self):
        hierarchical_sections = {
            "idx": self.idx,
            "level": self.level,
            "depth": self.depth,
            "title": self.title,
            "intro": self.intro,
            "children": [],
        }
        if self.children == []:
            return hierarchical_sections
        else:
            hierarchical_sections["children"] = [
                child.dump_to_hierarchical_sections_dict() for child in self.children
            ]
            return hierarchical_sections


class SectionTree:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.sections_json_parser = SectionsJsonParser(project_dir)
        self.construct_section_tree()

    def construct_section_tree(self):
        """
        Return:
        ```json
        [
            {
                "idx": 0, "level": "0", "title": "...", "intro": "...", "children": []
            },
            {
                "idx": 1, "level": "1",   "title": "...", "intro": "...",
                "children": [
                    { "idx": 2, "level": "1.1", "title": "...", "intro": "..."
                        "children": [
                            {"idx": 3, "level": "1.1.1", "title": "...", "intro": "...",
                                "children": [],
                            },
                            {"idx": 4, "level": "1.1.2", "title": "...", "intro": "...",
                                "children": [],
                            },
                        ],
                    },
                    { "idx": 5, "level": "1.2", "title": "...", "intro": "...",
                        "children": [...],
                    },
                    ...
                ]
            },
            {
                "idx": 6, "level": "2",   "title": "...", "intro": "...",
                "children": [...]
            },
            ...
        ]
        ```
        """
        self.sections = self.sections_json_parser.load_sections()
        hierarchical_sections = []

        for section in self.sections:
            section["children"] = []

        section_root = SectionNode(section=self.sections[0])
        prev_section_node = section_root
        for section in self.sections[1:]:
            section_node = SectionNode(section=section)
            if section_node.depth == prev_section_node.depth:
                parent = prev_section_node.parent
            elif section_node.depth > prev_section_node.depth:
                parent = prev_section_node
            else:  # section_node.depth < prev_section_node.depth
                parent = prev_section_node.get_latest_node_with_depth(
                    section_node.depth - 1
                )
            section_node.parent = parent
            parent.children.append(section_node)
            prev_section_node = section_node
        hierarchical_sections = section_root.dump_to_hierarchical_sections_dict()

        with open(
            self.sections_json_parser.review_sections_hierarchical_json_path,
            "w",
            encoding="utf-8",
        ) as wf:
            json.dump(hierarchical_sections, wf, indent=4, ensure_ascii=False)

        self.hierarchical_sections = hierarchical_sections
        self.section_root = section_root
        self.section_tree = section_root


if __name__ == "__main__":
    section_tree = SectionTree("cancer_review")
    pprint.pprint(section_tree.hierarchical_sections)
