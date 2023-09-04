import fitz
import json
import os
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image
from sentence_transformers.util import semantic_search
from termcolor import colored
from tqdm import tqdm

from utils.calculator import get_int_digits
from utils.envs import init_os_envs
from utils.file import rmtree_and_mkdir
from utils.layout_analyzer import (
    DITLayoutAnalyzer,
    RegionsOrderer,
    calc_regions_overlaps,
    remove_regions_overlaps,
    draw_regions_on_page,
)
from utils.logger import logger, add_fillers, Runtimer
from utils.tokenizer import (
    WordTokenizer,
    SentenceTokenizer,
    BiEncoderX,
    CrossEncoderX,
    remove_newline_seps_from_text,
    df_column_to_torch_tensor,
)
from documents.text_extractor import TextExtractor

init_os_envs(cuda_device=0, huggingface=True)


class PDFVisualExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.pdf_parent = self.pdf_path.parent
        self.pdf_filename = self.pdf_path.name
        self.pdf_doc = fitz.open(self.pdf_path)
        self.init_paths()

    def init_paths(self):
        self.assets_path = self.pdf_parent / Path(self.pdf_filename).stem

        self.page_images_path = self.assets_path / "pages"
        self.annotated_page_images_path = self.assets_path / "pages_annotated"
        self.cropped_annotated_page_images_path = self.assets_path / "crops_annotated"
        self.no_overlap_page_images_path = self.assets_path / "pages_no_overlap"
        self.cropped_no_overlap_page_images_path = self.assets_path / "crops_no_overlap"
        self.ordered_page_images_path = self.assets_path / "pages_ordered"
        self.cropped_ordered_page_images_path = self.assets_path / "crops_ordered"
        self.page_texts_path = self.assets_path / "texts"
        self.doc_texts_path = self.page_texts_path / "doc.json"
        self.doc_embeddings_path = self.page_texts_path / "embeddings.pkl"
        self.queries_results_path = self.assets_path / "queries"

    def dump_pdf_to_page_images(self, dpi=300, overwrite=False, quiet=True):
        logger.enter_quiet(quiet)

        rmtree_and_mkdir(self.page_images_path, overwrite=overwrite)
        # transform_matrix = fitz.Matrix(dpi / 72, dpi / 72)
        logger.note(f"> Dumping PDF to image pages [dpi={dpi}]")
        logger.file(f"- {self.page_images_path}")
        pdf_idx_digits = get_int_digits(len(self.pdf_doc))
        logger.store_indent()
        logger.indent(2)
        for page_idx, page in enumerate(tqdm(self.pdf_doc)):
            logger.back(f"- Page {page_idx+1:>{pdf_idx_digits}}")
            image_path = (
                self.page_images_path / f"page_{page_idx+1:0>{pdf_idx_digits}}.png"
            )
            if not overwrite and image_path.exists():
                continue
            else:
                pix = page.get_pixmap(dpi=dpi)
                pix.save(image_path)
        logger.restore_indent()
        logger.exit_quiet(quiet)

    def annotate_page_images(
        self, layout_analyzer=None, overwrite=False, quiet=True, draw_on_page=False
    ):
        rmtree_and_mkdir(self.annotated_page_images_path, overwrite=overwrite)
        logger.enter_quiet(quiet)
        logger.store_indent()
        logger.note(f"> Annotating page images")
        # logger.file(f"  * {self.annotated_page_images_path}")
        logger.indent(2)

        page_image_paths = sorted(
            [
                self.page_images_path / p
                for p in os.listdir(self.page_images_path)
                if Path(p).suffix.lower() in [".jpg", ".png", "jpeg"]
                and not Path(p).stem.endswith("_annotated")
            ],
            key=lambda x: int(x.stem.split("_")[-1]),
        )

        if not layout_analyzer:
            layout_analyzer = DITLayoutAnalyzer(size="large")

        for page_image_path in tqdm(page_image_paths):
            output_image_path = self.annotated_page_images_path / page_image_path.name
            annotate_info_json_path = self.annotated_page_images_path / (
                page_image_path.stem + ".json"
            )
            if not overwrite and (
                (draw_on_page and output_image_path.exists())
                or (not draw_on_page and annotate_info_json_path.exists())
            ):
                continue

            if not layout_analyzer.is_setup_model:
                layout_analyzer.setup_model()

            logger.file(f"- {page_image_path.name}",indent=2)
            logger.store_indent()
            logger.indent(2)
            pred_output = layout_analyzer.annotate_image(
                annotate_info_json_path=annotate_info_json_path,
                input_image_path=page_image_path,
                output_image_path=output_image_path,
                quiet=quiet,
            )
            if draw_on_page:
                draw_regions_on_page(
                    annotate_info_json_path,
                    output_parent_path=self.annotated_page_images_path,
                )
            logger.restore_indent()
        logger.restore_indent()
        logger.exit_quiet(quiet)

    def crop_page_image(
        self,
        cropped_page_images_path,
        page_info_json_path,
        padding=2,
        show_score=True,
        overwrite=False,
        quiet=True,
        add_leading_zero_to_idx=True,
        add_crop_image_path_to_page_info_json=True,
    ):
        logger.enter_quiet(quiet)
        with open(page_info_json_path, "r") as rf:
            page_infos = json.load(rf)
        page_image_path = Path(page_infos["page"]["original_image_path"])
        page_num = page_image_path.stem.split("_")[-1]
        page_image = Image.open(page_image_path)
        page_image_width, page_image_height = page_image.size
        regions = page_infos["regions"]

        region_images_page_path = cropped_page_images_path / f"page_{page_num}"
        region_images_page_path.mkdir(parents=True, exist_ok=True)

        logger.mesg(f"- Crop Page {page_num} to {len(regions)} regions")

        region_idx_max_num = max([int(region["idx"]) for region in regions], default=0)
        region_idx_digits = get_int_digits(region_idx_max_num)
        for i, region in enumerate(regions):
            region_idx = region["idx"]
            region_box = region["box"]
            region_thing = region["thing"]
            region_score = region["score"]
            region_box = [round(x) for x in region_box]
            crop_region_box = [
                max(0, region_box[0] - padding),
                max(0, region_box[1] - padding),
                min(page_image_width, region_box[2] + padding),
                min(page_image_height, region_box[3] + padding),
            ]

            if show_score:
                region_score_str = f"_{region_score}"
            else:
                region_score_str = ""

            if add_leading_zero_to_idx:
                region_idx_str = f"_{region_idx:0>{region_idx_digits}}"
            else:
                region_idx_str = f"_{region_idx}"

            region_image_path = region_images_page_path / (
                f"region{region_idx_str}_{region_thing}{region_score_str}"
                + page_image_path.suffix
            )

            if add_crop_image_path_to_page_info_json:
                page_infos["regions"][i]["crop_image_path"] = str(region_image_path)
                with open(page_info_json_path, "w") as wf:
                    json.dump(page_infos, wf, indent=4)

            if not overwrite and region_image_path.exists():
                continue
            else:
                region_image = page_image.crop(crop_region_box)
                region_image.save(region_image_path)

        logger.exit_quiet(quiet)

    def get_page_info_json_paths(self, page_type):
        page_type_images_paths = {
            "annotated": self.annotated_page_images_path,
            "no-overlap": self.no_overlap_page_images_path,
            "ordered": self.ordered_page_images_path,
            "texts": self.page_texts_path,
        }
        page_images_path = page_type_images_paths[page_type]
        page_info_json_paths = sorted(
            [
                page_images_path / p
                for p in os.listdir(page_images_path)
                if Path(p).name.startswith("page") and Path(p).suffix.lower() == ".json"
            ],
            key=lambda x: int(x.stem.split("_")[-1]),
        )
        return page_info_json_paths

    def crop_page_images(self, page_type, overwrite=False, quiet=True):
        logger.enter_quiet(quiet)
        page_type_cropped_images_paths = {
            "annotated": self.cropped_annotated_page_images_path,
            "no-overlap": self.cropped_no_overlap_page_images_path,
            "ordered": self.cropped_ordered_page_images_path,
        }
        cropped_page_images_path = page_type_cropped_images_paths[page_type]

        rmtree_and_mkdir(cropped_page_images_path)

        page_info_json_paths = self.get_page_info_json_paths(page_type)

        logger.note(f"> Croping {page_type} page images")
        logger.store_indent()
        logger.indent(2)
        for page_info_json_path in tqdm(page_info_json_paths):
            self.crop_page_image(
                cropped_page_images_path,
                page_info_json_path,
                show_score=False,
                overwrite=overwrite,
            )
        logger.restore_indent()
        logger.exit_quiet(quiet)

    def remove_overlapped_layout_regions_from_page(
        self,
        annotate_info_json_path,
        draw_on_page=False,
        overwrite=False,
        quiet=True,
    ):
        logger.enter_quiet(quiet)
        with open(annotate_info_json_path, "r") as rf:
            annotate_infos = json.load(rf)
        regions = annotate_infos["regions"]
        no_overlap_regions_info_json_path = str(
            self.no_overlap_page_images_path
            / (Path(annotate_infos["page"]["current_image_path"]).stem + ".json")
        )

        if (
            not overwrite
            and Path(no_overlap_regions_info_json_path).exists()
            and not draw_on_page
        ):
            logger.exit_quiet(quiet)
            return

        no_overlap_regions_infos = annotate_infos.copy()
        no_overlap_regions_infos["page"]["original_image_path"] = annotate_infos[
            "page"
        ]["original_image_path"]

        no_overlap_regions_infos["page"]["current_image_path"] = str(
            self.no_overlap_page_images_path
            / Path(annotate_infos["page"]["original_image_path"]).name
        )
        no_overlap_regions_infos["page"]["regions_num"] = len(
            no_overlap_regions_infos["regions"]
        )

        logger.store_indent()
        logger.indent(2)
        logger.note(f"- Detect overlaps of {len(annotate_infos['regions'])} regions")
        regions_overlaps = calc_regions_overlaps(regions)

        logger.note(f"- Filter overlaps of {len(annotate_infos['regions'])} regions")

        logger.indent(2)

        no_overlap_regions_infos["regions"] = remove_regions_overlaps(
            regions, regions_overlaps
        )
        logger.indent(-2)

        logger.note("> Dump no-overlap regions info json")
        logger.back(f"  - {no_overlap_regions_info_json_path}")
        with open(no_overlap_regions_info_json_path, "w") as wf:
            json.dump(no_overlap_regions_infos, wf, indent=4)
        logger.indent(2)
        if draw_on_page:
            draw_regions_on_page(
                no_overlap_regions_info_json_path, self.no_overlap_page_images_path
            )
        logger.restore_indent()
        logger.exit_quiet()

    def remove_overlapped_layout_regions_from_pages(self, overwrite=False, quiet=True):
        logger.enter_quiet(quiet)
        rmtree_and_mkdir(self.no_overlap_page_images_path, overwrite=overwrite)
        annotate_json_paths = self.get_page_info_json_paths("annotated")
        for page_idx, annotate_json_path in enumerate(annotate_json_paths):
            logger.store_indent()
            logger.note(f"- Remove overlaps in Page {page_idx+1}")
            self.remove_overlapped_layout_regions_from_page(
                annotate_json_path,
                draw_on_page=False,
                quiet=quiet,
                overwrite=overwrite,
            )
            logger.restore_indent()
        logger.exit_quiet(quiet)

    def order_pages_regions(self, overwrite=False, quiet=True, draw_on_page=True):
        page_info_json_paths = self.get_page_info_json_paths("no-overlap")
        rmtree_and_mkdir(self.ordered_page_images_path, overwrite=overwrite)
        logger.enter_quiet(quiet)
        logger.note(f"- Sort regions")
        logger.store_indent()
        page_idx_digits = get_int_digits(len(page_info_json_paths))
        for page_idx, page_info_json_path in enumerate(page_info_json_paths):
            with open(page_info_json_path, "r") as rf:
                page_infos = json.load(rf)
            ordered_page_infos = page_infos.copy()
            regions = page_infos["regions"]
            logger.mesg(f"- Sort regions in Page {page_idx+1}")
            ordered_page_info_json_path = (
                self.ordered_page_images_path
                / f"page_{page_idx+1:0>{page_idx_digits}}.json"
            )
            if (
                not overwrite
                and ordered_page_info_json_path.exists()
                and not draw_on_page
            ):
                continue

            regions_orderer = RegionsOrderer()
            ordered_regions = regions_orderer.sort_regions_by_reading_order(regions)

            ordered_page_infos["regions"] = ordered_regions
            ordered_page_infos["page"]["current_image_path"] = str(
                self.ordered_page_images_path
                / Path(page_infos["page"]["original_image_path"]).name
            )
            ordered_page_infos["page"]["regions_num"] = len(ordered_regions)
            ordered_page_infos["page"]["page_idx"] = page_idx + 1

            logger.store_indent()
            logger.indent(2)
            logger.success(f"- Dump ordered regions info")
            logger.back(f"- {ordered_page_info_json_path}")
            with open(ordered_page_info_json_path, "w") as wf:
                json.dump(ordered_page_infos, wf, indent=4)

            if draw_on_page:
                draw_regions_on_page(
                    ordered_page_info_json_path,
                    self.ordered_page_images_path,
                    overwrite=overwrite,
                )
            logger.restore_indent()
        logger.restore_indent()
        logger.exit_quiet(quiet)

    def extract_text_from_page(self, page_info_json_path, overwrite=False, quiet=True):
        logger.enter_quiet(quiet)
        page_texts_infos_path = self.page_texts_path / page_info_json_path.name
        if not overwrite and page_texts_infos_path.exists():
            logger.exit_quiet(quiet)
            return

        with open(page_info_json_path, "r") as rf:
            page_infos = json.load(rf)
        page_texts_infos = page_infos.copy()
        regions = page_infos["regions"]
        logger.store_indent()
        logger.indent(2)
        for i, region in enumerate(regions):
            if region["thing"] in ["text", "title", "list"]:
                region_image_path = Path(region["crop_image_path"])
                region_text = self.text_extractor.extract_from_image(region_image_path)
                logger.line(f"- Extract text from {region['thing']} region {i+1}:")
                logger.indent(2)
                logger.success(f"{region_text}")
                logger.indent(-2)
                page_texts_infos["regions"][i]["text"] = region_text.replace("\f", "")
            else:
                logger.line(f"- Skip {region['thing']} region {i+1}")

        with open(page_texts_infos_path, "w", encoding="utf-8") as wf:
            json.dump(page_texts_infos, wf, indent=4, ensure_ascii=False)
        logger.restore_indent()
        logger.exit_quiet(quiet)

    def extract_texts_from_pages(self, overwrite=False, quiet=True):
        rmtree_and_mkdir(self.page_texts_path, overwrite=overwrite)
        logger.enter_quiet(quiet)
        self.text_extractor = TextExtractor()
        page_info_json_paths = self.get_page_info_json_paths("ordered")
        logger.note(f"> Extracting texts from {len(page_info_json_paths)} pages")
        for page_idx, page_info_json_path in enumerate(page_info_json_paths):
            logger.store_indent()
            logger.note(f"- Extract Page {page_idx+1}")
            self.extract_text_from_page(page_info_json_path, overwrite=overwrite)
            logger.restore_indent()
        logger.exit_quiet(quiet)

    def combine_page_texts_to_doc(self, overwrite=False, quiet=True):
        logger.enter_quiet(quiet)
        if not overwrite and self.doc_texts_path.exists():
            logger.exit_quiet(quiet)
            return

        page_texts_info_json_paths = self.get_page_info_json_paths("texts")
        doc_text_infos = {
            "pdf_filename": self.pdf_filename,
            "pdf_fullpath": str(self.pdf_path),
            "pages_num": len(page_texts_info_json_paths),
            "pages": [],
        }
        for page_idx, page_texts_info_json_path in enumerate(
            page_texts_info_json_paths
        ):
            with open(page_texts_info_json_path, "r", encoding="utf-8") as rf:
                page_texts_infos = json.load(rf)
                doc_text_infos["pages"].append(page_texts_infos)

        doc_text_infos["pages"] = sorted(
            doc_text_infos["pages"], key=lambda x: int(x["page"]["page_idx"])
        )

        logger.success("> Dump texts infos to doc")
        logger.store_indent()
        logger.indent(2)
        logger.file(f"- {self.doc_texts_path}")
        logger.restore_indent()

        with open(self.doc_texts_path, "w", encoding="utf-8") as wf:
            json.dump(doc_text_infos, wf, indent=4, ensure_ascii=False)
        logger.exit_quiet(quiet)

    def doc_texts_to_embeddings(self, bi_encoder=None, overwrite=False, quiet=True):
        logger.enter_quiet(quiet)
        if not overwrite and self.doc_embeddings_path.exists():
            logger.exit_quiet(quiet)
            return

        if not bi_encoder:
            bi_encoder = BiEncoderX()
        if not bi_encoder.is_load_model:
            bi_encoder.load_model()

        with open(self.doc_texts_path, "r", encoding="utf-8") as rf:
            doc_texts_infos = json.load(rf)

        page_region_embeddings_list = []
        for page_idx, page_infos in enumerate(doc_texts_infos["pages"]):
            region_text_chunk = ""
            previous_title = ""
            for region_idx, region_infos in enumerate(page_infos["regions"]):
                if region_infos["thing"] in ["text", "title", "list"]:
                    region_text = region_infos["text"]
                    region_thing = region_infos["thing"]
                    region_text_chunk = region_text
                    if region_thing in ["title"]:
                        region_text_chunk += " - "
                        previous_title = region_text
                        # FIXME: if last region is title, this would be droppred
                        continue

                    chunk_embedding = bi_encoder.calc_embedding(region_text_chunk)
                    region_embeddings_dict = {
                        "page_idx": page_idx + 1,
                        "region_idx": region_idx + 1,
                        "previous_title": previous_title,
                        "thing": region_thing,
                        "sentence_idx": -1,
                        "text": remove_newline_seps_from_text(region_text_chunk),
                        "level": "region",
                        "embedding": chunk_embedding,
                    }

                    page_region_embeddings_list.append(region_embeddings_dict)

                    sentence_tokenizer = SentenceTokenizer()
                    chunk_sentences = sentence_tokenizer.text_to_sentences(
                        region_text_chunk
                    )
                    region_text_chunk = ""

                    continue
                    for sentence_idx, sentence in enumerate(chunk_sentences):
                        sentence_embedding = bi_encoder.calc_embedding(
                            sentence, normalize_embeddings=True
                        )
                        sentence_embeddings_dict = {
                            "page_idx": page_idx + 1,
                            "region_idx": region_idx + 1,
                            "thing": region_infos["thing"],
                            "sentence_idx": sentence_idx + 1,
                            "text": sentence,
                            "level": "sentence",
                            "embedding": sentence_embedding,
                        }
                        page_region_embeddings_list.append(sentence_embeddings_dict)
        embeddings_df = pd.DataFrame.from_dict(page_region_embeddings_list)
        logger.line(embeddings_df)
        logger.success("> Dump embeddings to pickle")
        logger.file(f"- {self.doc_embeddings_path}")
        embeddings_df.to_pickle(self.doc_embeddings_path)
        logger.exit_quiet(quiet)

    def query_region_texts(self, query):
        # query_prefix = "Represent this sentence for searching relevant passages:"
        # query_body = f"what is the title of this paper?"
        # query = f"{query_prefix}{query_body}"
        # query = f"Tree of Thoughts vs Graph of Thoughts"
        # query = f"figure captions of paper"
        # query = "References with names, publishments and years"
        # query = "Explain Graph of Thoughts"
        # query = "Architecture of GoT (Graph of Thoughts)"
        # query = "How GoT (Graph of Thoughts) outperforms other prompt techniques"
        # query = "summarize this paper"

        df = pd.read_pickle(self.doc_embeddings_path)
        doc_embeddings_tensors = df_column_to_torch_tensor(df["embedding"])
        df_doc_texts = df["text"].values.tolist()
        df_page_idxs = df["page_idx"].values.tolist()
        df_region_idxs = df["region_idx"].values.tolist()
        levels = df["level"].values.tolist()

        bi_encoder = BiEncoderX()
        query_embedding_tensor = bi_encoder.model.encode(query, convert_to_tensor=True)

        top_k = min(100, len(df_doc_texts))
        top_results = semantic_search(
            query_embeddings=query_embedding_tensor,
            corpus_embeddings=doc_embeddings_tensors,
            top_k=top_k,
        )[0]
        # logger.line(top_results)

        query_log = f"Query: {colored(query,'light_cyan')}"
        statistics_str = f"Top 10 most related chunks in {len(df_doc_texts)}:"
        logger.note(query_log)
        logger.line(statistics_str)

        logger.store_indent()
        logger.indent(2)
        for item_idx, item in enumerate(top_results[:10]):
            score = item["score"]
            chunk_idx = item["corpus_id"]
            page_idx = df_page_idxs[chunk_idx]
            region_idx = df_region_idxs[chunk_idx]
            logger.line(
                f"{item_idx+1}: ({score:.4f}) [Page {page_idx}, Region {region_idx}]\n"
                + f"{colored(df_doc_texts[chunk_idx],'light_green')}"
            )
        logger.restore_indent()

        # Re-ranking
        cross_encoder = CrossEncoderX().model
        cross_inp = [
            [query, df_doc_texts[top_result["corpus_id"]]] for top_result in top_results
        ]
        cross_scores = cross_encoder.predict(cross_inp)
        for idx in range(len(cross_scores)):
            top_results[idx]["cross_score"] = cross_scores[idx]
        top_results = sorted(top_results, key=lambda x: x["cross_score"], reverse=True)

        sentence_tokenizer = SentenceTokenizer()
        logger.note(query_log)
        logger.line(statistics_str)

        for item_idx, item in enumerate(top_results[:10]):
            score = item["cross_score"]
            chunk_idx = item["corpus_id"]
            page_idx = df_page_idxs[chunk_idx]
            region_idx = df_region_idxs[chunk_idx]
            chunk_level = levels[chunk_idx]
            chunk_text = df_doc_texts[chunk_idx]
            sentences = sentence_tokenizer.text_to_sentences(chunk_text)
            sentences_str = "\n".join(sentences)
            logger.store_indent()
            logger.indent(2)
            logger.line(
                f"{item_idx+1}: ({score:.4f}) [Page {page_idx}, Region {region_idx}, Level {chunk_level}]"
            )
            logger.indent(2)
            logger.success(sentences_str)
            logger.restore_indent()

        # Dump to query results page json
        query_results_page_region_idxs = defaultdict(list)
        for item_idx, item in enumerate(top_results[:10]):
            chunk_idx = item["corpus_id"]
            page_idx = df_page_idxs[chunk_idx]
            region_idx = df_region_idxs[chunk_idx]
            rank = item_idx + 1
            query_results_page_region_idxs[page_idx].append((region_idx, rank))
        query_results_page_region_idxs = {
            k: sorted(v, key=lambda x: x[0])
            for k, v in sorted(query_results_page_region_idxs.items())
        }
        query_results_path = self.queries_results_path / f"{query[:100]}"
        rmtree_and_mkdir(query_results_path)
        page_idx_digits = get_int_digits(len(self.pdf_doc))
        for page_idx, region_idxs_and_ranks in query_results_page_region_idxs.items():
            page_info_json_name = f"page_{page_idx:0>{page_idx_digits}}.json"
            query_results_page_info_json_path = query_results_path / page_info_json_name
            ordered_page_info_path = self.ordered_page_images_path / page_info_json_name
            with open(ordered_page_info_path, "r") as rf:
                page_infos = json.load(rf)

            query_results_page_infos = page_infos.copy()
            query_results_page_infos["page"]["current_image_path"] = str(
                query_results_path
                / Path(page_infos["page"]["original_image_path"]).name
            )
            query_results_page_infos["page"]["regions_num"] = len(region_idxs_and_ranks)
            query_results_page_infos["regions"] = []
            for item_idx, region_idx_and_rank in enumerate(region_idxs_and_ranks):
                region_idx, rank = region_idx_and_rank
                query_results_page_infos["regions"].append(
                    page_infos["regions"][region_idx - 1]
                )
                query_results_page_infos["regions"][item_idx]["score"] = rank
            logger.store_indent()
            logger.indent(2)
            logger.success("> Dump query results page info json")
            logger.file(f"- {query_results_page_info_json_path}")
            with open(query_results_page_info_json_path, "w") as wf:
                json.dump(query_results_page_infos, wf, indent=4)
            draw_regions_on_page(
                query_results_page_info_json_path,
                query_results_path,
                show_region_idx=False,
                score_use_percent=False,
            )
            logger.restore_indent()

    def run(self):
        # self.dump_pdf_to_page_images()
        # self.annotate_page_images()
        # self.remove_overlapped_layout_regions_from_pages()
        # self.order_pages_regions()
        # self.crop_page_images("ordered")
        # self.extract_texts_from_pages()
        # self.combine_page_texts_to_doc()
        self.doc_texts_to_embeddings()
        # self.query_region_texts()


if __name__ == "__main__":
    with Runtimer():
        pdf_parent = Path(__file__).parents[1] / "pdfs" / "cancer_review"
        pdf_filename = "Exploring pathological signatures for predicting the recurrence of early-stage hepatocellular carcinoma based on deep learning.pdf"
        # pdf_filename = "Deep learning predicts postsurgical recurrence of hepatocellular carcinoma from digital histopathologic images.pdf"
        # pdf_filename = "HEP 2020 Predicting survival after hepatocellular carcinoma resection using.pdf"
        # pdf_filename = "Nature Cancer 2020 Pan-cancer computational histopathology reveals.pdf"
        # pdf_filename = "Deep learning for evaluation of microvascular invasion in hepatocellular carcinoma from tumor areas of histology images.pdf"
        # pdf_filename = "2308.09687 - Graph of Thoughts.pdf"
        pdf_path = pdf_parent / pdf_filename
        pdf_visual_extractor = PDFVisualExtractor(pdf_path)
        pdf_visual_extractor.run()
