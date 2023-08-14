import ctypes
import json
import os
from ctypes.util import find_library
from pathlib import Path
from utils.logger import Logger

logger = Logger().logger


def init_os_envs(secrets=True, apis=[], set_proxy=True, cuda_device=None):
    if secrets:
        with open(Path(__file__).parents[1] / "secrets.json", "r") as rf:
            secrets = json.load(rf)

    if type(apis) == str:
        apis = [apis]
    apis = [api.lower() for api in apis]

    if set_proxy:
        for proxy_env in ["http_proxy", "https_proxy"]:
            os.environ[proxy_env] = secrets["http_proxy"]

    if "openai" in apis:
        os.environ["OPENAI_API_KEY"] = secrets["openai_api_key"]

    if "huggingface" in apis:
        """
        https://stackoverflow.com/questions/63312859/how-to-change-huggingface-transformers-default-cache-directory
        https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables
        """
        hf_envs = {
            "TRANSFORMERS_CACHE": "models",
            "HF_DATASETS_CACHE": "datasets",
            "HF_HOME": "misc",
        }
        for env_name, env_path in hf_envs.items():
            os.environ[env_name] = str(
                Path(__file__).parent / f".cache/huggingface/{env_path}"
            )

    if cuda_device:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(cuda_device)


def check_camelot_dependencies():
    logger.info("Checking camelot dependencies:")
    gs_res = find_library(
        "".join(("gsdll", str(ctypes.sizeof(ctypes.c_voidp) * 8), ".dll"))
    )
    logger.info(f"GhostScript: {gs_res}")


if __name__ == "__main__":
    # init_os_envs()
    check_camelot_dependencies()
