from IPython.display import HTML, display
from IPython.core.magic import register_cell_magic

def set_background(color):    
    script = (
        "var cell = this.closest('.jp-CodeCell');"
        "var editor = cell.querySelector('.jp-Editor');"
        "editor.style.background='{}';"
        "this.parentNode.removeChild(this)"
    ).format(color)
    
    display(HTML(f'<img src onerror="{script}" style="display:none">'))

@register_cell_magic
def bg(color, cell):
    set_background(color)
    return eval(cell)
