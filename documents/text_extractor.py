from pathlib import Path
from PIL import Image
from utils.logger import logger
import pytesseract


class TextExtractor:
    """
    ```bash
    $ tesseract --help-extra

    Usage:
    tesseract --help | --help-extra | --help-psm | --help-oem | --version
    tesseract --list-langs [--tessdata-dir PATH]
    tesseract --print-parameters [options...] [configfile...]
    tesseract imagename|imagelist|stdin outputbase|stdout [options...] [configfile...]

    OCR options:
    --tessdata-dir PATH   Specify the location of tessdata path.
    --user-words PATH     Specify the location of user words file.
    --user-patterns PATH  Specify the location of user patterns file.
    -l LANG[+LANG]        Specify language(s) used for OCR.
    -c VAR=VALUE          Set value for config variables.
                          Multiple -c arguments are allowed.
    --psm NUM             Specify page segmentation mode.
    --oem NUM             Specify OCR Engine mode.

    NOTE: These options must occur before any config file.

    Page segmentation modes:
      0    Orientation and script detection (OSD) only.
      1    Automatic page segmentation with OSD.
      2    Automatic page segmentation, but no OSD, or OCR.
      3    Fully automatic page segmentation, but no OSD. (Default)
      4    Assume a single column of text of variable sizes.
      5    Assume a single uniform block of vertically aligned text.
      6    Assume a single uniform block of text.
      7    Treat the image as a single text line.
      8    Treat the image as a single word.
      9    Treat the image as a single word in a circle.
     10    Treat the image as a single character.
     11    Sparse text. Find as much text as possible in no particular order.
     12    Sparse text with OSD.
     13    Raw line. Treat the image as a single text line,
           bypassing hacks that are Tesseract-specific.

    OCR Engine modes: (see https://github.com/tesseract-ocr/tesseract/wiki#linux)
      0    Legacy engine only.
      1    Neural nets LSTM engine only.
      2    Legacy + LSTM engines.
      3    Default, based on what is available.

    Single options:
      -h, --help            Show minimal help message.
      --help-extra          Show extra help for advanced users.
      --help-psm            Show page segmentation modes.
      --help-oem            Show OCR Engine modes.
      -v, --version         Show version information.
      --list-langs          List available languages for tesseract engine.
      --print-parameters    Print tesseract parameters.
    ```
    """

    def __init__(self, configs=None):
        # --oem 3: Default, based on what is available.
        # --psm 6: Assume a single uniform block of text.
        if configs:
            self.configs = configs
        else:
            self.configs = "--oem 3 --psm 6"

    def extract_from_image(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, config=self.configs)
        return text


if __name__ == "__main__":
    text_extractor = TextExtractor()
    text = text_extractor.extract_from_image(
        Path(__file__).parents[1]
        / "pdfs"
        / "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images"
        / "crops_ordered"
        / "page_13"
        / "region_2_text.png"
    )
    logger.success(text)
