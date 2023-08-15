import os
import sys
from termcolor import colored
import torch
from pathlib import Path
from utils.logger import logger, shell_cmd
from utils.envs import setup_envs_of_dit
from PIL import Image

# setup_envs_of_dit()

try:
    # GPT-Paper repo path
    repo_path = Path(__file__).parents[1]
    # GPT-Paper repo parent path
    repo_parent_path = repo_path.parent

    detectron2_path = repo_parent_path / "detectron2"
    unilm_path = repo_parent_path / "unilm"

    sys.path.insert(0, os.path.abspath(str(detectron2_path)))
    sys.path.insert(0, os.path.abspath(str(unilm_path)))

    from detectron2.config import CfgNode as CN
    from detectron2.config import get_cfg
    from detectron2.utils.visualizer import ColorMode, Visualizer
    from detectron2.data import MetadataCatalog
    from detectron2.data.detection_utils import read_image
    from detectron2.engine import DefaultPredictor

    from dit.object_detection.ditod import add_vit_config
except Exception as e:
    logger.error(colored(e, "red"))


class DITLayoutAnalyzer:
    def __init__(self) -> None:
        pass

    def run(self):
        # Step 1: instantiate config
        cfg = get_cfg()
        add_vit_config(cfg)

        cascade_dit_base_yml = str(repo_path / "configs" / "cascade_dit_base.yml")
        cfg.merge_from_file(cascade_dit_base_yml)

        # Step 2: add model weights URL to config
        cfg.MODEL.WEIGHTS = str(repo_path / "configs" / "publaynet_dit-b_cascade.pth")

        # Step 3: set device
        cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

        # Step 4: define model
        predictor = DefaultPredictor(cfg)

        def analyze_image(image_path):
            image = read_image(str(image_path))
            md = MetadataCatalog.get(cfg.DATASETS.TEST[0])
            if cfg.DATASETS.TEST[0] == "icdar2019_test":
                md.set(thing_classes=["table"])
            else:
                md.set(thing_classes=["text", "title", "list", "table", "figure"])

            output = predictor(image)["instances"]
            v = Visualizer(
                image[:, :, ::-1], md, scale=1.0, instance_mode=ColorMode.SEGMENTATION
            )
            result = v.draw_instance_predictions(output.to("cpu"))
            result_image = result.get_image()[:, :, ::-1]

            return result_image

        input_image_path = repo_path / "tests" / "example_pdf_4.png"
        output_image_path = repo_path / "tests" / "example_pdf_4_output.png"
        output_image = analyze_image(input_image_path)
        logger.info(colored("Saving output image...", "light_green"))
        Image.fromarray(output_image).save(output_image_path)


if __name__ == "__main__":
    dit_layout_analyzer = DITLayoutAnalyzer()
    dit_layout_analyzer.run()
