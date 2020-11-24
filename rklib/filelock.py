"""High-level interface to fcntl file locks.
"""

import errno
import fcntl
import logging
import os

modes = {'EX':fcntl.LOCK_EX, 'SH':fcntl.LOCK_SH}

log = logging.getLogger(__name__)

class AlreadyLockedError(OSError):
    pass

class filelock:
    """Acquire a lock on a file.

    Open a file and acquire a lock on it.  In read only mode the file
    must and will be opened for reading.  In read/write mode, the
    default, the file will be opened for reading and writing and is
    created if it does not already exist.

    :param path: the path to the file.  This will be passed to
        :func:`os.open`, which accepts a path-like object for Python
        3.6 or newer.
    :type path: :class:`str` or path-like
    :param mode: either :const:`fcntl.LOCK_EX` to acquire an exclusive
        lock or :const:`fcntl.LOCK_SH` to acquire a shared lock.
    :type mode: :class:`int`
    :param ro: read only mode.
    :type ro: :class:`bool`

    Read only mode may be needed of the current user does not have
    write permission on the file or if the file resides on a read only
    file system.  Read only mode is incompatible with acquiring an
    exclusive lock.

    This class may either be used as a context manager or by calling
    the constructor and the release() method explicitly.
    """
    def __init__(self, path, mode=fcntl.LOCK_EX, ro=False):
        self.ro = ro
        self.fd = None
        if self.ro and mode == fcntl.LOCK_EX:
            raise ValueError("cannot acquire an exclusive lock "
                             "in read only mode")
        log.debug("trying to lock %s ...", path)
        open_flags = os.O_RDONLY if self.ro else os.O_RDWR | os.O_CREAT
        self.fd = os.open(path, open_flags, 0o666)
        try:
            self._acquire(mode)
        except:
            try:
                self.release()
            except:
                pass
            raise
        log.debug("lock on %s acquired", path)

    def _acquire(self, mode):
        try:
            fcntl.lockf(self.fd, mode | fcntl.LOCK_NB)
        except Exception as e:
            if (isinstance(e, OSError) and
                e.errno in [errno.EACCES, errno.EAGAIN]):
                raise AlreadyLockedError(*e.args) from None
            else:
                raise

    def release(self):
        """Close the file and release the lock.
        """
        if self.fd is not None:
            log.debug("releasing lock")
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.release()

    def __del__(self):
        self.release()

    def relock(self, mode=fcntl.LOCK_EX):
        """Acquire the lock again, possibly with a different mode.

        :param mode: either :const:`fcntl.LOCK_EX` to acquire an
            exclusive lock or :const:`fcntl.LOCK_SH` to acquire a
            shared lock.
        :type mode: :class:`int`

        This is particularly useful to change an exclusive lock in a
        shared one or vice versa, without intermediately releasing the
        lock.
        """
        if self.ro and mode == fcntl.LOCK_EX:
            raise ValueError("cannot acquire an exclusive lock "
                             "in read only mode")
        self._acquire(mode)
