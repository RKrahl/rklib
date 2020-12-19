"""Test module rklib.filelock.
"""

import fcntl
import logging
from multiprocessing import Process, Queue
from pathlib import Path
import sys
import time
import pytest
from rklib.filelock import filelock, AlreadyLockedError

log = logging.getLogger(__name__)


class LockProcess:
    """Spawn a subprocess to try locking a file.

    Concurrent file locking can only by tried using multiple
    processes.  This class set up a subprocess that troes to acquire a
    lock on a file.  Furthermore, timing is crucial for the tests.
    This class allows to synchronize acquiring and releasing the lock
    in the child process.
    """

    def __init__(self, path, mode):
        self.sig_queue = Queue()
        self.res_queue = Queue()
        self.child = Process(target=self._lock_file, args=(path, mode))
        self.child.start()

    def _lock_file(self, path, mode):
        try:
            log.debug("waiting for signal to acquire lock")
            msg = self.sig_queue.get()
            assert msg == "lock"
            with filelock(path, mode):
                log.debug("waiting for signal to release lock")
                msg = self.sig_queue.get()
                assert msg == "release"
            self.res_queue.put(0)
        except Exception as e:
            log.error("%s: %s" % (type(e).__name__, e))
            self.res_queue.put(e)

    def lock(self):
        self.sig_queue.put("lock")

    def release(self):
        self.sig_queue.put("release")

    def join(self):
        res = self.res_queue.get()
        self.child.join()
        return res


@pytest.mark.parametrize("mode",
                         [fcntl.LOCK_SH, fcntl.LOCK_EX],
                         ids=["LOCK_SH", "LOCK_EX"])
def test_filelock_single(tmpdir, mode):
    """One single process acquiring a lock.
    Nothing special.
    """
    lockfile = str(tmpdir.join("lock"))
    p = LockProcess(lockfile, mode)
    time.sleep(0.5)
    p.lock()
    time.sleep(0.5)
    p.release()
    assert p.join() == 0


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="requires Python 3.6 or higher")
def test_filelock_single_path(tmpdir):
    """One single process acquiring a lock.
    Same as last test, but pass a Path object as the path parameter to
    filelock().  This requires Python 3.6 or newer.
    """
    lockfile = Path(tmpdir.join("lock"))
    p = LockProcess(lockfile, fcntl.LOCK_SH)
    time.sleep(0.5)
    p.lock()
    time.sleep(0.5)
    p.release()
    assert p.join() == 0


@pytest.mark.parametrize("mode1",
                         [fcntl.LOCK_SH, fcntl.LOCK_EX],
                         ids=["LOCK_SH", "LOCK_EX"])
@pytest.mark.parametrize("mode2",
                         [fcntl.LOCK_SH, fcntl.LOCK_EX],
                         ids=["LOCK_SH", "LOCK_EX"])
def test_filelock_double(tmpdir, mode1, mode2):
    """Two processes trying to acquiring a lock.

    This should work if both locks are shared.  In all other
    combinations, the second process should fail to acquire the lock.
    """
    lockfile = str(tmpdir.join("lock"))
    p1 = LockProcess(lockfile, mode1)
    p2 = LockProcess(lockfile, mode2)
    time.sleep(0.5)
    p1.lock()
    time.sleep(0.5)
    p2.lock()
    time.sleep(0.5)
    p1.release()
    p2.release()
    res1 = p1.join()
    res2 = p2.join()
    assert res1 == 0
    if mode1 == fcntl.LOCK_SH and mode2 == fcntl.LOCK_SH:
        assert res2 == 0
    else:
        assert isinstance(res2, AlreadyLockedError)
