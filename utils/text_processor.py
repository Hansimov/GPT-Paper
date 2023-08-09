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
