from pathlib import Path
import pypandoc

md_path = (
    # Path(__file__).parents[1] / "pdfs" / "cancer_review" / "_results" / "review_v1.md"
    Path(__file__).parents[1]
    / "pdfs"
    / "cancer_review"
    / "_results"
    # / "facts" / "facts.md"
    / "review_v2.md"
)

docx_path = md_path.with_suffix("").with_suffix(".docx")

pypandoc.convert_file(md_path, "docx", format="md", outputfile=docx_path)
