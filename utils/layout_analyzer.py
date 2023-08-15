import cv2
import distutils
import os
import sys
import subprocess
from termcolor import colored
import torch
from pathlib import Path
from utils.logger import logger, shell_cmd
from utils.envs import setup_envs_of_dit

try:
    repo_path = Path(__file__).parents[1]
    repo_parent_path = repo_path.parent

    detectron2_path = repo_parent_path / "detectron2"
    unilm_path = repo_parent_path / "unilm"

    sys.path.insert(0, os.path.abspath(str(detectron2_path)))
    sys.path.insert(0, os.path.abspath(str(unilm_path)))

    from detectron2.config import CfgNode as CN
    from detectron2.config import get_cfg
    from detectron2.utils.visualizer import ColorMode, Visualizer
    from detectron2.data import MetadataCatalog
    from detectron2.engine import DefaultPredictor

    from dit.object_detection.ditod import add_vit_config
except Exception as e:
    logger.error(colored(e, "red"))


class DITLayoutAnalyzer:
    # GPT-Paper repo path
    repo_path = Path(__file__).parents[1]
    # GPT-Paper repo parent path
    repo_parent_path = repo_path.parent

    def __init__(self) -> None:
        pass

    def setup_envs(self):
        setup_envs_of_dit()


if __name__ == "__main__":
    dit_layout_analyzer = DITLayoutAnalyzer()
    # dit_layout_analyzer.setup_envs()
