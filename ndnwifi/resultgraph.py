import re
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
from mininet.log import setLogLevel, output, info

def drawGraph(dataPath, dataDir):
    dataList = os.listdir("%s/data/%s" % (dataPath, dataDir))
    readDataFile(dataList)
    print dataList
    sortDataFile(dataList)
    print dataList
    genGraphData(dataPath, dataDir, dataList)
    drawStatGraph(dataPath, dataDir)
    

def readDataFile(dataFileList):
    # Delete other files that they are "statResult" from a data file list
    i = 0
    for dataFileName in dataFileList:
        if not ("statResult" in dataFileName):
            dataFileList.pop(i)
        i = i+1

def sortDataFile(dataFileList):
    # Sort data file by using bubble algorithm
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
                print int(nodeNumber_j1.strip()), "||", int(nodeNumber_j.strip())
                if int(nodeNumber_j1.strip()) < int(nodeNumber_j.strip()):
                    tmp = dataFileList[j]
                    dataFileList[j] = dataFileList[j+1]
                    dataFileList[j+1] = tmp
                j = j+1
        except:
            pass
        i = i+1
# Calculate graph data from statistic data file
def genGraphData(dataFilePath, dataFileDir, dataFileList):
    graphData_file = open ("%s/data/%s/graphData.dat" % (dataFilePath,dataFileDir), "a")
    for statDataFileName in dataFileList:
        try:
            startChar = statDataFileName.index("-") + len("-")
            endChar = statDataFileName.index(".", startChar)
            nodeNumber = statDataFileName[startChar : endChar]
            statData_file = open ("%s/data/%s" % (dataFilePath, statDataFileName), "r")
            pacLossRate = 0
            intSatRate = 0
            aveDelay = 0
            expNumber = 0
            lineField = []
            for line in statData_file:
                expNumber = expNumber + 1
                lineString = ""
                i=0
                # read a line data and generate list of fields
                while i < len(line):
                    if not (line[i] == " "):
                        lineString = lineString + str(line[i].strip())
                        if i == len(line)-1:
                            lineField.append(lineString.strip())
                    else:
                        lineField.append(lineString.strip())
                        lineString = ""
                    i = i+1
                pacLossRate = pacLossRate + float(lineField[2])
                intSatRate = intSatRate + float(lineField[3])
                aveDelay = aveDelay + float(lineField[4])
                lineField = []
            pacLossRate = pacLossRate / expNumber
            intSatRate = intSatRate / expNumber
            aveDelay = aveDelay /expNumber
            # Get the number of nodes according to the file name of a statistical data file. 
            graphData = nodeNumber + " " + str(pacLossRate) + " " + str(intSatRate) + " " + str(aveDelay)
            graphData_file.write("{0}\n".format(graphData))
            statData_file.close()
        except:
            pass
    graphData_file.close()
# Draw statistical graph
def drawStatGraph(dataFilePath,graphDataDir):
    nodes=[]
    aveDelay=[]
    pacLossRate=[]
    intSatRate=[]
    input_file = open("%s/data/%s/graphData.dat" % (dataFilePath,graphDataDir), "r")
    lineField=[]
    for line in input_file:
        lineString = ""
        i=0
        # read a line data and generate list of fields
        while i < len(line):
            if not (line[i] == " "):
                lineString = lineString + str(line[i].strip())
                if i == len(line)-1:
                    lineField.append(lineString.strip())
            else:
                lineField.append(lineString.strip())
                lineString = ""
            i = i+1
        nodes.append(int(lineField[0]))
        pacLossRate.append(float(lineField[1]))
        intSatRate.append(float(lineField[2]))
        aveDelay.append(float(lineField[3]))
        lineField=[]
    input_file.close()
    # setting a style to use
    plt.style.use('fivethirtyeight')
    # create a figure
    fig = plt.figure()
    # define subplots and their positions in figure
    plt1 = fig.add_subplot(221)
    plt2 = fig.add_subplot(222)
    plt3 = fig.add_subplot(223)
    #plt4 = fig.add_subplot(224)
    y1 = [0.3,0.2,0.7]
    x1 = [6,11,21]
    # plotting the line 1 points 

    plt1.axis([5, 30, 0, 1])
    plt2.axis([5, 30, 0, 2])
    plt3.axis([5, 30, 0, 1000])
    plt1.plot(nodes, pacLossRate, color='blue', linestyle='solid', label = "PLR",marker='x', markerfacecolor='blue', markersize=12)
    plt1.plot(x1, y1, label = "line 1")

    plt2.plot(nodes, intSatRate, color='green', linestyle='solid', label = "ISR",marker='v', markerfacecolor='green', markersize=12)
    plt2.plot(x1, y1, label = "line 1")

    plt3.plot(nodes, aveDelay, color='red', linestyle='solid',label="AVD", marker='s', markerfacecolor='red', markersize=12)
    plt1.set_title('packet Loss Rate')
    plt2.set_title('Interest Satisfaction Rate')
    plt3.set_title('Average Delay')
    #plt1.xlabel('nodes')
    #plt1.ylabel('ISR')
    #plt1.title('Average Delay')
    plt1.legend(loc='upper left')
    plt2.legend(loc='upper left')
    plt3.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':

    setLogLevel('info')
    dataFilePath = os.path.abspath(os.path.dirname(sys.argv[0]))
    drawGraph(dataFilePath, 'oppo')
