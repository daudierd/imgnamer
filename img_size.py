#-------------------------------------------------------------------------------
# Name:        get_image_size
# Purpose:     extract image dimensions given a file path using just
#              core modules
#
# Author:      Paulo Scardine (based on code from Emmanuel VAÏSSE)
# Adaptation:  Dorian Daudier
#
# Modified:    08/08/2017
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import struct

class UnknownImageFormat(Exception):
    pass

def get_image_size(file_path):
    """
    Return (width, height) for a given img file content - no external
    dependencies except the os and struct modules from core
    """
    size = os.path.getsize(file_path)

    with open(file_path, 'rb') as f:
        height = -1
        width = -1
        data = f.read(25)

        if (size >= 10) and data[:6] in (b'GIF87a', b'GIF89a'):
            # GIFs
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        elif ((size >= 24) and data.startswith(b'\211PNG\r\n\032\n')
              and (data[12:16] == b'IHDR')):
            # PNGs
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        elif (size >= 16) and data.startswith(b'\211PNG\r\n\032\n'):
            # older PNGs?
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        elif (size >= 2) and data.startswith(b'\377\330'):
            # JPEG
            msg = " raised while trying to decode as JPEG."
            f.seek(0)
            f.read(2)
            b = f.read(1)
            try:
                while (b and ord(b) != 0xDA):
                    while (ord(b) != 0xFF): b = f.read(1)
                    while (ord(b) == 0xFF): b = f.read(1)
                    if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                        f.read(3)
                        h, w = struct.unpack(">HH", f.read(4))
                        break
                    else:
                        f.read(int(struct.unpack(">H", f.read(2))[0])-2)
                    b = f.read(1)
                width = int(w)
                height = int(h)
            except struct.error:
                raise UnknownImageFormat("StructError" + msg)
            except ValueError:
                raise UnknownImageFormat("ValueError" + msg)
            except Exception as e:
                raise UnknownImageFormat(e.__class__.__name__ + msg)
        else:
            raise UnknownImageFormat(
                "Sorry, don't know how to get information from this file."
            )

    return width, height
