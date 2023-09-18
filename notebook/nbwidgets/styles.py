from bs4 import BeautifulSoup
from cssutils import parseStyle


def apply_style(html_text, style, tag="div"):
    soup = BeautifulSoup(html_text, "html.parser")
    element = soup.find(tag)
    if "style" in element.attrs:
        style_dict = dict(parseStyle(element["style"]))
    else:
        style_dict = {}

    style_dict.update(parseStyle(style))
    element["style"] = "; ".join(
        [f"{key}: {value}" for key, value in style_dict.items()]
    )

    return str(soup)


def calc_font_color_by_background(bg_rgba, mode="greyscale"):
    # Formula to determine perceived brightness of RGB color - Stack Overflow
    #   https://stackoverflow.com/questions/596216/formula-to-determine-perceived-brightness-of-rgb-color
    luma = (
        (0.299 * bg_rgba[0] + 0.587 * bg_rgba[1] + 0.114 * bg_rgba[2])
        / 255
        * bg_rgba[-1]
    )
    if mode == "greyscale":
        if luma > 0.5:
            font_color = "black"
        else:
            font_color = "white"
    else:
        font_color = (
            f"rgba{tuple(list(map(lambda x: 255 - x, list(bg_rgba)[:3])) + [1])}"
        )
    return font_color


def get_code_highlight_css(class_name="highlight", theme="monokai"):
    # https://github.com/richleland/pygments-css/blob/master
    # ANCHOR[id=code-highlight-css]
    theme_css_dict = {
        "vs": [
            ".hll { background-color: #ffffcc }",
            " { background: #ffffff; }",
            ".c { color: #008000 } /* Comment */",
            ".err { border: 1px solid #FF0000 } /* Error */",
            ".k { color: #0000ff } /* Keyword */",
            ".ch { color: #008000 } /* Comment.Hashbang */",
            ".cm { color: #008000 } /* Comment.Multiline */",
            ".cp { color: #0000ff } /* Comment.Preproc */",
            ".cpf { color: #008000 } /* Comment.PreprocFile */",
            ".c1 { color: #008000 } /* Comment.Single */",
            ".cs { color: #008000 } /* Comment.Special */",
            ".ge { font-style: italic } /* Generic.Emph */",
            ".gh { font-weight: bold } /* Generic.Heading */",
            ".gp { font-weight: bold } /* Generic.Prompt */",
            ".gs { font-weight: bold } /* Generic.Strong */",
            ".gu { font-weight: bold } /* Generic.Subheading */",
            ".kc { color: #0000ff } /* Keyword.Constant */",
            ".kd { color: #0000ff } /* Keyword.Declaration */",
            ".kn { color: #0000ff } /* Keyword.Namespace */",
            ".kp { color: #0000ff } /* Keyword.Pseudo */",
            ".kr { color: #0000ff } /* Keyword.Reserved */",
            ".kt { color: #2b91af } /* Keyword.Type */",
            ".s { color: #a31515 } /* Literal.String */",
            ".nc { color: #2b91af } /* Name.Class */",
            ".ow { color: #0000ff } /* Operator.Word */",
            ".sa { color: #a31515 } /* Literal.String.Affix */",
            ".sb { color: #a31515 } /* Literal.String.Backtick */",
            ".sc { color: #a31515 } /* Literal.String.Char */",
            ".dl { color: #a31515 } /* Literal.String.Delimiter */",
            ".sd { color: #a31515 } /* Literal.String.Doc */",
            ".s2 { color: #a31515 } /* Literal.String.Double */",
            ".se { color: #a31515 } /* Literal.String.Escape */",
            ".sh { color: #a31515 } /* Literal.String.Heredoc */",
            ".si { color: #a31515 } /* Literal.String.Interpol */",
            ".sx { color: #a31515 } /* Literal.String.Other */",
            ".sr { color: #a31515 } /* Literal.String.Regex */",
            ".s1 { color: #a31515 } /* Literal.String.Single */",
            ".ss { color: #a31515 } /* Literal.String.Symbol */",
        ],
        "monokai": [
            ".hll { background-color: #49483e }",
            " { background: #272822; color: #f8f8f2 }",
            ".c { color: #75715e } /* Comment */",
            ".err { color: #960050; background-color: #1e0010 } /* Error */",
            ".k { color: #66d9ef } /* Keyword */",
            ".l { color: #ae81ff } /* Literal */",
            ".n { color: #f8f8f2 } /* Name */",
            ".o { color: #f92672 } /* Operator */",
            ".p { color: #f8f8f2 } /* Punctuation */",
            ".ch { color: #75715e } /* Comment.Hashbang */",
            ".cm { color: #75715e } /* Comment.Multiline */",
            ".cp { color: #75715e } /* Comment.Preproc */",
            ".cpf { color: #75715e } /* Comment.PreprocFile */",
            ".c1 { color: #75715e } /* Comment.Single */",
            ".cs { color: #75715e } /* Comment.Special */",
            ".gd { color: #f92672 } /* Generic.Deleted */",
            ".ge { font-style: italic } /* Generic.Emph */",
            ".gi { color: #a6e22e } /* Generic.Inserted */",
            ".gs { font-weight: bold } /* Generic.Strong */",
            ".gu { color: #75715e } /* Generic.Subheading */",
            ".kc { color: #66d9ef } /* Keyword.Constant */",
            ".kd { color: #66d9ef } /* Keyword.Declaration */",
            ".kn { color: #f92672 } /* Keyword.Namespace */",
            ".kp { color: #66d9ef } /* Keyword.Pseudo */",
            ".kr { color: #66d9ef } /* Keyword.Reserved */",
            ".kt { color: #66d9ef } /* Keyword.Type */",
            ".ld { color: #e6db74 } /* Literal.Date */",
            ".m { color: #ae81ff } /* Literal.Number */",
            ".s { color: #e6db74 } /* Literal.String */",
            ".na { color: #a6e22e } /* Name.Attribute */",
            ".nb { color: #f8f8f2 } /* Name.Builtin */",
            ".nc { color: #a6e22e } /* Name.Class */",
            ".no { color: #66d9ef } /* Name.Constant */",
            ".nd { color: #a6e22e } /* Name.Decorator */",
            ".ni { color: #f8f8f2 } /* Name.Entity */",
            ".ne { color: #a6e22e } /* Name.Exception */",
            ".nf { color: #a6e22e } /* Name.Function */",
            ".nl { color: #f8f8f2 } /* Name.Label */",
            ".nn { color: #f8f8f2 } /* Name.Namespace */",
            ".nx { color: #a6e22e } /* Name.Other */",
            ".py { color: #f8f8f2 } /* Name.Property */",
            ".nt { color: #f92672 } /* Name.Tag */",
            ".nv { color: #f8f8f2 } /* Name.Variable */",
            ".ow { color: #f92672 } /* Operator.Word */",
            ".w { color: #f8f8f2 } /* Text.Whitespace */",
            ".mb { color: #ae81ff } /* Literal.Number.Bin */",
            ".mf { color: #ae81ff } /* Literal.Number.Float */",
            ".mh { color: #ae81ff } /* Literal.Number.Hex */",
            ".mi { color: #ae81ff } /* Literal.Number.Integer */",
            ".mo { color: #ae81ff } /* Literal.Number.Oct */",
            ".sa { color: #e6db74 } /* Literal.String.Affix */",
            ".sb { color: #e6db74 } /* Literal.String.Backtick */",
            ".sc { color: #e6db74 } /* Literal.String.Char */",
            ".dl { color: #e6db74 } /* Literal.String.Delimiter */",
            ".sd { color: #e6db74 } /* Literal.String.Doc */",
            ".s2 { color: #e6db74 } /* Literal.String.Double */",
            ".se { color: #ae81ff } /* Literal.String.Escape */",
            ".sh { color: #e6db74 } /* Literal.String.Heredoc */",
            ".si { color: #e6db74 } /* Literal.String.Interpol */",
            ".sx { color: #e6db74 } /* Literal.String.Other */",
            ".sr { color: #e6db74 } /* Literal.String.Regex */",
            ".s1 { color: #e6db74 } /* Literal.String.Single */",
            ".ss { color: #e6db74 } /* Literal.String.Symbol */",
            ".bp { color: #f8f8f2 } /* Name.Builtin.Pseudo */",
            ".fm { color: #a6e22e } /* Name.Function.Magic */",
            ".vc { color: #f8f8f2 } /* Name.Variable.Class */",
            ".vg { color: #f8f8f2 } /* Name.Variable.Global */",
            ".vi { color: #f8f8f2 } /* Name.Variable.Instance */",
            ".vm { color: #f8f8f2 } /* Name.Variable.Magic */",
            ".il { color: #ae81ff } /* Literal.Number.Integer.Long */",
        ],
    }

    class_name = class_name.strip(".")
    code_highlight_css_template = theme_css_dict[theme]
    code_highlight_css = [
        f".{class_name} " + line for line in code_highlight_css_template
    ]
    code_highlight_css_str = "\n".join(code_highlight_css)
    return code_highlight_css_str
