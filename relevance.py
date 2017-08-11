# This module implements a collection of functions designed to estimate the
# relevance of search results, thus helping naming functions to determine the
# best match when naming a picture.

import re
from urllib.parse import urlparse

# The following parameters can be edited to adjust how relevance scores ar
# calculated

#######################
# EDITABLE PARAMETERS #
#######################

# Dictionary of (regex, score) entries that boost result relevance when regex
# pattern is matched, by applyin the multiplication factor.
# The placeholder is reserved to the source website name
pattern_matches = {
    r'(.*) by (.*) on @DeviantArt - Pinterest': 2,
    r'(.*) by (.*) (on|\||\-) %s' : 2,
    r'(.*) by (.*) \| (.*) \| %s' : 2,
    r'(.*) (on|\||\-) %s' : 1.75,
    r'(.*) \| (.*) \| %s' : 1.75,
    r'(.*) by (.*)' : 1.5,
    r'(.*) \| (.*) \| (.*)' : 1.5
}

#######################

def dimensions_similarity(dim1, dim2):
    """
    Returns a value reflecting a similarity of dimensions between two images.
    The value is 1 if dimensions are the same, and closer to 0 as it is less
    similar.
    """
    def norm(x, y): return math.sqrt(x**2 + y**2)

    diff = norm(dim2[0]-dim1[0], dim2[1]-dim1[1])
    normal_diff = diff / max(norm(dim2[0], dim2[1]), norm(dim1[0], dim1[1]))
    return(1 - normal_diff)

def pattern_score(title, location):
    for expr, val in pattern_matches.items():
        if (expr.find('%s') == -1):
            pattern = expr
        else:
            site = urlparse(location).hostname
            site = site.split('.')
            if (site[0] == 'www'):
                site = site[1]
            else:
                site = site[0]
            pattern = expr % site

        if re.findall(pattern, title, re.IGNORECASE):
            return val
