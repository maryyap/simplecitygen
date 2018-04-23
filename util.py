from __future__ import division
from random import random, uniform


def random_angle(limit):
    non_uniform_norm = abs(limit) ** 3
    val = 0
    while (val == 0 or random() < abs(val) ** 3 / non_uniform_norm):
        val = uniform(-limit, limit)
    return val

def random_branch_angle():
    return random_angle(3)

def random_straight_angle():
    return random_angle(15)

def min_degree_difference(angle1, angle2):
    diff = abs(angle1 - angle2) % 180
    return min(diff, abs(diff-180))
