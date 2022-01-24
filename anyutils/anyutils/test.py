from collections import namedtuple
from random import randbytes, randint, random, randrange, sample
from typing import Type

from pydantic import parse_obj_as

string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
num_string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def randstr(l):
    return "".join(sample(string, l))


def randnumstr(l):
    return "".join(sample(num_string, l))


def make_data(model: Type, siz: int, **kwargs):
    tp = namedtuple("np", list(kwargs.keys()))
    res = []
    for i in range(siz):
        res += [tp(*[j[i] for j in kwargs.values()])]
    obj = parse_obj_as(list[model], res)
    return [i.dict() for i in obj]
