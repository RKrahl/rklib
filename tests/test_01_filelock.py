"""Test module rklib.filelock.
"""

import fcntl
import logging
from multiprocessing import Process, Queue
import time
import pytest
from rklib.filelock import filelock, AlreadyLockedError

log = logging.getLogger(__name__)


def lock_file(sig_queue, res_queue, path, mode):
    try:
        log.debug("waiting for signal to acquire lock")
        msg = sig_queue.get()
        assert msg == "lock"
        with filelock(path, mode):
            log.debug("waiting for signal to release lock")
            msg = sig_queue.get()
            assert msg == "release"
        res_queue.put(0)
    except Exception as e:
        log.error("%s: %s" % (type(e).__name__, e))
        res_queue.put(e)


@pytest.mark.parametrize("mode",
                         [fcntl.LOCK_SH, fcntl.LOCK_EX],
                         ids=["LOCK_SH", "LOCK_EX"])
def test_filelock_single(tmpdir, mode):
    """One single process acquiring a lock.
    Nothing special.
    """
    lockfile = tmpdir.join("lock")
    sig_queue = Queue()
    res_queue = Queue()
    p = Process(target=lock_file, args=(sig_queue, res_queue, lockfile, mode))
    p.start()
    time.sleep(0.5)
    sig_queue.put("lock")
    time.sleep(0.5)
    sig_queue.put("release")
    res = res_queue.get()
    p.join()
    assert res == 0


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
    lockfile = tmpdir.join("lock")
    sig1_queue = Queue()
    res1_queue = Queue()
    sig2_queue = Queue()
    res2_queue = Queue()
    p1 = Process(target=lock_file,
                 args=(sig1_queue, res1_queue, lockfile, mode1))
    p1.start()
    p2 = Process(target=lock_file,
                 args=(sig2_queue, res2_queue, lockfile, mode2))
    p2.start()
    time.sleep(0.5)
    sig1_queue.put("lock")
    time.sleep(0.5)
    sig2_queue.put("lock")
    time.sleep(0.5)
    sig1_queue.put("release")
    sig2_queue.put("release")
    res1 = res1_queue.get()
    res2 = res2_queue.get()
    p1.join()
    p2.join()
    assert res1 == 0
    if mode1 == fcntl.LOCK_SH and mode2 == fcntl.LOCK_SH:
        assert res2 == 0
    else:
        assert isinstance(res2, AlreadyLockedError)
