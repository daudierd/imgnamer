import logging
import operator

import requests
import bs4

from .search import SearchResult
from .search.google import fetch_url
from .img_search import search
from .relevance import score

__all__ = ['suggested_name']

# Prepare a table of forbidden filename characters to remove from filenames
forbidden_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
forbidden_chars = str.maketrans({key: None for key in forbidden_chars})

# Compatible User Agent for Google search
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'

def prettify(name):
    new_name = name.translate(forbidden_chars)  # Strip forbidden characters
    new_name = new_name.title()  # titlecase name
    return new_name

def suggested_name(filepath, method='BEST_GUESS', hint=''):
    """
    Returns a suggested name for a file specified by its location.

    Arguments:
    - method: the method used to find an appropriate name, among the methods
    available: BEST_GUESS (default), RESULTS
    - hint: (optional) A hint for naming the picture.
    """
    if method == 'BEST_GUESS':
        return prettify(best_guess(filepath))
    elif method == 'RESULTS':
        res = search(filepath)
        return prettify(choose_best(res, filepath, hint=hint))
    else:
        return ''

def best_guess(filepath):
    """"
    Returns Google's best guess for an image specified by its location.
    If no suggestion can be found, an empty string is returned.
    """
    fetchUrl = fetch_url(filepath)

    if (fetchUrl):
        try:
            response = requests.get(fetchUrl,
                headers={'User-Agent': user_agent})
            soup = bs4.BeautifulSoup(response.content, "html.parser")
            # get the tag containing Google's suggested search
            suggestion = soup.find("a", class_="_gUb")
            return prettify(suggestion.string)
        except Exception as e:
            logging.warning(str(e))
            return ''
    else:
        return ''

def choose_best(results, original_file=None, hint=''):
    """
    Determine the best name from a list of results.
    """
    # Rank results by score with a dictionary
    ranked = dict()
    for i, res in enumerate(results):
        s = score(res, original_file=original_file, hint=hint)
        s = s - i / 10  # include a positional malus
        if s not in ranked:
            ranked[s] = []
        ranked[s].append(res)
    # Return the first of the best ranked results
    ranked = sorted(ranked.items(), key=operator.itemgetter(0))
    top_list = list(ranked)[-1][1]
    return top_list[0].title
