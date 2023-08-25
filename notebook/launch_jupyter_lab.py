import os
from pathlib import Path
from utils.logger import shell_cmd


class JupyterLabLauncher:
    def __init__(self):
        self.init_envs()
        self.ipynb_path = Path(__file__).parent / "test_jupyter_lab.ipynb"

    def init_envs(self):
        self.envs = {
            "JUPYTER_CONFIG_DIR": str(Path(__file__).parent),
        }
        for env in self.envs:
            os.environ[env] = self.envs[env]

    def generate_config(self):
        shell_cmd("jupyter lab --generate-config")

    def run(self):
        # shell_cmd(f"jupyter lab {self.ipynb_path}")
        shell_cmd(f"jupyter lab")


if __name__ == "__main__":
    jupyter_lab_launcher = JupyterLabLauncher()
    jupyter_lab_launcher.run()
