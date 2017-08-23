import logging
import operator

import requests
import bs4

from .search import SearchResult
from .search.google import fetch_url
from .img_search import search
from .relevance import score

__all__ = ['suggested_name']

# Compatible User Agent for Google search
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'

def prettify(name):
    new_name = new_name.title()  # titlecase name
    return new_name

def suggested_name(results, filepath, hint=''):
    """
    Returns a suggested name for a file from the results obtained by reverse
    image search.

    Arguments:
    - results: list of SearchResult objects
    - filepath: path to the original file
    - hint: (optional) A hint for naming the picture.
    """
    return prettify(choose_best(results, filepath, hint=hint))

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
