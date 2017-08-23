#ImgNamer
#The python script that searches the web to name your images
#Author: Dorian Daudier <daudierd@users.noreply.github.com>
#Version 1.0
#License: GNU GPL v3 <www.gnu.org/licenses/gpl.html>

"""
ImgNamer:
Python script that searches the web to name your images.

Functions:
- img_rename: renames an image at the specified path
- img_batch_rename: renames all images from a folder at the specified path
"""

import os
import logging

from . import namer
from .img_search import search
from .utils import rename
from .utils.exceptions import UnknownImageFormat

# Set working directory to the namespace where __main__.py is defined
os.chdir(os.path.dirname(__file__))

# Global variable specifying all supported image file extensions
supported_ext = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

def img_rename(filepath, method='BEST_GUESS', engines=None):
    """
    Rename an image at the specified path with Google Images suggestion.
    If the file is not a valid image file, UnknownImageFormat is raised.

    - filepath: path to the image file to rename.
    - method: string indicating the method used to look for name suggestions.
    Methods available: BEST_GUESS (default), RESULTS
    - engines: a list of the reverse image search engines to use with RESULTS
    method, listed in preffered order.
    """
    extension = os.path.basename(filepath).split('.')[-1]
    if extension.lower() not in supported_ext:
        raise UnknownImageFormat("The image extension is not supported.")

    # In all cases, BEST_GUESS is used at least as a hint.
    hint = namer.suggested_name(filepath, method='BEST_GUESS')
    if (method == 'BEST_GUESS'):
        new_name = hint
    elif (method == 'RESULTS'):
        # aggregate resuls from the various engines
        res = []
        for engine in engines:
            res.append(search(filepath))
        # use 'suggested_name' function to get an appropriate new name
        new_name = namer.suggested_name(filepath, results, hint=hint)

    if new_name:
        rename(filepath, new_name)

def img_batch_rename(folder_path, sub_folders=False, method='BEST_GUESS', engines=None):
    """
    Rename all images in the specified folder with Google Images suggestion.

    Arguments:
    - folder_path: the path to the folder containing the images to rename.
    - sub_folders: boolean indicating whether sub_folders are also be included
    or not (default: False).
    - method: string indicating the method used to look for name suggestions.
    Methods available: BEST_GUESS (default), RESULTS
    - engines: a list of the reverse image search engines to use with RESULTS
    method, listed in preffered order.
    """
    if os.path.isdir(folder_path):
        l = os.listdir(folder_path)
        for basename in l:
            path = os.path.join(folder_path, basename)
            if os.path.isfile(path):
                img_rename(path, method=method, engines=engines)
            elif os.path.isdir(path) and sub_folders:
                img_batch_rename(path)
    else:
        logging.error("No valid directory was found.")
