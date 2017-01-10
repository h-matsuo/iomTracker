#!/usr/bin/python
# coding: UTF-8

"""
Implementation of command: track
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

# ===== Configuration ==========================================================

# ----- Disk I/O tracking ------------------------------------------------------
#DEVICE_NAME = "mmcblk0"
# Read from: "/sys/block/<DEVICE_NAME>/queue/physical_block_size"
SECTOR_SIZE = 512 # [Bytes]
# Source: https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats
DISKSTATS_ROW       = 24
DISKSTATS_COL_READ  = 5
DISKSTATS_COL_WRITE = 9

# ----- Memory usage tracking --------------------------------------------------
# NOTE: 実験の特性上，ここでは
#       　「使用メモリ」＝「メモリ合計容量」－「メモリ未割り当て容量」
#       と定義する．バッファ領域やキャッシュ領域等は考慮しない．
#       参考：http://nopipi.hatenablog.com/entry/2015/09/13/181026
MEMINFO_ROW_TOTAL = 0
MEMINFO_ROW_FREE  = 1

# ----- Network communications tracking ----------------------------------------
NET_DEV_ROW_WLAN0 = 2
NET_DEV_ROW_LO    = 3
NET_DEV_ROW_ETH0  = 4
NET_DEV_COL_RECV  = 1
NET_DEV_COL_SEND  = 9

# ===== END Configuration ======================================================

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
        self.__tracked_data = []
        # Stop flag for tracking
        self.__stop_flag = False
        # Default values
        self.__interval = 1.0
        self.__out_file = None
        # self.__pid      = None
        # Default tracking mode
        self.__mode_io  = True
        self.__mode_mem = True
        self.__mode_net = True
        # Compile regex pattern
        self.__regex_pattern = re.compile(r"\s*") # Raw string to avoid the backslash plague

    def setTrackingInterval(self, interval):
        """
        Set tracking interval

        @param interval Tracking interval
        """
        self.__interval = interval

    def setOutputFilename(self, filename):
        """
        Set filename to write output

        @param filename Filename to write output
        """
        self.__out_file = filename

    # def setPid(self, pid):
    #     """
    #     Set process ID to track

    #     @param process ID
    #     """
    #     if not os.path.exists("/proc/%d" % pid):
    #         sys.stderr.write("ERROR: PID %d: No such process.\n" % pid)
    #         sys.exit(1)
    #     self.__pid = pid

    def setTrackingMode(self, io = False, mem = False, net = False):
        """
        Set tracking mode

        @param io  True if track disk I/O
        @param mem True if track memory usage
        @param net True if track network communications
        """
        self.__mode_io  = io
        self.__mode_mem = mem
        self.__mode_net = net

    def start(self):
        """
        Start tracking
        """
        # Initialize valiables for analyzing "/proc/diskstats"
        if self.__mode_io:
            total_data = self.__getIOTotalData()
            self.__io_read_bytes_begin  = total_data["total_read_bytes"]
            self.__io_write_bytes_begin = total_data["total_write_bytes"]
        # Initialize valiables for analyzing "/proc/net/dev"
        if self.__mode_net:
            total_data = self.__getNetTotalData()
            self.__net_recv_total_bytes_begin = total_data["total_recv_bytes"]
            self.__net_send_total_bytes_begin = total_data["total_send_bytes"]
        # Start tracking
        self.__track()

    def stop(self):
        """
        Stop tracking
        """
        self.__stop_flag = True
        if self.__out_file != None:
            fout = open(self.__out_file, "w")
            json.dump(self.__tracked_data, fout, indent = 2, separators = (",", ": "))
            fout.close()

    def __track(self):
        """
        Track INA219 repeatedly
        """
        while not self.__stop_flag:
            begin = datetime.today()
            tracked_data = self.__getTrackedData()
            if self.__out_file != None:
                self.__tracked_data.append(tracked_data)
            else:
                print json.dumps(tracked_data, indent = 2, separators = (",", ": "))
            end = datetime.today()

            diff = self.__interval - (end - begin).total_seconds()
            if diff < 0: diff = 0
            time.sleep(diff)

    def __getTrackedData(self):
        """
        Get data from "/proc"

        @return Tracked data
        """
        data = {}
        now = datetime.today()
        if self.__mode_io:  data_io  = self.__getIOData()
        if self.__mode_mem: data_mem = self.__getMemData()
        if self.__mode_net: data_net = self.__getNetData()
        data["date"] = Utils.formatDatetime(now)
        if self.__mode_io:  data["io"]  = data_io
        if self.__mode_mem: data["mem"] = data_mem
        if self.__mode_net: data["net"] = data_net
        return data

    def __getIOData(self):
        """
        Get disk I/O data

        @return Disk I/O data
        """
        total_data = self.__getIOTotalData()
        return {
            "read_bytes" : total_data["total_read_bytes"]  - self.__io_read_bytes_begin,
            "write_bytes": total_data["total_write_bytes"] - self.__io_write_bytes_begin
        }

    def __getMemData(self):
        """
        Get memory usage data

        @return Memory usage data
        """
        fin = open("/proc/meminfo", "r")
        meminfo = fin.readlines()
        fin.close()
        return {
            "used_kilobytes": int(meminfo[MEMINFO_ROW_TOTAL][9:-3].strip()) - int(meminfo[MEMINFO_ROW_FREE][8:-3].strip())
        }

    def __getNetData(self):
        """
        Get network communications data

        @return Network communications data
        """
        total_data = self.__getNetTotalData()
        return {
            "recv_bytes": total_data["total_recv_bytes"] - self.__net_recv_total_bytes_begin,
            "send_bytes": total_data["total_send_bytes"] - self.__net_send_total_bytes_begin
        }

    def __getIOTotalData(self):
        """
        Get data from "/proc/diskstats"

        @return Analyzed data
        """
        fin = open("/proc/diskstats", "r")
        diskstats = fin.readlines()
        fin.close()
        diskstats = self.__regex_pattern.split(diskstats[DISKSTATS_ROW].strip())
        return {
            "total_read_bytes" : int(diskstats[DISKSTATS_COL_READ])  * SECTOR_SIZE,
            "total_write_bytes": int(diskstats[DISKSTATS_COL_WRITE]) * SECTOR_SIZE
        }

    def __getNetTotalData(self):
        """
        Get data from "/proc/net/dev"

        @return Analyzed data
        """
        fin = open("/proc/net/dev", "r")
        net_dev = fin.readlines()
        fin.close()
        recv_bytes = 0
        send_bytes = 0
        for row in [NET_DEV_ROW_WLAN0, NET_DEV_ROW_LO, NET_DEV_ROW_ETH0]:
            line = self.__regex_pattern.split(net_dev[row].strip())
            recv_bytes += int(line[NET_DEV_COL_RECV])
            send_bytes += int(line[NET_DEV_COL_SEND])
        return {
            "total_recv_bytes": recv_bytes,
            "total_send_bytes": send_bytes
        }

def SIGINTHandler(signum, frame):
    """
    Signal SIGINT handler
    """
    global controller
    controller.stop()

def exec_track(flags):
    """
    Execute command: track

    @param flags Result of parsing argv
    """

    # Instantiate controller
    global controller
    controller = TrackController()

    # Set tracking interval
    controller.setTrackingInterval(flags.interval)

    # Set output filename
    if flags.out_file != None:
        controller.setOutputFilename(flags.out_file)

    # Set process id to track
    # if flags.pid != None:
    #     controller.setPid(flags.pid)

    # Set tracking mode
    controller.setTrackingMode(io  = flags.mode_io,
                               mem = flags.mode_mem,
                               net = flags.mode_net)

    # Print message
    print "Start tracking..."
    print 'Press "Ctrl + c" to quit.'

    # Handle SIGINT
    signal.signal(signal.SIGINT, SIGINTHandler)

    # Start tracking
    controller.start()
