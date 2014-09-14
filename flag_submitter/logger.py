#!/usr/bin/python

import sys, time

class Logger:
    DEBUG = 1
    INFO = 2
    ERROR = 3
    LEVELS = ("", "DEBUG", "INFO ", "ERR")
    
    def __init__(self, name="", logfilename=None, level=0):
        self.name = name
        self.level = level
        if logfilename:
            self.logfile = open(logfilename, "a")
        else:
            self.logfile = None

    def log(self, level, msg, *args):
        t = time.localtime()
        formatted_message = "[%s %s %s] %s" % (
                self.name,
                self.LEVELS[level],
                ("%02d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)),
                (msg % args))
        if level >= self.level:
            print>>sys.stderr, formatted_message
        if self.logfile:
            print>>self.logfile, formatted_message

    def debug(self, msg, *args):
        self.log(self.DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(self.INFO, msg, *args)

    def error(self, msg, *args):
        self.log(self.ERROR, msg, *args)
