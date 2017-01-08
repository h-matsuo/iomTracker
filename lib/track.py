#!/usr/bin/python
# coding: UTF-8

"""
Implementation of command: track
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

from datetime import datetime
import json
import os.path
import re
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
        # Compile regex pattern for analyzing "/proc/net/dev"
        self.pattern = re.compile(r"\s*") # Raw string to avoid the backslash plagu
        # Initialize valiables for analyzing "/proc/net/dev"
        self.rec_bytes_begin = -1
        self.snd_bytes_begin = -1

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
                continue
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
            fin_status = open("/proc/%d/status"  % self.pid, "r")
            fin_io     = open("/proc/%d/io"      % self.pid, "r")
            fin_dev    = open("/proc/%d/net/dev" % self.pid, "r")
            status  = fin_status.readlines()
            io      = fin_io.readlines()
            net_dev = fin_dev.readlines()
            fin_status.close()
            fin_io.close()
            fin_dev.close()
        except IOError:
            self.stop()
            print "Process %d terminated." % self.pid
            return None
        # Analyze /proc/<PID>/status
        n_item = 0
        for line in status:
            if line.startswith("VmPeak"):
                self.vmpeak = int(line[7:-3].strip())
                n_item += 1
                continue
            if line.startswith("VmSize"):
                vmsize      = int(line[7:-3].strip())
                n_item += 1
                continue
            if line.startswith("VmHWM"):
                self.vmhwm  = int(line[6:-3].strip())
                n_item += 1
                continue
            if line.startswith("VmRSS"):
                vmrss       = int(line[6:-3].strip())
                n_item += 1
                continue
            if n_item == 4:
                break
        if n_item < 4:
            return None
        # Analyze /proc/<PID>/io
        n_item = 0
        for line in io:
            if n_item == 4:
                break
            if line.startswith("rchar:"):
                rchar       = int(line[7:-1])
                n_item += 1
                continue
            if line.startswith("wchar:"):
                wchar       = int(line[7:-1])
                n_item += 1
                continue
            if line.startswith("read_bytes:"):
                read_bytes  = int(line[12:-1])
                n_item += 1
                continue
            if line.startswith("write_bytes:"):
                write_bytes = int(line[13:-1])
                n_item += 1
                continue
        if n_item < 4:
            return None
        # Analyze /proc/net/dev
        rec_bytes = 0
        snd_bytes = 0
        for line in net_dev:
            line = self.pattern.split(line.strip())
            if line[0].find(":") < 0:
                continue
            rec_bytes += int(line[1])
            snd_bytes += int(line[9])
        if self.rec_bytes_begin < 0:
            self.rec_bytes_begin = rec_bytes
            self.snd_bytes_begin = snd_bytes
        rec_bytes = rec_bytes - self.rec_bytes_begin
        snd_bytes = snd_bytes - self.snd_bytes_begin
        return {
            "date"       : Utils.formatDatetime(now),
            "vmsize"     : vmsize,
            "vmrss"      : vmrss,
            "rchar"      : rchar,
            "wchar"      : wchar,
            "read_bytes" : read_bytes,
            "write_bytes": write_bytes,
            "rec_bytes"  : rec_bytes,
            "snd_bytes"  : snd_bytes
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
