import json
import os
from pathlib import Path
from utils.logger import shell_cmd


class JupyterLabLauncher:
    def __init__(self):
        self.init_envs()
        self.ipynb_path = Path(__file__).parent / "review_writer.ipynb"

    def init_envs(self):
        with open(Path(__file__).parents[1] / "secrets.json", "r") as rf:
            secrets = json.load(rf)
        jupyter_token = secrets["jupyter_token"]
        self.envs = {
            "JUPYTER_CONFIG_DIR": str(Path(__file__).parent),
            "JUPYTER_TOKEN": jupyter_token,
        }
        for env in self.envs:
            os.environ[env] = self.envs[env]
        self.ip = "0.0.0.0"
        self.port = "28888"

    def generate_config(self):
        shell_cmd("jupyter lab --generate-config")

    def run(self):
        # shell_cmd(f"jupyter lab {self.ipynb_path}")
        shell_cmd(f"jupyter lab --ip={self.ip} --port={self.port} {self.ipynb_path}")


if __name__ == "__main__":
    jupyter_lab_launcher = JupyterLabLauncher()
    jupyter_lab_launcher.run()
