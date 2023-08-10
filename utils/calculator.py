from itertools import chain


def flatten_len(nested_list):
    return len(list(chain.from_iterable(nested_list)))


def kilo_count(number, ndigits=1):
    return round(number / 1024, ndigits)


def font_flags_to_list(flags):
    def int_to_bits(number, length=5):
        return list(map(int, list(bin(number)[2:].zfill(length))))

    def bits_to_font_properties(bits):
        font_properties = ["superscripted", "italic", "serifed", "monospaced", "bold"]
        return [font_properties[i] for i, bit in enumerate(bits) if bit == 1]

    return bits_to_font_properties(int_to_bits(flags))


def each_is_different(iter1, iter2):
    # return all([i != j for i, j in zip(iter_1, iter_2)])
    return not (set(iter1) & set(iter2))


def rect_area(x0, y0, x1, y1):
    return int(abs((y1 - y0) * (x1 - x0)))


def char_per_pixel(char_num, rect_area):
    return round(char_num / rect_area, 3)


def avg_line_width(text):
    lines = text.splitlines()
    return int(len(text) / len(lines))
