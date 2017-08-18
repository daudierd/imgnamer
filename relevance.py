# This module implements a collection of functions designed to estimate the
# relevance of search results, thus helping naming functions to determine the
# best match when naming a picture.

import re
import math
from urllib.parse import urlparse

from .tools import get_image_size
from .search import SearchResult

# The following parameters can be edited to adjust how relevance scores ar
# calculated

#######################
# EDITABLE PARAMETERS #
#######################

# Dictionary of (regex, score) entries that boost result relevance when regex
# pattern is matched, by applyin the multiplication factor.
# The placeholder is reserved to the source website name
pattern_matches = {
    r'profile': 0.5,
    r'favorites': 0.5,
    r'(.*) by (.*) on @DeviantArt - Pinterest': 2.2,
    r'(.*) best (.*) on Pinterest': 0.9,
    r'(.*) by (.*) (on|\||\-) %s' : 2,
    r'(.*) by (.*) \| (.*) \| %s' : 2,
    r'(.*) (on|\||\-) %s' : 1.5,
    r'(.*) \| (.*) \| %s' : 1.5,
    r'(.*) by (.*)' : 1.5,
    r'(.*) \| (.*) \| (.*)' : 1.3
}

#######################

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

def pattern_bonus(title, location):
    for expr, val in pattern_matches.items():
        if (expr.find('%s') == -1):
            pattern = expr
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
            pattern = expr % site

        if re.findall(pattern, title, re.IGNORECASE):
            return val
    # Default value on loop end if no value has been returned beforehand
    return 1

def score(result, original_file=None):
    score = pattern_bonus(result.title, result.location)
    if original_file:
        score = score * dimensions_similarity(result.dimensions,
                                              get_image_size(original_file))
    return score
