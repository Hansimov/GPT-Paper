import re
from pathlib import Path
import itertools


class MarkdownParser:
    def __init__(self, markdown_path):
        self.markdown_path = markdown_path
        self.headers = []

    def calc_header_level(self, header_text, mark="#"):
        return len(list(itertools.takewhile(lambda x: x == mark, header_text)))

    def structurize(self):
        with open(markdown_path, "r", encoding="utf-8") as rf:
            markdown_text = rf.read()
        for line in markdown_text.split("\n"):
            text = line.strip()
            header = re.sub(r"^#+", "", text)
            if text.startswith("#"):
                level = self.calc_header_level(text)
                self.headers.append(
                    {
                        "level": level,
                        "text": text,
                        "header": header,
                    }
                )
                # print(text)
                # print(level, header)

    def run(self):
        self.structurize()


if __name__ == "__main__":
    pdf_name = "2308.08155 - AutoGen - Enabling Next-Gen LLM Applications via Multi-Agent Conversation"
    markdown_path = (
        Path(__file__).parents[1] / "pdfs" / "llm_agents" / pdf_name / f"{pdf_name}.mmd"
    )
    markdown_parser = MarkdownParser(markdown_path)
    markdown_parser.run()
