from __future__ import division
from random import random, uniform


def random_angle(limit):
    non_uniform_norm = abs(limit) ** 3
    val = 0
    while (val == 0 or random() < abs(val) ** 3 / non_uniform_norm):
        val = uniform(-limit, limit)
    return val
