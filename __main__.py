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

# Set working directory to the namespace where __main__.py is defined
os.chdir(os.path.dirname(__file__))

# Global variable specifying all supported image file extensions
supported_ext = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

def img_rename(filepath, **kws):
    """
    Rename an image at the specified path with Google Images suggestion.
    If the file is not a valid image file, nothing happens.
    """
    extension = os.path.basename(filepath).split('.')[-1]
    if extension.lower() in supported_ext:
        new_name = namer.suggested_name(filepath, **kws)
        if new_name:
            new_name =  new_name + '.' + extension
            # Constitute new filepath & rename the file
            directory = os.path.dirname(filepath)
            new_filepath = os.path.join(directory, new_name)
            os.rename(filepath, new_filepath)
            print("renamed '" + os.path.basename(filepath)
                + "' into '" + os.path.basename(new_filepath))

def img_batch_rename(folder_path, sub_folders=False, **kws):
    """
    Rename all images in the specified folder with Google Images suggestion.
    In order to rename the images in subfolders, the argument 'sub_folders'
    must be set to 'True'
    """
    if os.path.isdir(folder_path):
        l = os.listdir(folder_path)
        for basename in l:
            path = os.path.join(folder_path, basename)
            if os.path.isfile(path):
                img_rename(path, **kws)
            elif os.path.isdir(path) and sub_folders:
                img_batch_rename(path)
    else:
        logging.error("No valid directory was found.")
