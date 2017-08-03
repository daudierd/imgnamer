import logging

import requests
import bs4

from img_search import fetch_results, fetch_google_url
from img_search import SearchResult

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
    - sites: (optional) A list of preffered sites or domains to look for first.
    """
    if method == 'BEST_GUESS':
        return prettify(best_guess(filepath))
    elif method == 'RESULTS':
        res = fetch_results(filepath)
        return prettify(res[0].title)
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

##################################################
# ---------------------------------------------- #
# ---- CHOICE ALGORITHM NEEDS TO BE REVIEWED --- #
# ---------------------------------------------- #
##################################################

def choose_best(suggestion_list):
    # In the event that the suggestion list is empty, return empty string
    if not suggestion_list:
        return ''

    # Create a dictionary of number of occurences for each encountered word
    words = dict()
    for i, sug in enumerate(suggestion_list):
        new_sug = sug.split(' | ')[0]
        if new_sug == sug:
            new_sug = new_sug.split(' - ')[0]
        suggestion_list[i] = new_sug
        for w in new_sug.split(' '):
            if len(w) > 2:
                if w in words:
                    words[w] = words[w] + 1
                else:
                    words[w] = 1

    # If keyword 'by' is identified, this may match pattern 'title by artist'
    for s in suggestion_list:
        new_s = s.split(' by ')[0]
        if new_s != s:
            return s

    # Return the two words with the most occurences
    words = sorted(words)
    return (words[-1] + ' ' + words[-2])

    # A suggestion score is the geometric mean of the score of each word (number
    # of occurences). Short words (< 2 letters) impact the score negatively.
    suggestion_scores = dict()
    highest_score = 0
    for s in suggestion_list:
        score = 0
        for w in s.split(' '):
                score = score + words[w]
        score = score / len(words)
        # Update highest score & add it as a key in suggestion_scores
        highest_score = max(score, highest_score)
        suggestion_scores[score] = s

    # Return the suggestion with the highest score is
    return suggestion_scores[highest_score]
