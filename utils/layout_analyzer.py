import os
import sys
import torch
import warnings
from pathlib import Path
from PIL import Image
from termcolor import colored
from utils.logger import logger, shell_cmd
from utils.envs import init_os_envs, setup_envs_of_dit

warnings.filterwarnings("ignore")

setup_envs_of_dit()
# init_os_envs(cuda_device=0)

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

    def setup_model(self):
        self.load_configs()
        self.load_weights()
        self.set_device()
        self.create_predictor()
        self.set_metadata()

    def run(self):
        self.setup_model()
        self.annotate_image()

    # Step 1: Instantiate config
    def load_configs(self):
        self.cfg = get_cfg()
        add_vit_config(self.cfg)

        cascade_dit_base_yml = (
            unilm_path
            / "dit"
            / "object_detection"
            / "publaynet_configs"
            / "cascade"
            / "cascade_dit_base.yaml"
        )

        logger.note(f"> Loading configs from `cascade_dit_base.yaml`:")
        logger.file(f"  - {cascade_dit_base_yml}")

        self.cfg.merge_from_file(cascade_dit_base_yml)

    # Step 2: Load model weights to config
    def load_weights(self):
        publaynet_dit_b_cascade_pth = (
            repo_path / "configs" / "publaynet_dit-b_cascade.pth"
        )
        if not publaynet_dit_b_cascade_pth.exists():
            raise FileNotFoundError("`publaynet_dit-b_cascade.pth` not found.")

        logger.note(f"> Loading weights from `publaynet_dit-b_cascade.pth`:")
        logger.file(f"  - {publaynet_dit_b_cascade_pth}")

        self.cfg.MODEL.WEIGHTS = str(publaynet_dit_b_cascade_pth)

    # Step 3: Set CUDA device
    def set_device(self):
        if torch.cuda.is_available():
            cuda_device = os.environ.get("CUDA_VISIBLE_DEVICES", 0)
            logger.note(f"> Using GPU:{cuda_device} ...")
            self.cfg.MODEL.DEVICE = "cuda"
        else:
            logger.note(f"> Using CPU ...")
            self.cfg.MODEL.DEVICE = "cpu"

    # Step 4: Create Predictor
    def create_predictor(self):
        logger.note("> Creating predictor ...")
        self.predictor = DefaultPredictor(self.cfg)

    # Step 5: Set meta data
    def set_metadata(self):
        logger.note("> Setting metadata ...")
        # logger.msg(self.cfg.DATASETS)
        dataset_name = "publaynet_val"
        self.metadata = MetadataCatalog.get(dataset_name)
        # logger.msg(self.metadata)
        self.thing_classes = ["text", "title", "list", "table", "figure"]
        self.metadata.set(thing_classes=self.thing_classes)

    def annotate_image(
        self,
        input_image_path=repo_path / "examples" / "example_pdf_4.png",
        output_image_path=repo_path / "examples" / "example_pdf_4_output.png",
    ):
        logger.note(f"> Analyzing input image:")
        logger.file(f"  - {input_image_path}")

        image = read_image(str(input_image_path))
        output = self.predictor(image)["instances"]
        # logger.msg(output)
        pred_things = [self.thing_classes[c] for c in output.pred_classes]

        logger.note("Results:")
        image_height, image_width = output.image_size
        logger.msg(f" - image_size: {image_width}(w) * {image_height}(h)")
        logger.msg(f" - num_instances: {len(output)}")
        logger.msg(f" - pred_classes: {output.pred_classes.tolist()}")
        logger.msg(f" - pred_things: {pred_things}")
        logger.msg(f" - pred_boxes: {output.pred_boxes.tensor.tolist()}")
        logger.msg(f" - scores: {output.scores.tolist()}")
        # logger.msg(f" - fields {output.fields}")

        visualizer = Visualizer(
            image[:, :, ::-1],
            metadata=self.metadata,
            scale=1.0,
            instance_mode=ColorMode.SEGMENTATION,
        )
        result = visualizer.draw_instance_predictions(output.to("cpu"))

        result_image = result.get_image()[:, :, ::-1]

        logger.success(f"> Saving output image:")
        logger.file(f"  - {output_image_path}")

        Image.fromarray(result_image).save(output_image_path)

        return result_image, output


if __name__ == "__main__":
    dit_layout_analyzer = DITLayoutAnalyzer()
    dit_layout_analyzer.run()
