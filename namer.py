import logging

import requests
import bs4

from .img_search import fetch_results, fetch_google_url
from .img_search import SearchResult

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

def suggested_name(filepath, method='BEST_GUESS', sites=None):
    """
    Returns a suggested name for a file specified by its location.

    Arguments:
    - method: the method used to find an appropriate name, among the methods
    available: BEST_GUESS (default), RESULTS
    - sites: (optional) A list of preferred sites or domains to look for first.
    """
    if method == 'BEST_GUESS':
        return prettify(best_guess(filepath))
    elif method == 'RESULTS':
        res = fetch_results(filepath)
        return prettify(choose_best(res))
    else:
        return ''

def best_guess(filepath):
    """"
    Returns Google's best guess for an image specified by its location.
    If no suggestion can be found, an empty string is returned.
    """
    fetchUrl = fetch_google_url(filepath)

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

def choose_best(results):
    """
    Determine the best name from a list of results.
    """
    # TO DO: for now, return the first result
    return results[0].title
