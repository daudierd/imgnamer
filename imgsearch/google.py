import os
import logging
import re

import requests
import bs4

from .result import SearchResult

# Global variables for Google search
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'
baseUrl = 'https://encrypted.google.com/searchbyimage/upload'

def fetch_url(filepath):
    """
    Returns the URL containing Google's search results for an image specified
    by its location.
    """
    try:
        with open(filepath, 'rb') as f:
            multipart = {'encoded_image': (filepath, f), 'image_content': ''}
            response = requests.post(baseUrl,
                files=multipart,
                allow_redirects=False)
            return response.headers['Location']
    except Exception as e:
        logging.error(str(e))
        return None

def search(filepath, num=5, **params):
    out=[]
    searchUrl = fetch_url(filepath)
    for param, val in params:
        searchUrl = searchUrl + '&' + param + '=' + val
    try:
        response = requests.get(searchUrl,
            headers={'User-Agent': user_agent})
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        # extract results from the "Pages that include matching images" block
        result_block = soup.select('._NId')[-1]
        results = result_block.select(".rc")
        for res in results:
            snippet = res.select(".st")[0]
            dimensions = snippet.select(".f")[0].extract()
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
