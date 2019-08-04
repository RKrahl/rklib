"""Tools for reading and writing files.
"""

import hashlib
from pathlib import Path
import zlib


class _CRC32():
    """Provide an hashlib compatible interface to zlib.crc32().
    """
    def __init__(self):
        self.crc32 = 0
    def update(self, chunk):
        self.crc32 = zlib.crc32(chunk, self.crc32)
    def hexdigest(self):
        return "%x" % (self.crc32 & 0xffffffff)

def _new_checksum(name):
    if name == "crc32":
        return _CRC32()
    else:
        return hashlib.new(name)

def copy_file_crc(src_file, dest_file, checksums=None, chunksize=8192):
    """Copy a file and calculate checksums on the fly.
    """

    if not hasattr(src_file, "read"):
        if not hasattr(src_file, "open"):
            src_file = Path(src_file)
        with src_file.open("rb") as sf:
            return copy_file_crc(sf, dest_file, checksums, chunksize)

    if not hasattr(dest_file, "write"):
        if not hasattr(dest_file, "open"):
            dest_file = Path(dest_file)
        with dest_file.open("wb") as df:
            return copy_file_crc(src_file, df, checksums, chunksize)

    checksums = checksums or []
    m = { c:_new_checksum(c) for c in checksums }
    while True:
        chunk = src_file.read(chunksize)
        if not chunk:
            break
        for c in checksums:
            m[c].update(chunk)
        dest_file.write(chunk)
    return tuple( m[c].hexdigest() for c in checksums )
