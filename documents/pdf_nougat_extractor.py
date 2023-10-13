from pathlib import Path
from utils.logger import logger, shell_cmd, Runtimer
from utils.envs import enver


class PDFNougatExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.pdf_parent = self.pdf_path.parent
        self.pdf_filename = self.pdf_path.name
        self.init_paths()

    def init_paths(self):
        # ANCHOR[id=pdf-nougat-extractor-paths]
        self.assets_path = self.pdf_parent / Path(self.pdf_filename).stem
        self.mmd_path = self.assets_path / "pages"

    def run_nougat(self):
        model_name = "0.1.0-small"
        # checkpoint_path = (
        #     Path(__file__).parents[2]
        #     / ".cache"
        #     / "huggingface"
        #     / "torch"
        #     / "hub"
        #     / f"nougat-{model_name}"
        # )
        self.nougat_command = (
            f'nougat "{str(self.pdf_path)}"'
            f' --out "{self.assets_path}"'
            f" --recompute"
            f" --no-skipping"
            f" --markdown"
            f" --model {model_name}"
            f" --batchsize 4"
            # f" --checkpoint {checkpoint_path}"
        )
        enver.set_envs(cuda_device=1)
        shell_cmd(self.nougat_command, env=enver.envs)
        enver.restore_envs()

    def run(self):
        self.run_nougat()


if __name__ == "__main__":
    with Runtimer():
        pdf_parent = Path(__file__).parents[1] / "pdfs" / "llm_agents"
        pdf_filename = "2308.08155 - AutoGen - Enabling Next-Gen LLM Applications via Multi-Agent Conversation.pdf"
        pdf_path = pdf_parent / pdf_filename
        pdf_nougat_extractor = PDFNougatExtractor(pdf_path)
        pdf_nougat_extractor.run()
