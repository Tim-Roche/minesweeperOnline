#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      TimRo
#
# Created:     24/08/2018
# Copyright:   (c) TimRo 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from fileManagement import fileManagement
import time

class testing():
    def __init__(self, fileLocation):
        self._start = 0
        self._stop = 0
        self._ttime = 0
        self._times = []
        self._average = 0
        self._file = fileManagement(fileLocation)
    def start(self):
        self._start = time.time()
    def stop(self):
        self._stop = time.time()
        self._ttime = self._stop - self._start
        return(self._ttime)
    def update(self):
        self._times.append(self._ttime)
    def avg(self):
        total = 0
        amount = 0
        for t in self._times:
            total += t
            amount += 1
        self._average = total / amount
        return(self._average)
    def saveAverage(self):
        self._file.appendToFile(str(self._average)+"\n")

