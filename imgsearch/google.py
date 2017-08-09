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
    Returns the URL containing Google Images' search results for an image.

    Arguments:
        - filepath: the path to the image file to search
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

    while(len(out) < num):
        # Get results page
        try:
            response = requests.get(
                searchUrl + '&start=' + str(page*10) + params,
                headers={'User-Agent': user_agent})
        except Exception as e:
            logging.error(str(e))
            return out

        soup = bs4.BeautifulSoup(response.content, "html.parser")
        # extract results from the "Pages that include matching images" block
        result_block = soup.select('._NId')
        if len(result_block) > 0:
            results = result_block[-1].select(".rc")
            for res in results:
                snippet = res.select(".st")[0]
                dimensions = snippet.select(".f")[0].extract()
                dimensions = re.findall(r"(\d+) × (\d+)", dimensions.string)[0]

                out.append(SearchResult(
                    dimensions,
                    res.find_all("h3", class_="r")[0].string,
                    res.find_all("cite", class_="_Rm")[0].string,
                    snippet.text))
                # No need to continue if enough results have been gathered
                if (len(out) >= num): break
        else:   # We may have reached the end of results
            break
    return out
