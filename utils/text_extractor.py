from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from utils.logger import logger
from utils.envs import init_os_envs

init_os_envs()


class TextExtractor:
    def __init__(self):
        self.model_name = "microsoft/trocr-large-printed"

    def run(self):
        image = Image.open(
            "/mnt/sh_flex_storage/home/zehanyu/repos/GPT-Paper/pdfs/Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning/crops/page_2/region_1_text_99.9.png"
        )
        processor = TrOCRProcessor.from_pretrained(self.model_name)
        model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
        pixel_values = processor(images=image, return_tensors="pt").pixel_values

        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        logger.note("Text extracted from image:")
        logger.success(generated_text)


if __name__ == "__main__":
    text_extractor = TextExtractor()
    text_extractor.run()
