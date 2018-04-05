# Average the experimental results according to the specified colume.
# this program is same as avesultgraph-bread.py and avesultgraph-oppo.py
# use avesultgraph-bread.py and avesultgraph-oppo.py because the value of x,y axios are is different.
# this program maybe use for backuping.
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
                conNumOutInt = conNumOutInt + float(sortDataList[j][2].strip())
                Delay = Delay + float(sortDataList[j][3].strip())
                numOutInt = numOutInt + float(sortDataList[j][4].strip())
                IntPLR = IntPLR + float(sortDataList[j][8].strip())
                DataPLR = DataPLR + float(sortDataList[j][9].strip())
                PLR = PLR + float(sortDataList[j][10].strip())
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
# Generate average data for averaging data in x-axios is the of consumer
def genGraphData(dataFilePath, dataFileDir, aveCol):
    dataFileList = sortDataFile (dataFilePath, dataFileDir)
    colors = ["b","g","r","y","b"]
    cmap = get_cmap(len(dataFileList)) #generate different color
    conNOI_1 = []
    conNOI_3 = []
    conNOI_5 = []
    conNOI_7 = []
    conNOI_9 = []
    delay_1 = []
    delay_3 = []
    delay_5 = []
    delay_7 = []
    delay_9 = []
    numOutInt_1 = []
    numOutInt_3 = []
    numOutInt_5 = []
    numOutInt_7 = []
    numOutInt_9 = []
    intPLR_1 = []
    intPLR_3 = []
    intPLR_5 = []
    intPLR_7 = []
    intPLR_9 = []
    for dataFileName in dataFileList:
        conNodes, aveConNumOutInt, aveDelay, aveNumOutInt, aveIntPLR, aveDataPLR, avePLR = \
        aveStatResult(dataFilePath, dataFileDir, dataFileName, aveCol)
        conNOI_1.append(aveConNumOutInt[0])
        conNOI_3.append(aveConNumOutInt[1])
        conNOI_5.append(aveConNumOutInt[2])
        conNOI_7.append(aveConNumOutInt[3])
        conNOI_9.append(aveConNumOutInt[4])
        delay_1.append(aveDelay[0])
        delay_3.append(aveDelay[1])
        delay_5.append(aveDelay[2])
        delay_7.append(aveDelay[3])
        delay_9.append(aveDelay[4])
        numOutInt_1.append(aveNumOutInt[0])
        numOutInt_3.append(aveNumOutInt[1])
        numOutInt_5.append(aveNumOutInt[2])
        numOutInt_7.append(aveNumOutInt[3])
        numOutInt_9.append(aveNumOutInt[4])
        intPLR_1.append(aveIntPLR[0])
        intPLR_3.append(aveIntPLR[1])
        intPLR_5.append(aveIntPLR[2])
        intPLR_7.append(aveIntPLR[3])
        intPLR_9.append(aveIntPLR[4])
    aveConNOI_1 = 0
    aveConNOI_3 = 0
    aveConNOI_5 = 0
    aveConNOI_7 = 0
    aveConNOI_9 = 0
    aveDelay_1 = 0
    aveDelay_3 = 0
    aveDelay_5 = 0
    aveDelay_7 = 0
    aveDelay_9 = 0
    aveNumOutInt_1 = 0
    aveNumOutInt_3 = 0
    aveNumOutInt_5 = 0
    aveNumOutInt_7 = 0
    aveNumOutInt_9 = 0
    aveIntPLR_1 = 0
    aveIntPLR_3 = 0
    aveIntPLR_5 = 0
    aveIntPLR_7 = 0
    aveIntPLR_9 = 0
    i = 0
    while i < 5:
        aveConNOI_1 = aveConNOI_1 + float(conNOI_1[i])
        aveConNOI_3 = aveConNOI_3 + float(conNOI_3[i])
        aveConNOI_5 = aveConNOI_5 + float(conNOI_5[i])
        aveConNOI_7 = aveConNOI_7 + float(conNOI_7[i])
        aveConNOI_9 = aveConNOI_9 + float(conNOI_9[i])
        aveDelay_1 = aveDelay_1 + float(delay_1[i])
        aveDelay_3 = aveDelay_3 + float(delay_3[i])
        aveDelay_5 = aveDelay_5 + float(delay_5[i])
        aveDelay_7 = aveDelay_7 + float(delay_7[i])
        aveDelay_9 = aveDelay_9 + float(delay_9[i])
        aveNumOutInt_1 = aveNumOutInt_1 + float(numOutInt_1[i])
        aveNumOutInt_3 = aveNumOutInt_3 + float(numOutInt_3[i])
        aveNumOutInt_5 = aveNumOutInt_5 + float(numOutInt_5[i])
        aveNumOutInt_7 = aveNumOutInt_7 + float(numOutInt_7[i])
        aveNumOutInt_9 = aveNumOutInt_9 + float(numOutInt_9[i])
        aveIntPLR_1 = aveIntPLR_1 + float(intPLR_1[i])
        aveIntPLR_3 = aveIntPLR_3 + float(intPLR_3[i])
        aveIntPLR_5 = aveIntPLR_5 + float(intPLR_5[i])
        aveIntPLR_7 = aveIntPLR_7 + float(intPLR_7[i])
        aveIntPLR_9 = aveIntPLR_9 + float(intPLR_9[i])
        i = i + 1
    aveConNOI_1 = aveConNOI_1 / 5
    aveConNOI_3 = aveConNOI_3 / 5
    aveConNOI_5 = aveConNOI_5 / 5
    aveConNOI_7 = aveConNOI_7 / 5
    aveConNOI_9 = aveConNOI_9 / 5
    aveDelay_1 = aveDelay_1 / 5
    aveDelay_3 = aveDelay_3 / 5
    aveDelay_5 = aveDelay_5 / 5
    aveDelay_7 = aveDelay_7 / 5
    aveDelay_9 = aveDelay_9 / 5
    aveNumOutInt_1 = aveNumOutInt_1 / 5
    aveNumOutInt_3 = aveNumOutInt_3 / 5
    aveNumOutInt_5 = aveNumOutInt_5 / 5
    aveNumOutInt_7 = aveNumOutInt_7 / 5
    aveNumOutInt_9 = aveNumOutInt_9 / 5
    aveIntPLR_1 = aveIntPLR_1 / 5
    aveIntPLR_3 = aveIntPLR_3 / 5
    aveIntPLR_5 = aveIntPLR_5 / 5
    aveIntPLR_7 = aveIntPLR_7 / 5
    aveIntPLR_9 = aveIntPLR_9 / 5
    aveConNumOutInt = []
    aveDelay = []
    aveNumOutInt = []
    aveIntPLR = []
    aveConNumOutInt.append(aveConNOI_1)
    aveConNumOutInt.append(aveConNOI_3)
    aveConNumOutInt.append(aveConNOI_5)
    aveConNumOutInt.append(aveConNOI_7)
    aveConNumOutInt.append(aveConNOI_9)
    aveDelay.append(aveDelay_1)
    aveDelay.append(aveDelay_3)
    aveDelay.append(aveDelay_5)
    aveDelay.append(aveDelay_7)
    aveDelay.append(aveDelay_9)
    aveNumOutInt.append(aveNumOutInt_1)
    aveNumOutInt.append(aveNumOutInt_3)
    aveNumOutInt.append(aveNumOutInt_5)
    aveNumOutInt.append(aveNumOutInt_7)
    aveNumOutInt.append(aveNumOutInt_9)
    aveIntPLR.append(aveIntPLR_1)
    aveIntPLR.append(aveIntPLR_3)
    aveIntPLR.append(aveIntPLR_5)
    aveIntPLR.append(aveIntPLR_7)
    aveIntPLR.append(aveIntPLR_9)
    aveDataPLR = 0
    avePLR = 0
    return conNodes, aveConNumOutInt, aveDelay, aveNumOutInt, aveIntPLR, aveDataPLR, avePLR


# Draw statistical graph
def drawStatGraph(dataFilePath, dataFileDir1, dataFileDir2, aveCol):
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
    plt1.axis([0, 10, 5, 10])
    plt2.axis([0, 10, 2, 8])
    plt3.axis([0, 10, 0, 150])
    plt4.axis([0, 10, 1, 3])
    labelChar = "Bread Crumb"
    conNodes, aveConNumOutInt, aveDelay, aveNumOutInt, aveIntPLR, aveDataPLR, avePLR = \
    genGraphData(dataFilePath, dataFileDir1, aveCol)
    print aveIntPLR
    plt1.plot(conNodes, aveConNumOutInt, color='blue', linestyle='solid',label = labelChar, marker='s',markerfacecolor='blue', markersize=10)
    plt2.plot(conNodes, aveDelay, color='blue', linestyle='solid', label = labelChar, marker='s', markerfacecolor='blue', markersize=10)
    plt3.plot(conNodes, aveNumOutInt, color='blue', linestyle='solid', label = labelChar, marker='s', markerfacecolor='blue', markersize=10)
    plt4.plot(conNodes, aveIntPLR, color='blue', linestyle='solid', label = labelChar, marker='s', markerfacecolor='blue', markersize=10)
    labelChar = "Oppo"
    conNodes, aveConNumOutInt, aveDelay, aveNumOutInt, aveIntPLR, aveDataPLR, avePLR = \
    genGraphData(dataFilePath, dataFileDir2, aveCol)
    # extract the number of nodes according to the data file name
    plt1.plot(conNodes, aveConNumOutInt, color='red', linestyle='solid', label = labelChar,marker='s',markerfacecolor='red', markersize=10)
    plt2.plot(conNodes, aveDelay, color='red', linestyle='solid', label = labelChar,marker='s', markerfacecolor='red', markersize=10)
    plt3.plot(conNodes, aveNumOutInt, color='red', linestyle='solid',label=labelChar, marker='s', markerfacecolor='red', markersize=10)
    plt4.plot(conNodes, aveIntPLR, color='red', linestyle='solid', label = labelChar,marker='s', markerfacecolor='red', markersize=10)
    plt1.set_title('The Number of Interest Packet')
    plt2.set_title('Average Delay')
    plt3.set_title('The Total Number of Interest Packet')
    plt4.set_title('Packet Loss Rate of Interest Packet')
    plt1.legend(loc='upper left')
    plt2.legend(loc='upper lef')
    plt3.legend(loc='upper left')
    plt4.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':
    setLogLevel('info')
    dataFilePath = os.path.abspath(os.path.dirname(sys.argv[0]))
#    drawStatGraph(dataFilePath, 'oppo', 0)
    drawStatGraph(dataFilePath, 'bread', 'oppo', 0)
