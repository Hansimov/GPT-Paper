import os
import sys
from termcolor import colored
import torch
from pathlib import Path
from utils.logger import logger, shell_cmd
from utils.envs import init_os_envs, setup_envs_of_dit
from PIL import Image

setup_envs_of_dit()
init_os_envs(cuda_device=2)

try:
    from detectron2.config import CfgNode as CN
    from detectron2.config import get_cfg
    from detectron2.utils.visualizer import ColorMode, Visualizer
    from detectron2.data import MetadataCatalog
    from detectron2.data.detection_utils import read_image
    from detectron2.engine import DefaultPredictor

    from unilm.dit.object_detection.ditod import add_vit_config
except Exception as e:
    logger.err(e)
    raise e

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
        # Step 1: Instantiate config
        cfg = get_cfg()
        add_vit_config(cfg)

        cascade_dit_base_yml = (
            unilm_path
            / "dit"
            / "object_detection"
            / "publaynet_configs"
            / "cascade"
            / "cascade_dit_base.yaml"
        )

        logger.note(f"> Loading configs from `cascade_dit_base.yaml`:")
        logger.msg(f"  - {cascade_dit_base_yml}")

        cfg.merge_from_file(cascade_dit_base_yml)

        # Step 2: Load model weights URL to config
        publaynet_dit_b_cascade_pth = (
            repo_path / "configs" / "publaynet_dit-b_cascade.pth"
        )
        logger.note(f"> Loading weights from `publaynet_dit-b_cascade.pth`:")
        logger.file(f"  - {publaynet_dit_b_cascade_pth}")

        cfg.MODEL.WEIGHTS = str(publaynet_dit_b_cascade_pth)

        # Step 3: Set CUDA device
        if torch.cuda.is_available():
            cuda_device = os.environ.get("CUDA_VISIBLE_DEVICES", 0)
            logger.msg(f"> Using GPU:{cuda_device} ...")
            cfg.MODEL.DEVICE = "cuda"
        else:
            logger.msg(f"> Using CPU ...")
            cfg.MODEL.DEVICE = "cpu"

        # Step 4: Define model
        self.predictor = DefaultPredictor(cfg)
        self.cfg = cfg

        input_image_path = repo_path / "examples" / "example_pdf_4.png"
        output_image_path = repo_path / "examples" / "example_pdf_4_output.png"

        logger.note(f"> Analyzing input image:")
        logger.file(f"  - {input_image_path}")

        output_image = self.analyze_image(input_image_path)

        logger.success(f"> Saving output image:")
        logger.file(f"  - {output_image_path}")
        Image.fromarray(output_image).save(output_image_path)

    def analyze_image(self, image_path):
        cfg = self.cfg
        md = MetadataCatalog.get(cfg.DATASETS.TEST[0])
        if cfg.DATASETS.TEST[0] == "icdar2019_test":
            md.set(thing_classes=["table"])
        else:
            md.set(thing_classes=["text", "title", "list", "table", "figure"])

        image = read_image(str(image_path))
        output = self.predictor(image)["instances"]
        logger.msg(output)

        visualizer = Visualizer(
            image[:, :, ::-1],
            md,
            scale=1.0,
            instance_mode=ColorMode.SEGMENTATION,
        )
        result = visualizer.draw_instance_predictions(output.to("cpu"))

        result_image = result.get_image()[:, :, ::-1]

        return result_image


if __name__ == "__main__":
    dit_layout_analyzer = DITLayoutAnalyzer()
    dit_layout_analyzer.load_configs()
