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
    dit_layout_analyzer.setup_envs()
