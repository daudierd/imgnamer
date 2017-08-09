import os
import logging
import re

import requests
import bs4

from imgsearch import google, tineye

def search(filepath, engine='GOOGLE', num=5, **params):
    """
    Returns a list of SearchResult objects for an image search.

    Arguments:
    - engine (GOOGLE | TINEYE): The search engine used for reverse image search
    - pages: Maximum number of search results to return (default = 5)
    - params: a dictionary of search parameters
    """
    if (engine == 'GOOGLE'):
        return google.search(filepath, num=num, **params)
    elif (engine == 'TINEYE'):
        return tineye.search(filepath, num=num, **params)
    else:
        print("Unsupported search engine")
        return []
