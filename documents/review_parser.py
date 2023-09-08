import json
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
        print(self.sections)
        return self.sections


if __name__ == "__main__":
    parser = ReviewParser("cancer_review")
    parser.load_sections()
