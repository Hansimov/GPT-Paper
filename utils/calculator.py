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
    return round(abs((y1 - y0) * (x1 - x0)))


def rect_center(x0, y0, x1, y1):
    return (x0 + x1) // 2, (y0 + y1) // 2


def rect_overlap(rect1, rect2, t=10):
    """
    `t` is the shrunk padding of the rect.
    
    The larger the `t`, the more strict the condition.
    
    When `dpi=300`, recommend to set `t=10`.
    """
    l1, t1, r1, b1 = rect1
    l2, t2, r2, b2 = rect2
    l1, l2, t1, t2 = list(
        map(lambda x, m: min(x + t, m), (l1, l2, t1, t2), (r1, r2, b1, b2))
    )
    r1, r2, b1, b2 = list(
        map(lambda x, m: max(x - t, m), (r1, r2, b1, b2), (l1, l2, t1, t2))
    )

    horizontal_intersected = ((l1 - r2) * (r1 - l2)) < 0
    vertical_intersected = ((t1 - b2) * (b1 - t2)) < 0

    if horizontal_intersected and vertical_intersected:
        rect1_area = rect_area(l1, t1, r1, b1)
        rect2_area = rect_area(l2, t2, r2, b2)
        intersected_area = rect_area(max(l1, l2), max(t1, t2), min(r1, r2), min(b1, b2))
        intersected_ratio = round(intersected_area / rect1_area, 3)
        return 1, intersected_ratio
    else:
        return 0, 0


def rect_contain(rect1, rect2, t=3) -> int:
    """
    Recommend to use `rect_overlap` instead of this for most cases.

    `t` is the expansion padding of the rect.

    The less the `t`, the more strict the condition.

    When `dpi=300`, recommend to set `t=3`.
    """
    l1, t1, r1, b1 = rect1
    l2, t2, r2, b2 = rect2
    diffs = [l1 - l2, t1 - t2, r2 - r1, b2 - b1]
    rect1_contains_rect2 = all(diff <= t for diff in diffs)
    rect2_contains_rect1 = all(diff >= -t for diff in diffs)
    if rect1_contains_rect2 and rect2_contains_rect1:
        return 2
    elif rect1_contains_rect2:
        return 1
    elif rect2_contains_rect1:
        return -1
    else:
        return 0


def euclidean_distance(point1, point2, value_type=int):
    p1 = np.array(point1)
    p2 = np.array(point2)
    return value_type(np.linalg.norm(p1 - p2))


def rect_distance(rect1, rect2=None, direction="diag"):
    if not rect2:
        x0, y0, x1, y1 = rect1
        x_distance = abs(x0 - x1)
        y_distance = abs(y0 - y1)
        diag_distance = euclidean_distance((x0, y0), (x1, y1))
        distance_direction_map = {
            "x": x_distance,
            "y": y_distance,
            "diag": diag_distance,
            "min": min(x_distance, y_distance, diag_distance),
        }
        distance = distance_direction_map[direction]
    else:
        rect1_center = rect_center(*rect1)
        rect2_center = rect_center(*rect2)
        distance = euclidean_distance(rect1_center, rect2_center)
    return distance


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


def distribute_weights(weights, distribution="one", center_idx=None, distances=None):
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
    elif distribution == "distance":
        scales = 1 / np.array(distances)
    elif distribution == "one":
        scales = np.ones(n)
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
