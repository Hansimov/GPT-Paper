import re
from collections import Counter
from termcolor import colored
from utils.logger import logger
from utils.tokenizer import Tokenizer


def text_blocks_to_paragraphs(blocks):
    """
    Blocks:

    ```json
    [
        {
            "type": <int> (0),
            "number": <int>,
            "fontsize": <float>,
            "bbox": <tuple> (4 floats),
            "page": <int>,
            "text": <str> (multi-lines),
        }
    ]
    ```

    Paragraphs:

    ```json
    [
        {
            "fontsize": <float>,
            "block": [(<PAGE_NUM, BLOCK_NUM>), ...],
            "text": <str> (multi-lines),
        },
        ...
    ]
    ```
    """
    pass


def regroup_blocks(self):
    """
    1. Concatenate last block of page[i] and first block of page[i+1],
       if they are in the same paragraph.
    2. Split the concatenated block into multiple blocks,
       if there are different paragraphs.
    """


class TextBlock:
    def __init__(self, block):
        self.block = block
        self.lines = self.block["lines"]
        self.spans = [spans for line in self.lines for spans in line["spans"]]
        self.bbox = self.block["bbox"]

    def replace_chars(self):
        chars_map = {"\s*ﬁ\s*": "fi"}
        for k, v in chars_map.items():
            self.block_text = re.sub(k, v, self.block_text)

    def get_block_text(self):
        block_text = ""
        for line in self.lines:
            spans = line["spans"]
            line_text = ""
            for span in spans:
                span_text = span["text"]
                line_text += f"{span_text}"
            block_text += f"{line_text}\n"
        self.block_text = block_text
        self.replace_chars()
        return self.block_text

    def get_block_main_font(self):
        """
        Get the main font of a block.
        The main font is the font with the largest number of spans.
        """
        lines = self.block["lines"]
        font_list = []
        fontsize_list = []
        for line in lines:
            spans = line["spans"]
            for span in spans:
                span_font = span["font"]
                span_fontsize = round(span["size"], 1)
                span_flags = span["flags"]
                fontsize_list.append(span_fontsize)
                font_list.append(span_font)
                logger.debug(f"<font: {span_font}> <fontsize: {span_fontsize}>")
        self.block_most_common_font = Counter(font_list).most_common(1)[0][0]
        self.block_most_common_fontsize = Counter(fontsize_list).most_common(1)[0][0]
        return (self.block_most_common_font, self.block_most_common_fontsize)

    def get_block_tokens_num(self):
        tokenizer = Tokenizer()
        self.tokens_num = tokenizer.count_tokens(self.block_text.replace("\n", " "))
        return self.tokens_num
