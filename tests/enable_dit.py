"""
* app.py · nielsr/dit-document-layout-analysis at main
  * https://huggingface.co/spaces/nielsr/dit-document-layout-analysis/blob/main/app.py
"""
import cv2
import os
import sys
import torch

from pathlib import Path


def git_clone_repos():
    os.system("git clone https://github.com/facebookresearch/detectron2.git")
    os.system("pip install -e detectron2")
    os.system("git clone https://github.com/microsoft/unilm.git")


# git_clone_repos()
detectron2_path = Path(__file__).parents[2] / "detectron2"
unilm_path = Path(__file__).parents[2] / "unilm"
# print(str(detectron2_path))
# print(str(unilm_path))


def patch_dit_data_structure():
    os.system(
        f"sed -i 's/from collections import Iterable/from collections.abc import Iterable/' {str(unilm_path)}/dit/object_detection/ditod/table_evaluation/data_structure.py"
    )


# patch_dit_data_structure()


def download_publaynet_dit_b_cascade_pth():
    os.system(
        "curl --proxy 'http://localhost:11111' -LJ -o publaynet_dit-b_cascade.pth 'https://layoutlm.blob.core.windows.net/dit/dit-fts/publaynet_dit-b_cascade.pth?sv=2022-11-02&ss=b&srt=o&sp=r&se=2033-06-08T16:48:15Z&st=2023-06-08T08:48:15Z&spr=https&sig=a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D'"
    )


# download_publaynet_dit_b_cascade_pth()


sys.path.insert(0, os.path.abspath(str(detectron2_path)))
sys.path.insert(0, os.path.abspath(str(unilm_path)))

from detectron2.config import CfgNode as CN
from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor

from dit.object_detection.ditod import add_vit_config

import gradio as gr


def main():
    # Step 1: instantiate config
    cfg = get_cfg()
    add_vit_config(cfg)

    cascade_dit_base_yml = str(Path(__file__).parent / "cascade_dit_base.yml")
    cfg.merge_from_file(cascade_dit_base_yml)

    # Step 2: add model weights URL to config
    cfg.MODEL.WEIGHTS = "publaynet_dit-b_cascade.pth"

    # Step 3: set device
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # Step 4: define model
    predictor = DefaultPredictor(cfg)

    def analyze_image(img):
        md = MetadataCatalog.get(cfg.DATASETS.TEST[0])
        if cfg.DATASETS.TEST[0] == "icdar2019_test":
            md.set(thing_classes=["table"])
        else:
            md.set(thing_classes=["text", "title", "list", "table", "figure"])

        output = predictor(img)["instances"]
        v = Visualizer(
            img[:, :, ::-1], md, scale=1.0, instance_mode=ColorMode.SEGMENTATION
        )
        result = v.draw_instance_predictions(output.to("cpu"))
        result_image = result.get_image()[:, :, ::-1]

        return result_image

    title = "Interactive demo: Document Layout Analysis with DiT"
    description = "Demo for Microsoft's DiT, the Document Image Transformer for state-of-the-art document understanding tasks. This particular model is fine-tuned on PubLayNet, a large dataset for document layout analysis (read more at the links below). To use it, simply upload an image or use the example image below and click 'Submit'. Results will show up in a few seconds. If you want to make the output bigger, right-click on it and select 'Open image in new tab'."
    article = "<p style='text-align: center'><a href='https://arxiv.org/abs/2203.02378' target='_blank'>Paper</a> | <a href='https://github.com/microsoft/unilm/tree/master/dit' target='_blank'>Github Repo</a></p> | <a href='https://huggingface.co/docs/transformers/master/en/model_doc/dit' target='_blank'>HuggingFace doc</a></p>"
    examples = [
        [
            str(Path(__file__).parents[1] / "examples" / f"example_pdf_{i+1}.png")
            for i in range(4)
        ]
    ]
    css = ".output-image, .input-image, .image-preview {height: 600px !important}"

    iface = gr.Interface(
        fn=analyze_image,
        inputs=gr.inputs.Image(type="numpy", label="document image"),
        outputs=gr.outputs.Image(type="numpy", label="annotated document"),
        title=title,
        description=description,
        examples=examples,
        article=article,
        css=css,
        enable_queue=True,
    )
    iface.launch(debug=True, server_name="0.0.0.0", server_port=23456, share=True)


if __name__ == "__main__":
    main()
