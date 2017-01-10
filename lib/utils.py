#!/usr/bin/python
# coding: UTF-8

"""
Utilities for internal implementation
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

from argparse import ArgumentParser
import sys

class Utils:
    """
    Utility class for internal implementation
    """

    prog_name = "procTracker.py"

    @staticmethod
    def getUsage():
        """
        Get usage
        """
        fin = open("usage.txt", "r")
        usage = fin.read()
        fin.close()
        return usage

    @staticmethod
    def formatDatetime(datetime_obj):
        """
        Receive a datetime.datetime object and format it like "2016/09/22-09:59:30.005"
    
        @param datetime_obj datetime.datetime object
        @return Formatted string
        """
        return datetime_obj.strftime("%Y/%m/%d-%H:%M:%S.") + "%03d" % (datetime_obj.microsecond // 1000)

    @staticmethod
    def parseArgv(argv):
        """
        Received the command line arguments and parse them

        @param argv Command line arguments
        @return Result of parsing
        """
        parser = ArgumentParser(prog        = Utils.prog_name,
                                description = "track disk I/O, memory usage and network communications")

        parser.add_argument("-i",
                            type    = float,
                            default = 1.0,
                            metavar = "<interval>",
                            dest    = "interval",
                            help    = "set the tracking interval in [sec]; default = %(default)s")
        parser.add_argument("-o",
                            metavar = "<filename>",
                            dest    = "out_file",
                            help    = "write output to %(metavar)s")
        # parser.add_argument("-p",
        #                     type    = int,
        #                     metavar = "<pid>",
        #                     dest    = "pid",
        #                     help    = "specify the target process id to track; default = the whole device")

        group = parser.add_argument_group("tracking mode")
        group.add_argument("--all",
                           action = "store_true",
                           dest   = "mode_all",
                           help   = "track all of the disk I/O, memory usage and network communications; default mode")
        group.add_argument("--io",
                           action = "store_true",
                           dest   = "mode_io",
                           help   = "track disk I/O; allowed with --mem and --net")
        group.add_argument("--mem",
                           action = "store_true",
                           dest   = "mode_mem",
                           help   = "track memory usage; allowed with --io and --net")
        group.add_argument("--net",
                           action = "store_true",
                           dest   = "mode_net",
                           help   = "track network communications; allowed with --io and --mem")

        result = parser.parse_args()

        if result.interval <= 0:
            parser.print_usage(file = sys.stderr)
            sys.stderr.write("%s: error: interval must be more than 0\n" % Utils.prog_name)
            sys.exit(1)

        # if result.pid != None and result.pid < 1:
        #     parser.print_usage(file = sys.stderr)
        #     sys.stderr.write("%s: error: process id must be 1 or more\n" % Utils.prog_name)
        #     sys.exit(1)

        if result.mode_all and (result.mode_io or result.mode_mem or result.mode_net):
            parser.print_usage(file = sys.stderr)
            sys.stderr.write("%s: error: cannot use --all with --io, --mem and --net\n" % Utils.prog_name)
            sys.exit(1)

        # Default tracking mode is --all
        if not result.mode_io and not result.mode_mem and not result.mode_net:
            result.mode_all = True

        if result.mode_all:
            result.mode_io  = True
            result.mode_mem = True
            result.mode_net = True

        return result
