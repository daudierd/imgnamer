import os
import logging

from .exceptions import UnknownImageFormat

# Prepare a table of forbidden filename characters to remove from filenames
forbidden_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
forbidden_chars = str.maketrans({key: None for key in forbidden_chars})

def rename(filepath, new_name):
    """
    Rename a file at the specified 'filepath' with it 'new_name'.
    The exension and contaning directory will the same as before.
    """
    new_name = new_name.translate(forbidden_chars)  # Strip forbidden characters
    extension = os.path.basename(filepath).split('.')[-1]
    if new_name:
        new_name =  new_name + '.' + extension
        # Constitute new filepath & rename the file
        directory = os.path.dirname(filepath)
        new_filepath = os.path.join(directory, new_name)
        os.rename(filepath, new_filepath)
        logging.info("renamed '" + os.path.basename(filepath)
            + "' into '" + os.path.basename(new_filepath))
