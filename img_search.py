import os
import logging
import re

import requests
import bs4

from .imgsearch import google, tineye

def search(filepath, engine='GOOGLE', num=5, **params):
    """
    Performs a reverse image search and returns a list of SearchResult objects.

    Arguments:
        - filepath: the path to the image file to search
    Optional:
        - engine (GOOGLE | TINEYE): The search engine used (default = 'GOOGLE')
        - num: Maximum number of search results to return (default = 5)
        - params: a dictionary of search GET parameters
    """
    if (engine == 'GOOGLE'):
        return google.search(filepath, num=num, **params)
    elif (engine == 'TINEYE'):
        return tineye.search(filepath, num=num, **params)
    else:
        print("Unsupported search engine")
        return []
