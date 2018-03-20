import re
import time
from time import strftime
# Calculate packet loss ratio
input_file = open("communicateData.dat", "r")
packLossData_file = open ("packLossData.dat", "a")
delayData_file = open ("delayData.dat", "a")
firstGoInterest = True
firstInData = True
numOutInterest = 0 # The number of interest pactet that successfully sent
numInData = 0 # The number of data packets that received
lineField = []
delayData = ""
firstGoIntTime = ""
firstInDataTime = ""
for line in input_file:
    lineString = ""
    i=0
    # read a line data and generate list of fields
    while i < len(line):
        if not (line[i] == " "):
            lineString = lineString + str(line[i])
        else:
            lineField.append(lineString)
            lineString = ""
        i = i+1
    if lineField[3] == "onOutgoingInterest":
        numOutInterest = numOutInterest + 1
        if firstGoInterest:
            firstGoIntTime = lineField[0]
            firstGoInterest = False
    if lineField[3] == "onIncomingData":
        numInData = numInData +1
        if firstInData:
            firstInDataTime = lineField[0]
            firstInData = False
    lineField = []

if firstGoInterest:
    firstGoIntTime = "9999999999.999999"
if firstInData:
    firstInDataTime = "9999999999.999999"
packLossData = "sta1" + " " + "10" + " " + str(numOutInterest) + " " + str(numInData)
delayData = "sta1" + " " + firstGoIntTime + " " + firstInDataTime
packLossData_file.write("{0}\n".format(packLossData))
delayData_file.write("{0}\n".format(delayData))
packLossData_file.close()
delayData_file.close()
print("All done!")
