from pathlib import Path
from PIL import Image

from utils.logger import logger
from utils.envs import init_os_envs
import platform
import pytesseract

if platform.system() == "Windows":
    init_os_envs(apis=["huggingface"], cuda_device=0)
else:
    init_os_envs()


class TextExtractor:
    def __init__(self):
        pass

    def run(self):
        image = Image.open(
            Path(__file__).parents[1]
            / "pdfs"
            / "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning"
            / "crops"
            / "page_1"
            # / "region_1_text_99.95.png"
            # / "region_5_text_99.31.png"
            / "region_6_text_98.92.png"
            # / "region_14_text_13.72.png"
        )
        text = pytesseract.image_to_string(image)
        logger.note("Text extracted from image:")
        logger.success(text)


if __name__ == "__main__":
    text_extractor = TextExtractor()
    text_extractor.run()
