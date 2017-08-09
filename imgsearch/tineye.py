import os
import logging
import re

import requests
import bs4

from .result import SearchResult

# Global variables for Google search
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'
baseUrl = 'https://tineye.com/search'

def fetch_url(filepath):
    """
    Returns the URL containing TinEye's search results for an image.

    Arguments:
        - filepath: the path to the image file to search
    """
    try:
        with open(filepath, 'rb') as f:
            # ATTENTION!!!
            # The file basename needs to be specified for the request to work
            multipart = {'image': (os.path.basename(filepath), f)}
            response = requests.post(baseUrl,
                files=multipart,
                allow_redirects=False)
            return response.headers['Location']
    except Exception as e:
        logging.error(str(e))
        return None

def search(filepath, num=5, **search_params):
    """
    Returns a list of SearchResult objects obtained with TinEye.

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
            response = requests.get(searchUrl + '?page=' + str(page) + params,
                headers={'User-Agent': user_agent})
        except Exception as e:
            logging.error(str(e))
            return out

        soup = bs4.BeautifulSoup(response.content, "html.parser")
        # extract results in 'match-row' blocks
        results = soup.find_all("div", class_="match-row")
        if len(results) > 0:
            for res in results:
                thumbnail = res.select('.match-thumb')[0]
                details = res.select('.match-details')[0]
                img_link = details.select('.image-link')[0]
                dimensions = thumbnail.p.extract()
                dimensions = re.findall(r"(\d+)x(\d+)", dimensions.text)[0]

                out.append(SearchResult(
                    dimensions,
                    img_link.a.string,
                    img_link.find_next_siblings('p')[1].a.get('href'),
                    details.select('.match')[0].text))
                # No need to continue if enough results have been gathered
                if (len(out) >= num): break

            page = page + 1
        else:   # We may have reached the end of results
            break
    return out
