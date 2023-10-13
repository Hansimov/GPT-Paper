"""
Workflow of Paper Read App:
0. Load PDF
1. PDFVisualExtractor: Extract layout in page level, and crop images and tables
2. PDFTexterizer: Mask images and tables in PDF with texts of relative paths
3. PDFNougatExtractor: Convert PDF to .mmd with nougat in prev step
4. TextChunker: Construct chunks, indexes and embeddings for texts
5. Retrieve and Re-rank, then answer with the retrieved results
"""
