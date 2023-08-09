from itertools import chain


def flatten_len(nested_list):
    return len(list(chain.from_iterable(nested_list)))


def kilo_count(number, ndigits=1):
    return round(number / 1024, ndigits)
