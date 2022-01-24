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
