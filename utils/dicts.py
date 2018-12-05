from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

def merge(*dicts):
    result = {}

    for d in dicts:
        result.update(d)

    return result

def get_value(dic, key, default=None):
    result = default

    if key in dic.keys():
        result = dic[key]

    return result