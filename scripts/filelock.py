#! python
"""Try acquiring a fcntl file lock on a file.

The lock may either be shared or exclusive.  Run a command while
holding the lock.
"""

import argparse
import fcntl
import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys

from rklib.filelock import AlreadyLockedError, filelock

try:
    shell = os.environ['SHELL']
except KeyError:
    shell = '/bin/sh'

modes = {'EX':fcntl.LOCK_EX, 'SH':fcntl.LOCK_SH}

cli = argparse.ArgumentParser(description=__doc__.split("\n")[0].rstrip("."))
cli.add_argument("--debug",
                 action='store_const', dest='loglevel',
                 const=logging.DEBUG, default=logging.INFO,
                 help="enable debug output")
cli.add_argument("--read-only", "--ro", action='store_true',
                 help="open the lock file read only")
cli.add_argument("--mode", choices=modes.keys(), default='EX',
                 help="lock mode, either exclusive or shared")
cli.add_argument("-e", "--cmd", default=shell,
                 help="external command to execute while holding the lock")
cli.add_argument('lockfile', type=Path,
                 help="the file to acquire the lock on")
args = cli.parse_args()

prog_name = Path(sys.argv[0]).name if sys.argv[0] else "-"
logformat = "%(asctime)-15s %(name)s %(levelname)s: %(message)s"
logging.basicConfig(level=args.loglevel, format=logformat)
log = logging.getLogger(prog_name)


try:
    with filelock(str(args.lockfile), mode=modes[args.mode], ro=args.read_only):
        log.debug("run %s", args.cmd)
        subprocess.run(shlex.split(args.cmd), cwd=args.lockfile.parent)
except AlreadyLockedError:
    log.critical("%s is already locked", args.lockfile)
    sys.exit(1)
