from itertools import chain


def flatten_len(nested_list):
    return len(list(chain.from_iterable(nested_list)))
