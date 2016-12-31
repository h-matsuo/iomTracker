#!/usr/bin/python
# coding: UTF-8

"""
memTracker -- Utility Tool for Linux with Procfs (Process Filesystem)

Track memory usage of specified process.
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

import sys

from lib.utils import Utils
from lib.track import exec_track

def SIGINTHandler(signum, frame):
    global controller
    controller.stop()

def main():

    # Get command line args (argv)
    argv = sys.argv

    # Print usage if pid is not specified
    if len(argv) < 3:
        Utils.printUsage()
        sys.exit(1)

    # Execute tracking
    exec_track(argv)

if __name__ == "__main__":
    main()
