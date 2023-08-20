import json
import networkx as nx
import os
import platform
import sys
import torch
import warnings
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from termcolor import colored
from utils.logger import logger, shell_cmd
from utils.envs import init_os_envs, setup_envs_of_dit
from utils.calculator import rect_area, rect_overlap, rect_contain, union_rects

warnings.filterwarnings("ignore")

# setup_envs_of_dit()
if platform.system() == "Windows":
    init_os_envs(apis=["huggingface"], cuda_device=0)
else:
    init_os_envs(cuda_device=3)


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
    """
    * app.py · nielsr/dit-document-layout-analysis
        * https://huggingface.co/spaces/nielsr/dit-document-layout-analysis/blob/main/app.py
    * unilm/dit/object_detection/inference.py
        * https://github.com/microsoft/unilm/blob/master/dit/object_detection/inference.py
    """

    def __init__(self, size="base"):
        self.model_size = size

    def setup_model(self):
        self.load_configs()
        self.load_weights()
        self.set_device()
        self.create_predictor()
        self.set_metadata()

    def test_run(self):
        self.setup_model()
        # self.annotate_image(
        #     input_image_path=repo_path / "examples" / "example_pdf_4.png",
        #     output_image_path=repo_path / "examples" / "example_pdf_4_output.png",
        # )

    # Step 1: Instantiate config
    def load_configs(self):
        self.cfg = get_cfg()
        add_vit_config(self.cfg)

        if self.model_size == "large":
            size_str = "large"
        else:
            size_str = "base"

        yaml_name = f"cascade_dit_{size_str}.yaml"
        cascade_dit_yml = (
            unilm_path
            / "dit"
            / "object_detection"
            / "publaynet_configs"
            / "cascade"
            / yaml_name
        )

        logger.note(f"> Loading configs from `{yaml_name}`:")
        logger.file(f"  - {cascade_dit_yml}")

        self.cfg.merge_from_file(cascade_dit_yml)

    # Step 2: Load model weights to config
    def load_weights(self):
        if self.model_size == "large":
            size_str = "l"
        else:
            size_str = "b"

        pth_name = f"publaynet_dit-{size_str}_cascade.pth"
        publaynet_dit_cascade_pth = repo_path / "configs" / pth_name
        if not publaynet_dit_cascade_pth.exists():
            raise FileNotFoundError(f"`{pth_name}` not found.")

        logger.note(f"> Loading weights from `{pth_name}`:")
        logger.file(f"  - {publaynet_dit_cascade_pth}")

        self.cfg.MODEL.WEIGHTS = str(publaynet_dit_cascade_pth)

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

    def annotate_image(self, input_image_path=None, output_image_path=None):
        if input_image_path is None:
            raise ValueError("`input_image_path` is None!")

        logger.note(f"> Analyzing the layout of input image:")
        logger.file(f"  - {input_image_path}")

        image = read_image(str(input_image_path))
        pred_output = self.predictor(image)["instances"]
        # logger.msg(output)
        pred_things = [self.thing_classes[c] for c in pred_output.pred_classes]

        logger.note("> Results:")
        image_height, image_width = pred_output.image_size
        logger.msg(f"  - image_size: {image_width}(w) * {image_height}(h)")
        logger.msg(f"  - num_instances: {len(pred_output)}")
        logger.debug(f"  - pred_classes: {pred_output.pred_classes.tolist()}")
        logger.msg(f"  - pred_things: {pred_things}")
        logger.debug(f"  - pred_boxes: {pred_output.pred_boxes.tensor.tolist()}")
        logger.debug(f"  - scores: {pred_output.scores.tolist()}")
        # logger.msg(f"  - fields {output.fields}")

        # visualizer = Visualizer(
        #     image[:, :, ::-1],
        #     metadata=self.metadata,
        #     scale=1.0,
        #     instance_mode=ColorMode.SEGMENTATION,
        # )
        # result = visualizer.draw_instance_predictions(output.to("cpu"))

        # result_image = result.get_image()[:, :, ::-1]

        # logger.success(f"> Saving output image:")
        # logger.file(f"  - {output_image_path}")

        # Image.fromarray(result_image).save(output_image_path)

        annotate_info_json_path = self.dump_annotate_info(
            input_image_path, output_image_path, pred_output
        )

        return pred_output, annotate_info_json_path

    def dump_annotate_info(self, input_image_path, output_image_path, output):
        image_height, image_width = output.image_size
        self.annotate_infos = {
            "page": {
                "original_image_path": str(input_image_path),
                "current_image_path": str(output_image_path),
                "image_width": image_width,
                "image_height": image_height,
                "regions_num": len(output),
            },
            "regions": [],
        }
        pred_classes = output.pred_classes.tolist()
        pred_things = [self.thing_classes[c] for c in pred_classes]
        pred_boxes = [
            [round(x, 1) for x in box] for box in output.pred_boxes.tensor.tolist()
        ]
        pred_scores = [round(x * 100, 2) for x in output.scores.tolist()]
        for i in range(len(output)):
            region_info = {
                "idx": i + 1,
                "thing": pred_things[i],
                "score": pred_scores[i],
                "box": pred_boxes[i],
            }
            self.annotate_infos["regions"].append(region_info)

        annotate_info_json_path = output_image_path.parent / (
            output_image_path.stem + ".json"
        )
        logger.success(f"> Saving annotated info:")
        logger.file(f"  - {annotate_info_json_path}")
        with open(annotate_info_json_path, "w") as wf:
            wf.write(json.dumps(self.annotate_infos, indent=4))

        return annotate_info_json_path


class LayoutLMv3Analyzer:
    """
    * unilm/layoutlmv3 at master · microsoft/unilm
        * https://github.com/microsoft/unilm/tree/master/layoutlmv3#document-layout-analysis-on-publaynet
    """

    def __init__(self) -> None:
        pass


def draw_regions_on_page(regions_info_json_path, output_parent_path, spacing=2):
    region_colors = {
        "text": (0, 128, 0),
        "title": (128, 0, 0),
        "list": (0, 0, 128),
        "table": (128, 128, 0),
        "figure": (0, 0, 128),
    }
    with open(regions_info_json_path, "r") as rf:
        regions_infos = json.load(rf)
    original_page_image_path = Path(regions_infos["page"]["original_image_path"])
    page_num = int(original_page_image_path.stem.split("_")[-1])
    page_image = Image.open(original_page_image_path)
    page_image_width, page_image_height = page_image.size
    regions = regions_infos["regions"]

    image_draw = ImageDraw.Draw(page_image, "RGBA")

    drawn_page_image_path = output_parent_path / original_page_image_path.name
    logger.msg(f"- Draw on Page {page_num} with {len(regions)} regions")
    logger.file(f"  - {drawn_page_image_path}")

    for region in regions:
        region_idx = region["idx"]
        region_box = region["box"]
        region_thing = region["thing"]
        region_score = region["score"]

        region_box = [
            region_box[0] - spacing,
            region_box[1] - spacing,
            region_box[2] + spacing,
            region_box[3] + spacing,
        ]

        text_font = ImageFont.truetype("times.ttf", 40)
        text_str = f"{region_idx}.{region_thing}({round(region_score)}%)"
        text_bbox = image_draw.textbbox(
            region_box[:2], text_str, font=text_font, anchor="rt"
        )
        image_draw.text(
            region_box[:2], text_str, fill="black", font=text_font, anchor="rt"
        )
        region_rect_color = region_colors[region_thing]
        image_draw.rectangle(
            region_box,
            outline=region_rect_color,
            fill=(*region_rect_color, 64),
            width=2,
        )

        image_draw.rectangle(text_bbox, fill=(*region_rect_color, 80))
    page_image.save(drawn_page_image_path)


def calc_regions_overlaps(regions):
    """
    Return: List of list of tuples. List length is num of regions.
    In each level-1 list, there is level-2 list of tuples.

    For each tuple in i-th list:
    The 1st element is the idx of overlapped region with region i, and
    the 2nd element is the overlapped area ratio of overlapped region in region i.
    """
    regions_overlaps = []
    for i in range(len(regions)):
        region_i_overlaps = []
        for j in range(len(regions)):
            region_i = regions[i]
            region_j = regions[j]
            region_i_overlaps_j, region_i_j_overlapped_area_ratio = rect_overlap(
                region_i["box"], region_j["box"], t=5
            )
            if i != j and region_i_overlaps_j:
                region_i_overlaps.append(
                    (regions[j]["idx"], region_i_j_overlapped_area_ratio)
                )
        regions_overlaps.append(region_i_overlaps)

    for i in range(len(regions)):
        region_i_overlaps = regions_overlaps[i]
        region_i = regions[i]

        if region_i_overlaps:
            region_i_overlaps_str = ", ".join(
                [f"{x[0]}({round(x[1],2)})" for x in region_i_overlaps]
            )
            region_i_overlaps_str = f"- {region_i_overlaps_str}"
            line_color = "light_red"
            overlap_region_num_str = f", overlaps with {len(region_i_overlaps)} regions"
        else:
            region_i_overlaps_str = ""
            line_color = "light_cyan"
            overlap_region_num_str = ""

        logger.store_indent()
        logger.indent(2)
        logger.line(
            colored(
                f"- {region_i['idx']}: {region_i['thing']} region ({region_i['score']})"
                + overlap_region_num_str,
                line_color,
            )
        )
        if region_i_overlaps_str:
            logger.indent(2)
            logger.line(region_i_overlaps_str)
        logger.restore_indent()

    return regions_overlaps


def remove_regions_overlaps(
    regions,
    regions_overlaps,
    overlap_area_ratio_threshold=0.9,
    ignore_score_threshold=0.1,
):
    """
    Rules of thumb:

    The higher the score of "thing", and the larger the region area:
    the more likely it is a separated region with category "thing".

    Common cases in overlapped regions:

    1. (Page 12) Text t1 is in Table/Figure t2, and t2's score is higher than t1's.
    Solution: Only keep table region t2.

    2. (Page 13) List overlapped with Text:
    Solution: Keep the region with higher score. And in later process, treat list same as text.

    3. (Page 3,8) Large False Figure overlapped with other Figures and Texts:
    Solution: If the score of the large false figure is too lower, ignore/remove it.
    And process other regions. As the other regions are also possibly detected.

    4. (Page 13) Large Text overlapped with small Texts.
    Solution: Keep the larger one, if its score is not too low.

    5. (Page 5) Table overlapped with inside-table and outside-table Texts:
    Solution: Keep the table, and the outside-table texts.

    """
    filtered_regions = []
    for i in range(len(regions)):
        region_i = regions[i]
        region_i_overlaps = regions_overlaps[i]
        keep_region_i = True
        if region_i_overlaps:
            if region_i["score"] / 100 <= ignore_score_threshold:
                # keep_region_i = False
                # regions_overlaps[i] = []
                logger.success(
                    f"Ignore region {i+1} its score {(region_i['score'])} "
                    f"is lower than {round(ignore_score_threshold*100)}"
                )
            else:
                for j in range(len(region_i_overlaps)):
                    region_j_idx, region_i_j_overlapped_area_ratio = region_i_overlaps[
                        j
                    ]
                    region_j = regions[region_j_idx - 1]
                    logger.msg(
                        f"region {i+1} ({region_i['score']}) and region {region_j_idx} ({(region_j['score'])}) "
                        f"[{round(region_i_j_overlapped_area_ratio*100)}%]"
                    )
                    if (
                        region_i_j_overlapped_area_ratio >= overlap_area_ratio_threshold
                        and region_j["score"] >= region_i["score"]
                    ):
                        # Means this region is a totally child region, ignore it.
                        logger.success(
                            f"Ignore region {i+1} as region {region_j_idx} has score {(region_j['score'])} "
                            f"[{round(region_i_j_overlapped_area_ratio*100)}%]"
                        )
                        keep_region_i = False
                        regions_overlaps[i] = []
                        break
        if keep_region_i:
            filtered_regions.append(region_i)

    """
    1. Overlaps: References: List and text
    2. Overlaps: Title and text
    Solution: Group the regions, and union them with large rects.
    """

    # print(filtered_regions)

    # Re-create the overlapped regions after removing the totally child regions
    new_overlap_regions = []
    for i in range(len(regions_overlaps)):
        region_i_overlaps = regions_overlaps[i]
        region_i = regions[i]
        if region_i_overlaps:
            new_region_i_overlaps = []
            for j in range(len(region_i_overlaps)):
                region_j_idx, region_i_j_overlapped_area_ratio = region_i_overlaps[j]
                if regions_overlaps[region_j_idx - 1]:  # region_j is not removed
                    new_region_i_overlaps.append(
                        (region_j_idx, region_i_j_overlapped_area_ratio)
                    )

            if new_region_i_overlaps:
                new_overlap_regions.append(region_i)

    if new_overlap_regions:
        new_overlap_regions_idxs = [x["idx"] for x in new_overlap_regions]
        new_overlap_regions_str = ", ".join(map(str, new_overlap_regions_idxs))
        logger.warn(
            f"{len(new_overlap_regions)} regions remains overlapped: [{new_overlap_regions_str}]"
        )

        # Re-calculate the regions overlaps
        new_regions_overlaps = calc_regions_overlaps(new_overlap_regions)
        new_overlap_regions_edges = []
        for i, new_regions_overlaps in enumerate(new_regions_overlaps):
            region_idx = new_overlap_regions_idxs[i]
            for new_region_idx, new_region_overlap_area_ratio in new_regions_overlaps:
                new_overlap_regions_edges.append((region_idx, new_region_idx))

        # print(new_regions_overlaps)
        # print(new_overlap_regions_edges)

        # Union (Combine) connected regions
        G = nx.Graph()
        G.add_nodes_from(new_overlap_regions_idxs)
        G.add_edges_from(new_overlap_regions_edges)
        connected_regions_components = list(nx.connected_components(G))
        # print(connected_regions_components)
        # print(len(connected_regions_components))

        filtered_regions = [
            region
            for region in filtered_regions
            if region["idx"] not in new_overlap_regions_idxs
        ]

        for c_idx, connected_regions_component in enumerate(
            connected_regions_components
        ):
            connected_regions_boxes = [
                regions[region_idx - 1]["box"]
                for region_idx in list(connected_regions_component)
            ]
            union_region_box = union_rects(connected_regions_boxes)
            union_region_score = 0
            union_region_thing = ""
            union_region_idx = len(regions) + c_idx + 1
            for i in new_overlap_regions_idxs:
                region_i = regions[i - 1]
                if region_i["score"] > union_region_score:
                    union_region_score = region_i["score"]
                    union_region_thing = region_i["thing"]

            union_region = {
                "idx": union_region_idx,
                "thing": union_region_thing,
                "score": union_region_score,
                "box": union_region_box,
            }
            filtered_regions.append(union_region)

    print(filtered_regions)
    return filtered_regions


if __name__ == "__main__":
    dit_layout_analyzer = DITLayoutAnalyzer(size="large")
    dit_layout_analyzer.test_run()
