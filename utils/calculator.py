from itertools import chain


def flatten(nested_list):
    return list(chain.from_iterable(nested_list))


def flatten_len(nested_list):
    return len(flatten(nested_list))


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


def rect_center(x0, y0, x1, y1):
    return (x0 + x1) // 2, (y0 + y1) // 2


def char_per_pixel(char_num, rect_area):
    return round(char_num / rect_area, 3)


def avg_line_width(text):
    lines = text.splitlines()
    return int(len(text) / len(lines))


def get_neighbors(i, elements, n=5, include_i=True):
    list_len = len(elements)

    if list_len <= n + 1:
        if include_i:
            neighbor_idxs = list(range(0, list_len))
        else:
            neighbor_idxs = list(range(0, i)) + list(range(i + 1, list_len))
    else:
        n_after = n // 2
        # if n is odd, before element is one more than after element
        n_before = n - n_after

        if n_before > i:
            n_before = i
            n_after = n - n_before
        elif n_after > (list_len - 1) - i:
            n_after = (list_len - 1) - i
            n_before = n - n_after
        else:
            pass

    if include_i:
        neighbor_idxs = list(range(i - n_before, i + 1 + n_after))
    else:
        neighbor_idxs = list(range(i - n_before, i)) + list(
            range(i + 1, i + 1 + n_after)
        )
    neighbor_elements = [elements[idx] for idx in neighbor_idxs]
    return neighbor_idxs, neighbor_elements


def weighted_sum(values, weights):
    return sum([v * w for v, w in zip(values, weights)])
