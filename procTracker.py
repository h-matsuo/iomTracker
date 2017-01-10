#!/usr/bin/python
# coding: UTF-8

"""
procTracker -- Utility Tool for Linux with Procfs (Process Filesystem)

Track disk I/O, memory usage and network communications.
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

import os
import sys

from lib.utils import Utils
from lib.track import exec_track

def main():

    # Get command line args (argv)
    argv = sys.argv

    # Parse argv
    result = Utils.parseArgv(argv)

    # Check if procfs (process filesystem) is enabled
    if not os.path.exists("/proc"):
        sys.stderr.write("%s: error: procfs (process filesystem) is not avaliable on this system\n" % Utils.prog_name)
        sys.exit(1)

    # Execute tracking
    exec_track(result)

if __name__ == "__main__":
    main()
