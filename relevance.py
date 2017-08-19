# This module implements a collection of functions designed to estimate the
# relevance of search results, thus helping naming functions to determine the
# best match when naming a picture.

import re
import json
import math
from urllib.parse import urlparse

from .tools import get_image_size
from .search import SearchResult

# In order to improve your results, please update 'patterns.json' file
# JSON fields:
#   specific -> List of specific patterns, usually relevant with the source of
#               the images. GREATLY BOOSTS RESULTS
#   generic  -> List of generic patterns, usually applicable with different
#               sources. BOOSTS RESULTS
#   avoid    -> List of words that negatively impacts results
# YOU can use '%s' in patterns to refer to a website's name

patterns_file = 'patterns.json'

# Implementation of a 2D Vector
class Vector():
    """Class used to describe 2D vectors."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)
    def __add__(self, v):
        return(Vector(self.x + v.x, self.y + v.y))
    def __sub__(self, v):
        return(Vector(self.x - v.x, self.y - v.y))
    def __mul__(self, v):
        return ((self.x * v.x) + (self.y * v.y))

def dimensions_similarity(dim1, dim2):
    """
    Returns a value representing the similarity between two images' sizes.
    The closer to 1, the more similar the images in terms of dimensions.
    """
    u = Vector(int(dim1[0]), int(dim1[1]))
    v = Vector(int(dim2[0]), int(dim2[1]))

    diff = (u-v).norm()
    normal_diff = diff / max(u.norm(), v.norm())
    return(1 - normal_diff)

def build_pattern(expr, location):
    if (expr.find('%s') == -1):
        return expr
    else:
        if location[:4] == 'http':
            site = urlparse(location).hostname
        else:
            site = urlparse('http://' + location).hostname
        site = site.split('.')
        if (site[0] == 'www'):
            site = site[1]
        else:
            site = site[0]
        return expr % site

def apply_bonus(value, title, pattern_list):
    for pattern in pattern_list:
        if re.findall(pattern, title, re.IGNORECASE):
            return value
    # Default value on loop end if no value has been returned beforehand
    return 1

def pattern_bonus(title, location):
    val = 1
    with open(patterns_file, 'r') as f:
        data = json.loads(f.read())
        val = val * apply_bonus(2, title,
            [build_pattern(e, location) for e in data['specific']])
        val = val * apply_bonus(1.5, title,
            [build_pattern(e, location) for e in data['generic']])
        val = val * apply_bonus(0.5, title,
            [build_pattern(e, location) for e in data['avoid']])
        return val

def score(result, original_file=None):
    score = pattern_bonus(result.title, result.location)
    if original_file:
        score = score * dimensions_similarity(result.dimensions,
                                              get_image_size(original_file))
    return score
