from pathlib import Path


class PDFPather:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.pdf_parent = self.pdf_path.parent
        self.pdf_filename = self.pdf_path.name
        self.assets_path = self.pdf_parent / Path(self.pdf_filename).stem

        # LINK documents/pdf_visual_extractor.py#pdf-visual-extractor-paths
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

        # LINK documents/pdf_nougat_extractor.py#pdf-nougat-extractor-paths
