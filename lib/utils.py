#!/usr/bin/python
# coding: UTF-8

"""
Utilities for internal implementation
"""

__author__  = "Hiroyuki Matsuo <h-matsuo@ist.osaka-u.ac.jp>"

class Utils:
    """
    Utility class for internal implementation
    """

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
