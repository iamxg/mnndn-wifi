# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.
import re
import time
import sys,os
import os.path
from itertools import cycle
from subprocess import call
from ndnwifi import WifiExperimentManager
from time import strftime

class wifiExperiment:
    def __init__(self, args):
        self.workDir = args["workDir"]
        self.isWiFi = args["isWiFi"]
        self.isVndn = args["isVndn"]
        self.isSumoVndn = args["isSumoVndn"]
        self.net = args["net"]
        self.convergenceTime = args["ctime"]
        self.nPings = args["nPings"]
        self.nConsumers=args["nConsumers"]
        self.strategy = args["strategy"]
        self.pctTraffic = args["pctTraffic"]
        self.nlsrSecurity = args["nlsrSecurity"]
        self.nodeSet = " " # for cars or stations 
        self.carSTASet = " " # for car station
        self.wlanFaceId =" "  # ID of wireless interface for a node
        # Used to restart pings on the recovered node if any
        self.pingedDict = {}

        if self.isWiFi:
            if self.isVndn or self.isSumoVndn:
                self.carSTASet = self.net.carsSTA
                self.nodeSet = self.net.cars
            else:
                self.nodeSet = self.net.stations
        else:
            self.nodeSet = self.net.hosts
    def start(self):
        self.setup()
        self.run()

    def setup(self):
        for host in self.nodeSet:
            # Set strategy
            host.nfd.setStrategy("/ndn/", self.strategy)

            # Start ping server
            host.cmd("ndnpingserver /ndn/" + str(host) + "-site/" + str(host) + " > ping-server &")

            # Create folder to store ping data
            host.cmd("mkdir ping-data")
        if not self.isWiFi:
            self.checkConvergence()
        else:
            self.createFib()
    # add the function to add route for stations in WiFi network
    def createFib(self, convergenceTime = None):
        if convergenceTime is None:
            convergenceTime = self.convergenceTime

        # Wait for convergence time period
        print "Waiting " + str(convergenceTime) + " seconds for convergence..."
        time.sleep(convergenceTime)
        print "...done"
        # To check whether converged and to create car/station FIB table
        didNetworkCoverge=True
        for sta in self.nodeSet:
            wlanFaceList = sta.cmd("nfdc face list | grep wlan")
            if "wlan" in wlanFaceList:
                self.wlanFaceId=re.search("faceid=(.*?) ", str(wlanFaceList)).group(1)
                sta.cmd("nfdc route add /ndnwifi/" + " " + self.wlanFaceId + " >> add-route.txt &")
                sta.cmd("mkdir peek-data")
            else:
               didNetworkCoverge = False
        # To check whether converged and to create car station FIB table
        if self.isVndn or self.isSumoVndn:
            for carsta in self.carSTASet:
                wlanFaceList = carsta.cmd("nfdc face list | grep wlan")
                if "wlan" in wlanFaceList:
                    self.wlanFaceId=re.search("faceid=(.*?) ", str(wlanFaceList)).group(1)
                    carsta.cmd("nfdc route add /ndnwifi/" + " " + self.wlanFaceId + " >> add-route.txt &")
                    carsta.cmd("mkdir peek-data")
                else:
                    didNetworkCoverge = False

        if didNetworkCoverge:
            print("WiFi network successfully converged.")
        else:
            print("WiFi network has not converged. Exiting...")
            self.net.stop()
            print('Cleaning up...')
            call(["nfd-stop"])
            call(["sudo", "mn", "--clean"])
            sys.exit(1)

    #To add a route point to the other stations
    def addRoute(self):
        for sta in self.nodeSet:
            wlanFaceList = sta.cmd("nfdc face list | grep wlan")
            if "wlan" in wlanFaceList:
                self.wlanFaceId=re.search("faceid=(.*?) ", str(wlanFaceList)).group(1)
                for other in self.nodeSet:
                    if sta.name != other.name:
                        sta.cmd("nfdc route add /ndn/" + str(other) + "-site/" + str(other) +" " + self.wlanFaceId + " >> add-route.txt &")
            else:
               didNetworkCoverge = False

    # Extract experimental data from log file
    def statisticData(self, consumerSet):
         "consumerSet: a set of consumers that randomly select from experiment module."
         if self.isWiFi:
             if self.isVndn or self.isSumoVndn:
                 self.extractData(self.net.carsSTA, consumerSet)
                 self.extractData(self.net.cars, consumerSet)
             else:
                 self.extractData(self.net.stations, consumerSet)
         else:
             self.extractData(self.net.hosts, consumerSet)
         if self.isWiFi:
             if self.isVndn or self.isSumoVndn:
                 self.statisticResult(self.net.carsSTA, consumerSet)
                 self.statisticResult(self.net.cars, consumerSet)
             else:
                 self.statisticResult(self.net.stations, consumerSet)
         else:
             self.statisticResult(self.net.hosts, consumerSet)

    def extractData(self, nodeSet, consumerSet):
        "nodeSet: a set of nodes in the network"
        experimentData_file = open ("%s/experimentData.dat" % self.workDir, "w")
        for sta in nodeSet:
            #dataFile = "%s" % self.workDir + "/" +str(sta)+ "/" + "communicateData.dat"
            dataFile = "{}/{}/communicateData.dat".format(self.workDir, sta)
            sta.cmd("cat {}.log | grep face={} > communicateData.dat".format(sta, self.wlanFaceId))
            input_file = open(dataFile, "r")
            firstGoInterest = True
            firstInData = True
            numOutInterest = 0 # The number of interest pactet that successfully sent
            numInData = 0 # The number of data packets that received
            lineField = []
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
                if lineField[3].strip() == "onOutgoingInterest":
                    numOutInterest = numOutInterest + 1
                    if firstGoInterest:
                        firstGoIntTime = lineField[0]
                        firstGoInterest = False
                if lineField[3].strip() == "onIncomingData":
                    numInData = numInData +1
                    if firstInData:
                        firstInDataTime = lineField[0]
                        firstInData = False
                lineField = []
            if firstGoInterest:
                firstGoIntTime = "9999999999.999999"
            if firstInData:
                firstInDataTime = "9999999999.999999"
            if sta in consumerSet:
                experimentData = str(sta) + " " + str(self.nPings) + " " + str(numOutInterest) + " " + str(numInData)
            else:
                experimentData = str(sta) + " " + "0"  + " " + str(numOutInterest) + " " + str(numInData)
            experimentData = experimentData + " " + str(firstGoIntTime) + " " + str(firstInDataTime)
            experimentData_file.write("{0}\n".format(experimentData))
            input_file.close()
        experimentData_file.close()
    # Generate the file used to save statistical data
    def statisticResult(self, nodeSet, consumerSet):
        #runProgramPath = os.path.abspath(os.path.dirname(sys.argv[0]))
        nodeNumber = str(len(nodeSet))
        statResult_file = open ("%s/data/oppo/statResult-%s.dat" % (self.workDir, nodeNumber), "a")
        input_file = open("%s/experimentData.dat" % self.workDir, "r")
        pacLossRate = 0
        intSatiRate = 0
        aveDelay = 0
        lineField = []
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
            if int(lineField[1].strip()) != 0:
                pacLossRate = pacLossRate + float(lineField[2].strip())/float(lineField[1].strip())
            if int(lineField[2].strip()) != 0:
                intSatiRate = intSatiRate + float(lineField[3].strip())/float(lineField[2].strip())
            if (lineField[4].strip() != "9999999999.999999") and (lineField[5].strip() != "9999999999.999999"):
                aveDelay = aveDelay + (float(lineField[5].strip())-float(lineField[4].strip()))
            lineField = []
        statResult = str(self.nConsumers) + " " + str(self.nPings) + " " + str(pacLossRate/self.nConsumers)\
                     + " " + str(intSatiRate/self.nConsumers) + " " + str(aveDelay/self.nConsumers)
        statResult_file.write("{0}\n".format(statResult))
        statResult_file.close()
        input_file.close()

    def checkConvergence(self, convergenceTime = None):
        if convergenceTime is None:
            convergenceTime = self.convergenceTime

        # Wait for convergence time period
        print "Waiting " + str(convergenceTime) + " seconds for convergence..."
        time.sleep(convergenceTime)
        print "...done"

        # To check whether all the nodes of NLSR have converged
        didNlsrConverge = True

        # Checking for convergence
        for host in self.nodeSet:
            statusRouter = host.cmd("nfdc fib list | grep site/%C1.Router/cs/")
            statusPrefix = host.cmd("nfdc fib list | grep ndn | grep site | grep -v Router")
            didNodeConverge = True
            for node in self.nodeSet:
                # Node has its own router name in the fib list, but not name prefix
                if ( ("/ndn/" + node.name + "-site/%C1.Router/cs/" + node.name) not in statusRouter or
                      host.name != node.name and ("/ndn/" + node.name + "-site/" + node.name) not in statusPrefix ):
                    didNodeConverge = False
                    didNlsrConverge = False

            host.cmd("echo " + str(didNodeConverge) + " > convergence-result &")

        if didNlsrConverge:
            print("NLSR has successfully converged.")
        else:
            print("NLSR has not converged. Exiting...")
            self.net.stop()
            sys.exit(1)

    def ping(self, source, dest, nPings):
        # Use "&" to run in background and perform parallel pings
        print "Scheduling ping(s) from %s to %s" % (source.name, dest.name)
        source.cmd("ndnping -t -c "+ str(nPings) + " /ndn/" + dest.name + "-site/" + dest.name + " >> ping-data/" + dest.name + ".txt &")
        time.sleep(0.2)

    def startPings(self):
        for host in self.nodeSet:
            for other in self.nodeSet:
                # Do not ping self
                if host.name != other.name:
                    self.ping(host, other, self.nPings)

    def failNode(self, host):
        print("Bringing %s down" % host.name)
        host.nfd.stop()

    def recoverNode(self, host):
        print("Bringing %s up" % host.name)
        host.nfd.start()
        host.nlsr.createFaces()
        host.nlsr.start()
        host.nfd.setStrategy("/ndn/", self.strategy)
        host.cmd("ndnpingserver /ndn/" + str(host) + "-site/" + str(host) + " > ping-server &")

    def startPctPings(self):
        nNodesToPing = int(round(len(self.nodeSet)*self.pctTraffic))-1
        print "Each node will ping %d node(s)" % nNodesToPing
        # Temporarily store all the nodes being pinged by a particular node
        nodesPingedList = []

        for host in self.nodeSet:

            # Create a circular list
            pool = cycle(self.nodeSet)

            # Move iterator to current node
            next(x for x in pool if host.name == x.name)

            # Track number of nodes to ping scheduled for this node
            nNodesScheduled = 0

            while nNodesScheduled < nNodesToPing:
                other = pool.next()

                # Do not ping self
                if host.name != other.name:
                    self.ping(host, other, self.nPings)
                    nodesPingedList.append(other)

                # Always increment because in 100% case a node should not ping itself
                nNodesScheduled = nNodesScheduled + 1

            self.pingedDict[host] = nodesPingedList
            nodesPingedList = []

    @staticmethod
    def register(name, experimentClass):
       WifiExperimentManager.register(name, experimentClass)
