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
        j=0
        # read a line data and generate list of fields
        while j < len(line):
            if not (line[j] == " "):
                lineString = lineString + str(line[j].strip())
                if j == len(line)-1:
                    lineField.append(lineString.strip())
            else:
                lineField.append(lineString.strip())
                lineString = ""
            j = j+1
        dataLine.append(lineField)
        lineField = []
    return dataLine

# Sort two dimession List
def listSort(dataList, sortCol):
    "sortCol: the specified colume used for sorting."
    i = 0
    while i < len(dataList)-1:
        try:
            j = 0
            while j < len(dataList)-1-i:
                if float(dataList[j+1][sortCol]) < float(dataList[j][sortCol].strip()):
                    tmp = dataList[j]
                    dataList[j] = dataList[j+1]
                    dataList[j+1] = tmp
                j = j+1
        except:
            pass
        i = i+1
    return dataList
#Calculate average statistic result in one experiment.
def aveStatResult(dataFilePath, dataFileDir, dataFileName, aveCol):
    "aveCol: the specified colume used for calculating a average value"
    # Caculate average value according to a specified column
    # Read data file and generate a list
    dataList = readFileData(dataFilePath, dataFileDir, dataFileName)
    sortDataList = listSort(dataList, aveCol)
    conNodes = []
    aveConNumOutInt = []
    aveDelay = []
    aveNumOutInt = []
    aveIntPLR = []
    aveDataPLR = []
    avePLR = []
    i = 0
    while i < len(sortDataList):
        conNumOutInt = float(sortDataList[i][2].strip())
        Delay = float(sortDataList[i][3].strip())
        numOutInt = float(sortDataList[i][4].strip())
        IntPLR = float(sortDataList[i][8].strip())
        DataPLR = float(sortDataList[i][9].strip())
        PLR = float(sortDataList[i][10].strip())
        tmp = sortDataList[i][aveCol].strip()
        j = i+1
        n = 1
        flag = True
        while (j < len(sortDataList)) and flag:
            if sortDataList[j][aveCol] == tmp:
                n = n + 1
                conNumOutInt = float(sortDataList[i][2].strip())
                Delay = float(sortDataList[i][3].strip())
                numOutInt = float(sortDataList[i][4].strip())
                IntPLR = float(sortDataList[i][8].strip())
                DataPLR = float(sortDataList[i][9].strip())
                PLR = float(sortDataList[i][10].strip())
                j = j+1
            else:
                flag = False
        i = j
        conNodes.append(int(tmp))
        aveConNumOutInt.append(conNumOutInt/n)
        aveDelay.append(Delay/n)
        aveNumOutInt.append(numOutInt/n)
        aveIntPLR.append(IntPLR/n)
        aveDataPLR.append(DataPLR/n)
        avePLR.append(PLR/n)

    return conNodes, aveConNumOutInt, aveDelay, aveNumOutInt, aveIntPLR, aveDataPLR, avePLR
# randomly generate color
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

# Draw statistical graph
def drawStatGraph(dataFilePath, dataFileDir, aveCol):
    # setting a style to use
    plt.style.use('fivethirtyeight')
    # create a figure
    fig = plt.figure()
    # define subplots and their positions in figure
    plt1 = fig.add_subplot(221, axisbg='white')
    plt2 = fig.add_subplot(222, axisbg='white')
    plt3 = fig.add_subplot(223, axisbg='white')
    plt4 = fig.add_subplot(224, axisbg='white')
    # plotting the line 1 points
    plt1.axis([0, 10, 0, 15])
    plt2.axis([0, 10, 0, 10])
    plt3.axis([0, 10, 0, 25])
    plt4.axis([0, 10, 0, 1.0])
    dataFileList = sortDataFile (dataFilePath, dataFileDir)
    i = 5
    colors = ["b","g","r","y","b"]
    cmap = get_cmap(len(dataFileList)) #generate different color
    for dataFileName in dataFileList:
        conNodes, aveConNumOutInt, aveDelay, aveNumOutInt, aveIntPLR, aveDataPLR, avePLR = \
        aveStatResult(dataFilePath, dataFileDir, dataFileName, aveCol)
        # extract the number of nodes according to the data file name
        startChar = dataFileName.index("-") + len("-")
        endChar = dataFileName.index(".", startChar)
        nodeNumber = dataFileName[startChar : endChar]
        labelChar = "nodes=" + nodeNumber
        colorN = int(nodeNumber)/5 - 1
        color = colors[colorN]
        plt1.plot(conNodes, aveConNumOutInt, color=color, linestyle='solid', label = labelChar,marker='s',markerfacecolor=cmap(i), markersize=10)
        plt2.plot(conNodes, aveDelay, color=color, linestyle='solid', label = labelChar,marker='s', markerfacecolor=cmap(i), markersize=10)
        plt3.plot(conNodes, aveNumOutInt, color=color, linestyle='solid',label=labelChar, marker='s', markerfacecolor=cmap(i), markersize=10)
        plt4.plot(conNodes, aveIntPLR, color=color, linestyle='solid', label = labelChar,marker='s', markerfacecolor=cmap(i), markersize=10)
#        plt4.plot(conNodes, dataPacLossRate, color=cmap(i), linestyle='solid', label = labelChar,marker='s', markerfacecolor=cmap(i), markersize=10)
#        plt4.plot(conNodes, PacLossRate, color=cmap(i), linestyle='solid',label=labelChar, marker='s', markerfacecolor=cmap(i), markersize=10)
        i = i + 10
     
#    nodes,pacLossRate, intSatRate, aveDelay = genAxiosData(dataFilePath, graphDataDir2)
#    plt1.plot(nodes, pacLossRate, color='blue', linestyle='dashed')
#    plt2.plot(nodes, intSatRate, color='green', linestyle='dashed')
#    plt3.plot(nodes, aveDelay, color='red', linestyle='dashed')
    plt1.set_title('The Number of Interest Packet')
    plt2.set_title('Average Delay')
    plt3.set_title('The Total Number of Interest Packet')
    plt4.set_title('Packet Loss Rate of Interest Packet')
    #plt1.xlabel('nodes')
    #plt1.ylabel('ISR')
    #plt1.title('Average Delay')
    plt1.legend(loc='upper left')
    plt2.legend(loc='upper right')
    plt3.legend(loc='upper left')
    plt4.legend(loc='upper right')
    plt.show()

if __name__ == '__main__':
    setLogLevel('info')
    dataFilePath = os.path.abspath(os.path.dirname(sys.argv[0]))
#    drawStatGraph(dataFilePath, 'oppo', 0)
    drawStatGraph(dataFilePath, 'bread', 0)
