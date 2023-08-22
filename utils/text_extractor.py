from pathlib import Path
from PIL import Image

from utils.logger import logger
from utils.envs import init_os_envs
import platform
import pytesseract

if platform.system() == "Windows":
    init_os_envs(cuda_device=0)
else:
    init_os_envs()


class TextExtractor:
    def __init__(self):
        pass

    def extract_from_image(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text


if __name__ == "__main__":
    text_extractor = TextExtractor()
