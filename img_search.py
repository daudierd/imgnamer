import os
import logging
import re

import requests
import bs4

class SearchResult():
    """SearchResult class"""
    def __init__(self, dimensions, title, location, snippet):
        self.dimensions = dimensions
        self.title = title
        self.location = location
        self.snippet = snippet

# Global variables for Google search
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'
googleSearchUrl = 'https://encrypted.google.com/searchbyimage/upload'
tineyeSearchUrl = 'https://tineye.com/search'

def fetch_google_url(filepath):
    """
    Returns the URL containing Google's search results for an image specified
    by its location.
    """
    try:
        with open(filepath, 'rb') as f:
            multipart = {'encoded_image': (filepath, f), 'image_content': ''}
            response = requests.post(googleSearchUrl,
                files=multipart,
                allow_redirects=False)
            return response.headers['Location']
    except Exception as e:
        logging.error(str(e))
        return None

def fetch_tineye_url(filepath):
    """
    Returns the URL containing TinEye's search results for an image specified
    by its location.
    """
    try:
        with open(filepath, 'rb') as f:
            # ATTENTION!!!
            # The file basename needs to be specified for the request to work
            multipart = {'image': (os.path.basename(filepath), f)}
            response = requests.post(tineyeSearchUrl,
                files=multipart,
                allow_redirects=False)
            return response.headers['Location']
    except Exception as e:
        logging.error(str(e))
        return None

def fetch_results(filepath, engine='GOOGLE', **params):
    """
    Returns a list of min(num, total_nb_results) SearchResult objects.
    """
    if (engine == 'GOOGLE'):
        return google_search(fetch_google_url(filepath), **params)
    elif (engine == 'TINEYE'):
        return tineye_search(fetch_tineye_url(filepath), **params)
    else:
        print("Unsupported search engine")

def google_search(url, **params):
    out=[]
    searchUrl = url
    for param, val in params:
        searchUrl = searchUrl + '&' + param + '=' + val
    try:
        response = requests.get(searchUrl,
            headers={'User-Agent': user_agent})
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        # extract results from the "Pages that include matching images" block
        result_block = soup.find_all("div", class_="_NId")[-1]
        results = result_block.find_all("div", class_="rc")
        for res in results:
            snippet = res.find_all("span", class_="st")[0]
            dimensions = snippet.find_all("span", class_="f")[0].extract()
            dimensions = re.findall(r"(\d+) × (\d+)", dimensions.string)[0]

            out.append(SearchResult(
                dimensions,
                res.find_all("h3", class_="r")[0].string,
                res.find_all("cite", class_="_Rm")[0].string,
                snippet.text))
        return out
    except Exception as e:
        logging.error(str(e))
        return []

def tineye_search(url, num=10, **params):
    pass
