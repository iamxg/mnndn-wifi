import re
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
from mininet.log import setLogLevel, output, info

# Read the experimental result data file in a specfied directory and generate a list of data file name. 
def sortDataFile(dataFilePath, dataFileDir):
    dataFileList = os.listdir("%s/data/%s" % (dataFilePath, dataFileDir))
    # delete file names that are not statistic result.
    i = 0
    for dataFileName in dataFileList:
        if not ("statResult" in dataFileName):
            dataFileList.pop(i)
        i = i+1
    # Sort data file according to file name (the number of nodes) by using bubble algorithm
    i = 0
    while i < len(dataFileList)-1:
        try:
            j = 0
            while j < len(dataFileList)-1-i:
                fileName = dataFileList[j].strip()
                startChar = fileName.index("-") + len("-")
                endChar = fileName.index(".", startChar)
                nodeNumber_j = fileName[startChar : endChar]
                # after j
                fileName=dataFileList[j+1].strip()
                startChar = fileName.index("-") + len("-")
                endChar = fileName.index(".", startChar)
                nodeNumber_j1 = fileName[startChar : endChar]
                if int(nodeNumber_j1.strip()) < int(nodeNumber_j.strip()):
                    tmp = dataFileList[j]
                    dataFileList[j] = dataFileList[j+1]
                    dataFileList[j+1] = tmp
                j = j+1
        except:
            pass
        i = i+1
    return dataFileList

# Read a data file and convert to two dimession List.
def readFileData(dataFilePath, dataFileDir, dataFileName):
    data_file = open ("%s/data/%s/%s" % (dataFilePath, dataFileDir, dataFileName), "r")
    lineField = []
    dataLine = []
    for line in data_file:
        lineString = ""
        k = 0 # count the number of blanks in one line 
        j=0
        # read a line data and generate list of fields
        while j < len(line):
            if not (line[j] == " "):
                lineString = lineString + str(line[j].strip())
                if j == len(line)-1:
                    lineField.append(lineString.strip())
            else:
                k = k + 1
                if k == 3:
                    lineField.append("0")
                lineField.append(lineString.strip())
                lineString = ""
            j = j+1
        dataLine.append(lineField)
        lineField = []
    return dataLine
def fileAddField(dataFilePath, dataLine, dataFileName):
    new_data_file = open ("%s/data/oppo-new/%s" % (dataFilePath, dataFileName), "a")
    i = 0
    lineString = ""
    while i < len(dataLine):
        dataLine[i][2] = dataLine[i][4].strip()
        try:
            j = 0
            while j < len(dataLine[i]):
                lineString = lineString + " " + dataLine[i][j].strip()
                j = j+1
            lineStrig = lineString + " "
        except:
            pass
        i = i+1
        new_data_file.write("{0}\n".format(lineString))
        lineString = ""

if __name__ == '__main__':
    setLogLevel('info')
    dataFilePath = os.path.abspath(os.path.dirname(sys.argv[0]))
    dataLine = readFileData(dataFilePath, 'oppo-back', 'statResult-20.dat')
    fileAddField(dataFilePath, dataLine, 'statResult-20.dat')
#    drawStatGraph(dataFilePath, 'bread', 0)
