#!/usr/bin/python
import re
import time
import sys
import signal
from mininet.log import info
from itertools import cycle
from subprocess import call
import random
from ndnwifi.experiments.wifiexperiment import wifiExperiment

def endExperiment():
    print('Cleaning up...')
    call(["nfd-stop"])
    call(["sudo", "mn", "--clean"])
    sys.exit(1)
class OpportunityExperiment(wifiExperiment):
    def __init__(self, args):
        wifiExperiment.__init__(self, args)
        self.producerNo = 0
        self.producerName = " "
        self.consumerName = " "
        self.producerSTA = " "
        self.consumerSTA = " "
    def signal_handler(signal, frame):
        print('Cleaning up...')
        call(["nfd-stop"])
        call(["sudo", "mn", "--clean"])
        sys.exit(1)

    def setup(self):
        # create Fib
        self.createFib()

    def run(self):
        # Randomly select a producuer
        # There are two wireless interface on one car in VNDN/SUMOVNDN.
        # One that is on carx is used for V2I communication and another one that is on carxSTA is used for V2V communication 
        if self.isVndn or self.isSumoVndn:
            self.producerNo = random.randrange(0, len(self.net.cars), 1)
            self.producerName=self.net.cars[self.producerNo]
            # For V2I communication in VNDN/SUMOVNDN
            producerIntf = "%s-wlan0" % self.producerName
            proDumpOutputFile="dump.%s" % producerIntf
            self.producerName.cmd("sudo ndndump -i %s > %s &" % (producerIntf, proDumpOutputFile))
            # For V2V communication in VNDN/SUMOVNDN
            self.producerSTA = self.net.carsSTA[self.producerNo]
            producerSTAIntf = "%s-wlan0" % self.producerSTA
            proSTAOutputFile="dump.%s" % producerSTAIntf
            self.producerSTA.cmd("sudo ndndump -i %s > %s &" % (producerSTAIntf, proSTAOutputFile))
        else:
            #For Communications between stations in Ad hoc networks
            self.producerNo = random.randrange(0, len(self.net.stations), 1)
            self.producerName = self.net.stations[self.producerNo]
            producerIntf = "%s-wlan0" % self.producerName
            proDumpOutputFile = "dump.%s" % producerIntf
            self.producerName.cmd("sudo ndndump -i %s > %s &" % (producerIntf, proDumpOutputFile))
        print "The randomly seleted producer %s is producing a content chunck..." % self.producerName

        # Randomly select several consumers
        consumerN = self.nConsumers # The number of consumer that specificed in advance.
        if self.isVndn or self.isSumoVndn:
            # nodeList and self.net.cars use the same memory space if [:] is not used
            nodeList = self.net.cars[:]
            nodeSTAList = self.net.carsSTA[:]
            nodeList.pop(self.producerNo)
            nodeSTAList.pop(self.producerNo)

        else:
            nodeList = self.net.stations[:]
            nodeList.pop(self.producerNo)
        consumerList = [] # List of the selected consumers
        consumerSTAList = [] # List of car station in vndn and sumovndn
        if consumerN > len(nodeList):
            consumerN = len(nodeList)
        i = 1
        while i <= consumerN:
            consumerNo = random.randrange(0, len(nodeList), 1)
            consumerList.append(nodeList[consumerNo])
            nodeList.pop(consumerNo)
            if self.isVndn or self.isSumoVndn:
                consumerSTAList.append(nodeSTAList[consumerNo])
                nodeSTAList.pop(consumerNo)
            i = i+1
        # Extracts data from interfaces of consumers
        for consumer in consumerList:
            # For V2I communication in VNDN/SUMOVNDN or communication between stations in Ad Hoc Networks
            consumerIntf = "%s-wlan0" % consumer
            conDumpOutputFile = "dump.%s" % consumerIntf
            consumer.cmd("sudo ndndump -i %s > %s &" % (consumerIntf, conDumpOutputFile))
            # For V2V communication in VNDN/SUMOVNDN
            if self.isVndn or self.isSumoVndn:
                consumerSTAIntf = "%sSTA-wlan0" % consumer
                conSTAOutputFile="dump.%s" % consumerSTAIntf
                consumer.cmd("sudo ndndump -i %s > %s &" % (consumerSTAIntf, conSTAOutputFile))
        # The consumer request the interested content.
        info('List of the consumers that randomly selects:')
        for consumer in consumerList:
            info(consumer)
            info(' ')
        info('\n')

        print "Each consumer that randomly seletes will send %s interest packets. waiting ...." % str(self.nPings)
        self.producerName.cmd("echo 'hello UoM!' | ndnpoke -w 800000 /ndnwifi/hello &")
        if self.isVndn or self.isSumoVndn:
            self.producerSTA.cmd("echo 'hello UoM!' | ndnpoke -w 800000 /ndnwifi/hello &")
        i = 1
        while i <= self.nPings:
            for consumer in consumerList:
                print "%s send the %s interest packet ..." % (consumer, str(i))
                consumer.cmd("ndnpeek -p /ndnwifi/hello &")
                if self.isVndn or self.isSumoVndn:
                    for consumerSTA in consumerSTAList:
                        carSTA = "car" + re.search('car(.+?)STA', str(consumerSTA)).group(1)
                        if str(consumer) == carSTA:
                           consumerSTA.cmd("ndnpeek -p /ndnwifi/hello &")
            time.sleep(3) # The interval time for sending a interest packet.
            i=i+1
        dataFilePath = "/tmp/data/oppo"
        self.statisticData(consumerList, dataFilePath)
        # Generate statistic data and end of the running of program.
        endExperiment()
wifiExperiment.register("opportunity", OpportunityExperiment)

