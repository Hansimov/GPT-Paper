def calc_font_color_by_backround(bg_rgba, mode="greyscale"):
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
