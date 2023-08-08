import json
import os
from pathlib import Path


def init_os_envs(apis=[], set_proxy=True):
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
