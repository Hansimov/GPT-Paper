import nbformat
import ipynbname
from IPython.core.magic import (
    register_line_magic,
    register_cell_magic,
    register_line_cell_magic,
)


def get_notebook_cells(notebook_path=None, cell_types=["markdown", "code", "raw"]):
    if not notebook_path:
        notebook_path = ipynbname.path()

    with open(notebook_path, "r", encoding="utf-8") as rf:
        nb = nbformat.read(rf, as_version=4)

    cells = [cell for i, cell in enumerate(nb.cells) if cell["cell_type"] in cell_types]
    return cells


def get_cell_id():
    cell_id = get_ipython().get_parent()["metadata"]["cellId"]
    return cell_id


def get_cell_index():
    cell_id = get_cell_id()
    cells = get_notebook_cells()
    for idx, cell in enumerate(cells):
        if cell["id"] == cell_id:
            return idx


def get_above_cell_content():
    cell_idx = get_cell_index()
    if cell_idx == 0:
        return None
    cells = get_notebook_cells()
    above_cell = cells[cell_idx - 1]
    above_cell_content = above_cell["source"]

    return above_cell_content
