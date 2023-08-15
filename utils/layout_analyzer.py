import os
import sys
from termcolor import colored
import torch
from pathlib import Path
from utils.logger import logger, shell_cmd
from utils.envs import init_os_envs, setup_envs_of_dit
from PIL import Image

# setup_envs_of_dit()
init_os_envs(cuda_device=2)

try:
    from detectron2.detectron2.config import CfgNode as CN
    from detectron2.detectron2.config import get_cfg
    from detectron2.detectron2.utils.visualizer import ColorMode, Visualizer
    from detectron2.detectron2.data import MetadataCatalog
    from detectron2.detectron2.data.detection_utils import read_image
    from detectron2.detectron2.engine import DefaultPredictor

    from unilm.dit.object_detection.ditod import add_vit_config
except Exception as e:
    logger.err(e)

# GPT-Paper repo path
repo_path = Path(__file__).parents[1]
# GPT-Paper repo parent path
repo_parent_path = repo_path.parent

detectron2_path = repo_parent_path / "detectron2"
unilm_path = repo_parent_path / "unilm"


class DITLayoutAnalyzer:
    def __init__(self):
        pass

    def load_configs(self):
        cascade_dit_base_yml = (
            unilm_path
            / "dit"
            / "object_detection"
            / "publaynet_configs"
            / "cascade"
            / "cascade_dit_base.yaml"
        )
        logger.note(f"> Loading `cascade_dit_base.yaml`:")
        logger.msg(f"  - {cascade_dit_base_yml}")

        cfg = get_cfg()
        add_vit_config(cfg)
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
                image[:, :, ::-1],
                md,
                scale=1.0,
                instance_mode=ColorMode.SEGMENTATION,
            )
            result = v.draw_instance_predictions(output.to("cpu"))
            result_image = result.get_image()[:, :, ::-1]

            return result_image

        input_image_path = repo_path / "tests" / "example_pdf_4.png"
        output_image_path = repo_path / "tests" / "example_pdf_4_output.png"

        logger.note(f"> Analyzing input image:")
        logger.msg(f"  - {input_image_path}")

        output_image = analyze_image(input_image_path)

        logger.success(f"> Saving output image:")
        logger.msg(f"  - {output_image_path}")
        Image.fromarray(output_image).save(output_image_path)


if __name__ == "__main__":
    dit_layout_analyzer = DITLayoutAnalyzer()
    dit_layout_analyzer.load_configs()
