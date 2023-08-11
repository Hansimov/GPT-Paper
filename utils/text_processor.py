import re
from collections import Counter
from termcolor import colored
from utils.calculator import (
    each_is_different,
    rect_area,
    avg_line_width,
    char_per_pixel,
)
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


def regroup_blocks(blocks):
    """
    1. Concatenate last block of page[i] and first block of page[i+1],
       if they are in the same paragraph.
    2. Split the concatenated block into multiple blocks,
       if there are different paragraphs.
    """


class TextBlock:
    def __init__(self, block):
        self.block = block
        self.lines = self.get_lines()
        self.spans = self.get_spans()
        self.bbox = self.get_bbox()

    def get_bbox(self):
        self.bbox = self.block["bbox"]
        return self.bbox

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

    def get_lines(self):
        self.lines = self.block["lines"]
        return self.lines

    def get_spans(self):
        self.spans = [spans for line in self.lines for spans in line["spans"]]
        return self.spans

    def get_line_num(self):
        self.line_num = len(self.block["lines"])
        return self.line_num

    def get_span_num(self):
        self.span_num = len(self.get_spans())
        return self.span_num

    def get_char_num(self):
        self.char_num = len(self.get_block_text().replace("\n", ""))
        return self.char_num

    def get_area(self):
        self.area = rect_area(*self.bbox)
        return self.area

    def get_char_per_pixel(self):
        self.char_per_pixel = char_per_pixel(self.get_char_num(), self.get_area())
        return self.char_per_pixel

    def get_avg_line_width(self):
        self.avg_line_width = avg_line_width(self.get_block_text().replace("\n", ""))
        return self.avg_line_width

    def get_block_main_font(self) -> tuple(str, float):
        """return (font, fontsize)"""
        lines = self.block["lines"]

        line_font_list = []
        line_fontsize_list = []
        old_line_font_and_size = (None, None)

        line_font_counter = Counter()
        line_fontsize_counter = Counter()
        for line in lines:
            span_font_counter = Counter()
            span_fontsize_counter = Counter()
            span_font_list = []
            span_fontsize_list = []
            old_span_font_and_size = (None, None)
            spans = line["spans"]
            line_text = ""
            for span in spans:
                span_font = span["font"]
                span_text = span["text"]
                span_fontsize = round(span["size"], 1)
                new_span_font_and_size = (span_font, span_fontsize)
                if new_span_font_and_size != old_span_font_and_size:
                    logger.debug(f"span: <{span_font}> <{span_fontsize}>")
                    old_span_font_and_size = new_span_font_and_size

                logger.debug(f"<font: {span_font}> <fontsize: {span_fontsize}>")
                logger.debug(span["text"])
                span_flags = span["flags"]
                span_fontsize_list.append(span_fontsize)
                span_font_list.append(span_font)
                line_text += f"{span_text}"
                span_font_counter.update({span_font: len(span_text)})
                span_fontsize_counter.update({span_fontsize: len(span_text)})

            line_font = span_font_counter.most_common(1)[0][0]
            line_fontsize = span_fontsize_counter.most_common(1)[0][0]

            new_line_font_and_size = (line_font, line_fontsize)
            if each_is_different(new_line_font_and_size, old_line_font_and_size):
                logger.warning(
                    colored(f"line: <{line_font}> <{line_fontsize}>", "light_red")
                )
                old_line_font_and_size = new_line_font_and_size

            logger.info(f"{line_text}")
            line_font_list.append(line_font)
            line_fontsize_list.append(line_fontsize)
            line_font_counter.update({line_font: len(line_text)})
            line_fontsize_counter.update({line_fontsize: len(line_text)})

        self.block_most_common_font = line_font_counter.most_common(1)[0][0]
        self.block_most_common_fontsize = line_fontsize_counter.most_common(1)[0][0]
        return (self.block_most_common_font, self.block_most_common_fontsize)

    def get_block_tokens_num(self):
        tokenizer = Tokenizer()
        self.tokens_num = tokenizer.count_tokens(self.block_text.replace("\n", " "))
        return self.tokens_num

    def replace_chars(self):
        chars_map = {"\s*ﬁ\s*": "fi"}
        for k, v in chars_map.items():
            self.block_text = re.sub(k, v, self.block_text)
