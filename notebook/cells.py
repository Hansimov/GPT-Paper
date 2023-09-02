import json
import nbformat
import ipynbname


def read_cells(notebook_path=None, cell_types=["markdown", "code", "raw"]):
    if not notebook_path:
        notebook_path = ipynbname.path()

    with open(notebook_path, "r", encoding="utf-8") as rf:
        nb = nbformat.read(rf, as_version=4)

    cells = [
        (i, cell) for i, cell in enumerate(nb.cells) if cell["cell_type"] in cell_types
    ]
    return cells
