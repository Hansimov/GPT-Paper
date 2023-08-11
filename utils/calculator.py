from itertools import chain
from utils.logger import logger
import numpy as np


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
        # if n is odd, before element is one more than after element
        n_before = n // 2
        n_after = (n - 1) - n_before

        if i < n_before:
            n_before = i
            n_after = (n - 1) - n_before
        elif (list_len - 1) - i < n_after:
            n_after = (list_len - 1) - i
            n_before = (n - 1) - n_after
        else:
            pass

        logger.debug(f"n_before: {n_before}, n_after: {n_after}")

        if include_i:
            neighbor_idxs = list(range(i - n_before, i + 1 + n_after))
        else:
            neighbor_idxs = list(range(i - n_before, i)) + list(
                range(i + 1, i + 1 + n_after)
            )

    neighbor_elements = [elements[idx] for idx in neighbor_idxs]
    idx_in_neighbors = neighbor_idxs.index(i)
    return neighbor_idxs, neighbor_elements, idx_in_neighbors


def weighted_sum(values, weights):
    return sum([v * w for v, w in zip(values, weights)])


def distribute_weights(weights, distribution=None, center_idx=None):
    n = len(weights)

    if center_idx == None:
        # if n is even, one more before than after for center element
        center_idx = n // 2

    n_before = center_idx
    n_after = (n - 1) - center_idx

    if distribution == "normal":
        seq = np.concatenate(
            (
                np.linspace(0, n_before, n_before + 1)[1:][::-1],
                [0],
                np.linspace(0, n_after, n_after + 1)[1:],
            )
        )
        scales = np.exp(-seq / n)
    elif distribution == "linear":
        linear_min = 0.25
        scales = np.concatenate(
            (
                np.linspace(1, linear_min, n_before + 1)[1:][::-1],
                [1],
                np.linspace(1, linear_min, n_after + 1)[1:],
            )
        )

    else:
        scales = np.ones(n)

    logger.debug(center_idx)
    logger.debug(weights)
    logger.debug(scales)
    scales = scales.reshape(1, len(weights)).flatten()
    weights = weights * scales
    weights = weights / np.sum(weights)

    return weights


def weighted_avg(values, weights):
    return np.average(values, weights=weights)


def closest_category(value, category_enums, dist_func=None, prefer_new=True):
    def abs_diff(x, y):
        return abs(x - y)

    if dist_func is None:
        dist_func = abs_diff

    distances = [dist_func(value, category) for category in category_enums]

    min_dist_idx = 0
    for i, dist in enumerate(distances):
        if prefer_new:
            if dist <= distances[min_dist_idx]:
                min_dist_idx = i
        else:
            if dist < distances[min_dist_idx]:
                min_dist_idx = i
    return category_enums[min_dist_idx]
