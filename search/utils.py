import re
import os
import logging

import requests

def page_title(url):
    try:
        r = requests.get(url, stream=True)
        # Read up to the </title> closing
        chunk = r.iter_lines(decode_unicode=True, delimiter='</title>')
    except:
        logging.info('Couldn\'t retrieve page title at ' + url)
        return os.path.basename(url)  # Title by default if none can be found

    chunk = chunk.__next__()
    title = re.findall(r"<title>(.*)", chunk)
    if title:
        return title[0].strip()
    else:
        return ''
