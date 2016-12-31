#!/usr/bin/python
# coding: UTF-8

"""
Implementation of command: track
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

from datetime import datetime
import json
import os.path
import signal
import sys
import time

from lib.utils import Utils

class TrackController:
    """
    Control tracking memory usage
    """

    def __init__(self):
        """
        Constructor
        """
        # Initialize output data
        self.tracked_data = {}
        self.tracked_data["data"] = []
        # Stop flag
        self.stop_flag = False
        # Whether exporting data to the external file or not
        self.does_export = False
        # Default output: standard output
        self.output_path = None

    def setPid(self, pid):
        """
        Set process ID to track

        @param process ID
        """
        if not os.path.exists("/proc/%d" % pid):
            sys.stderr.write("ERROR: PID %d: No such process.\n" % pid)
            sys.exit(1)
        self.pid = pid

    def setInterval(self, interval):
        """
        Set interval between tracking

        @param interval Interval
        """
        self.interval = interval

    def setOutputPath(self, output_path):
        """
        Set file path for writing tracked data

        @param output_path Output file path
        """
        self.output_path = output_path
        self.does_export = True

    def start(self):
        """
        Start tracking
        """
        self.__track()

    def stop(self):
        """
        Stop tracking
        """
        self.stop_flag = True
        if self.does_export:
            self.tracked_data["vmpeak"] = self.vmpeak
            self.tracked_data["vmhwm"]  = self.vmhwm
            fout = open(self.output_path, "w")
            json.dump(self.tracked_data, fout, indent = 2, separators = (",", ": "))
            fout.close()
        else:
            print {
                "vmpeak": self.vmpeak,
                "vmhwm" : self.vmhwm
            }

    def __track(self):
        """
        Track INA219 repeatedly
        """
        while not self.stop_flag:
            begin = datetime.today()
            tracked_data = self.__getTrackedData()
            if tracked_data == None:
                break
            if self.does_export:
                self.tracked_data["data"].append(tracked_data)
            else:
                print json.dumps(tracked_data, indent = 2, separators = (",", ": "))
            end = datetime.today()

            diff = self.interval - (end - begin).total_seconds()
            if diff < 0: diff = 0
            time.sleep(diff)

    def __getTrackedData(self):
        """
        Prepare for data
        """
        now = datetime.today()
        try:
            fin = open("/proc/%d/status" % self.pid, "r")
        except IOError:
            self.stop()
            print "Process %d terminated." % self.pid
            return None
        data = fin.read().split("\n")
        fin.close()
        self.vmpeak = int(data[15][7:-2].strip())
        self.vmhwm  = int(data[19][6:-2].strip())
        return {
            "date"  : Utils.formatDatetime(now),
            "vmsize": int(data[16][7:-2].strip()),
            "vmrss" : int(data[20][6:-2].strip())
        }

def SIGINTHandler(signum, frame):
    """
    Signal SIGINT handler
    """
    global controller
    controller.stop()

def exec_track(argv):
    """
    Execute command: track

    @param argv Command options
    """

    # Instantiate controller
    global controller
    controller = TrackController()

    # Set pid
    controller.setPid(int(argv[1]))

    # Set interval
    controller.setInterval(float(argv[2]))

    # Set output file path
    if len(argv) > 3:
        controller.setOutputPath(argv[3])

    # Print message
    print "Start tracking..."
    print 'Press "Ctrl + c" to quit.'

    # Handle SIGINT
    signal.signal(signal.SIGINT, SIGINTHandler)

    # Start tracking
    controller.start()
