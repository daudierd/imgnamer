# IMPORTANT REMARK:
# google_images modules retrieves Google Images search results accessed by
# display 'All sizes' of an image from the main results page, which results are
# obtained via the google module

import os
import logging
import re
import json

import requests
import bs4

from .result import SearchResult
from . import google

# Global variables for Google search
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'
baseUrl = 'https://encrypted.google.com/searchbyimage/upload'

def fetch_url(filepath):
    """
    Returns the URL containing Google Image search results (page with all sizes
    available) for an image.

    Arguments:
        - filepath: the path to the image file to search
    """
    main_url = google.fetch_url(filepath)
    try:
        response = requests.get(main_url, headers={'User-Agent': user_agent})
    except Exception as e:
        logging.error(str(e))
        return None

    soup = bs4.BeautifulSoup(response.content, "html.parser")
    base = 'https://encrypted.google.com'
    if soup.find_all('div', class_='_v6'):
        if soup.select('._v6')[0].select('.gl'):
            return base + soup.select('._v6')[0].select('.gl')[0].a['href']

def search(filepath, num=5, **search_params):
    """
    Returns a list of SearchResult objects obtained with Google Images.

    Arguments:
        - filepath: the path to the image file to search
    Optional:
        - num: Maximum number of search results to return (default = 5)
        - params: a dictionary of search GET parameters
    """
    searchUrl = fetch_url(filepath)
    out=[]      # Output list of SearchResult objects
    page = 1    # Results page
    params = '' # String containing specific search GET parameters
    for p, val in search_params:
        params = params + '&' + p + '=' + val

    # Get image results page
    if searchUrl:
        try:
            response = requests.get(searchUrl + params,
                headers={'User-Agent': user_agent})
        except Exception as e:
            logging.error(str(e))
            return out
    else:
        logging.warning("No image results for " + os.path.basename(filepath))
        return out

    soup = bs4.BeautifulSoup(response.content, "html.parser")
    results = soup.select('.rg_bx')

    for res in results:
        meta = json.loads(res.select(".rg_meta")[0].text)
        dimensions = res.select(".rg_anbg")[0].select(".rg_an")[0]
        dimensions = re.findall(r"(\d+)\s×\s(\d+)", dimensions.string)[0]

        out.append(SearchResult(
            dimensions,
            meta['pt'],
            meta['ru'],
            meta['s']))
        # No need to continue if enough results have been gathered
        if (len(out) >= num): break
    return out
