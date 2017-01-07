#!/usr/bin/python
# coding: UTF-8

"""
iomTracker -- Utility Tool for Linux with Procfs (Process Filesystem)

Track IO and memory usage of specified process.
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

import os
import sys

from lib.utils import Utils
from lib.track import exec_track

def SIGINTHandler(signum, frame):
    global controller
    controller.stop()

def main():

    # Check if executed as root
    if os.getuid() != 0:
      sys.stderr.write("Sorry, iomTracker must be executed as root user.\n")
      sys.exit(1)

    # Get command line args (argv)
    argv = sys.argv

    # Print usage if pid is not specified
    if len(argv) < 3:
        sys.stderr.write(Utils.getUsage())
        sys.exit(1)

    # Execute tracking
    exec_track(argv)

if __name__ == "__main__":
    main()
