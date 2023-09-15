import ctypes
import inspect
import json
import nltk
import os
import platform
import re
import site
import shutil
from ctypes.util import find_library
from pathlib import Path
from termcolor import colored
from utils.logger import logger, shell_cmd


class OSEnver:
    def __init__(self, global_scope=True):
        self.envs_stack = []
        self.global_scope = global_scope
        self.envs = os.environ.copy()

    def store_envs(self):
        self.envs_stack.append(self.envs)

    def restore_envs(self):
        self.envs = self.envs_stack.pop()
        if self.global_scope:
            os.environ = self.envs

    def set_envs(
        self,
        secrets=True,
        set_proxy=False,
        cuda_device=True,
        cuda_alloc=True,
        huggingface=True,
        openai=False,
        ninomae=False,
        store_envs=True,
    ):
        # caller_info = inspect.stack()[1]
        # logger.back(f"OS Envs is set by: {caller_info.filename}")

        if store_envs:
            self.store_envs()

        if secrets:
            with open(Path(__file__).parents[1] / "secrets.json", "r") as rf:
                secrets = json.load(rf)

        if set_proxy:
            for proxy_env in ["http_proxy", "https_proxy"]:
                self.envs[proxy_env] = secrets["http_proxy"]

        if openai:
            self.envs["OPENAI_API_KEY"] = secrets["openai_api_key"]

        if ninomae:
            self.envs["OPENAI_API_KEY"] = secrets["ninomae_api_key"]

        if huggingface:
            """
            * https://stackoverflow.com/questions/63312859/how-to-change-huggingface-transformers-default-cache-directory
            * https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables
            """
            cache_root = Path(__file__).parents[2] / ".cache"
            cache_root.mkdir(parents=True, exist_ok=True)
            hf_envs = {
                "HF_HOME": ".",
                "XDG_CACHE_HOME": ".",
                "TRANSFORMERS_CACHE": "hub",
                "HUGGINGFACE_HUB_CACHE": "hub",
                "HUGGINGFACE_ASSETS_CACHE": "assets",
                "HUGGING_FACE_HUB_TOKEN": "token",
                # "HF_DATASETS_CACHE": "datasets",
            }
            for env_name, env_path in hf_envs.items():
                self.envs[env_name] = str(cache_root / "huggingface" / f"{env_path}")
                # logger.note(str(cache_root / "huggingface" / f"{env_path}"))

            st_envs = {
                "SENTENCE_TRANSFORMERS_HOME": "sentence_transformers",
            }
            for env_name, env_path in st_envs.items():
                self.envs[env_name] = str(cache_root / f"{env_path}")

        if cuda_device is True:
            if platform.system() == "Windows":
                self.envs["CUDA_VISIBLE_DEVICES"] = "0"
            else:
                self.envs["CUDA_VISIBLE_DEVICES"] = "3"

        if cuda_alloc:
            self.envs["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

        if self.global_scope:
            os.environ = self.envs


enver = OSEnver()


def copy_to_site_packaegs(package_path):
    folder_base_name = Path(package_path).name
    site_packages_paths = site.getsitepackages()
    site_packages_path = None
    for p in site_packages_paths:
        if p.endswith("site-packages"):
            site_packages_path = Path(p)
    package_path_in_site_packages = site_packages_path / folder_base_name

    if package_path_in_site_packages.exists():
        logger.warn(f"> Removing {folder_base_name} in site-packages:")
        logger.file(f"  - {package_path_in_site_packages}")
        shutil.rmtree(site_packages_path / folder_base_name)

    logger.note(f"> Copying {folder_base_name} to site-packages:")
    logger.file(f"  - From: {package_path}")
    logger.file(f"  -   To: {package_path_in_site_packages}")
    shutil.copytree(
        package_path,
        package_path_in_site_packages,
        ignore=shutil.ignore_patterns(".git"),
    )


def check_camelot_dependencies():
    logger.info("Checking camelot dependencies:")
    gs_res = find_library(
        "".join(("gsdll", str(ctypes.sizeof(ctypes.c_voidp) * 8), ".dll"))
    )
    logger.info(f"GhostScript: {gs_res}")


repo_path = Path(__file__).parents[1]
repo_parent_path = repo_path.parent


def setup_envs_of_detectron2(clone_repo=True, install_dependencies=True):
    # git clone repo of detectron2
    detectron2_path = repo_parent_path / "detectron2"

    if clone_repo and not detectron2_path.exists():
        shell_cmd(
            f"git clone https://github.com/facebookresearch/detectron2.git {str(detectron2_path)}"
        )

    # install dependencies of detectron2
    if install_dependencies:
        logger.warn("See README.md to install `detectron2` dependencies.")

        logger.note("Installing required packages of detectron2:")
        required_packages = [
            "Pillow>=7.1",
            "matplotlib",
            "pycocotools>=2.0.2",
            "termcolor>=1.1",
            "yacs>=0.1.8",
            "tabulate",
            "cloudpickle",
            "tqdm>4.29.0",
            "tensorboard",
            "fvcore>=0.1.5,<0.1.6",
            "iopath>=0.1.7,<0.1.10",
            "omegaconf>=2.1,<2.4",
            "hydra-core>=1.1",
            "black",
            "packaging",
        ]
        required_packages_str = " ".join([f'"{p}"' for p in required_packages])
        shell_cmd(f"pip install {required_packages_str}")

        extra_packages = [
            "fairscale",
            "timm",
            "scipy>1.5.1",
            "shapely",
            "pygments>=2.2",
            "psutil",
            "panopticapi @ https://github.com/cocodataset/panopticapi/archive/master.zip",
        ]
        logger.note("Installing extra packages of detectron2:")
        extra_packages_str = " ".join([f'"{p}"' for p in extra_packages])
        shell_cmd(f"pip install {extra_packages_str}")

    copy_to_site_packaegs(detectron2_path / "detectron2")


def setup_envs_of_unilm():
    # git clone repo of unilm
    unilm_path = repo_parent_path / "unilm"
    if not unilm_path.exists():
        shell_cmd(f"git clone https://github.com/microsoft/unilm.git {str(unilm_path)}")

    # patch `data_structure.py` in dit
    logger.note("> Patching `data_structure.py` in dit ...")
    orignial_str = "from collections import Iterable"
    replaced_str = "from collections.abc import Iterable"
    data_structure_py = (
        unilm_path
        / "dit"
        / "object_detection"
        / "ditod"
        / "table_evaluation"
        / "data_structure.py"
    )

    with open(data_structure_py, "r", encoding="utf-8") as rf:
        original_text = rf.read()
        replaced_text = re.sub(orignial_str, replaced_str, original_text)

    with open(data_structure_py, "w", encoding="utf-8") as wf:
        wf.write(replaced_text)

    copy_to_site_packaegs(unilm_path)


def download_layout_blob(
    url_head,
    output_path=None,
    output_filename=None,
    http_proxy="http://localhost:11111",
    overwrite=False,
    resume=False,
):
    url_params = {
        "sv": "2022-11-02",
        "ss": "b",
        "srt": "o",
        "sp": "r",
        "se": "2033-06-08T16:48:15Z",
        "st": "2023-06-08T08:48:15Z",
        "spr": "https",
        "sig": "a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D",
    }

    download_url = url_head + "?" + "&".join(f"{k}={v}" for k, v in url_params.items())
    if http_proxy:
        proxy_str = f' --proxy "{http_proxy}"'
    else:
        proxy_str = ""

    if resume:
        resume_str = " -C -"
        remote_header_str = ""
    else:
        resume_str = ""
        remote_header_str = " -J"

    if platform.system().lower() == "windows":
        download_url = download_url.replace("&", "&&")

    if not output_path:
        output_path = repo_path / "data" / output_filename

    if overwrite or not output_path.exists():
        os.makedirs(output_path.parent, exist_ok=True)
        logger.info(colored(f"Downloading {str(output_path)} ...", "light_magenta"))
        shell_cmd(
            f'curl{proxy_str}{resume_str}{remote_header_str} -L -o "{output_path}" "{download_url}"'
        )


def download_publaynet_dit_cascade_pth(size="base"):
    """
    Download weights of Fine-tuning on PubLayNet (Document Layout Analysis):
    * https://github.com/microsoft/unilm/blob/master/dit/README.md#fine-tuning-on-publaynet-document-layout-analysis
    """
    if size == "large":
        size_str = "l"
    else:
        size_str = "l"

    pth_name = f"publaynet_dit-{size_str}_cascade.pth"
    url_head = f"https://layoutlm.blob.core.windows.net/dit/dit-fts/{pth_name}"

    download_layout_blob(url_head=url_head, output_filename=pth_name)


def setup_envs_of_dit():
    setup_envs_of_detectron2()
    setup_envs_of_unilm()
    download_publaynet_dit_cascade_pth(size="large")


def download_reading_bank_dataset():
    """
    Download ReadingBank dataset:
    * https://layoutlm.blob.core.windows.net/readingbank/dataset/ReadingBank.zip?sv=2022-11-02&ss=b&srt=o&sp=r&se=2033-06-08T16:48:15Z&st=2023-06-08T08:48:15Z&spr=https&sig=a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D

    Download LayoutReader pre-trained model:
    * https://layoutlm.blob.core.windows.net/readingbank/model/layoutreader-base-readingbank.zip?sv=2022-11-02&ss=b&srt=o&sp=r&se=2033-06-08T16:48:15Z&st=2023-06-08T08:48:15Z&spr=https&sig=a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D

    Ubuntu Command:
    unzip ReadingBank.zip -d ReadingBank
    """
    url_head = (
        "https://layoutlm.blob.core.windows.net/readingbank/dataset/ReadingBank.zip"
    )
    output_filename = "ReadingBank.zip"

    download_layout_blob(
        url_head=url_head,
        output_filename=output_filename,
        overwrite=True,
        resume=True,
    )


def download_nltk_data():
    nltk.download("punkt")


if __name__ == "__main__":
    enver.set_envs(set_proxy=True)
    os.environ = enver.envs
    setup_envs_of_dit()
    # download_reading_bank_dataset()
    download_nltk_data()
    enver.restore_envs()
    os.environ = enver.envs
