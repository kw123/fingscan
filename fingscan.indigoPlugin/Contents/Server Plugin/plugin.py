#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# FINGSCAN Plugin
# Developed by Karl Wachs
# karlwachs@me.com

import os
import sys
import subprocess
import pwd
import socket
import datetime
import time
import simplejson as json
import copy
import math
import shutil
import versionCheck.versionCheck as VS
import MACMAP.MAC2Vendor as M2Vclass
import ip.IP as IPaddressCalcClass


nOfDevicesInEvent   = 35
nOfIDevicesInEvent  = 5
piBeaconStart       = 22
unifiStart          = 30
milesMeters         = 1609.34
kmMeters	        = 1000.
nEvents		        = 12

iFindPluginMinText = "com.corporatechameleon.iFind"

emptyAllDeviceInfo={
    "ipNumber": "0.0.0.0",
    "timeOfLastChange": "0",
    "status": "down",
    "nickName": "iphonexyz",
    "noOfChanges": 0,
    "hardwareVendor": "",
    "deviceInfo": "",
    "WiFi": "",
    "setWiFi": "",
    "WiFiSignal": "",
    "usePing": "doNotUsePing",
    "useWakeOnLanSecs":0,
    "useWakeOnLanLast":0,
    "suppressChangeMSG": "show",
    "deviceId": 0,
    "deviceName": "",
    "fingLastUp": 0,
    "expirationTime": 0,
    "variableName": ""
    }
emptyindigoIpVariableData={
    "ipNumber": "0.0.0.0",
    "timeOfLastChange": "0",
    "status": "down",
    "nickName": "iphonexyz",
    "noOfChanges": 0,
    "hardwareVendor": "",
    "deviceInfo": "",
    "variableName": "",
    "ipDevice": "00",
    "index": 0,
    "WiFi": "",
    "WiFiSignal": "0",
    "usePing": "",
    "suppressChangeMSG": "show"
    }
emptyEVENT ={#              -including Idevices option-------------                                                                                                                                            --------mother cookies ---  ------------pi beacons---------------------   --------------  unifi ---------------------
    "IPdeviceMACnumber"   :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "timeOfLastON"        :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "timeOfLastOFF"       :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "secondsOfLastON"     :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0, "24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "secondsOfLastOFF"    :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0, "24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "currentStatusHome"   :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "currentStatusAway"   :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "iDeviceUseForHome"   :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "iDeviceUseForAway"   :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "iDeviceAwayDistance" :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "iDeviceHomeDistance" :{"1":"0","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"0","9":"0","10":"0","11":"0","12":"0","13":"0","14":"0","15":"0","16":"0","17":"0","18":"0","19":"0","20":"0","21":"0","22":"0","23":"0","24":"0","25":"0","26":"0","27":"0","28":"0","29":"0","30":"0","31":"0","32":"0","33":"0","34":"0"},
    "iDeviceName"         :{"1":"" ,"2":"" ,"3":"" ,"4":"" ,"5":"" ,"6":"" ,"7":"" ,"8":"" ,"9":"" ,"10":"" ,"11":"" ,"12":"" ,"13":"" ,"14":"" ,"15":"" ,"16":"" ,"17":"" ,"18":"" ,"19":"" ,"20":"" ,"21":"" ,"22":"" ,"23":"" ,"24":"" ,"25":"" ,"26":"" ,"27":"" ,"28":"" ,"29":"" ,"30":"" ,"31":"" ,"32":"" ,"33":"" ,"34":"" },
    "iDistance"           :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "iSpeed"              :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "iUpdateSecs"         :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "iDistanceLast"       :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "iSpeedLast"          :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "iUpdateSecsLast"     :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "itimeNextUpdate"	  :{"1": 0 ,"2": 0 ,"3": 0 ,"4": 0,"5": 0,"6": 0,"7": 0,"8": 0,"9": 0,"10": 0,"11": 0,"12": 0,"13": 0,"14": 0,"15": 0,"16": 0,"17": 0,"18": 0,"19": 0,"20": 0,"21": 0,"22": 0,"23": 0,"24": 0 ,"25": 0 ,"26": 0 ,"27": 0 ,"28": 0 ,"29": 0 ,"30": 0 ,"31": 0 ,"32": 0 ,"33": 0 ,"34": 0 },
    "iMaxSpeed"	          :{"1":1.0,"2":1.0,"3":1.0,"4":1.0,"5":1.0,"6":1.0,"7":1.0,"8":1.0,"9":1.0,"10":1.0,"11":1.0,"12":1.0,"13":1.0,"14":1.0,"15":1.0,"16":1.0,"17":1.0,"18":1.0,"19":1.0,"20":1.0,"21":1.0,"22":1.0,"23":1.0,"24":1.0,"25":1.0,"26":1.0,"27":1.0,"28":1.0,"29":1.0,"30":1.0,"31":1.0,"32":1.0,"33":1.0,"34":1.0},
    "iFindMethod"         :{"1":"" ,"2":"" ,"3":"" ,"4":"" ,"5":"" ,"6":"" ,"7":"" ,"8":"" ,"9":"" ,"10":"" ,"11":"" ,"12":"" ,"13":"" ,"14":"" ,"15":"" ,"16":"" ,"17":"" ,"18":"" ,"19":"" ,"20":"" ,"21":"" ,"22":"" ,"23":"" ,"24":"" ,"25":"" ,"26":"" ,"27":"" ,"28":"" ,"29":"" ,"30":"" ,"31":"" ,"32":"" ,"33":"" ,"34":"" },
    "nextTimeToCheck"	  :{"1":1.0,"2":1.0,"3":1.0,"4":1.0,"5":1.0,"6":1.0,"7":1.0,"8":1.0,"9":1.0,"10":1.0,"11":1.0,"12":1.0,"13":1.0,"14":1.0,"15":1.0,"16":1.0,"17":1.0,"18":1.0,"19":1.0,"20":1.0,"21":1.0,"22":1.0,"23":1.0,"24":1.0,"25":1.0,"26":1.0,"27":1.0,"28":1.0,"29":1.0,"30":1.0,"31":1.0,"32":1.0,"33":1.0,"34":1.0},
    "oneAway": "0",
    "allAway": "0",
    "allHome": "0",
    "oneHome": "0",
    "distanceAwayLimit": 66666.,
    "distanceHomeLimit": -1,
    "minimumTimeAway": 300,
    "minimumTimeHome": 0,
    "enableDisable": "0",
    "dataFormat": "3.0",
    "maxLastTimeUpdatedDistanceMinutes": 900
    }
emptyWiFiMacList=["x","x","","x","x","","","","","","",""]
indigoMaxDevices = 1024
emptyWifiMacAv={"sumSignal":{"2GHz":0.,"5GHz":0.},"numberOfDevices":{"2GHz":0.,"5GHz":0.},"curAvSignal":{"2GHz":0.,"5GHz":0.},"curDev":{"2GHz":0.,"5GHz":0.},"numberOfCycles":{"2GHz":0.,"5GHz":0.},"noiseLevel":{"2GHz": "0","5GHz": "0"}}



################################################################################
class Plugin(indigo.PluginBase):

####-----------------             ---------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        
        self.pathToPlugin       =os.getcwd()+"/"
        ## = /Library/Application Support/Perceptive Automation/Indigo 6/Plugins/piBeacon.indigoPlugin/Contents/Server Plugin
        p=max(0,self.pathToPlugin.lower().find("/plugins/"))+1
        self.indigoPath         = self.pathToPlugin[:p]
        #self.errorLog(self.indigoPath)
        #self.errorLog(self.pathToPlugin)
        self.pluginVersion      = pluginVersion
        self.pluginId           = pluginId
        self.pluginName         = pluginId.split(".")[-1]
     
####-----------------             ---------
    def __del__(self):
        indigo.PluginBase.__del__(self)


###########################     INIT    ## START ########################
    
####----------------- @ startup set global parameters, create directories etc ---------
    def startup(self):
        if self.pathToPlugin.find("/"+self.pluginName+".indigoPlugin/")==-1:
            self.errorLog(u"--------------------------------------------------------------------------------------------------------------" )
            self.errorLog(u"The pluginname is not correct, please reinstall or rename")
            self.errorLog(u"It should be   /Libray/....../Plugins/"+self.pluginName+".indigPlugin")
            p=max(0,self.pathToPlugin.find("/Contents/Server"))
            self.errorLog(u"It is: "+self.pathToPlugin[:p])
            self.errorLog(u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update")
            self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
            self.sleep(1000)
            exit(1)
            return
        self.initialized=0
        self.pluginState = "init"
        try:

############ directory & file names ...
            userName = pwd.getpwuid( os.getuid() )[ 0 ]
            ##self.getIndigoPath()
            self.MAChome                = os.path.expanduser("~")
            self.indigoDir                  = self.MAChome +"/indigo/"
            self.fingDataDir                = self.MAChome +"/indigo/fing/"
            self.fingDataDirOLD             = self.MAChome +"/Documents/fing/"
            self.fingLogFileName            = self.fingDataDir+"fing.log"
            self.fingErrorFileName          = self.fingDataDir+"fingerror.log"
            self.fingPasswordFileName       = self.fingDataDir+"parameter"
            self.fingSaveFileName           = self.fingDataDir+"fingsave.data"
            self.fingServicesFileName       = self.fingDataDir+"fingservices.json"
            self.fingServicesOutputFileName = self.fingDataDir+"fingservices.txt"
            self.fingServicesLOGFileName    = self.fingDataDir+"fingservices.log"
            self.ignoredMACFile             = self.fingDataDir+"ignoredMAC"



###   move from old place to new path
            if not os.path.exists(self.indigoDir):
                os.mkdir(self.indigoDir)

            if not os.path.exists(self.fingDataDir):
                os.mkdir(self.fingDataDir)
    
                if not os.path.exists(self.fingDataDir):
                    self.errorLog("error creating the plugin data dir did not work, can not create: "+ self.fingDataDir)
                    self.sleep(1000)
                    exit()
                
                if os.path.exists(self.fingDataDirOLD) and not os.path.exists(self.fingDataDir+"pings"):
                    indigo.server.log(" moving "+ "cp -R" + self.fingDataDirOLD+"* " + self.fingDataDir )
                    os.system("cp -R " + self.fingDataDirOLD+"* " + self.fingDataDir )




############ startup message
            self.debugLevel                                                   = ""
            if self.pluginPrefs.get(u"debugLogic", False):   self.debugLevel += "Logic,"
            if self.pluginPrefs.get(u"debugPing", False):    self.debugLevel += "Ping,"
            if self.pluginPrefs.get(u"debugWifi", False):    self.debugLevel += "WiFi,"
            if self.pluginPrefs.get(u"debugEvents", False):  self.debugLevel += "Events,"
            if self.pluginPrefs.get(u"debugMother", False):  self.debugLevel += "Mother,"
            if self.pluginPrefs.get(u"debugiFind", False):   self.debugLevel += "iFind,"
            if self.pluginPrefs.get(u"debugpiBeacon", False):self.debugLevel += "piBEacon,"
            if self.pluginPrefs.get(u"debugpUnifi", False):  self.debugLevel += "Unifi,"
            if self.pluginPrefs.get(u"debugpAll", False):    self.debugLevel += "all,"
            self.logFileActive          = self.pluginPrefs.get("logFileActive", True)
            self.logFile                = self.MAChome + "/indigo/fing/fingPlugin.log"
            if self.logFileActive: 
                indigo.server.log(u"FINGSCAN--   initializing     will take ~ 2 minutes...; sending logs to "+ self.logFile)
            else:
                self.myLog("all",u"FINGSCAN--V    initializing     will take ~ 2 minutes...")
            self.checkLogFiles()

############ set basic parameters to default before we use them
            self.updateStatesList={}
            self.updatePrefs =False
            self.fingDataModTimeOLD = 0
            self.fingDataModTimeNEW = 0
            self.fingData =[]
            self.fingIPNumbers =[]
            self.fingMACNumbers =[]
            self.fingDate =[]
            self.fingVendor =[]
            self.fingDeviceInfo = []
            self.fingNumberOfdevices = 0
            self.fingLogFileSizeold = 0
            self.fingLogFileSizeNEW = 0
            self.doubleIPnumbers={}
            self.pingJobs={}
            self.inbetweenPing={}
            self.excludeMacFromPing={}
            self.iDevicesEnabled =False
            self.ipDevsPasswordMode = 5
            self.indigoStoredNoOfDevices = 0
            self.fingDataErrorCount = 0
            self.fingDataErrorCount2 =0
            self.finglogerrorCount = 0
            self.fingRestartCount = 0
            self.myPID = str(os.getpid())
            self.theServices=[]
            self.indigoInitialized = False
            self.stopConcurrentCounter = 0
            self.doNOTupdate=False
            self.piBeaconUpDateNeeded=False
            self.unifiUpDateNeeded=False
            self.allDeviceInfo={}
            self.wifiMacList ={}
            self.oldwifiMacList={}
            self.wifiMacAv=copy.deepcopy(emptyWifiMacAv)
            self.triggerList=[]
            self.EVENTS = {}
            self.indigoVariablesFolderID =0
            self.passwordOK ="no"
            self.yourPassword =""
            self.quitNOW ="no"
            self.WiFiChanged={}
            self.wifiErrCounter  =0          
            self.callingPluginName		= []
            self.callingPluginCommand	= []
            self.triggerFromPlugin		= False

            self.executionMode ="noInterruption"  ## interrupted by plugin/fingscan/configuration
            self.signalDelta ={"5":{"2GHz":0,"5GHz":0},"2":{"2GHz":0,"5GHz":0},"1":{"2GHz":0,"5GHz":0}}
            self.theNetwork = "0.0.0.0"



########### try to setup folders, create directories if they do not exist
            try:
                ret = subprocess.Popen("mkdir "+  self.fingDataDir + "  > /dev/null 2>&1 &",shell=True)
                ret = subprocess.Popen("mkdir "+  self.fingDataDir+"pings" + "  > /dev/null 2>&1 &",shell=True)
                del ret
            except:
                pass
            self.fingDataFileName = self.fingDataDir+"fing.data"
            if not os.path.isfile(self.fingDataFileName):
                subprocess.Popen("echo 0 > "+ self.fingDataFileName+ " &",shell=True )
                self.sleep(0.1)
                if not os.path.isfile(self.fingDataFileName):
                    self.myLog(u"all",u"could not create file: "+self.fingDataFileName+" stopping program")
                    self.quitNOW =True
                    return

            
############ if there are PING jobs left from last run, kill them
            self.killPing("all")
            
            
############ get plugin prefs parameters
            
            self.inbetweenPingType=self.pluginPrefs.get(u"inbetweenPingType","0")
            self.sleepTime =int(self.pluginPrefs.get(u"sleepTime", 1))
            self.newSleepTime=self.sleepTime


############ get & setup WiFi parameters
            self.badWiFiTrigger={"minSignalDrop":10,"numberOfSecondsBad":0,"minNumberOfDevicesBad":3,"minNumberOfSecondsBad":200,"minWiFiSignal":-90,"trigger":0}
            try:
                self.badWiFiTrigger["minSignalDrop"]			= float(self.pluginPrefs.get(u"minSignalDrop"		 ,self.badWiFiTrigger["minSignalDrop"]))
                self.badWiFiTrigger["minNumberOfDevicesBad"]	= float(self.pluginPrefs.get(u"minNumberOfDevicesBad",self.badWiFiTrigger["minNumberOfDevicesBad"]))
                self.badWiFiTrigger["minNumberOfSecondsBad"]	= float(self.pluginPrefs.get(u"minNumberOfSecondsBad",self.badWiFiTrigger["minNumberOfSecondsBad"]))
                self.badWiFiTrigger["minWiFiSignal"]			= float(self.pluginPrefs.get(u"minWiFiSignal"		 ,self.badWiFiTrigger["minWiFiSignal"]))
            except:
                self.myLog("all",u"leaving WiFi parameters at default, not configured in 'fingscan/Configure...'")



            self.initIndigoParms()

            self.acceptNewDevices=self.pluginPrefs.get(u"acceptNewDevices","0") =="1"
            self.getIgnoredMAC()

############ get password
            self.myLog("all",u"getting password")
            test = self.getPWD("fingscanpy")
            if test == "0":  # no password stored in keychain, check config file
                self.yourPassword = self.pluginPrefs.get(u"password", "yourPassword")

                self.passwordOK =1  # a password has been entered before
                if self.yourPassword == "yourPassword" : self.passwordOK =0  # nothing changed from the beginning
                if self.yourPassword == "password is already stored" : self.passwordOK =2  ## password was enteered and was stored into keychain

                    
                if self.passwordOK == 1:
                    self.storePWD(self.yourPassword,"fingscanpy")
                    self.pluginPrefs[u"password"] = "password is already stored"  # set text to everything ok ...
                    self.passwordOK = 2
                
                ## wait for password
                while self.passwordOK == "0":
                    self.myLog("all",u"no password entered:  please do plugin/fingscan/configure and enter your password ")
                    self.sleep(10)
                    
                ## password entered, check if it is NOW in keychain

                test = self.getPWD("fingscanpy")
                if test !="0":	## password is in keychain
                    self.pluginPrefs[u"password"] = "password is already stored"  # set text to everything ok ...
                    self.yourPassword = test
                    self.passwordOK = "2"
                    self.quitNOW ="no"

                else:  ## no password in keychain error exit, stop plugin
                    self.passwordOK = 0
                    self.pluginPrefs[u"password"] = "yourPassword"  # set text enter password
                    self.myLog("all",u"password error please enter password in configuration menue, otherwise FING can not be started ")
                    self.quitNOW="noPassword"

            else:  # password is in keychain, done
                self.yourPassword = test
                self.pluginPrefs[u"password"] = "password is already stored"  # set text to everything ok ...
                self.quitNOW ="no"
                self.passwordOK = "2"
            self.myLog("all",u"get password done;  checking if FING is installed ")

############ install FING executables
            #paths for fing executables files to be installed
            if self.passwordOK == "2": 
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :
                        self.myLog("all","mk fing dir:   "+ret.strip("\n"))
                        if ret.find("incorrect password") >-1  or ret.find("Sorry, try again") >-1: 
                            self.myLog("all","please corrrect password in config and reload plugin , skipping fing install")
                            self.passwordOK = "0"
                            self.sleep(2)
                except:
                    pass

            if self.passwordOK == "2": 
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/bin/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/lib/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/share/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/share/fing/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/lib/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/lib/fing/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /etc/fing/   ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /var/log/fing/  ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /var/data/ ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                try:
                    ret = unicode(subprocess.Popen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /var/data/fing/ ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                    if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1 :self.myLog("all","mk fing dir:  "+ret.strip("\n"))
                except:
                    pass
                ## copy files to /usr/local/bin  ..
                self.fingEXEpath="/usr/local/bin/fing"
                cmd = "echo '"+self.yourPassword+ "' | sudo -S /bin/cp -r  '" +self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/fing'            /usr/local/bin"
                ret = unicode(subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1:self.myLog("all","copy fing:  "+ret.strip("\n"))
                cmd = "echo '"+self.yourPassword+ "' | sudo -S /bin/cp -r  '" +self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/share/'          /usr/local/share"
                ret = unicode(subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1:self.myLog("all","copy fing:  "+ret.strip("\n"))
                cmd = "echo '"+self.yourPassword+ "' | sudo -S /bin/cp -r  '" +self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/lib/'            /usr/local/lib"
                ret = unicode(subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                self.myLog("Logic",cmd)
                if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1:self.myLog("all","copy fing:  "+ret.strip("\n"))
                cmd = "echo '"+self.yourPassword+ "' | sudo -S /bin/cp -r  '" +self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/var/data/'       /var/data"
                ret = unicode(subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                self.myLog("Logic",u"mv fing files: "+cmd)
                if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1:self.myLog("all","copy fing:  "+ret.strip("\n"))
                cmd = "echo '"+self.yourPassword+ "' | sudo -S /bin/cp -r  '" +self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/var/log/'        /var/log/fing"
                ret = unicode(subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                self.myLog("Logic",u"mv fing files: "+cmd)
                if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1:self.myLog("all","copy fing:  "+ret.strip("\n"))
                cmd = "echo '"+self.yourPassword+ "' | sudo -S /bin/cp -r  '" +self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/etc/fing'        /etc"
                ret = unicode(subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1])
                self.myLog("Logic",u"mv fing files: "+cmd)
                if len(ret) > 1 and ret.find("File exists") ==-1 and ret.find("Password:") ==-1:self.myLog("all","copy fing:  "+ret.strip("\n"))

                self.myLog("all","fing install done")
############ get WIFI router info if available
            self.routerType	= self.pluginPrefs.get(u"routerType","0")
            self.routerPWD	= ""
            self.routerUID	= ""
            self.routerIPn	= ""
            if self.routerType !="0":
                self.routerUID	= self.pluginPrefs.get(u"routerUID","0")
                self.routerIPn	= self.pluginPrefs.get(u"routerIPn","0")
                
                test = self.getPWD("fingrt")
                if test != "0":
                    self.routerPWD	= test
                else:
                    self.routerType ="0"
                    self.routerPWD	= ""

                self.checkWIFIinfo()

############ kill old pending PING jobs
            self.killPing("all")

############ here we get stored setup etc
            self.getIndigoIpVariablesIntoData()		# indigo variable data to  into self.indigoIpVariableData
            self.updateallDeviceInfofromVariable()	# self.indigoIpVariableData  to self.allDeviceInfo
            self.getIndigoIpDevicesIntoData()       # indigo dev data to self.allDeviceInfo
            self.checkDEVICES()
            self.checkIfDevicesChanged()
            self.updateAllIndigoIpVariableFromDeviceData()
            self.myLog("all",u"loaded indigo data")

############ get network info
            
            self.theNetwork = ""
            network         = self.pluginPrefs.get(u"network","")

            self.netwType   = self.pluginPrefs.get(u"netwType","24")
            if str(self.netwType) == "8":
                self.netwType = "24"
            
            nn= network.split(".")
            if len(nn) !=4:
                network =""
            else:
                ok =True
                for ii in nn:
                    try:    int(ii)
                    except: ok=False; break
            if network !="" and  ok:
                self.theNetwork = network
            else:    
                self.theNetwork =""
                
            self.pluginPrefs[u"network"]  = self.theNetwork
            self.pluginPrefs[u"netwType"] = self.netwType
            self.IPaddressCalc = IPaddressCalcClass.IPCalculator(self.theNetwork+"/"+self.netwType)
            self.netwInfo =  self.IPaddressCalc.makeJson()
            indigo.server.log("network info: "+unicode(self.netwInfo))
            self.broadcastIP = self.netwInfo["broadcast"]

############ for triggers:
            self.currentEventN = "0"
            try:
                self.EVENTS=json.loads(self.pluginPrefs["EVENTS"])
            except:
                self.EVENTS = {}

            timeNow = time.time()
            self.checkTriggerInitialized =False
          



############ check if FMID is enabled
            self.IDretList=[]
            self.iFindStuffPlugin = "com.corporatechameleon.iFindplugBeta"
            self.checkIfiFindisEnabled()

############ en/ disable mac to vendor lookup
        
            self.enableMACtoVENDORlookup    = self.pluginPrefs.get(u"enableMACtoVENDORlookup","21")
            self.waitForMAC2vendor = False
            if self.enableMACtoVENDORlookup != "0":
                self.M2V = M2Vclass.MAP2Vendor(refreshFromIeeAfterDays = int(self.enableMACtoVENDORlookup) )
                self.waitForMAC2vendor = self.M2V.makeFinalTable()





############ check for piBeacon plugin devcies
            try:
                self.piBeaconDevices=json.loads(self.pluginPrefs["piBeacon"])
            except:
                self.piBeaconDevices = {}
            self.cleanUppiBeacon()


            self.enablepiBeaconDevices=self.pluginPrefs.get(u"enablepiBeaconDevices","0")
            self.piBeaconIsAvailable =False
            self.piBeaconDevicesAvailable=[]
            self.getpiBeaconAvailable()
            if self.piBeaconIsAvailable:
                self.pluginPrefs["piBeaconEnabled"] =True
                self.updatepiBeacons()
            else:
                self.pluginPrefs["piBeaconEnabled"] =False
############ check for UNIFI plugin devcies
            try:
                self.unifiDevices=json.loads(self.pluginPrefs["UNIFI"])
            except:
                self.unifiDevices = {}
            self.cleanUpUnifi()
            self.enableUnifiDevices=self.pluginPrefs.get(u"enableUnifiDevices","0")
            self.unifiAvailable =False
            self.unifiDevicesAvailable=[]
            self.getUnifiAvailable()
            if self.unifiAvailable:
                self.pluginPrefs["unifiEnabled"] =True
                self.updateUnifi()
            else:
                self.pluginPrefs["unifiEnabled"] =False



############ setup mac / devname /number selection list
            self.IPretList=[]
            for theMAC in self.allDeviceInfo:
                devI=self.allDeviceInfo[theMAC]
                theString = devI["deviceName"]+"-"+devI["ipNumber"]+"-"+theMAC
                self.IPretList.append(( theMAC,theString ))
            self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
            self.IPretList.append((1,"Not used"))


############ check if version 1 if yes, upgrade to version 2
            retCode = self.checkIndigoVersion()

            try:
                indigo.variable.create("averageWiFiSignal_GHz",folder=self.indigoVariablesFolderID)
                indigo.variable.create("averageWiFiSignal_5GHz",folder=self.indigoVariablesFolderID)
            except:
                pass


############ create indigo Event variables  and initialize ..
                
            self.cleanUpEvents()
            self.setupEventVariables(init=True)
     

############ initialize indigo settings ..
            self.quitNOW ="no"
            self.myLog("all",u"FING initializing")
            retCode = self.initFing(1)
            if retCode !=1:
                self.myLog("all",u" fing not running... quit")
                self.quitNOW ="fing not running"
            else:
                pass

############ print info to indigo logfile
            self.printConfig()
            self.printEvents()
            if self.routerType !="0":
                errorMSG = self.getWifiDevices(self.routerUID,self.routerPWD,self.routerIPn,type=self.routerType)
                if errorMSG !="ok":
                    self.myLog("all", "Router wifi not reachable, userid, password or ipnumber wrong?\n"+ unicode(errorMSG))
                
                self.printWiFi()
            self.printpiBeaconDevs()
            self.printUnifiDevs()
            

############ try to find hw vendor 
            self.myLog("all", "getting vendor info ")
            self.MacToNamesOK = True
            for theMAC in self.allDeviceInfo:
                for item in emptyAllDeviceInfo:
                    if item not in self.allDeviceInfo[theMAC]:
                        self.allDeviceInfo[theMAC][item] = emptyAllDeviceInfo[item]

                if not self.MacToNamesOK: continue 
                update = 0
                if self.allDeviceInfo[theMAC]["hardwareVendor"].find("\n") >-1: 
                    update = 1
                    self.allDeviceInfo[theMAC]["hardwareVendor"] = self.allDeviceInfo[theMAC]["hardwareVendor"].strip("\n").strip()
                self.myLog("Logic", theMAC+"  devID:"+str(self.allDeviceInfo[theMAC]["deviceId"])+" existingVendor >>"+self.allDeviceInfo[theMAC]["hardwareVendor"]+"<<" )
                if self.allDeviceInfo[theMAC]["deviceId"] !=0:             
                    if len(self.allDeviceInfo[theMAC][u"hardwareVendor"]) < 3 or  (self.allDeviceInfo[theMAC][u"hardwareVendor"].find("<html>")) > -1 :
                        vend= self.getVendortName(theMAC)
                        self.myLog("Logic", theMAC+" Vendor info  >>"+vend+"<<" )
                        if vend != ""  or self.allDeviceInfo[theMAC][u"hardwareVendor"].find("<html>") > -1: 
                            update = 2

                if update > 0:
                    if update == 1: 
                        vend = self.allDeviceInfo[theMAC]["hardwareVendor"].strip("\n")
                    try: 
                        self.myLog("all", " updating :"+theMAC+"  "+str(self.allDeviceInfo[theMAC]["deviceId"])+"  to >>"+vend +"<<")
                        self.allDeviceInfo[theMAC][u"hardwareVendor"]  = vend
                        dev = indigo.devices[self.allDeviceInfo[theMAC]["deviceId"]]
                        dev.updateStateOnServer("hardwareVendor",vend)
                    except  Exception, e:
                        self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
                        
            self.MacToNamesOK = True
                

        except  Exception, e:
            indigo.server.log( u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )


        self.initialized=1
    
        return


########################################
    def refreshVariables(self):
        try:    indigo.variable.delete("ipDevsLastUpdate")
        except: pass
        try:    indigo.variable.create("ipDevsLastUpdate","",self.indigoVariablesFolderID)	
        except: pass
        try:    indigo.variable.delete("ipDevsNewDeviceNo")
        except: pass
        try:    indigo.variable.create("ipDevsNewDeviceNo","",self.indigoVariablesFolderID)	
        except: pass
        try:    indigo.variable.delete("ipDevsNewIPNumber")
        except: pass
        try:    indigo.variable.create("ipDevsNewIPNumber","",self.indigoVariablesFolderID)	
        except: pass
        try:    indigo.variable.delete("ipDevsNoOfDevices")
        except: pass
        try:    indigo.variable.create("ipDevsNoOfDevices","",self.indigoVariablesFolderID)	
        except: pass
        return
        
########################################
    def setupEventVariables(self,init=False):
        try:
            try:
                indigo.variables.folder.create("FINGscanEvents")
                self.myLog("all",u"FINGscanFolder folder created")
            except:
                pass
            FINGscanFolderID = indigo.variables.folders["FINGscanEvents"].id
            for i in self.EVENTS:
                try:
                    indigo.variable.create("allHome_"+str(i),"",folder=FINGscanFolderID)
                    indigo.variable.create("oneHome_"+str(i),"",folder=FINGscanFolderID)
                except:
                    pass

            
            if init: 
                try:    indigo.variable.delete("FingEventDevChangedIndigoId")
                except: pass
            
            try:
                indigo.variable.create("FingEventDevChangedIndigoId",folder=self.FINGscanFolderID)
            except:  pass



            for i in self.EVENTS:
                try:
                    indigo.variable.create("allAway_"+str(i),"",folder=FINGscanFolderID)
                    indigo.variable.create("oneAway_"+str(i),"",folder=FINGscanFolderID)
                except:
                    pass
            for nEvent in self.EVENTS:
                evnt=self.EVENTS[nEvent]
                if "oneHome" not in evnt: continue
                
                xx=  indigo.variables["oneHome_"+nEvent].value
                if evnt["oneHome"]  !=  xx:                     indigo.variable.updateValue("oneHome_"+nEvent,evnt["oneHome"])
                xx=  indigo.variables["allHome_"+nEvent].value
                if evnt["allHome"]  !=  xx:                     indigo.variable.updateValue("allHome_"+nEvent,evnt["allHome"])
                xx=  indigo.variables["oneAway_"+nEvent].value
                if evnt["oneAway"]  !=  xx:                     indigo.variable.updateValue("oneAway_"+nEvent,evnt["oneAway"])
                xx=  indigo.variables["allAway_"+nEvent].value
                if evnt["allAway"]  !=  xx:                     indigo.variable.updateValue("allAway_"+nEvent,evnt["allAway"])
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return




########################################
    def sendWakewOnLanAndPing(self, MAC, nBC= 2, waitForPing=500, nPings=1, countPings=1, waitBeforePing = 0.5, waitAfterPing = 0.5, calledFrom=""):
        self.sendWakewOnLan(MAC, calledFrom=calledFrom)
        if nBC ==2:
            self.sleep(0.05)
            self.sendWakewOnLan(MAC, calledFrom=calledFrom)
        self.sleep(waitBeforePing)
        return self.checkPing(MAC, waitForPing=waitForPing, countPings=countPings, nPings=nPings, waitAfterPing = 0.5)
        
########################################
    def checkPing(self, MAC, waitForPing=100, countPings = 1,nPings = 1, waitAfterPing = 0.5):
        if (MAC not in self.allDeviceInfo): return 2
        ipN= self.allDeviceInfo[MAC]["ipNumber"]
        Wait = ""
        if waitForPing != "": 
            Wait = "-W "+ str(waitForPing)
        Count = "-c 1"
        if countPings != "":
            Count = "-c "+str(countPings)
        if nPings == 1:
            waitAfterPing =0.

        retCode = 1
        for nn in range(nPings):            
            retCode = subprocess.call('/sbin/ping -o '+Wait+' '+Count+' -q '+ipN+' >/dev/null',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # "call" will wait until its done and deliver retcode 0 or >0
            self.myLog("Ping",u"ping resp:"+ipN+"  :" +str(retCode) )
            if retCode ==0: return 0
            if nn != nPings-1: self.sleep(waitAfterPing)
        return retCode

########################################
    def sendWakewOnLan(self, MAC, calledFrom=""):
        data = ''.join(['FF' * 6, MAC.replace(':', '') * 16])
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data.decode("hex"), (self.broadcastIP, 9))
        self.myLog("Ping",u"sendWakewOnLan for "+MAC+";  called from "+calledFrom+";  bc ip: "+self.broadcastIP) 

########################################
    def checkIfiFindisEnabled(self):
        try:
            self.iDevicesEnabled =False
            self.getiFindFile()
            if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
                for dev in indigo.devices.iter(self.iFindStuffPlugin):
                    #if  dev.pluginId.find(self.iFindStuffPlugin) == -1 :continue
                    if dev.deviceTypeId!="iAppleDeviceAuto": continue
                    self.iDevicesEnabled =True
                    self.pluginPrefs["iDevicesEnabled"] =True
                    return
            self.pluginPrefs["iDevicesEnabled"] =False
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return

########################################
    def getiFindFile(self):
        try:
            ret =subprocess.Popen("ls '"+self.indigoPath+"Preferences/Plugins/' | grep  '"+iFindPluginMinText+"' | grep -v grep",shell=True,stdout=subprocess.PIPE)
            retText=ret.communicate()
            line=retText[0]

            if len(line) > 0:
                self.iFindStuffPlugin = line.split(".indiPref")[0]
            self.myLog("all",u"ifind plugin: "+ self.iFindStuffPlugin)

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
########################################
    def getpiBeaconAvailable(self):
        try:
            self.piBeaconDevicesAvailable=[]
            if  indigo.server.getPlugin("com.karlwachs.piBeacon").isEnabled():
                for dev in indigo.devices.iter("com.karlwachs.piBeacon"):
                        self.piBeaconIsAvailable =True
                        if "Pi_0_Signal" in dev.states and "status" in dev.states: # only interested in iBeacons
                            self.piBeaconDevicesAvailable.append((dev.id,dev.name))
                            if dev.states["status"] =="up" or dev.states["status"] =="1":
                                                            status="up"
                            else:                           status="0"
                            if str(dev.id) not in self.piBeaconDevices:
                                self.piBeaconDevices[str(dev.id)]={"currentStatus":status,"lastUpdate":time.time(),"name":dev.name,"used": "0"}
                            else:
                                self.piBeaconDevices[str(dev.id)]["name"]=dev.name
                                self.piBeaconDevices[str(dev.id)]["currentStatus"]=status
                            
            ## remove devices that do not exist anymore
            delList=[]
            list=unicode(self.piBeaconDevicesAvailable)
            for nDev in self.piBeaconDevices:
                if list.find(nDev)==-1 : delList.append(nDev)
            for d in delList:
                del self.piBeaconDevices[d] 
            self.piBeaconDevicesAvailable= sorted(self.piBeaconDevicesAvailable, key=lambda tup: tup[1])    
            self.piBeaconDevicesAvailable.append((1,"do not use"))
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
########################################
    def getUnifiAvailable(self):
        try:
            self.unifiDevicesAvailable=[]
            if  indigo.server.getPlugin("com.karlwachs.uniFiAP").isEnabled():
                for dev in indigo.devices.iter("com.karlwachs.uniFiAP"):
                    #if  dev.pluginId.find("com.karlwachs.uniFiAP") > -1 :
                        self.unifiAvailable =True
                        self.unifiDevicesAvailable.append((dev.id,dev.name))
                        if "status" in dev.states:
                            if dev.states["status"] =="up" or dev.states["status"] =="1":
                                                            state="up"
                            else:                           state="0"
                            if str(dev.id) not in self.unifiDevices:
                                self.unifiDevices[str(dev.id)]={"currentStatus": "0","lastUpdate":time.time(),"name":dev.name,"used": "0"}
                            else:
                                self.unifiDevices[str(dev.id)]["name"]=dev.name
                                self.unifiDevices[str(dev.id)]["currentStatus"]=state
            ## remove devices that do not exist anymore
            #self.myLog("all",unicode(self.unifiDevicesAvailable))
            #self.myLog("all",unicode(self.unifiDevices))
            delList=[]
            list=unicode(self.unifiDevicesAvailable)
            for nDev in self.unifiDevices:
                if list.find(nDev)==-1 : delList.append(nDev)
            for d in delList:
                del self.unifiDevices[d]
            self.unifiDevicesAvailable= sorted(self.unifiDevicesAvailable, key=lambda tup: tup[1])                
            self.unifiDevicesAvailable.append((1,"do not use"))
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return


########################################
    def printConfig(self):
        try:
            self.myLog("all",u"settings:  iDevicesEnabled              "+ str(self.iDevicesEnabled))
            self.myLog("all",u"settings:  inbetweenPingType            "+ str(self.inbetweenPingType))
            self.myLog("all",u"settings:  wifiRouter                   "+ str(self.routerType))
            self.myLog("all",u"settings:  wait seconds between cycles  "+ str(self.sleepTime))
            self.myLog("all",u"settings:  password entered             "+ str(self.passwordOK=="2"))
            self.myLog("all",u"settings:  debugLevel                   "+ str(self.debugLevel))
            try:
                nwP= self.theNetwork.split(".")
                self.myLog("all",u"settings:  FINGSCAN will scan Network   "+str(nwP[0])+"."+str(nwP[1])+"."+str(nwP[2])+ "....  # fixed bits in ip range:"+str(self.netwType))
            except:
                pass
            self.myLog("all",u"\n")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))


########################################
    def deviceDeleted(self,dev):
        try:
            devID= dev.id
            for theMAC in self.allDeviceInfo:
                if self.allDeviceInfo[theMAC]["deviceId"] ==dev.id:
                    self.deleteIndigoIpDevicesData(theMAC)
                    return
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

########################################
    def deviceStartComm(self, dev):
        try:
            if self.pluginState == "init":
                dev.stateListOrDisplayStateIdChanged()  # update device.xml info if changed
            else:
                self.myLog("Logic",u"dev start called for "+dev.name)
            return
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
    
########################################
    def deviceStopComm(self, dev):
        if self.pluginState != "init":
            self.myLog("Logic",u"dev Stop called for "+dev.name)
        
        
########################################
    def intToBin(self,iNumber):
        try:
            nBinString=""
            for i in range(17):
                j=16-i
                k=int(math.pow(2,j))
                if iNumber >=k:
                    iNumber -= k
                    nBinString+="1"
                else:nBinString+="0"
            return nBinString
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))


########################################
    def shutdown(self):
        self.myLog("all",u"shutdown called")
        retCode = self.killFing("all")
        retCode = self.killPing("all")


########################################
    def stopConcurrentThread(self):
        self.stopConcurrentCounter +=1
        self.myLog("all",u"stopConcurrentThread called " + str(self.stopConcurrentCounter))
        if self.stopConcurrentCounter ==1:
            self.stopThread = True


########################################
    def CALLBACKIPdeviceMACnumber1(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"1")
    def CALLBACKIPdeviceMACnumber2(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"2")
    def CALLBACKIPdeviceMACnumber3(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"3")
    def CALLBACKIPdeviceMACnumber4(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"4")
    def CALLBACKIPdeviceMACnumber5(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"5")
    def CALLBACKIPdeviceMACnumber6(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"6")
    def CALLBACKIPdeviceMACnumber7(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"7")
    def CALLBACKIPdeviceMACnumber8(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"8")
    def CALLBACKIPdeviceMACnumber9(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"9")
    def CALLBACKIPdeviceMACnumber10(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"10")
    def CALLBACKIPdeviceMACnumber11(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"11")
    def CALLBACKIPdeviceMACnumber12(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"12")
    def CALLBACKIPdeviceMACnumber13(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"13")
    def CALLBACKIPdeviceMACnumber14(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"14")
    def CALLBACKIPdeviceMACnumber15(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"15")
    def CALLBACKIPdeviceMACnumber16(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"16")
    def CALLBACKIPdeviceMACnumber17(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"17")
    def CALLBACKIPdeviceMACnumber18(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"18")
    def CALLBACKIPdeviceMACnumber19(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"19")
    def CALLBACKIPdeviceMACnumber20(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"20")
    def CALLBACKIPdeviceMACnumber21(self, valuesDict,typeId=""):
        return self.CALLBACKIPdevice(valuesDict,"21")

########################################
    def CALLBACKIPdevice(self, valuesDict,nDev):
        try:
            self.currentEventN=str(valuesDict["selectEvent"])
            if self.currentEventN =="0":
                return valuesDict
            imac= valuesDict["IPdeviceMACnumber"+nDev]
            if imac =="0" or imac=="1" or imac =="":
                valuesDict["iDevicesEnabled"+nDev] =False
                return valuesDict
                
            if self.iDevicesEnabled:
                valuesDict["iDevicesEnabled"+nDev] =True
            else:
                valuesDict["iDevicesEnabled"+nDev] =False
                valuesDict["iDevicesEnabled"+nDev+"a"] =False
            
        
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return valuesDict


########################################
    def CALLBACKIdevice1Selected(self, valuesDict,typeId=""):
        return self.CALLBACKIdeviceSelected(valuesDict,"1")
    def CALLBACKIdevice2Selected(self, valuesDict,typeId=""):
        return self.CALLBACKIdeviceSelected(valuesDict,"2")
    def CALLBACKIdevice3Selected(self, valuesDict,typeId=""):
        return self.CALLBACKIdeviceSelected(valuesDict,"3")
    def CALLBACKIdevice4Selected(self, valuesDict,typeId=""):
        return self.CALLBACKIdeviceSelected(valuesDict,"4")
    def CALLBACKIdevice5Selected(self, valuesDict,typeId=""):
        return self.CALLBACKIdeviceSelected(valuesDict,"5")
    def CALLBACKIdevice6Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice7Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice8Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice9Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice10Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice11Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice12Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice13Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice14Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice15Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice16Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice17Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice18Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice19Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice20Selected(self, valuesDict,typeId=""):
        return valuesDict
    def CALLBACKIdevice21Selected(self, valuesDict,typeId=""):
        return valuesDict

    def CALLBACKIdeviceSelected(self, valuesDict,nDev):
###		self.myLog("all",u"currentEventN"+str(self.currentEventN)+"  ndev"+str(nDev)+"  iDeviceName"+valuesDict["iDeviceName"+nDev])
        try:
            if self.currentEventN =="0":
                return valuesDict
            if self.iDevicesEnabled:
                if 	not ( valuesDict["iDeviceName"+nDev] =="1" or valuesDict["iDeviceName"+nDev] ==""):
                    valuesDict["iDevicesEnabled"+nDev+"a"] =True
                else:
                    valuesDict["iDevicesEnabled"+nDev+"a"] =False
            else:
                valuesDict["iDevicesEnabled"+nDev+"a"] =False
        
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return valuesDict


########################################
    def CALLBACKevent(self, valuesDict,typeId=""):

        try:
            self.getUnifiAvailable()
            self.getpiBeaconAvailable()
            
            self.currentEventN=str(valuesDict["selectEvent"])
            #self.myLog("all","CALLBACKevent currentEventN = " +self.currentEventN)
            if self.currentEventN =="0":
                errorDict = valuesDict
                return valuesDict
            
            if not self.currentEventN in self.EVENTS:
                self.EVENTS[self.currentEventN]= copy.deepcopy(emptyEVENT)
                
            for nDev in self.EVENTS[self.currentEventN]["IPdeviceMACnumber"]:
                #self.myLog("all",u"CALLBACKevent checking  nDev:"+nDev+ u";  self.EVENTS[self.currentEventN][IPdeviceMACnumber][nDev]:"+unicode(self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]) )
                valuesDict["IPdeviceMACnumber"+nDev]	=	self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]
                valuesDict["iDeviceName"+nDev]	        =	self.EVENTS[self.currentEventN]["iDeviceName"][nDev]
                #if nDev=="1": self.myLog("all",u"CALLBACKevent  IPdeviceMACnumber= " +valuesDict["IPdeviceMACnumber"+nDev])
                #idevD,idevName,idevId = self.getIdandName(str(self.EVENTS[self.currentEventN]["iDeviceName"][nDev]))
                #if idevName != "0":
                #    valuesDict["iDeviceName"+nDev]			=	str(idevId)
                valuesDict["iDeviceUseForHome"+nDev]	=	self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]
                valuesDict["iDeviceUseForAway"+nDev]	=	self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]
                imac= valuesDict["IPdeviceMACnumber"+nDev]
                if imac =="0" or imac=="1" or imac =="":
                    valuesDict["iDevicesEnabled"+nDev] =False
                else:
                    if self.iDevicesEnabled and (self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev] =="1" or self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev] =="1"):
                        valuesDict["iDevicesEnabled"+nDev] =True
                        valuesDict["iDevicesEnabled"+nDev+"a"] =True
                    else:
                        valuesDict["iDevicesEnabled"+nDev] =False
                        valuesDict["iDevicesEnabled"+nDev+"a"] =False

        
            valuesDict["minimumTimeHome"]				    =	str(int(float(self.EVENTS[self.currentEventN]["minimumTimeHome"])))
            valuesDict["minimumTimeAway"]				    =	str(int(float(self.EVENTS[self.currentEventN]["minimumTimeAway"])))
            valuesDict["distanceAwayLimit"]				    =	str(int(float(self.EVENTS[self.currentEventN]["distanceAwayLimit"])))
            valuesDict["distanceHomeLimit"]				    =	str(int(float(self.EVENTS[self.currentEventN]["distanceHomeLimit"])))
            valuesDict["maxLastTimeUpdatedDistanceMinutes"]	=   str(int(float(self.EVENTS[self.currentEventN]["maxLastTimeUpdatedDistanceMinutes"])))
            valuesDict["enableDisable"]					    =	self.EVENTS[self.currentEventN]["enableDisable"]

            if self.iDevicesEnabled:	valuesDict["iDevicesEnabled"]   =True
            else:						valuesDict["iDevicesEnabled"]   =False
                
                
            if self.piBeaconIsAvailable:	
                valuesDict["piBeaconEnabled"]     =True
                for npiBeacon in ("25","26","27","28","29"):
                    valuesDict["IPdeviceMACnumber"+npiBeacon]=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]
            else:	
                valuesDict["piBeaconEnabled"]     =False

            if self.unifiAvailable:	
                valuesDict["unifiEnabled"]     =True
                for nUnifi in ("30","31","32","33","34"):
                    valuesDict["IPdeviceMACnumber"+nUnifi]=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]
            else:	
                valuesDict["unifiEnabled"]     =False

        
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        #self.myLog("all","CALLBACKevent valuesDict:"+unicode(valuesDict))
        self.updatePrefs =True
        return valuesDict

########################################
    def doPing(self, theMAC):
        try:
            ipn= self.allDeviceInfo[theMAC]["ipNumber"]
            ret = subprocess.Popen('/sbin/ping -c3 '+ipn,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            resp = ret.communicate()[0]
            ret.stdout.close()
            ret.stderr.close()
            del ret
            self.myLog("Ping",u"pinging device "+ self.allDeviceInfo[theMAC]["deviceName"]+" " +self.allDeviceInfo[theMAC]["ipNumber"])
            lines = resp.split("\n")
            for line in lines:
                self.myLog("Ping",str(line))
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

########################################
    def pingCALLBACKaction(self, action):

        theMAC= action.props["pingIpDevice"]
        self.doPing(theMAC)



        
########################################
    def actionFromCALLBACKaction(self, action):
        #self.myLog("iFind"," actionFromCALLBACK --"+ unicode(action))
        try:
            self.callingPluginName.append(action.props["from"])
            self.callingPluginCommand.append(action.props["msg"])
        except:
            pass
            self.myLog("all", u"actionFrom no plugin call back given" )
            return
        self.triggerFromPlugin=True
        return

########################################
    def piBeaconUpdateCALLBACKaction(self, action):
        #self.myLog("piBEacon"," self.piBeaconDevices "+unicode(self.piBeaconDevices))
        try:
            if "deviceId" in  action.props:
                for devId in action.props["deviceId"]:
                    devS=str(devId)
                    if devS not in self.piBeaconDevices:
                        self.myLog("piBEacon",u"piBeacon deviceId not used in fingscan: "+devS)
                        continue
                    dev=indigo.devices[int(devId)]
                    mdevName=dev.name
                    try:
                        try:
                            status= dev.states["status"].lower()
                            if status =="1": status="up"
                        except:
                            status ="notAvail"
                        
                        self.myLog("piBEacon",u" devName "+mdevName+"  Status "+status )
                        if self.piBeaconDevices[devS]["currentStatus"] !=status:
                            if self.piBeaconDevices[devS]["used"] == "1":
                                self.newSleepTime=0.
                                self.piBeaconUpDateNeeded=True
                            self.piBeaconDevices[devS]["lastUpdate"] = time.time()
                        self.piBeaconDevices[devS]["currentStatus"] = status
                        self.piBeaconDevices[devS]["name"] = mdevName
                    except:
                        self.myLog("piBEacon",u"status data not ready:"+unicode(status))
        
            else:
                self.myLog("piBEacon",u" error from piBeacon, deviceId not in action: "+unicode(action))
                return
        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.myLog("all",unicode(action))
            return
        self.pluginPrefs["piBeacon"]	=	json.dumps(self.piBeaconDevices)
        return
        

########################################
    def UnifiUpdateCALLBACKaction(self, action):
        self.myLog("Unifi",u" self.unifiDevices "+unicode(self.unifiDevices))
        try:
            if "deviceId" in  action.props:
                for devId in action.props["deviceId"]:
                    devS=str(devId)
                    if devS not in self.unifiDevices:
                        self.myLog("Unifi",u"unifi deviceId not used in fingscan: "+devS)
                        continue
                    dev=indigo.devices[int(devId)]
                    mdevName=dev.name
                    try:
                        try:
                            status= dev.states["status"]
                        except:
                            status ="notAvail"
                        
                        self.myLog("Unifi",u" devName "+mdevName+"  status "+status )
                        if self.unifiDevices[devS]["currentStatus"] !=status:
                            if self.unifiDevices[devS]["used"] == "1":
                                self.newSleepTime=0.
                                self.unifiUpDateNeeded=True
                            self.unifiDevices[devS]["lastUpdate"] = time.time()
                        self.unifiDevices[devS]["currentStatus"] = status
                        self.unifiDevices[devS]["name"] = mdevName
                    except:
                        self.myLog("Unifi",u"status data not ready:"+status)
        
            else:
                self.myLog("Unifi",u" error from unifi, deviceId not in action: "+unicode(action))
                return
        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.myLog("all",unicode(action))
            return
        self.pluginPrefs["UNIFI"]	=	json.dumps(self.unifiDevices)
        return


########################################
    def updatepiBeacons(self):
        try:
            status="not initialized"
            for deviceId in  self.piBeaconDevices:
                currentState= self.piBeaconDevices[deviceId]["currentStatus"]
                lastUpdate= self.piBeaconDevices[deviceId]["lastUpdate"]
                try:
                    devId= int(deviceId)
                except:
                    self.getpiBeaconAvailable()
                    try:
                        devId= int(deviceId)
                    except:
                        del self.piBeaconDevices[deviceId]
                        continue
                        
                dev=indigo.devices[devId]
                mdevName=dev.name
                try:
                    try:
                        status= dev.states["status"]
                        if status =="1": status="up"
                    except:
                        status ="notAvail"

                    if currentState !=status:
                        self.myLog("piBEacon",u"updating piBeacon:  devName "+mdevName+"  status "+status)
                        self.piBeaconUpDateNeeded=True
                        self.piBeaconDevices[deviceId]["currentStatus"]= status
                        self.piBeaconDevices[deviceId]["lastUpdate"] 	= time.time()
                        self.piBeaconDevices[deviceId]["name"] 		= mdevName
                        if self.piBeaconDevices[devS]["used"] == "1":
                            self.newSleepTime=0.
                except:
                        self.myLog("piBEacon",u"updating piBeacon:  devName "+unicode(mdevName)+"  status "+unicode(status) +" not ready"  )
    
        
        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.piBeaconDevices={}
        return

########################################
    def updateUnifi(self):
        try:
            Presence="not initialized"
            for deviceId in  self.unifiDevices:
                currentState  = self.unifiDevices[deviceId]["currentStatus"]
                lastUpdate    = self.unifiDevices[deviceId]["lastUpdate"]
                try:
                    devId= int(deviceId)
                except:
                    self.getUnifiAvailable()
                    try:
                        devId= int(deviceId)
                    except:
                        del self.unifiDevices[deviceId]
                        continue
                        
                dev=indigo.devices[devId]
                mdevName=dev.name
                try:
                    try:
                        Status= dev.states["status"]
                    except:
                        Status ="notAvail"

                    if currentState !=Presence:
                        self.myLog("Unifi",u"updating unifi:  devName "+mdevName+"  Status "+Status)
                        self.unifiUpDateNeeded=True
                        self.unifiDevices[deviceId]["currentStatus"] = Status
                        self.unifiDevices[deviceId]["lastUpdate"] 	= time.time()
                        self.unifiDevices[deviceId]["name"] 		= mdevName
                        if self.unifiDevices[devS]["used"] == "1":
                            self.newSleepTime=0.
                except:
                        self.myLog("Unifi",u"updating unifi:  devName "+unicode(mdevName)+"  Status "+unicode(Status) +" not ready"  )
    
        
        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.unifiDevices={}
        return

##

########################################
    def buttonConfirmAddIgnoredMACsCALLBACK(self, valuesDict,typeId=""):
        theMAC = valuesDict["selectedMAC"]
        if theMAC not in self.ignoredMAC:
            info = theMAC
            if theMAC in self.allDeviceInfo:
                info = theMAC+"-"+self.allDeviceInfo[theMAC]["deviceName"]+"-"+self.allDeviceInfo[theMAC]["ipNumber"]
            self.ignoredMAC[theMAC] = info
            self.saveIgnoredMAC()
        return valuesDict
########################################
    def buttonConfirmRemoveIgnoredMACsCALLBACK(self, valuesDict,typeId=""):
        theMAC = valuesDict["selectedMAC"]
        if theMAC in self.ignoredMAC:
            del self.ignoredMAC[theMAC]
            self.saveIgnoredMAC()
        return valuesDict


########################################
    def filterIgnoredMACs(self, filter="self", valuesDict=None, typeId="", targetId=0):
        retList =[]
        for theMAC in self.ignoredMAC:
            retList.append((theMAC,self.ignoredMAC[theMAC]))
        retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text
        return retList
########################################
    def filterNotIgnoredMACs(self, filter="self", valuesDict=None, typeId="", targetId=0):
        retList =[]
        for theMAC in self.allDeviceInfo:
            if theMAC not in self.ignoredMAC:
                retList.append((theMAC,theMAC+"-"+self.allDeviceInfo[theMAC]["deviceName"]+"-"+self.allDeviceInfo[theMAC]["ipNumber"]))
        retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text
        return retList

########################################
    def filterListIpDevices(self, filter="self", valuesDict=None, typeId="", targetId=0):
        retList =[]
        for theMAC in self.allDeviceInfo:
            devI=self.allDeviceInfo[theMAC]
            retList.append((theMAC,devI["deviceName"]+"-"+devI["ipNumber"]+"-"+devI["status"]))

        retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text

        return retList


########################################
    def selectiDeviceFilter(self, filter="self", valuesDict=None,typeId=""):
        try:
            self.IDretList=[]
            if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
                self.iDevicesEnabled = True
                for dev in indigo.devices.iter(self.iFindStuffPlugin):
                    if dev.deviceTypeId!="iAppleDeviceAuto": continue
                    self.IDretList.append((dev.id,dev.name))
                self.IDretList	= sorted(self.IDretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
                self.IDretList.append((1,"do not use iDevice"))
            else:
                self.iDevicesEnabled = False
            #self.myLog("all", u"selectiDeviceFilter called" )
            
            return self.IDretList
        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )

       

########################################
    def IPdeviceMACnumberFilter(self, filter="self", valuesDict=None,typeId=""):
        try:
            self.IPretList=[]
            for theMAC in self.allDeviceInfo:
                devI=self.allDeviceInfo[theMAC]
                theString = devI["deviceName"]+"-"+devI["ipNumber"]+"-"+theMAC
                self.IPretList.append(( theMAC,theString ))
            self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
            self.IPretList.append((1,"Not used"))
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        #self.myLog("all", u"IPdeviceMACnumberFilter called" )
        return self.IPretList


########################################
    def piBeaconFilter(self, filter="self", valuesDict=None,typeId=""):
        #self.myLog("all", u"piBeaconFilter called" )
        try:
            retList =copy.deepcopy(self.piBeaconDevicesAvailable)
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            return [(0,0)]
        return retList

########################################
    def unifiFilter(self, filter="self", valuesDict=None,typeId=""):
        #self.myLog("all", u"unifiFilter called" )
        try:
            retList =copy.deepcopy(self.unifiDevicesAvailable)
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            return [(0,0)]
        return retList


########################################
    def buttonConfirmDevicesCALLBACK(self, valuesDict,typeId=""):
        errorDict=indigo.Dict()

        try:
            self.currentEventN=str(valuesDict["selectEvent"])
            if self.currentEventN =="0" or  self.currentEventN =="":
    #			errorDict = valuesDict
                return valuesDict


    ########  do piBeacon stuff needed later in EVENTS
            for npiBeacon in ("22","23","24","25","26","27","28","29"):
                mId=str(valuesDict["IPdeviceMACnumber"+npiBeacon])
                if mId =="0":
                    mId = self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]
                elif mId =="1":
                    mId=""

                self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]	= mId
                if mId !="" and mId !="0"and mId !="1":
                    try:
                        mdevName=indigo.devices[int(mId)].name
                        if mId not in self.piBeaconDevices:
                            self.myLog("piBEacon",u"piBeacon mId 3 "+str(mId) + "  "+str(npiBeacon))
                    except:
                        pass


            ## clean up piBeacon list
            keep=[]
            for nEvent in self.EVENTS:
                for npiBeacon in ("25","26","27","28","29"):
                    mId=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]
                    if  mId !="" and mId !="0":
                        keep.append(mId)

            deleteM=[]
            for piBeaconId in self.piBeaconDevices:
                if piBeaconId not in keep: deleteM.append(piBeaconId)
            for piBeaconId in deleteM:
                del self.piBeaconDevices[piBeaconId]



    ########  do unifi stuff needed later in EVENTS
            for nUnifi in ("30","31","32","33","34"):
                mId=str(valuesDict["IPdeviceMACnumber"+nUnifi])
                if mId =="0":
                    mId = self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]
                elif mId =="1":
                    mId=""

                self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]	= mId
                if mId !="" and mId !="0"and mId !="1":
                    try:
                        mdevName=indigo.devices[int(mId)].name
                        if mId not in self.piBeaconDevices:
                            self.myLog("piBEacon",u"unifi mId 3 "+str(mId) + "  "+str(nUnifi))
                    except:
                        pass


            ## clean up unifi list
            keep=[]
            for nEvent in self.EVENTS:
                for nUnifi in ("30","31","32","33","34"):
                    mId=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]
                    if  mId !="" and mId !="0":
                        keep.append(mId)

            deleteM=[]
            for unifiId in self.unifiDevices:
                if unifiId not in keep: deleteM.append(unifiId)
            for unifiId in deleteM:
                del self.unifiDevices[unifiId]







            if not self.currentEventN in self.EVENTS:
                self.EVENTS[self.currentEventN]= copy.deepcopy(emptyEVENT)

            if valuesDict["DeleteEvent"]:
                for nDev in self.EVENTS[self.currentEventN]["IPdeviceMACnumber"]:
                    iDev= int(nDev)
                    valuesDict["IPdeviceMACnumber"+nDev]	="0"
                    if iDev <= nOfIDevicesInEvent:
                        valuesDict["iDeviceName"+nDev]			=""
                        valuesDict["iDeviceUseForHome"+nDev]	="0"
                        valuesDict["iDeviceUseForAway"+nDev]	="0"
                valuesDict["DeleteEvent"] 		= False
                valuesDict["distanceAwayLimit"]	= str(copy.deepcopy(emptyEVENT["distanceAwayLimit"]))
                valuesDict["distanceHomeLimit"]	= str(copy.deepcopy(emptyEVENT["distanceHomeLimit"]))
                valuesDict["minimumTimeAway"]	= str(copy.deepcopy(emptyEVENT["minimumTimeAway"]))
                valuesDict["enableDisable"] 	= False
                self.EVENTS[self.currentEventN] = copy.deepcopy(emptyEVENT)
                self.currentEventN ="0"
                valuesDict["selectEvent"] ="0"
                valuesDict["EVENT"] =json.dumps(self.EVENTS)
                return valuesDict

    ##### not delete
            if valuesDict["enableDisable"]      != "": self.EVENTS[self.currentEventN]["enableDisable"] 	= valuesDict["enableDisable"]
            else: self.EVENTS[self.currentEventN]["enableDisable"] = emptyEVENT["enableDisable"]; valuesDict["enableDisable"] =  emptyEVENT["enableDisable"];errorDict["enableDisable"]=emptyEVENT["enableDisable"]

            if valuesDict["minimumTimeHome"]    != "": self.EVENTS[self.currentEventN]["minimumTimeHome"] 	= float(valuesDict["minimumTimeHome"])
            else: self.EVENTS[self.currentEventN]["minimumTimeHome"] = emptyEVENT["minimumTimeHome"]; valuesDict["minimumTimeHome"] =  emptyEVENT["minimumTimeHome"];errorDict["minimumTimeHome"]=emptyEVENT["minimumTimeHome"]

            if valuesDict["minimumTimeAway"]    != "": self.EVENTS[self.currentEventN]["minimumTimeAway"]	= float(valuesDict["minimumTimeAway"])
            else: self.EVENTS[self.currentEventN]["minimumTimeAway"] = emptyEVENT["minimumTimeAway"]; valuesDict["minimumTimeAway"] =  emptyEVENT["minimumTimeAway"];errorDict["minimumTimeAway"]=emptyEVENT["minimumTimeAway"]

            if self.iDevicesEnabled:
                if valuesDict["distanceAwayLimit"]  != "": 
                        self.EVENTS[self.currentEventN]["distanceAwayLimit"] = int(float(valuesDict["distanceAwayLimit"]))
                else:   self.EVENTS[self.currentEventN]["distanceAwayLimit"] = emptyEVENT["distanceAwayLimit"]; valuesDict["distanceAwayLimit"] =  emptyEVENT["distanceAwayLimit"];errorDict["distanceAwayLimit"]=emptyEVENT["distanceAwayLimit"]

                if valuesDict["distanceHomeLimit"]  != "": 
                        self.EVENTS[self.currentEventN]["distanceHomeLimit"] = int(float(valuesDict["distanceHomeLimit"]))
                else:   self.EVENTS[self.currentEventN]["distanceHomeLimit"] = emptyEVENT["distanceHomeLimit"]; valuesDict["distanceHomeLimit"] =  emptyEVENT["distanceHomeLimit"];errorDict["distanceHomeLimit"]=emptyEVENT["distanceHomeLimit"]

                if valuesDict["maxLastTimeUpdatedDistanceMinutes"]!="":	
                        self.EVENTS[self.currentEventN]["maxLastTimeUpdatedDistanceMinutes"] =float(valuesDict["maxLastTimeUpdatedDistanceMinutes"])
                else:   self.EVENTS[self.currentEventN]["maxLastTimeUpdatedDistanceMinutes"] =float(emptyEVENT["maxLastTimeUpdatedDistanceMinutes"]);errorDict["maxLastTimeUpdatedDistanceMinutes"]=str(emptyEVENT["maxLastTimeUpdatedDistanceMinutes"])

            for lDev in range(1,nOfDevicesInEvent+1):
                nDev= str(lDev)
                if "IPdeviceMACnumber"+nDev not in valuesDict: continue
                selectedMAC = valuesDict["IPdeviceMACnumber"+nDev]
                if selectedMAC =="1" or selectedMAC =="":
                    self.EVENTS[self.currentEventN]["iDeviceName"][nDev]		= ""
                    self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	= "0"
                    self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	= "0"
                    self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]	= "0"
                    self.EVENTS[self.currentEventN]["currentStatusAway"][nDev]	= "0"
                    self.EVENTS[self.currentEventN]["currentStatusHome"][nDev]	= "0"
                    continue
                else:
                    self.EVENTS[self.currentEventN]["secondsOfLastON"][nDev]			= int(time.time()+20.)
                    self.EVENTS[self.currentEventN]["secondsOfLastOFF"][nDev]			= int(time.time()+20.)
                    idevName="0" # default, dont change..


                    if  self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]!= selectedMAC:
                        self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev] = selectedMAC


                    if self.iDevicesEnabled:
                        if not (str(valuesDict["iDeviceName"+nDev]) =="1" or str(valuesDict["iDeviceName"+nDev]) =="0" or str(valuesDict["iDeviceName"+nDev]) =="-1"):
                            idevD,idevName,idevId = self.getIdandName(valuesDict["iDeviceName"+nDev])
                            self.EVENTS[self.currentEventN]["iDeviceName"][nDev]= str(idevId)

                            if valuesDict["iDeviceUseForHome"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	="0";errorDict["iDeviceUseForHome"]=emptyEVENT["iDeviceUseForHome"]
                            else:										self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	=valuesDict["iDeviceUseForHome"+nDev]

                            if valuesDict["iDeviceUseForAway"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	="0";errorDict["iDeviceUseForAway"]=emptyEVENT["iDeviceUseForAway"]
                            else:										self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	=valuesDict["iDeviceUseForAway"+nDev]

                        elif str(valuesDict["iDeviceName"+nDev]) =="1" or str(valuesDict["iDeviceName"+nDev]) =="-1":
                            idevName =""
                        else:
                            if valuesDict["iDeviceUseForHome"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	="0";errorDict["iDeviceUseForHome"]=emptyEVENT["iDeviceUseForHome"]
                            else:										self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	=valuesDict["iDeviceUseForHome"+nDev]

                            if valuesDict["iDeviceUseForAway"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	="0";errorDict["iDeviceUseForAway"]=emptyEVENT["iDeviceUseForAway"]
                            else:										self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	=valuesDict["iDeviceUseForAway"+nDev]
                        if  idevName =="" :
                            self.EVENTS[self.currentEventN]["iDeviceName"][nDev]	    = ""
                            self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	= "0"
                            self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	= "0"





            valuesDict["EVENTS"]	=	json.dumps(self.EVENTS)

            valuesDict["MOTHER"]	=	{}

            valuesDict["piBeacon"]	=	json.dumps(self.piBeaconDevices)
            self.myLog("piBEacon",u"self.piBeaconDevices  "+unicode(self.piBeaconDevices))
            if valuesDict["piBeaconEnabled"]: self.updatepiBeacons()

            valuesDict["UNIFI"]	=	    json.dumps(self.unifiDevices)
            self.myLog("Unifi",u"self.unifiDevices  "+unicode(self.unifiDevices))
            if valuesDict["unifiEnabled"]: self.updateUnifi()

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        ##self.myLog("Mother","empty event "+ unicode(emptyEVENT))
        if len(errorDict) > 0: return  valuesDict, errorDict
        return  valuesDict




########################################
    def validatePrefsConfigUi(self, valuesDict):
        try:
            self.updatePrefs =True
            rebootRequired   = False
            
            self.debugLevel         = ""
            if valuesDict[u"debugLogic"]:   self.debugLevel += "Logic,"
            if valuesDict[u"debugPing"]:    self.debugLevel += "Ping,"
            if valuesDict[u"debugWifi"]:    self.debugLevel += "WiFi,"
            if valuesDict[u"debugEvents"]:  self.debugLevel += "Events,"
            if valuesDict[u"debugMother"]:  self.debugLevel += "Mother,"
            if valuesDict[u"debugiFind"]:   self.debugLevel += "iFind,"
            if valuesDict[u"debugpiBeacon"]:self.debugLevel += "piBEacon,"
            if valuesDict[u"debugpUnifi"]:  self.debugLevel += "Unifi,"
            if valuesDict[u"debugpAll"]:    self.debugLevel += "all,"

            xx   = valuesDict[u"indigoDevicesFolderName"]
            if xx != self.indigoDevicesFolderName:
                self.indigoDevicesFolderName    = xx
                try:
                    indigo.devices.folder.create(self.indigoDevicesFolderName)
                    self.myLog("all",self.indigoDevicesFolderName+ u" folder created")
                except:
                    pass
                self.indigoDeviceFolderID = indigo.devices.folders[self.indigoDevicesFolderName].id

            xx   = valuesDict[u"indigoVariablesFolderName"]
            if xx != self.indigoVariablesFolderName:
                self.indigoVariablesFolderName    = xx
                if self.indigoVariablesFolderName not in indigo.variables.folders:
                    self.indigoVariablesFolderID=indigo.variables.folder.create(self.indigoVariablesFolderName).id
                    self.myLog("all",self.indigoVariablesFolderName+ u" folder created")
                else:
                    self.indigoVariablesFolderID=indigo.variables.folders[self.indigoVariablesFolderName].id

            
            
    ## password handiling
            testi = valuesDict[u"inbetweenPingType"]
            try:
                testT = int(valuesDict[u"sleepTime"])
            except:
                testT = 5
            if testi != self.inbetweenPingType or testT != self.sleepTime:
                self.inbetweenPing={}
                self.killPing("all")
            self.inbetweenPingType = testi
            self.sleepTime = int(testT)
            pwdis = valuesDict[u"password"]

            netwT   = valuesDict[u"netwType"]
            network = str(valuesDict[u"network"])
            try:    str(int(netwT))
            except: netwT="24"
            
            nn= network.split(".")
            if len(nn) !=4:
                network =""
            else:
                ok =True
                for ii in nn:
                    try:    int(ii)
                    except: ok=False; break
            if self.theNetwork != network or self.netwType   != netwT:
                self.quitNOW="new Network"

            if network !="" and  ok:
                self.theNetwork = network
                self.netwType   = netwT
            valuesDict[u"netwType"] = str(self.netwType)
            valuesDict[u"network"]  = self.theNetwork
            self.IPaddressCalc      = IPaddressCalcClass.IPCalculator(self.theNetwork+"/"+self.netwType)
            self.netwInfo           =  self.IPaddressCalc.makeJson()
            self.broadcastIP        = self.netwInfo["broadcast"]
            


            error ="no"
            if pwdis == "yourPassword":
                self.passwordOK ="0"
                self.quitNOW ="no password"
                self.myLog("all",u"getting password.. not entered")
            else:
                valuesDict[u"password"] = "password is already stored"
                self.passwordOK ="2"
                if pwdis == "password is already stored":
                    self.yourPassword  = self.getPWD("fingscanpy")
                    self.myLog("Logic",u"getting password.. was already in system")

                else:  ## new password entered, store and send sucess message back
                    self.yourPassword = pwdis
                    valuesDict[u"password"] = "password is already stored"
                    self.myLog("Logic",u"password entered(&a3reversed#5B)=" +self.yourPassword)
                    self.storePWD(self.yourPassword,"fingscanpy")

            self.routerType = valuesDict[u"routerType"]
            if self.routerType !="0":
                try:
                    rtPW = valuesDict[u"routerPWD"]
                    if rtPW == "your router password here":
                        self.routerPWD	= ""
                        self.routerType = "0"
                    elif rtPW == "password is already stored":
                        self.routerPWD = self.getPWD("fingrt")
                    else:
                        self.routerPWD	= rtPW
                        self.storePWD(rtPW,"fingrt")
                        valuesDict[u"routerPWD"] ="password is already stored"
                    self.routerUID	= valuesDict[u"routerUID"]
                    self.routerIPn	= valuesDict[u"routerIPn"]
                    self.badWiFiTrigger["minSignalDrop"]			= float(valuesDict[u"minSignalDrop"])
                    self.badWiFiTrigger["minNumberOfDevicesBad"]	= float(valuesDict[u"minNumberOfDevicesBad"])
                    self.badWiFiTrigger["minNumberOfSecondsBad"]	= float(valuesDict[u"minNumberOfSecondsBad"])
                    self.badWiFiTrigger["minWiFiSignal"]			= float(valuesDict[u"minWiFiSignal"])
                except:
                    self.routerType =0
                    self.myLog("WiFi",u" router variables not initialized, bad data entered ")
        
                self.checkWIFIinfo()
                self.checkIfBadWiFi()
                self.checkDEVICES()
            else:
                self.wifiMacList={}
                self.oldwifiMacList={}
                valuesDict[u"wifiMacList"]=""



            if self.enableMACtoVENDORlookup != valuesDict[u"enableMACtoVENDORlookup"] and self.enableMACtoVENDORlookup == "0":
                rebootRequired                         = True
            self.enableMACtoVENDORlookup               = valuesDict[u"enableMACtoVENDORlookup"]

            self.acceptNewDevices = valuesDict[u"acceptNewDevices"] == "1"
#            if self.enableMotherDevices =="1":
#                indigo.devices.subscribeToChanges()
#            self.enableMotherDevices = valuesDict[u"enableMotherDevices"]
#            if self.enableMotherDevices =="1":
#                indigo.devices.subscribeToChanges()

    # clean up empty events
            self.cleanUpEvents()
    # save to indigo
            valuesDict["EVENTS"]	=	json.dumps(self.EVENTS)
            valuesDict["MOTHER"]	=	{}
            valuesDict["UNIFI"]	    =	json.dumps(self.unifiDevices)
            valuesDict["piBeacon"]	=	json.dumps(self.piBeaconDevices)

            self.printWiFi()
            self.printConfig()
            self.myLog("all","network info: "+unicode(self.netwInfo)+ " quitNow: "+ self.quitNOW)

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return True, valuesDict



########################################
    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        for theMAC in self.allDeviceInfo:
            if int(self.allDeviceInfo[theMAC]["deviceId"]) == devId:
                self.allDeviceInfo[theMAC]["hardwareVendor"]	= valuesDict["setHardwareVendor"]
                self.allDeviceInfo[theMAC]["deviceInfo"]		= valuesDict["setDeviceInfo"]
                self.allDeviceInfo[theMAC]["useWakeOnLanSecs"]	= int(valuesDict["setuseWakeOnLan"])
                if "useWakeOnLanLast" not in self.allDeviceInfo[theMAC]:
                    self.allDeviceInfo[theMAC]["useWakeOnLanLast"]		= 0
                self.allDeviceInfo[theMAC]["setWiFi"]			= valuesDict["setWiFi"]
                self.allDeviceInfo[theMAC]["usePing"]			= valuesDict["setUsePing"]
                self.allDeviceInfo[theMAC]["exprirationTime"]	= float(valuesDict["setExpirationTime"])
                self.allDeviceInfo[theMAC]["suppressChangeMSG"]	= valuesDict["setSuppressChangeMSG"]
                self.updateIndigoIpDeviceFromDeviceData(theMAC,["hardwareVendor","deviceInfo","WiFi","usePing","suppressChangeMSG"])
                self.updateIndigoIpVariableFromDeviceData(theMAC)
        return (True, valuesDict)




########################################
    def	cleanUppiBeacon(self):
    
        for nDev in self.piBeaconDevices:
            if "used" not in self.piBeaconDevices[nDev]:
                self.piBeaconDevices[nDev]["used"] = "0"

########################################
    def	cleanUpUnifi(self):
    
        for nDev in self.unifiDevices:
            if "used" not in self.unifiDevices[nDev]:
                self.unifiDevices[nDev]["used"] = "0"


########################################
    def	cleanUpEvents(self):
    
        try:
            
            for n in range(1,nEvents+1):
                nev= str(n)
                if nev not in self.EVENTS:
                    self.EVENTS[nev]= copy.deepcopy(emptyEVENT)
            
            for n in self.EVENTS:
                #evnt=self.EVENTS[n]

                for prop in emptyEVENT:
                    if prop not in self.EVENTS[n]:
                        self.EVENTS[n][prop]		= copy.deepcopy(emptyEVENT[prop])

                remProp=[]
                for prop in self.EVENTS[n]:
                    if prop not in emptyEVENT:
                        remProp.append(prop)
                for prop in remProp:
                    del self.EVENTS[n][prop]

                for i in range(1,nOfDevicesInEvent+1):
                    nDev= str(i)
                    if nDev not in self.EVENTS[n]["IPdeviceMACnumber"]:
                        for prop in emptyEVENT:
                            try:
                                self.EVENTS[n][prop][nDev]		= copy.deepcopy(emptyEVENT[prop]["1"])
                            except: 
                                pass                               
                                                
                    if int(nDev) >= piBeaconStart:#  here the mac number is the indigo device # , remove it if the indigo device is gone
                        if self.EVENTS[n]["IPdeviceMACnumber"][nDev] !="" and self.EVENTS[n]["IPdeviceMACnumber"][nDev] !="0":
                            try:
                                indigo.devices[int(self.EVENTS[n]["IPdeviceMACnumber"][nDev])]
                            except:
                                self.myLog("all",u"cleanupEVENTS removing device from evants as indigo device does not exist:"+ unicode(self.EVENTS[n]["IPdeviceMACnumber"][nDev]) ) 
                                self.EVENTS[n]["IPdeviceMACnumber"][nDev] = "0"   

                
                    if  int(nDev) <= piBeaconStart and int(nDev) < unifiStart:
                        if self.EVENTS[n]["IPdeviceMACnumber"][nDev] !="" and  self.EVENTS[n]["IPdeviceMACnumber"][nDev] !="0":
                            if self.EVENTS[n]["IPdeviceMACnumber"][nDev] in self.piBeaconDevices:
                                self.piBeaconDevices[self.EVENTS[n]["IPdeviceMACnumber"][nDev]]["used"]="1"
                
                    elif int(nDev) >= unifiStart:
                        if self.EVENTS[n]["IPdeviceMACnumber"][nDev] !="" and  self.EVENTS[n]["IPdeviceMACnumber"][nDev] !="0":
                            if self.EVENTS[n]["IPdeviceMACnumber"][nDev] in self.unifiDevices:
                                self.unifiDevices[self.EVENTS[n]["IPdeviceMACnumber"][nDev]]["used"]="1"
                
                if self.EVENTS[n]["distanceHomeLimit"]=="": self.EVENTS[n]["distanceHomeLimit"]	= copy.deepcopy(emptyEVENT["distanceHomeLimit"])
                if self.EVENTS[n]["distanceAwayLimit"]=="": self.EVENTS[n]["distanceAwayLimit"]	= copy.deepcopy(emptyEVENT["distanceAwayLimit"])
                if self.EVENTS[n]["minimumTimeHome"]=="":   self.EVENTS[n]["minimumTimeHome"]	= copy.deepcopy(emptyEVENT["minimumTimeHome"])

            try:
                del self.EVENTS["0"]
            except:
                pass
            try:
                del self.EVENTS[""]
            except:
                pass

            for nev in self.EVENTS:
                if "0" in self.EVENTS[nev]["IPdeviceMACnumber"]:
                    del  self.EVENTS[nev]["IPdeviceMACnumber"]["0"]
                for lll in range(1,nOfIDevicesInEvent+1):
                    lDev=str(lll)
                    idevD,idevName,idevId = self.getIdandName(self.EVENTS[nev]["iDeviceName"][lDev])
                    self.EVENTS[nev]["iDeviceName"][lDev]= str(idevId)
                    
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            
########################################
    def	resetEvents(self):
        try:
            self.EVENTS={}
            self.cleanUpEvents()
            self.pluginPrefs["EVENTS"]	=	json.dumps(self.EVENTS)
            self.myLog("Logic",u"ResetEVENTS done")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
########################################
    def	resetDevices(self):
        try:
            List =[]
            for dev in indigo.devices.iter("com.karlwachs.fingscan"):
                #if dev.pluginId.upper().find("FINGSCAN")>-1:  # put your plugin name here
                    List.append((dev.id,dev.name))
            self.myLog("all",u"deleting devices:"+ unicode(List))
            for devId in List:
                indigo.device.delete(devId[0])
    #		self.quitNOW = "loading data from file after Device reset"

            if not os.path.exists(self.fingSaveFileName):
                self.writeToFile()
            else:
                shutil.copy(self.fingSaveFileName,self.fingSaveFileName+str(time.time()))
                
            self.doLoadDevices()


            self.myLog("WiFi",u"ResetDEVICES done")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return

########################################
    def printEvents(self,printEvents="all"):
        try:
            if len(self.EVENTS) ==0:
                self.myLog("all",u"printEvents: no EVENT defined \n")
                return



            eventsToPrint=[]
            if printEvents=="all":
                for i in range(1,nEvents+1):
                    eventsToPrint.append(str(i))
            else:
                eventsToPrint.append(printEvents)
            eventsToPrint=sorted(eventsToPrint)
            
            timeNowSecs = str(int(time.time()))
            timeNowHMS = datetime.datetime.now().strftime("%H:%M:%S")
            
            for nEvent in eventsToPrint:
                if nEvent not in self.EVENTS: continue
                listOfDevs=[]
                evnt=self.EVENTS[nEvent]
                prntDist=False
                for nDev in evnt["IPdeviceMACnumber"]:
                    try:
                        if evnt["IPdeviceMACnumber"][nDev] =="": continue
                        if evnt["IPdeviceMACnumber"][nDev] =="0": continue
                        if evnt["iDeviceUseForHome"][nDev] =="1":prntDist=True
                        listOfDevs.append(int(nDev))
                    except:
                        continue
                if len(listOfDevs) ==0: continue
                self.myLog("all",u"EVENT:------------- "+nEvent.rjust(2)+"  ---------------------------------------------------------------")
                for iDev in range(1,nOfDevicesInEvent+1):
                    if iDev not in listOfDevs: continue
                    nDev = str(iDev)
                    #self.myLog("all",unicode(evnt["IPdeviceMACnumber"]))
                    try:
                        theMAC = evnt["IPdeviceMACnumber"][nDev]
                    except:
                        continue
                    
                    if int(nDev) < piBeaconStart:
                        devI = self.allDeviceInfo[theMAC]
                        self.myLog("all",u"dev#: "+str(nDev).rjust(2)+" -- devNam:"+devI["deviceName"].ljust(25)[:25] +" -- MAC#:"+theMAC+" -- ip#:"+devI["ipNumber"].ljust(15)+" -- status:"+devI["status"].ljust(8)+" -- WiFi:"+devI["WiFi"])
                    elif int(nDev) < piBeaconStart:
                        pass
                    elif int(nDev) < unifiStart:  # next section is pibeacon 
                        try:
                            name= 	self.piBeaconDevices[theMAC]["name"]
                        except:
                            self.getpiBeaconAvailable()
                            self.updatepiBeacons()
                            try:
                                name= 	self.piBeaconDevices[theMAC]["name"]
                            except:
                                self.myLog("all",u" piBeacon device IndigoID# "+theMAC+ " does not exist, check you piBeacon plugin" )
                                continue
                        status= self.piBeaconDevices[theMAC]["currentStatus"]
                        self.myLog("all",u"dev#: "+str(nDev)+" -- devNam:"+name.ljust(25)[:25] +" -- IND#:"+theMAC.ljust(17)+" --     "+" ".ljust(15)+" -- status:"+status.ljust(8))
                    else:
                        try:
                            name= 	self.unifiDevices[theMAC]["name"]
                        except:
                            self.getUnifiAvailable()
                            self.updateUnifi()
                            try:
                                name= 	self.unifiDevices[theMAC]["name"]
                            except:
                                self.myLog("all",u" unifi device IndigoID# "+theMAC+ " does not exist, check your unifi plugin" )
                                continue
                        status= self.unifiDevices[theMAC]["currentStatus"]
                        self.myLog("all",u"dev#: "+str(nDev)+" -- devNam:"+name.ljust(25)[:25] +" -- IND#:"+theMAC.ljust(17)+" --     "+" ".ljust(15)+" -- status:"+status.ljust(8))
                    


                self.printEventLine("currentStatusHome"	 ,"currentStatusHome"		,nEvent,listOfDevs)
                self.printEventLine("currentStatusAway"	 ,"currentStatusAway"		,nEvent,listOfDevs)
                if prntDist:
                    self.printEventLine("iDeviceName"			,"iDevice Name"				,nEvent,listOfDevs)
                    self.printEventLine("iDeviceUseForHome"		,"iDeviceUseForHome"		,nEvent,listOfDevs)
                    self.printEventLine("iDeviceUseForAway"		,"iDeviceUseForAway"		,nEvent,listOfDevs)
                    self.printEventLine("iDeviceAwayDistance"	,"iDeviceCurrntAwayDist"	,nEvent,listOfDevs)
                    self.printEventLine("iDeviceHomeDistance"	,"iDeviceCurrntHomeDist"	,nEvent,listOfDevs)
                self.printEventLine(	"timeOfLastOFF"			,"time WhenLast DOWN"		,nEvent,listOfDevs)
                self.printEventLine(	"timeOfLastON"			,"time WhenLast UP"			,nEvent,listOfDevs)
                self.printEventLine(	"secondsOfLastON"		,"seconds WhenLast UP"		,nEvent,listOfDevs)
                self.printEventLine(	"secondsOfLastOFF"		,"seconds WhenLast DOWN"	,nEvent,listOfDevs)
                if prntDist:
                    pass
                    #self.printEventLine("iDeviceInfoTimeStamp"	,"iDeviceInfoTimeStamp"		,nEvent,listOfDevs)
                self.myLog("all",  	"Time right now:          :"+timeNowHMS.rjust(12))
                self.myLog("all",  	"ALL Devices         Home :"+str(evnt["allHome"]).rjust(12)+"  -- reacts after minTimeNotHome")
                self.myLog("all",  	"AtLeast ONE Device  Home :"+str(evnt["oneHome"]).rjust(12)+"  -- reacts after minTimeNotHome")
                self.myLog("all",  	"ALL Devices         Away :"+str(evnt["allAway"]).rjust(12)+"  -- reacts minTimeAway bf Trig")
                self.myLog("all",  	"AtLeast ONE Device  Away :"+str(evnt["oneAway"]).rjust(12)+"  -- reacts minTimeAway bf Trig")
                if prntDist:
                    self.myLog("all", "minDist.toBeAway         :"+str("%5.2f"%float(evnt["distanceAwayLimit"])).rjust(12))
                    self.myLog("all", "minDist.toBeNotHome      :"+str("%5.2f"%float(evnt["distanceHomeLimit"])).rjust(12))
                    self.myLog("all", "max age of dist info     :"+str(evnt["maxLastTimeUpdatedDistanceMinutes"]).rjust(12))
                self.myLog("all",     "minTimeAway bf Trig      :"+str("%5.0f"%float(evnt["minimumTimeAway"])).rjust(12))
                self.myLog("all",     "minTimeNotHome bf re-Trig:"+str("%5.0f"%float(evnt["minimumTimeHome"])).rjust(12))
                self.myLog("all",     "Event enabled            :"+str(evnt["enableDisable"]).rjust(12))
                self.myLog("all",     "dataFormat               :"+str(evnt["dataFormat"]).rjust(12))
            self.myLog("all",u"\n")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
########################################
    def printEventLine(self, name,nameText,nEvent,listOfDevs):
        try:
            list =""
            for iDev in range(1,nOfDevicesInEvent+1):
                if iDev not in listOfDevs: continue
                nDev = str(iDev)
                if name == "secondsOfLastON" or  name == "secondsOfLastOFF" :
                    list +="#"+nDev.rjust(2)+":"+ str( int(time.time()) - int(self.EVENTS[nEvent][name][nDev]) ).rjust(15)+"  "
                elif name == "iDeviceName" :
                    idevD,idevName,idevId = self.getIdandName(str(self.EVENTS[nEvent][name][nDev]))
                    list +="#"+nDev.rjust(2)+":"+idevName.rjust(15)+"  "
                else:
                    list +="#"+nDev.rjust(2)+":"+str(self.EVENTS[nEvent][name][nDev]).rjust(15)+"  "
            self.myLog("all", (nameText+":").ljust(22) + list.strip("  "))
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e)+"\n"+unicode(self.EVENTS[nEvent]))
        return

#		self.myLog("all",u"<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )
########################################
    def	printWiFi(self,printWiFi="all"):
        
        try:
            if len(self.wifiMacList) ==0:
                self.myLog("all",u"printWiFi: no WiFi devices defined")
                return
            if self.routerType !=0:
                self.updateDeviceWiFiSignal()
                self.myLog("all",u"WiFi info router type:"+ self.routerType + "-- IP#/page: "+self.routerIPn+"   .....ACTIVE Wifi device list:" )
                self.myLog("all",u"---- MAC # ------ ---- device Name ----- ------ ip# ----- -WiFi- -Signal- -aveSign -Associated Authorized" )
                self.printWiFiDevs("5GHz",Header=True)
                self.printWiFiDevs("2GHz")
                self.printWiFiDevs("")
                self.myLog("all",u"")
                self.printWiFiAve("2GHz",Header=True)
                self.printWiFiAve("5GHz")
                self.myLog("all",u"")
                self.myLog("all",u"settings for badWiFiSignalTrigger ")
                self.myLog("all",u" minNumberOfSecondsBad: %5.1f"%(self.badWiFiTrigger["minNumberOfSecondsBad"]))
                self.myLog("all",u" minNumberOfDevicesBad: %5.1f"%(self.badWiFiTrigger["minNumberOfDevicesBad"]))
                self.myLog("all",u" minSignalDrop:         %5.1f"%(self.badWiFiTrigger["minSignalDrop"]))
                self.myLog("all",u" minWiFiSignal:         %5.1f"%(self.badWiFiTrigger["minWiFiSignal"]))
                self.myLog("all",u"-------------------------------------------------------------------------------------------------------- ")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        return
########################################
    def printpiBeaconDevs(self):
        try:
            ## refresh piBeacon cokkies
            self.getpiBeaconAvailable()
            if len(self.piBeaconDevices) ==0: return
            
            self.myLog("all",u"===      piBeacon devices  available  to fingscan    ===        START")
            #				 123456789012345678901234567890123412345678123456789012
            self.myLog("all",u"--Device Name------        indigoID--    --Status  lastUpdate  used")
            list=[]
            for theMAC in self.piBeaconDevices:
                list.append((theMAC,self.piBeaconDevices[theMAC]["name"]))
            list = sorted(list, key=lambda tup: tup[1])
            for ii in range(len(list)):
                theMAC = list[ii][0]
                if theMAC in self.piBeaconDevices:
                    try:
                        theString = self.piBeaconDevices[theMAC]["name"].ljust(27)
                        theString+= theMAC.ljust(14)
                        theString+= self.piBeaconDevices[theMAC]["currentStatus"].rjust(8)
                        lastUpdate= datetime.datetime.fromtimestamp(self.piBeaconDevices[theMAC]["lastUpdate"]).strftime('%H:%M:%S')
                        theString+= str(lastUpdate).rjust(12)
                        theString+= self.piBeaconDevices[theMAC]["used"].rjust(6)
                    
                        self.myLog("all",theString)
                    except:
                        self.myLog("all",u" data wrong for "+unicode(theMAC) +"    "+ unicode(self.piBeaconDevices))
            self.myLog("all",u"===      piBeacon devices  available  to fingscan    ===        END")
    
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

########################################
    def printUnifiDevs(self):
        try:
            ## refresh piBeacon cokkies
            self.getUnifiAvailable()
            if len(self.unifiDevices) ==0: return
            
            self.myLog("all",u"===      Unifi   devices  available  to fingscan    ===        START")
            #				 123456789012345678901234567890123412345678123456789012
            self.myLog("all",u"--Device Name------        indigoID--    --Status  lastUpdate  used")
            list=[]
            for theMAC in self.unifiDevices:
                list.append((theMAC,self.unifiDevices[theMAC]["name"]))
            list = sorted(list, key=lambda tup: tup[1])
            for ii in range(len(list)):
                theMAC = list[ii][0]
                if theMAC in self.unifiDevices:
                    try:
                        theString = self.unifiDevices[theMAC]["name"].ljust(27)
                        theString+= theMAC.ljust(14)
                        theString+= self.unifiDevices[theMAC]["currentStatus"].rjust(8)
                        lastUpdate= datetime.datetime.fromtimestamp(self.unifiDevices[theMAC]["lastUpdate"]).strftime('%H:%M:%S')
                        theString+= str(lastUpdate).rjust(12)
                        theString+= self.unifiDevices[theMAC]["used"].rjust(6)
                        self.myLog("all",theString)
                        
                    except Exception, e:
                        self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
                        self.myLog("all",u" data wrong for "+unicode(theMAC) +"    "+ unicode(self.unifiDevices[theMAC]))
            self.myLog("all",u"===      unifi devices  available  to fingscan    ===        END")
    
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))


########################################
    def printWiFiDevs(self, ghz,Header=False):
        try:
            for theMAC in self.wifiMacList:
                if theMAC in self.allDeviceInfo:
                    devI=self.allDeviceInfo[theMAC]
                    if devI["WiFi"] != ghz: continue
                    theString = theMAC
                    theString+= " "		+devI["deviceName"].ljust(22)
                    theString+= " "		+devI["ipNumber"].ljust(17)
                    theString+= " "		+devI["WiFi"].ljust(4)
                    try:
                        theString+= "  %7.0f"%(self.wifiMacList[theMAC][2])
                    except:
                        theString+= "  "+str(self.wifiMacList[theMAC][2]).ljust(7)
                    try:
                        theString+= "   %7.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))
                    except:
                        theString+= "   0      "
                    theString+= "  "	+self.wifiMacList[theMAC][0].rjust(7)
                    theString+= "    "	+self.wifiMacList[theMAC][1].rjust(7)
                    if devI["deviceName"].find("unidentifiedWiFiDevice") > -1:
                        theString+=" some times devices with wifi AND ethernet show this behaviour"
                    self.myLog("all",theString)
                else:
                    self.myLog("all",theMAC+
                        " -device is expired, not in dev list any more- "+str(self.wifiMacList[theMAC]) +" some times devices with wifi AND ethernet show this behaviour")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

########################################
    def printWiFiAve(self, ghz,Header=False):
        try:
            if Header: self.myLog("all",u"overall WiFi stats:")
            self.myLog("all",u" "+ghz+": ave.Signal[dBm]%4.0f,  curr.Signal:%4.0f,  NumberOfMeasurements:%6.0f,  NumberOfCycles:%6.0f, ave.NumberofDevices:%2.0f, curr.NumberOfDevicesConnected:%2.0f,  noiseLevel: %s"
                %( (self.wifiMacAv["sumSignal"][ghz]/max(1.0,self.wifiMacAv["numberOfDevices"][ghz]))
                 , self.wifiMacAv["curAvSignal"][ghz]
                 , self.wifiMacAv["numberOfDevices"][ghz]
                 , self.wifiMacAv["numberOfCycles"][ghz]
                 , (self.wifiMacAv["numberOfDevices"][ghz]/max(1.0,self.wifiMacAv["numberOfCycles"][ghz]))
                 , self.wifiMacAv["curDev"][ghz]
                 , self.wifiMacAv["noiseLevel"][ghz])
                 )
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
        

##### execute triggers:

######################################################################################
    # Indigo Trigger Start/Stop
######################################################################################

    def triggerStartProcessing(self, trigger):
#		self.myLog("WiFi",u"<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )iDeviceHomeDistance
        self.triggerList.append(trigger.id)
#		self.myLog("WiFi",u"exiting triggerStartProcessing -->>")

    def triggerStopProcessing(self, trigger):
#		self.myLog("WiFi",u"<<-- entering triggerStopProcessing: %s (%d)" % (trigger.name, trigger.id))
        if trigger.id in self.triggerList:
#			self.myLog("WiFi",u"TRIGGER FOUND")
            self.triggerList.remove(trigger.id)
#		self.myLog("WiFi", u"exiting triggerStopProcessing -->>")

    #def triggerUpdated(self, origDev, newDev):
    #	self.logger.log(4, u"<<-- entering triggerUpdated: %s" % origDev.name)
    #	self.triggerStopProcessing(origDev)
    #	self.triggerStartProcessing(newDev)


######################################################################################
    # Indigo Trigger Firing
######################################################################################

    def triggerEvent(self, eventId):
        try:
            self.myLog("Events",u"triggerEvent: %s " % eventId,type="EVENT")
            for trigId in self.triggerList:
                trigger = indigo.triggers[trigId]
                self.myLog("Events",u"testing trigger id: "+ str(trigId).rjust(12)+"; eventId:"+ str(eventId).rjust(12)+";  "+ unicode(trigger.pluginTypeId),type="EVENT")
                if trigger.pluginTypeId == eventId:
                    self.myLog("Events",u"firing trigger id : "+ str(trigId),type="EVENT")
                    indigo.trigger.execute(trigger)
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return






####################


    ####################  startup / config methods  #######################

########################################
    def storePWD(self,passw,name):
        try:
            ## store pwd into keychain
            storePassword = "&a3"+passw[::-1]+"#5B"  # fist reverse password, then add 4 char before and after,
            ret =subprocess.Popen( "/usr/bin/security add-generic-password -a fingscanpy -w \'"+ storePassword+"\' -s "+name+" -U",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            retCode =str(ret.communicate())
            ret.stdout.close()
            ret.stderr.close()
            return
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

########################################
    def getPWD(self,name):
        try:
            ## get pwd from keychain
            ret= subprocess.Popen(["security","find-generic-password","-gl",name], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            storePassword= ret.communicate()[1]
            ret.stdout.close()
            ret.stderr.close()
            self.myLog("Logic",u"password entered (&a3reversed#5B)=" +str(storePassword))
            try:
                storePassword.index("password")  # if the return text contains "password" its ok, continue
                storePassword= str(storePassword).split('"')[1]
                return storePassword[3:-3][::-1] ## 1. drop fist and last 3 characaters, then reverse string
            except:  # bad return, no password stored, return "0"
                return "0"
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))


########################################
    def inpDummy(self):
        return
########################################
########################################
    def pickDeviceCALLBACK(self,valuesDict,typeId):
        devId=int(valuesDict["device"])
        if devId >0:
            dev =indigo.devices[devId]
            devName= dev.name
            self.myLog("WiFi",u" device selected:"+str(devId)+"/"+devName)
        else:
            self.myLog("WiFi",u" device selected:"+ " all")
            
        return True
########################################
    def pickDeviceFilter(self,filter=None,valuesDict=None,typeId=0):
        retList =[]
        for dev in indigo.devices.iter("com.karlwachs.fingscan"):
#			self.myLog("WiFi",dev.pluginId+" "+dev.name)
            #if dev.pluginId.upper().find("FINGSCAN")>-1:  # put your plugin name here
#				self.myLog("WiFi",u" adding "+dev.name)
                retList.append((dev.id,dev.name))
        retList.append((0,"all devices"))
        return retList
########################################
    def triggerEventCALLBACK(self,valuesDict,typeId):
        self.myLog("all",u"received trigger event from menu: "+ unicode(valuesDict))
        self.triggerEvent(valuesDict["triggerEvent"])
        return



########### menue in and out ###########
    def getMenuActionConfigUiValues(self, menuId):
        #indigo.server.log(u'Called getMenuActionConfigUiValues(self, menuId):')
        #indigo.server.log(u'     (' + unicode(menuId) + u')')

        valuesDict = indigo.Dict()
        valuesDict["selectEvent"]="0"  
        errorMsgDict = indigo.Dict()
        return (valuesDict, errorMsgDict)
########################################
    def inpPrintEVENTS(self):
        self.indigoCommand = "PrintEVENTS"
        self.myLog("all",u"command: Print EVENTS and configuration")
        return
########################################
    def inpToggleDebug(self):
        if self.debugLevel !="":
            self.debugLevel =""
            self.myLog("all",u"command: debug set to OFF")
        else:
            self.debugLevel ="all"
            self.myLog("all",u"command: debug set to ON")
        self.pluginPrefs["debugLevel"] =self.debugLevel
        return

########################################
    def inpPrintWiFi(self):
        self.indigoCommand = "PrintWiFi"
        self.myLog("all",u"command: Print WiFi information and configuration")
        return
########################################
    def inpPrintMother(self):
        self.indigoCommand = "PrintMother"
        self.myLog("all",u"command: Print Mother information")
        return
########################################
    def inpPrintpiBeacon(self):
        self.indigoCommand = "PrintpiBeacon"
        self.myLog("all",u"command: Print piBeacon information")
        return
########################################
    def inpPrintUnifi(self):
        self.indigoCommand = "PrintUnifi"
        self.myLog("all",u"command: Print unifi information")
        return


########################################
    def inpResetEVENTS(self):
        self.indigoCommand = "ResetEVENTS"
        self.myLog("all",u"command: ResetEVENTS")
        return
########################################
    def inpResetDEVICES(self):
        self.indigoCommand = "ResetDEVICES"
        self.myLog("all",u"command: ResetDEVICES")
        return
########################################  not used anymore
    def inpEVENTAway1(self):
        self.indigoCommand = "EVENT_Away_1"
        self.myLog("all",u"command: EVENT_Away_1")
        return
########################################  not used anymore
    def inpEVENTHome1(self):
        self.indigoCommand = "EVENT_Home_1"
        self.myLog("all",u"command: EVENT_Home_1")
        return

########################################
    def inpSaveData(self):
        self.indigoCommand = "save"
        self.myLog("all",u"command: save")
        retCode = self.writeToFile()
        self.indigoCommand = "none"
        self.myLog("all",u"save done")
        return
        

########################################
    def inpLoadDevices(self):
        self.indigoCommand = "loadDevices"
        self.myLog("all",u"command: loadDevices")
        return


########################################
    def inpSortData(self):
        self.indigoCommand = "sort"
        self.myLog("all",u"command: sort")
        return

########################################
    def inpDetails(self):
        self.indigoCommand = "details"
        self.myLog("all",u"command: log IP-Services of your network")
        return

########################################
    def inpSoftrestart(self):
        self.quitNOW = "softrestart"
        self.myLog("all",u"command: softrestart")
        return


########################################


########################################
    def doLoadDevices(self):
        try:
            retcode = self.deleteIndigoIpDevicesData("all")
            self.sleep(1)
            retCode= self.readFromFile()
            self.sleep(1)
            retCode = self.getIndigoIpVariablesIntoData()
            self.sleep(1)
            retCode = self.updateallDeviceInfofromVariable()
            self.sleep(1)
            retcode = self.updateAllIndigoIpDeviceFromDeviceData()
            self.sleep(1)
            self.myLog("all",u"       restore done")
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return


########################################
    def doSortData(self):
        self.myLog("all",u"sorting ipDevices with IP Numbers")
        retCode = self.getIndigoIpVariablesIntoData()
        retCode = self.sortIndigoIndex()
        retCode = self.getIndigoIpVariablesIntoData()
        self.myLog("all",u" sorting  done")
        return

########################################
    def doDetails(self):

        self.myLog("all",u"starting log IP-Services of your network, might take several minutes, it will test each port on each ip-device")
        ## ask fing to produce details list of services per ip number
        ret=""
        try:
            cmd ="echo '"+self.yourPassword+"' | sudo -S "+self.fingEXEpath+"  -s "+self.theNetwork+"/"+str(self.netwType)+" -o json,"+self.fingServicesFileName+" > "+self.fingServicesLOGFileName
            self.myLog("all",u"fing network scan: "+self.theNetwork+u"/"+str(self.netwType))
            self.myLog("Events",cmd)
            
            ret =subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            self.myLog("all",u"  fing details failed: fing returned an error: "+unicode(ret))
            return

            
        ## read fing output file
        try:
            f = open(self.fingServicesFileName,"r")
            fingOut = f.read()
            f.close()
        except Exception, e:
            self.myLog("all",u"  fing details failed , no output file")
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            return
            
        ## now get the list into theServices
        try:
        
            self.theServices=json.loads(fingOut.replace(",},","},").replace("},]","}]").replace("':",'":').replace(":'",':"').replace("','",'","').replace("{'",'{"').replace("'}",'"}'))
            #self.theServices=json.loads(fingOut.replace("'",'"').replace(",},","},").replace("},]","}]"))  ## this replaces ' with " and removes comas:  ,} and },], json does not like these empty fields
#			self.myLog("all",u"  "+str(self.theServices[6]))
        except:
            self.myLog("all",u"  fing details failed: json command went wrong ")
            self.myLog("all",unicode(fingOut))
            return
        
        retCode = self.getIndigoIpVariablesIntoData()  ## refresh indigo data

        fout=open(self.fingServicesOutputFileName,"w")
        fout.write("IP-Device port scan on  "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"  -------------------------------------------------------------- "+"\n")
        self.myLog("all",u"IP-Device port scan on  "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"  --------------------------- ",type= "IP-Device Number, Name, Vendor,...")

##self.fingServicesOutputFileName
####
# now put the results into the logfile
        theLength1 = len(self.theServices)
        macIndex=[]
        for ii in range(0,theLength1):
            ipNo =str(self.theServices[ii][u"Address"])
                
            scanResult =str(self.theServices[ii][u"ScanResult"])
            ## have all indexes , merge indigo and fing info
            
            if scanResult !=u"OK": continue
            try:
                theMAC =str(self.theServices[ii][u"HardwareAddress"])
                if len(theMAC) < 16 : continue
                macIndex.append(theMAC)
                devV= self.indigoIpVariableData[theMAC]
                n1=devV[u"nickName"].strip()
                n2=devV[u"hardwareVendor"].strip()
                n3=devV[u"deviceInfo"].strip()
                if n3==u"-":n3=""
                nickname= (n1+u" "+n2+u" "+n3).strip()
            except:
                nickname= u""
                theMAC=u""
#				fout.write("IP-Device Number, Name, Vendor,..." +" "+"------------------------------------------------------------------------ "+"\n")
            fout.write("\n")
            self.myLog("all",u"------------------------------------------------------------------------ " ,type= u"IP-Device Number, Name, Vendor,...")
            theLength2 = len(self.theServices[ii]["Services"])
            if theLength2 >0:
                fout.write((u"IP-Device Number, Name, Vendor,... "
                    +self.theServices[ii]["Address"].ljust(17)
                    +theMAC												+" "
                    +self.theServices[ii][u"Hostname"].ljust(24)
                    +nickname.ljust(35)
                    +u"firewall:" + str(self.theServices[ii][u"FirewallDetected"])
                    +u"\n").encode("utf8"))
                self.myLog("all",
                     self.theServices[ii][u"Address"].ljust(17)
                    +theMAC												+" "
                    +self.theServices[ii][u"Hostname"].ljust(24)
                    +nickname.ljust(35)
                    +u"firewall:" + str(self.theServices[ii]["FirewallDetected"])
                    ,type= u"IP-Device Number, Name, Vendor,...")
                for kk in range(0,theLength2):
                    fout.write((u"..... service Port, Name, Comment: "
                        + str(self.theServices[ii][u"Services"][kk][u"Port"]).ljust(7)
                        + str(self.theServices[ii][u"Services"][kk][u"Name"]).ljust(18)
                        +             str(self.theServices[ii][u"Services"][kk][u"Description"])
                        +"\n").encode("utf8"))
                    self.myLog("all",u"    "
                        + str(self.theServices[ii][u"Services"][kk][u"Port"]).ljust(7)
                        + str(self.theServices[ii][u"Services"][kk][u"Name"]).ljust(18)
                        +             str(self.theServices[ii][u"Services"][kk][u"Description"])
                        ,type= u"..... service Port, Name, Comment:" )
            else:

                fout.write((u"IP-Device Number, Name, Vendor,... "
                    +self.theServices[ii][u"Address"].ljust(17)
                    +theMAC												+u" "
                    +self.theServices[ii][u"Hostname"].ljust(24)
                    +nickname.ljust(35)
                    +u"firewall:" + str(self.theServices[ii][u"FirewallDetected"])
                    +u"\n").encode("utf8"))
                self.myLog("all",
                     self.theServices[ii]["Address"].ljust(17)
                    +theMAC												+" "
                    +self.theServices[ii]["Hostname"].ljust(24)
                    +nickname.ljust(35)
                    +u"firewall:" + str(self.theServices[ii][u"FirewallDetected"])
                    ,type= u"IP-Device Number, Name, Vendor,...")
                fout.write("..... service Port, Name, Comment: "
                    +u"00000  Port Responding   No Answer from Device"
                    +u"\n")
                self.myLog("all",u"    "
                    + u"00000  Port Responding   No Answer from Device"
                    ,type= u"..... service Port, Name, Comment:" )
    
# not found in fing scan use indigo data only
        self.myLog("all",u"------------------------------------------------------------------------ " ,type= "uIP-Device Number, Name, Vendor,...")
        self.myLog("all",u"no FING info for devices: " ,type= u"IP-Device Number, Name, Vendor,...")
        fout.write(u"\n")
        fout.write(u"no answers form devicess: "+"\n")
        for theMAC in self.indigoIpVariableData:
            try:
                macIndex.index(theMAC) # if this ok, it was done already
                continue
            except:
                devI= self.allDeviceInfo[theMAC]
                n1=devI[u"nickName"].strip()
                n2=devI[u"hardwareVendor"].strip()
                n3=devI[u"deviceInfo"].strip()
                n4=u"status: "+devI[u"status"].strip()
                if n3=="-":n3=""
                nickname= (n1+" "+n2+" "+n3)
                fout.write(
                    (u"IP-Device Number, Name, Vendor,... "
                    + devI[u"ipNumber"].ljust(17)
                    +theMAC.ljust(19)
                    +n4.ljust(17)
                    +nickname
                    +u"\n").encode("utf8"))
                self.myLog("all",
                     devI[u"ipNumber"].ljust(17)
                    +theMAC.ljust(19)
                    +n4.ljust(17)
                    +nickname
                    ,type= u"IP-Device Number, Name, Vendor,...")
        fout.write(u"IP-Device port scan end             ------------------------------------------------------------------------ "+u"\n")
        self.myLog("all",u"------------------------------------------------------------------------ " ,type= u"IP-Device Number, Name, Vendor,...")
        fout.close()
        


        self.myLog("all",u"         log IP-Services of your network, .......  done")
        return
    
    
########################################
    def writeToFile(self):
        
        self.myLog("all",u"saving indigo data to file")
        f = open ( self.fingSaveFileName , u"w")
        nwrite= min( len(self.indigoDevicesNumbers),self.indigoNumberOfdevices )
        for kk in range(nwrite):
                writestring = unicode(self.indigoDevicesNumbers[kk] )+u";"+self.indigoDevicesValues[kk]+u"\n"
                f.write(writestring.encode("utf8"))
        f.close()
        self.myLog("all",u" saved")
        
        return 0


########################################
    def readFromFile(self):
        self.myLog("all",u"restore indigo data from file")
        f= open ( self.fingSaveFileName , "r")
        lastD=0
        self.indigoDevicesNumbers = []
        for line in f.readlines():
            ipDevNumber = line[:2]
            if len(ipDevNumber) >1 :
                lastD+=1
                kk00=self.int2hexFor2Digit(lastD)
                self.indigoDevicesNumbers.append(kk00)

                self.myLog("all",u" create re-store indigo data from file")
                try:
                    test = indigo.variable.updateValue("ipDevice"+kk00,line[3:])
                    self.myLog("all",u" updated variable:"+kk00 )
                except:
                    test = indigo.variable.create(u"ipDevice"+kk00,line[3:],folder=self.indigoVariablesFolderID)
                    self.myLog("all",u" created variable:"+kk00+u" folder:"+str(self.indigoVariablesFolderID))
        f.close()
        test = indigo.variable.updateValue(u"ipDevsNoOfDevices",str(lastD))
        
        for kk in range(lastD,indigoMaxDevices):
            kk00 = self.int2hexFor2Digit(kk+1)						# make it 01 02 ..09 10 11 ..99
            try:
                indigo.variable.delete(u"ipDevice"+kk00)  # delete any entry > # of devices
            except:
                pass
        
#		self.myLog("all",u"  restored")
        
        return 0
    
########################################
    def int2hexFor2Digit(self,numberIn):
        if numberIn < 10: return "0"+str(numberIn)
        if numberIn <100: return str(numberIn)
        nMod = str(numberIn%100)
        if len(nMod) <2: nMod ="0"+nMod  # 105 ==> A05; 115 ==> A15 205 ==> B05;  215 ==> B15
        x = numberIn/100
        if x ==1: return "A"+nMod
        if x ==2: return "B"+nMod
        if x ==3: return "C"+nMod
        if x ==4: return "D"+nMod
        if x ==5: return "E"+nMod
        return "F"+nMod


########################################
    def getIgnoredMAC(self):
        self.ignoredMAC ={}
        try:
            f= open (self.ignoredMACFile , "r")
            self.ignoredMAC =json.loads(f.read())
            f.close()
        except: pass
        self.saveIgnoredMAC()

########################################
    def saveIgnoredMAC(self):
        try:
            f= open (self.ignoredMACFile , "w")
            f.write(json.dumps(self.ignoredMAC))
            f.close()
        except: pass 


########################################
    def initIndigoParms(self):
        ## get folder if it exists, if not it is 0, then set it to IP devices


        self.indigoDevicesFolderName  = self.pluginPrefs.get(u"indigoDevicesFolderName",   u"ipDevices")
        if len(self.indigoDevicesFolderName)   < 2: self.indigoDevicesFolderName    = u"ipDevices"
        
        try:
            indigo.devices.folder.create(self.indigoDevicesFolderName)
            self.myLog("all",self.indigoDevicesFolderName+ u" folder created")
        except:
            pass
        self.indigoDeviceFolderID = indigo.devices.folders[self.indigoDevicesFolderName].id
        self.pluginPrefs["indigoDeviceFolderID"] = self.indigoDeviceFolderID


        self.indigoVariablesFolderName = self.pluginPrefs.get(u"indigoVariablesFolderName", "IP devices")
        if len(self.indigoVariablesFolderName) < 2: self.indigoVariablesFolderName  = u"IP devices"
        if self.indigoVariablesFolderName not in indigo.variables.folders:
            self.indigoVariablesFolderID=indigo.variables.folder.create(self.indigoVariablesFolderName).id
            self.myLog("all",self.indigoVariablesFolderName+ u" folder created")
        else:
            self.indigoVariablesFolderID=indigo.variables.folders[self.indigoVariablesFolderName].id

        self.pluginPrefs[u"indigoVariablesFolderName"] = self.indigoVariablesFolderName
               
                
        try:
            test = indigo.variable.create(u"ipDevice00",u"MAC-Number                ;     IP-Number       ;   Time-Of-Last-Change   ;Status;     N.of-Ch.    ;   Nick-Name                 ;   Hardware-Vendor        ;   DeviceInfo               ; WiFi  ;   usePing",self.indigoVariablesFolderID)
        except:
            test = indigo.variable.updateValue(u"ipDevice00",u"MAC-Number                ;     IP-Number       ;   Time-Of-Last-Change   ;Status;     N.of-Ch.    ;   Nick-Name                 ;   Hardware-Vendor        ;   DeviceInfo               ;  WiFi  ;   usePing")
        try:
            test = indigo.variable.create(u"ipDevsLastUpdate",u"1",self.indigoVariablesFolderID)	;
        except:
            pass
        try:
            test = indigo.variable.create(u"ipDevsNewIPNumber",u"1",self.indigoVariablesFolderID)	;
        except:
            pass
        try:
            test = indigo.variable.create(u"ipDevsNoOfDevices",u"0",self.indigoVariablesFolderID)	;
        except:
            pass
        try:
            test = indigo.variable.create(u"ipDevsNewDeviceNo",u"0",self.indigoVariablesFolderID)	;
        except:
            pass
        try:
            test = indigo.variable.updateValue(u"ipDevsCommand",u"-- not used anymore can be deleted --")	;
        except:
            pass
        try:
            test = indigo.variable.updateValue(u"ipDevsPid",u"-- not used anymore can be deleted --")		;
        except:
            pass
        try:
            test = indigo.variable.updateValue(u"ipDevsFormat",u"-- not used anymore can be deleted --")	;
        except:
            pass
        try:
            test = indigo.variable.updateValue(u"ipDevsDoNotAsk",u"-- not used anymore can be deleted --");
        except:
            pass
        try:
            test = indigo.variable.updateValue(u"ipDevsPasswordMode",u"-- not used anymore can be deleted --");
        except:
            pass
        try:
            test = indigo.variable.updateValue(u"ipDevsDebug",u"-- not used anymore can be deleted --")	;
        except:
            pass

        self.myLog("all",u"indigo variables initialized" )


        return 0
    
    
    
########################################
    def initFing(self,restartFing):
        
        self.fingRestartCount +=1

        if self.fingRestartCount > 5:  # starts # 1
            self.myLog("all",u"  (re)started FING 5 times, quiting ... reloading the plugin ")
            self.quitNOW ="FING problem"
            return -1
            
        ## create directory if it does not exist
        try:
            subprocess.Popen("mkdir "+  self.fingDataDir + "  > /dev/null 2>&1 &",shell=True)
        except:
            pass


        
        if os.path.exists(self.fingLogFileName):
            if int(os.path.getsize(self.fingLogFileName)) > 10000000:
                try:
                    try: os.remove(self.fingLogFileName+".log")
                    except: pass
                    os.rename(self.fingLogFileName, self.fingLogFileName+".log")
                except:
                    pass
            ## logfile exists
        else:  ## if not create file
            subprocess.Popen("echo 0 > "+ self.fingLogFileName + " &",shell=True)
        
            
        if os.path.exists(self.fingDataFileName):
            pass
        else:  ## if not create file
            subprocess.Popen("echo 0 > "+ self.fingDataFileName+ " &",shell=True )
            self.sleep(1)

        dataFileTimeOld = os.path.getmtime(self.fingDataFileName)  ## use for   if new filesize is longer  than old fs  fing is running


        if restartFing ==1:
            retCode = self.killFing("all")
        else:
            pids, parentPids = self.testFing()
            if len(pids) == 1 : return 1
            if len(pids) > 1 :
                retCode = self.killFing(u"onlyParents")
                return 1


#		try:
        # start fing, send to background, dont wait, create 2 output files:  one table format file and one logfile
        if self.theNetwork !="":
            cmd ="echo '" + self.yourPassword + "' | sudo -S '"+self.fingEXEpath+"' "+self.theNetwork+"/"+str(self.netwType)+" -o table,csv,'" +  self.fingDataFileName+ "'  log,csv,'" + self.fingLogFileName+ "'  >> '" + self.fingErrorFileName+ "'  > /dev/null 2>&1 &"
        else:
            cmd ="echo '" + self.yourPassword + "' | sudo -S '"+self.fingEXEpath+"' -o table,csv,'" +  self.fingDataFileName+ "'  log,csv,'" + self.fingLogFileName+ "'  >> '" + self.fingErrorFileName+ "'  > /dev/null 2>&1 &"
        self.myLog("Logic",u"FING cmd= %s" % cmd)
        ret = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        resp = ret.communicate()[0]
        pid = ret.pid
        del ret
        self.myLog("Logic",u"  waiting for FING to start and produce output " +  str(resp) + "pid:"+str(pid))
        self.sleep( 1 )
        self.killFing(u"onlyParents")


        found = False
        for ii in range(5):
            self.sleep( 25 )
            if dataFileTimeOld != os.path.getmtime(self.fingDataFileName):
                found = True
                break
                self.myLog("all",u"FING initialized ..  created new data   waiting ~ 1 minute for stable operation")
                return 1
#		except:
#			pass
        
        #test if it is actually running
        pids, parentPids = self.testFing()
        self.myLog("all",u"  FING pids 3= " +  str(pids))
        if len(pids) > 0:
            self.myLog("all",u"   (re)started FING ")
            self.myLog("all",u"FING initialized")
            return 1

        self.myLog("all",u"  (re)start FING not successful ")
        return 0 #  not successful
    
    
    
    
    
    
########################################
    def killFing(self,whomToKill):
        # all="all": kill fing and parents, if not just parents

        pids, parentPids = self.testFing()

        self.myLog("Logic",u"  killing FING Processes pids   " +whomToKill + " - " +str(pids))
        
        lenPid = len(pids)
        lenPidP = len(parentPids)

        pidsToKill =" "
        for kk in range (lenPidP):
            if parentPids[kk] !="1": pidsToKill += " "+parentPids[kk]
        
        if whomToKill == "all":
            for kk in range(lenPid):
                if pids[kk] !="1": pidsToKill += " "+pids[kk]


        if pidsToKill != " ":
            cmd = "echo '" + self.yourPassword + "' | sudo -S /bin/kill " + pidsToKill +" > /dev/null 2>&1 &"
            self.myLog("Logic",u"  FING kill cmd:" + cmd)
            ret= subprocess.Popen(cmd,shell=True) # kill fing
            del ret
            #self.myLog("Logic",u"  FING kill ret= " +  str(ret))
            self.sleep(1)

        # check if successfull killed,  ps ... should return nothing
        pids, parentPids = self.testFing()
        if len(pids) >0:
            self.myLog("Logic",u"  FING still running,  pids = " +  str(pids)+"--"+str(parentPids))
            return 0
        return 1
        
        
########################################
    def killPing(self,whomToKill, ipnumber="0.0.0.0"):
        self.myLog("Logic",u"killing ping jobs: "+str(whomToKill))
        
        if whomToKill =="all":
            for theMAC in self.pingJobs:
                pid = self.pingJobs[theMAC]
                if int(pid) < 10 : continue
                self.myLog("Logic",u"killing PID: "+theMAC+"-" +str(pid))
                ret= subprocess.Popen("/bin/kill " + str(pid),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                ret.stdout.close()
                ret.stderr.close()
                del ret
                self.pingJobs[theMAC] =-1

            ret =subprocess.Popen("ps -ef | grep 'do /sbin/ping' | grep -v grep | awk '{print$2}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            pids =ret.communicate()[0].split()
            ret.stdout.close()
            ret.stderr.close()
            del ret
                
            for pid  in pids:
                if int(pid) < 10: continue
                self.myLog("Logic",u"killing PID: "+pid)
                ret= subprocess.Popen("/bin/kill " + pid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                ret.stdout.close()
                ret.stderr.close()
                del ret


            for i in range (1,255):
                try:
                    os.remove(self.fingDataDir+"pings/"+str(i)+".ping")
                except:
                    pass

        else:
            if whomToKill in self.pingJobs:
                pid = self.pingJobs[whomToKill]
                if int(pid) > 10:
                    self.myLog("Logic",u"killing : "+whomToKill +"-" +str(pid))
                    ret= subprocess.Popen("/bin/kill " + str(pid),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    ret.stdout.close()
                    ret.stderr.close()
                    del ret
                    self.pingJobs[whomToKill] =-1
            if ipnumber !="0.0.0.0":
                try:
                    fname= ipnumber.split(".")[3]
                    os.remove(self.fingDataDir+"pings/"+fname+".ping")
                except:
                    pass

        return
        
        
########################################
    def testFing(self):
        self.myLog("Logic",u"testing if FING is running ")


        ret =subprocess.Popen("ps -ef | grep fing.bin | grep -v grep | grep -v fingscan| grep -v Indigo | awk '{print$2,$3}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        pids =ret.communicate()[0].strip("\n")
        ret.stdout.close()
        ret.stderr.close()
        del ret
        pids = pids.split("\n")
        fingPids=[]
        parentPids=[]
        self.myLog("Logic",u"  FING running pids2= " +  str(pids))
        
        for kk in range(len(pids)):
            p = pids[kk].split(" ")
            if len(p)==0: continue
            fingPids.append(p[0])
            if len(p)!=2: continue
            if p[1] =="1": continue
            if p[1] =="0": continue
            if p[1] ==" ": continue
            parentPids.append(p[1])
            # pids has the process ids #  of fing and parent shell as simple string have removed PID # 1 = the root
        return fingPids,parentPids
    
    
    
    
########################################
    def getfingLog(self):
        ## get size of finglog file to check if there is new data
        try:
            self.fingLogFileSizeNEW = int(os.path.getsize(self.fingLogFileName))
            if self.fingLogFileSizeold != self.fingLogFileSizeNEW:
#				self.myLog("Logic",u"  FING LOG data new " + str(self.fingLogFileSizeold) + " " + str(self.fingLogFileSizeNEW))
            
            ## get last line of finglog file

                lines = subprocess.Popen(["tail", "-1", self.fingLogFileName], stdout=subprocess.PIPE).communicate()[0].strip("\n")
                self.fingData =[ map(str,line.split(";")) for line in lines ]
                if len(self.fingData[0]) < 7: return 0
                if self.fingData[0][5] in self.ignoredMAC: return 0
                self.indigoNeedsUpdate = True
                
                self.fingNumberOfdevices = 1
                self.fingLogFileSizeold  = self.fingLogFileSizeNEW
                self.fingDate            = self.column(self.fingData[0])
                self.fingStatus          = self.column(self.fingData[1])
                self.fingIPNumbers       = self.column(self.fingData[2])
                self.fingDeviceInfo      = self.column(self.fingData[4])
                self.fingMACNumbers      = self.column(self.fingData[5])
                self.fingVendor          = self.column(self.fingData[6])
                self.finglogerrorCount   = 0
                for kk in range(1):
                    if self.fingMACNumbers[kk] in self.inbetweenPing:	# if this is listed as down in inbetween pings, remove as we have new info.
                        if self.fingStatus[kk] =="up":
                            del self.inbetweenPing[self.fingMACNumbers[kk]]

                    if self.fingStatus[kk] =="down":
                        if theMAC in self.allDeviceInfo and self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:  
                            if self.sendWakewOnLanAndPing(theMAC,nBC= 2, waitForPing=500, countPings=2, waitBeforePing = 0.5, waitAfterPing = 0.1, calledFrom="getfingLog") ==0:
                                self.fingStatus[kk] =="up"

                    self.fingDate[kk] =self.fingDate[kk].replace("/","-")
                return 1
            else:
                return 0
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            self.myLog("all",unicode(self.fingData))
            self.finglogerrorCount +=1
            if self.finglogerrorCount > 40 and self.totalLoopCounter > 100 :
                self.myLog("all",u"fing.log file does not exist or is empty \n    trying to stop and restart fing  " )
                self.initFing(1)  # restarting fing
                self.finglogerrorCount =0
            return -1
        return 1
    
    
########################################
    def getfingData(self):
        ## get time stamp of last mode of self.fingData file in secs since 197x.., if new data read
        nowdate = datetime.datetime.now()
        try:
            try:
                self.fingDataModTimeNEW = (os.path.getmtime(self.fingDataFileName))
            except:
                return 0    
            if self.fingDataModTimeOLD == self.fingDataModTimeNEW:
                return 0
            else:
                f = open ( self.fingDataFileName , "r")
                self.fingData = [ map(str,line.split(";")) for line in f ]
                f.close()
                self.fingNumberOfdevices    = len(self.fingData)
                self.fingDataModTimeOLD     = self.fingDataModTimeNEW
                self.fingIPNumbers          = self.column(self.fingData,0)
                self.fingStatus             = self.column(self.fingData,2)
                self.fingDate               = self.column(self.fingData,3)
                self.fingDeviceInfo         = self.column(self.fingData,4)
                self.fingMACNumbers         = self.column(self.fingData,5)
                self.fingVendor             = self.column(self.fingData,6)
                self.fingDataErrorCount     = 0
                self.doubleIPnumbers        = {}
                removeMAC=[]
                for kk in range(self.fingNumberOfdevices):
                    theMAC= self.fingMACNumbers[kk]
                    if theMAC in self.ignoredMAC: 
                        removeMAC.append(kk)
                        continue
                    if theMAC in self.doubleIPnumbers:
                        self.doubleIPnumbers[theMAC].append(self.fingIPNumbers[kk])
                    else:
                        self.doubleIPnumbers[theMAC]=[self.fingIPNumbers[kk]]
                    if self.fingMACNumbers[kk] in self.inbetweenPing:	# if this is listed as down in inbetween pings, remove as we have new info.
                        if self.fingStatus[kk] =="up":
                            del self.inbetweenPing[self.fingMACNumbers[kk]]
                    self.fingDate[kk] =self.fingDate[kk].replace("/","-")

                    if self.fingStatus[kk] == "down" and len(self.fingDate[kk]) > 5:
                        if theMAC in self.allDeviceInfo: 
                            if "useWakeOnLanSecs" in self.allDeviceInfo[theMAC]:
                                if self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:  
                                    if self.sendWakewOnLanAndPing(theMAC,nBC= 1, waitForPing=500, countPings=1, waitBeforePing = 0.2, waitAfterPing = 0.0, calledFrom="getfingData") ==0:
                                        self.fingStatus[kk] == "up"
                                        self.fingDate[kk] = nowdate.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                self.myLog("all","error: useWakeOnLanSecs not in devI for MAC#:"+ theMAC+" devI=\n"+unicode(self.allDeviceInfo[theMAC])) 
                                
                        deltaseconds = (  nowdate - datetime.datetime.strptime(self.fingDate[kk],"%Y-%m-%d %H:%M:%S")  ).total_seconds() 
                        if deltaseconds > 70 : 
                            removeMAC.append(kk)
                            #self.myLog("all",u"down > 70 secs for "+ self.fingMACNumbers[kk] +"  "+str(deltaseconds)) 

                for kk in removeMAC[::-1]:
                    del self.fingVendor[kk]
                    del self.fingIPNumbers [kk]
                    del self.fingStatus[kk]
                    del self.fingDate[kk]
                    del self.fingDeviceInfo[kk]
                    del self.fingMACNumbers[kk]
                self.fingNumberOfdevices = len(self.fingVendor) 
                 
                return 1
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            self.fingDataErrorCount +=1
            if self.fingDataErrorCount > 1 :
                self.myLog("all",u"fing.data file does not exist \n    trying "+str(5-self.fingDataErrorCount)+" more times")
                if self.fingDataErrorCount == 5:
                    self.myLog("all",u"   trying to stop and restart fing  " )
                    self.initFing(1)  # restarting fing
                    self.myLog("all",u"   restarted fing  " )
                    self.fingDataErrorCount =0
            else:
                return 0
        return 0
########################################
    def testfingError(self):
        fingOK1 = 0
        try:
            ret = subprocess.Popen('grep \'0/0 hosts up\' '+ self.fingErrorFileName,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            resp = ret.communicate()[0]
            ret.stdout.close()
            ret.stderr.close()
            del ret
            if len(resp) > 1  :  fingOK1 = 1
        except:
            pass
        fingOK2 = 0
        try:
            ret = subprocess.Popen('grep \'error\' ' + self.fingErrorFileName, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            resp = ret.communicate()[0]
            ret.stdout.close()
            ret.stderr.close()
            del ret
            if len(resp) > 1  :  fingOK2 = 1
        except:
            pass
        try:
            ret = subprocess.Popen("echo 0 > "+ self.fingErrorFileName,shell=True, stdout=subprocess.PIPE)
            ret.stdout.close()
            del ret
        except:
            pass
        if fingOK1 >0 or fingOK1 > 0:
            self.fingDataErrorCount2 +=1
            self.myLog(u"all",u" ERROR:  FING message -- network is not working  codes  0/0 hosts .. error codes:   " + str(fingOK1) + str(fingOK2) )
            if self.fingDataErrorCount2 > 1:
                self.myLog(u"all",u"  relaunching plugin")
                self.quitNOW ="FING problem 2"
        else:
            self.fingDataErrorCount2 =0
        

        return fingOK1 +  fingOK2
    
########################################
    def checkIndigoVersion(self):

        try:  ## test if any data and if version 2, if yes, return
            theTest = indigo.variables["ipDevice01"]
            theTest = theTest.value
            if len (theTest) < 5:  # variable exists, but empty or too short  should be 8 or 9
                self.quitNOW ="Indigo variable error 1"
                self.myLog(u"all",u"getting data from indigo: bad variable ipDevice01 \n    please check if it has bad data, in doubt delete and let the program recreate  \n    stopping fingscan " )
                return 1
            theValue = theTest.split(";")
            if theValue[0].strip().count(":") == 5:
                test = self.getIndigoIpVariablesIntoData()
                return 0  ## version 2 nothing to do
        except Exception, exc:
            return ## no data nothing to do


        ## this must be version 1  we have to convert the data

        for ii in range(1,indigoMaxDevices):
            ii00 = self.int2hexFor2Digit(ii)
            skip = 0
            try:
                theTest = indigo.variables["ipDevice"+ii00]
                skip = 1
                theTest = theTest.value
                if len (theTest) < 5:  # that is minimum, should be 8 or 9
                    skip = 1
                    self.quitNOW ="Indigo variable error 2"
                    self.myLog(u"all",u"getting data from indigo: bad variable ipDevice" + ii00 +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
                    break
                theValue = theTest.split(";")
                macNO = theValue[1].strip()
                if macNO.count(":") != 5:
                    self.quitNOW ="Indigo variable error 3"
                    self.myLog(u"all",u"getting data from indigo: bad variable ipDevice" + ii00  +"\n  MAC number does not seem to be real MAC number" + theValue[0].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
                    break
                ipNO =theValue[2].strip()
                if ipNO.count(".") != 3:
                    self.quitNOW ="Indigo variable error 4"
                    self.myLog(u"all",u"getting data from indigo: bad variable ipDevice" + ii00 +"\n  IP number does not seem to be real IP number" + theValue[1].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
                    break
                nick  = self.padNickName(theValue[0].strip())
                macNO = self.padMAC(macNO)
                ipNO  = self.padIP(ipNO)
                vend  = self.padVendor(theValue[3].strip())
                stat  = theValue[4].strip()
                dat	  = self.padDateTime(theValue[5].strip())
                nofch = self.padStatus(stat) + self.padNoOfCh(theValue[6].strip())
                devinf= self.padDeviceInfo(theValue[7].strip())
                updateString = macNO+";"+ipNO+";"+dat+";"+stat+";"+nofch+";"+nick+";"+vend+";"+devinf+"; "
                indigo.variable.updateValue("ipDevice"+ii00, updateString)
            except:
                pass
        test = self.getIndigoIpVariablesIntoData()
        return


########################################
    def getIndigoIpVariablesIntoData(self):

        try:
            self.indigoNumberOfdevices = 0
            # the index is the ipDevice#
            self.indigoDevicesValues =[]
            self.indigoDevicesNumbers =[]
            self.indigoEmpty =[]
            self.indigoIndexEmpty = 0
            self.indigoIpVariableData={}
            self.indigoNumberOfdevices =0

            for ii in range(1,indigoMaxDevices):
                ii00 = self.int2hexFor2Digit(ii)
                skip = 0
                try:
                    theTest = indigo.variables["ipDevice"+ii00]
                except Exception, exc:
                    self.indigoEmpty.append(ii00)
                    self.indigoIndexEmpty += 1
                    continue
                skip = 1
                theTest = theTest.value
                if len (theTest) < 5:  # that is minimum, should be 8 or 9
                    skip = 1
                    self.quitNOW ="Indigo variable error 6"
                    self.myLog(u"all",u"getting data from indigo: bad variable ipDevice" + ii00 +u"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan" )
                    break
                theValue = theTest.split(";")
                skip = "no"
                self.indigoNumberOfdevices +=1
                self.indigoDevicesValues.append(theTest)
                self.indigoDevicesNumbers.append(ii00)
                theMAC =theValue[0].strip()
                if theValue[0].strip().count(":") != 5:
                    skip = 1
                    self.quitNOW ="Indigo variable error 7"
                    self.myLog(u"all",u"getting data from indigo: bad variable ipDevice" + ii00 +u"\n  MAC number does not seem to be real MAC number" + theValue[0].strip() +u"\n   please check if it has bad data, in doubt delete and let the program recreate  \n  stopping fingscan " )
                    break



                if theValue[1].strip().count(".") != 3:
                    skip = 1
                    self.quitNOW ="Indigo variable error 8"
                    self.myLog(u"all",u"getting data from indigo: bad variable ipDevice" + ii00 +u"\n  IP number does not seem to be real IP number" + theValue[1].strip() +u"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
                    break

                self.indigoIpVariableData[theMAC]=copy.deepcopy(emptyindigoIpVariableData)
                devV =self.indigoIpVariableData[theMAC]
                devV["ipNumber"]			=theValue[1].strip()
                devV["timeOfLastChange"]	=theValue[2].strip()
                devV["status"]				=theValue[3].strip()
                try:
                    devV["noOfChanges"]		=int(theValue[4].strip())
                except:
                    devV["noOfChanges"]		=0
                devV["nickName"]			=theValue[5].strip()
                devV["hardwareVendor"]		=theValue[6].strip()
                devV["deviceInfo"]			=theValue[7].strip()
                try:
                    devV["WiFi"]			=theValue[8].strip()
                except:
                    devV["WiFi"]			=""
                try:
                    devV["usePing"]			=theValue[9].strip()
                except:
                    devV["usePing"]			="noPing-0"
                
                devV["ipDevice"]			=ii00
                devV["index"]				=self.indigoNumberOfdevices-1
                

            try:
                self.indigoStoredNoOfDevices = indigo.variables["ipDevsNoOfDevices"]
            except Exception, e:
                self.quitNOW ="Indigo variable error 9"  ## someting must be wrong, lets restart
                self.myLog(u"all",u"getting data from indigo: bad variable ipDevsNoOfDevices \n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan \n exec return code" +str(e) )
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))


        return
########################################
    def doInbetweenPing(self,force = False):
        try:
            sleepT = max(self.sleepTime/2., 1)
            pingWait = 900  #milli seconds
            maxOldTimeStamp = max(sleepT +pingWait/1000. +0.5,2)
            maxPingsBeforeReset= int(5.*60./(pingWait/1000.+sleepT)) # around 5 minutes equiv
    #		self.myLog("Ping","doInbetweenPing force= "+str(force))
    #		self.myLog("Ping","ping parameters: %5.2f   %5.2f   %5.2f   %5.2f "%(sleepT,pingWait,maxOldTimeStamp,maxPingsBeforeReset))
            oneDown=False
            ticks = time.time()
            nPing=0
            pingtimes=[]
            looptimes=[]
            lptime =time.time()
            msg=True
            maxPingTime=0
            for theMAC in self.allDeviceInfo:
                if theMAC in self.wifiMacList: continue
                if theMAC in self.excludeMacFromPing:
                    if force : self.excludeMacFromPing[theMAC]=0
                    if self.excludeMacFromPing[theMAC] >2:continue
                else:
                    self.excludeMacFromPing[theMAC] =0
                devI= self.allDeviceInfo[theMAC]
                if devI["status"] == "down": 
                    if devI["usePing"] in ["usePingifDown","usePingifUPdown"]:
                        retcode = 1
                        if devI["useWakeOnLanSecs"] > 0:
                            devI["useWakeOnLanLast"] = time.time()
                            self.sendWakewOnLan(theMAC, calledFrom="doInbetweenPing")
                            self.sleep(0.5)
                        retCode = self.checkPing(theMAC, waitForPing=pingWait, countPings=2, waitAfterPing = 0.1 )
                        self.myLog("Ping",u"pinged "+ theMAC+"; retcode="+str(retCode)+";  useWakeOnLan:"+str(devI["useWakeOnLanSecs"]) )
                        if retcode !=0: 
                            self.inbetweenPing[theMAC] = "down"
                        else:
                            devI["status"] = "up"
                            self.inbetweenPing[theMAC] = "up"
                        continue

                if devI["status"] == "up" and devI["usePing"] in ["usePingifUP","usePingifUPdown"]:
                    ipN = devI["ipNumber"].split("-")[0]# just in case ...it is "-changed"
                    nPing +=1
                    if self.inbetweenPingType == "parallel":
                        if theMAC in self.pingJobs:
                            pingPid = self.pingJobs[theMAC]
                            if pingPid >0:
                                try:
                                    if time.time() - os.path.getmtime(self.fingDataDir+"pings/"+ipN.split(".")[3]+".ping") < maxOldTimeStamp: # this will "except if it does not exist
                                        self.inbetweenPing[theMAC] = "up"
                                        self.excludeMacFromPing[theMAC] = -99999999 # it answered at least once, never never firewall again
                                        continue # all done still up
                                    resp = subprocess.Popen("ps -ef  | grep ' "+ str(pingPid)+" ' ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                                    ok = resp.communicate()[0].find("do /sbin/ping")>-1
                                    resp.stdout.close()
                                    resp.stderr.close()
                                    del resp
                                    if ok:
                                        self.myLog("Ping",u" ping file for "+ipN+" older than  : "+str(maxOldTimeStamp)+" secs")
                                        self.inbetweenPing[theMAC] = "down"
                                        self.updateIndigoIpDeviceFromDeviceData(theMAC, ["status"],justStatus="down")
                                        oneDown=True
                                        self.killPing (theMAC,ipnumber =ipN)
                                        pingPid=-1
                                        continue
                                except:  # file not created, either down or firewalled
                                    resp= subprocess.Popen("ps -ef  | grep ' "+ str(pingPid)+" ' ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                                    ok= resp.communicate()[0].find("do /sbin/ping")>-1
                                    resp.stdout.close()
                                    resp.stderr.close()
                                    del resp
                                    if ok: # still running?
                                            self.myLog("Ping",u" ping file  not created , device is down "+ipN)
                                            self.killPing (theMAC)# yes, kill it
                                            if self.excludeMacFromPing[theMAC] <0: continue
                                            if self.checkIfFirewalled(devI["deviceName"],theMAC, ipN) > 0: continue
                                        
                        ret =subprocess.Popen("for ((i=0;i<"+str(maxPingsBeforeReset)+";i++)); do /sbin/ping -c 2 -W "+str(pingWait)+" -o "+ipN+" &>/dev/null  && echo up>"+self.fingDataDir+"pings/"+ipN.split(".")[3]+".ping && sleep "+str(sleepT)+" ; done",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        #				self.myLog("Ping","ret : "+str(ret.communicate()))
                        pid = ret.pid
                        ret.stdout.close()
                        ret.stderr.close()
                        del ret
                        self.pingJobs[theMAC]=pid
                        self.myLog("Ping",u"launching ping for : "+ipN +" pid= "+ str(pid)+" theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
                        continue
                    
                        
                    if self.inbetweenPingType == "sequential":
                       #self.myLog("Ping","launching ping for : "+ipN +"  theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
                        looptimes.append(time.time()-lptime)
                        lptime=time.time()
                        npTime=time.time()
                        #   c 1: do 1 ping;  w: wait 800 msec; o: short output, q: quit if one response
                        retCode = self.checkPing(theMAC, waitForPing=pingWait, countPings=2, waitAfterPing = 0.1)
                        pingtimes.append(time.time()-npTime)
                        if retCode > 0:  # ret code = 2 : no response ==> "down"
                            #self.myLog("Ping"," ping response: "+str(resp).strip() )
                            if self.excludeMacFromPing[theMAC] >=0:
                                msg=False
                                if self.checkIfFirewalled(devI["deviceName"],theMAC, ipN) >0: continue
                            self.myLog("Ping",u" ping for  IP "+ipN +"  theMAC="  +theMAC +" timed out, status DOWN")
                            self.inbetweenPing[theMAC] = "down"
                            self.updateIndigoIpDeviceFromDeviceData(theMAC, ["status"], justStatus="down")
                            oneDown=True
                        else:
                            self.inbetweenPing[theMAC] = "up"
                            self.excludeMacFromPing[theMAC] = -99999999 # it answered at least once, never test never firewall again
                    #						self.myLog("Ping"," ping ok : "+ipN +"  theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
                    continue
                        
                        
    #		looptimes.append(time.time()-lptime)
    #		del looptimes[0]
            totalTime = time.time()-ticks
            if totalTime < 2  and msg: self.throttlePing = 0
            if totalTime > 4  and msg: self.throttlePing = 1
            if totalTime > 8  and msg: self.throttlePing = 2
            if totalTime > 12 and msg: self.throttlePing = 4
            if totalTime > 25 and msg: self.throttlePing = 8
    #		self.myLog("Ping"," nPings      : "+str(nPing) + "         seconds used: "+str(totalTime) + " throttlePing: " + str(self.throttlePing))
    #		self.myLog("Ping"," nPings      : "+str(nPing) + "         seconds used: "+str(totalTime) + " throttlePing: " + str(self.throttlePing)+" "+str(max(pingtimes)))
    #		self.myLog("Ping"," seconds loop: "+str( [("%1.2f" %looptimes[k]) for k in range(len(looptimes)) ] )  )
    #		self.myLog("Ping"," seconds ping: "+str( [("%1.2f" %pingtimes[k]) for k in range(len(pingtimes))])  )
            if self.inbetweenPingType=="sequential" and len(pingtimes) >0: self.myLog("Ping",u"time used for PINGing "+str(nPing) + " times: %2.2f"%totalTime+" seconds needed;   max ping time: %2.2f"%max(pingtimes) )



        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        
        return oneDown


########################################
    def checkIfFirewalled(self, devName,theMAC, ipN):
        try:
            if theMAC not in self.excludeMacFromPing: self.excludeMacFromPing[theMAC] =0 # start the counter
            self.myLog("Ping",u"testing if  "+devName+"/"+theMAC +"/"+ipN+"  is firewalled, does not answer to PINGs (%1d"%(self.excludeMacFromPing[theMAC]+1)+"/3 tests)" )
            resp= subprocess.Popen("echo '"+self.yourPassword+"' | sudo -S '"+self.fingEXEpath+"' -s "+ipN,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ret= str(resp.communicate())#[0]  # check if this device is answerings pings at all
            resp.stdout.close()
            resp.stderr.close()
            del resp
            if ret.find("incorrect password attempt")>-1:
                self.myLog(u"all","incorrect password  in config, please correct")
                return 3
            self.myLog("Ping",str(ret).replace("--","").replace("  ","") )
            if ret.find("host unreachable") >-1:
                self.excludeMacFromPing[theMAC] +=1
                return 1
            if ret.find("no service found, firewalled")>-1 or(
               ret.find("Non positive scan results")>-1 and ret.find("no service found")>-1) or(
               ret.find("Detected firewall")>-1):
                self.excludeMacFromPing[theMAC] +=1
                if self.excludeMacFromPing[theMAC] > 2:
                    self.myLog("Ping",u"excluding "+devName+"/"+theMAC +"/"+ipN+" from PING test as it is firewalled or does not answer on any port(%1d"%(self.excludeMacFromPing[theMAC])+"/3 tests)" )
                    return 3
                return 1

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        return 0



########################################
    def getIdandName(self,name):
        if name=="0": return "","0","0"
        if name=="1": return "","1","1"
        
        try:
            dev= indigo.devices[name]
            return dev, dev.name,  dev.id
        except:
            try:
                dev= indigo.devices[int(name)]
                return dev, dev.name,  dev.id
            except:
                pass
        return "","",-1



########################################
    def pluginCalled(self):
        try:
    
            for ii in range(len(self.callingPluginName)):
                self.myLog("iFind",u"trigger actionFrom  :  "+ unicode(self.callingPluginName[ii])+ " "+ unicode(self.callingPluginCommand[ii]))
                plug = indigo.server.getPlugin(self.callingPluginName[ii])
                if not plug.isEnabled():
                    self.myLog("iFind",u"trigger actionFrom Plugin  not enabled:  "+ unicode(plug)+ " "+ unicode(self.callingPluginCommand))
                    continue
                try:
                    idevId= self.callingPluginCommand[ii]
                except:
                    self.myLog("iFind",u"triggerFromPlugin  no msg:  "+ unicode(plug)+ " "+ unicode(self.idevId))
                    continue

                idevD,idevName,idevId = self.getIdandName(idevId)
                
                if idevName =="":
                    self.myLog("iFind",u"params for iFind  idevName empty" )
                    continue
                try:
                    distance					= float(idevD.states["distanceHome"])			# distance from home
                    distanceUnits				= idevD.states["distanceUnits"]					# convert to meters if needed, find ft or m and if display different from number
                    deviceTimeChecked			= time.mktime(time.strptime(idevD.states["deviceTimeChecked"],"%a %b %d %H:%M:%S %Y")) # format:  Thu Mar  3 07:32:49 2016  deviceTimeChecked of "iphone " in seconds
                    timeNextUpdate				= float(idevD.states["timeNextUpdate"])			#  time in secs of next check
                    iFindMethod					= idevD.states["calculateMethod"]				#  using avriable input or iFind nternal method
                except:
                    self.myLog("iFind",u"get params from iFind   not working:")
                    continue
                if distanceUnits.find("kilometres")>-1:	distance *=  kmMeters
                elif distanceUnits.find("miles")>-1:	distance *= milesMeters

                found = False
                #self.myLog("iFind","testing: iDeviceName  " +unicode(idevName) +" "+unicode(idevId) )
                for n in self.EVENTS:
                    evnt= self.EVENTS[n]
                    found =0
                    for nDev in evnt["iDeviceName"]:
                        if evnt["iDeviceName"][nDev]=="": continue
                        if unicode(evnt["iDeviceName"][nDev])=="-1": continue
                        found +=1
                        #self.myLog("iFind","trying iDeviceName  " +unicode(evnt["iDeviceName"][nDev]) +";  nDev"+unicode(nDev) +";  nEvent"+unicode(n) )
                    
                        if  unicode(evnt["iDeviceName"][nDev]) == unicode(idevId) or unicode(evnt["iDeviceName"][nDev]) == unicode(idevName):
                            found =10000
                            break
                    if  found > 0 and  found < 10000:
                        #self.myLog("iFind","iDeviceName not found:  " +unicode(idevName) +" "+unicode(idevId) )
                        continue
                    if  found  == 0: continue
                    #self.myLog("iFind","iDeviceName  found:  " +unicode(idevName) +" "+unicode(idevId) +";  nDev"+unicode(nDev) +";  nEvent"+unicode(n)+";  iDeviceName"+  unicode(evnt["iDeviceName"][nDev]))
                    
                    if deviceTimeChecked > float(evnt["iUpdateSecs"][nDev]) +1 :  # new info
                        
                        evnt["iSpeedLast"][nDev]		= evnt["iSpeed"][nDev]
                        evnt["iDistanceLast"][nDev]		= evnt["iDistance"][nDev]
                        evnt["iUpdateSecsLast"][nDev]	= evnt["iUpdateSecs"][nDev]
                        evnt["iDistance"][nDev]			= distance
                        evnt["iUpdateSecs"][nDev]		= deviceTimeChecked
                        evnt["itimeNextUpdate"][nDev]	= timeNextUpdate
                        dTime 							= evnt["iUpdateSecs"][nDev]  - evnt["iUpdateSecsLast"][nDev]
                        dDist							= evnt["iDistance"][nDev]    - evnt["iDistanceLast"][nDev]  
                        speed							= dDist  /   max(dTime,1.)
                        evnt["iSpeed"][nDev]			= speed
                        self.myLog("iFind",u"iFind old:  distance " +"%6.1f"%(evnt["iDistanceLast"][nDev])+ "; deviceTimeChecked " +"%6.1f"%(time.time()-evnt["iUpdateSecsLast"][nDev])+ ";  speed " +"%6.2f"%(evnt["iSpeedLast"][nDev])+";  ndev# "+ unicode(nDev))
                        self.myLog("iFind",u"      new:  distance " +"%6.1f"%(evnt["iDistance"][nDev])    + "; deviceTimeChecked " +"%6.1f"%(time.time()-evnt["iUpdateSecs"][nDev])    + ";  speed " +"%6.2f"%(evnt["iSpeed"][nDev])    +";  dDist " +"%6.2f"%(dDist)+";  dTime " +"%6.0f"%(dTime))
                    else:
                        self.myLog("iFind",u"iFind trigger delivered no new data")
                    evnt["iFindMethod"][nDev]			= iFindMethod
                    
                        
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        self.triggerFromPlugin		= False
        self.callingPluginName=[]
        self.callingPluginCommand=[]
        return

########################################
    def checkTriggers(self):
        try:
    #		self.myLog("Events","<<<--- entering checkTriggers")
            for nEvent in self.EVENTS:
                timeNowNumberSecs = time.time()
                timeNowm2 = int(timeNowNumberSecs-2.) ## drop the 10th of seconds
                timeNowHMS = datetime.datetime.now().strftime("%H:%M:%S")
                ticks = time.time()
                evnt=self.EVENTS[nEvent]
                InfoTimeStampSecs =0
    #			self.myLog("Events",
    #			" nevents "+nEvents+
    #			" EVENTS"+ str(self.EVENTS[nEvent])
    #			)
                if nEvent =="0": continue
                if evnt =="0": continue
                if evnt =="": continue
                if evnt["enableDisable"] != "1": continue
                minTime ={}
    #			evnt["oneHome"] ="0"
                self.metersAway = {}
                self.metersHome = {}
                Away={}
                Home={}
                HomeTime={}
                AwayTime={}
                AwayStat={}
                HomeStat={}
                AwayDist={}
                HomeDist={}
                minHomeTime =999999
                minAwayTime =999999
                maxHomeTime =0
                maxAwayTime =0
                
                for nDev in evnt["IPdeviceMACnumber"]:
                    if evnt["IPdeviceMACnumber"][nDev] == "0": continue
                    if evnt["IPdeviceMACnumber"][nDev] == "": continue
                    self.metersAway[nDev]	= -99999999999.
                    self.metersHome[nDev]	= -99999999999.
                    AwayTime[nDev]			=  999999999123
                    HomeTime[nDev]			=  999999999123
                    AwayStat[nDev]			=  False
                    HomeStat[nDev]			=  False
                    AwayDist[nDev]			=  True
                    HomeDist[nDev]			=  False


                for nDev in evnt["IPdeviceMACnumber"]:
                    AwayTime[nDev] = timeNowm2-float(evnt["secondsOfLastOFF"][nDev])
                    #self.myLog("all",u"nDev "+ str(nDev) +" AwayTime[nDev]"+ str(AwayTime[nDev]) )
                    minAwayTime = min(minAwayTime,AwayTime[nDev])  #################### need to check
                    maxAwayTime = max(maxAwayTime,AwayTime[nDev])
                    HomeTime[nDev] = timeNowm2-float(evnt["secondsOfLastON"][nDev])
                    minHomeTime = min(minHomeTime,HomeTime[nDev])
                    maxHomeTime = max(maxHomeTime,HomeTime[nDev])

                for nDev in evnt["IPdeviceMACnumber"]:
                    status ="0"
                    if evnt["IPdeviceMACnumber"][nDev] == "0": continue
                    if evnt["IPdeviceMACnumber"][nDev] == "": continue
                    iDev = int(nDev)
                    theMAC =evnt["IPdeviceMACnumber"][nDev]
                    ##self.myLog("all"," in trigger idev"+ nDev+"  "+ theMAC)
                    if iDev< piBeaconStart:
                        if len(theMAC) < 16:
                            self.myLog("Events",u"theMAC=0")
                            continue
                        if not theMAC in self.allDeviceInfo:
                            self.myLog("Ping",u"mac number "+theMAC+u"\n   not present in data, deleting EVENT/device source for trigger" )
                            evnt["IPdeviceMACnumber"][nDev] ="0"
                            break
                        devI= self.allDeviceInfo[theMAC]
                        status		= devI["status"]
                    elif iDev< piBeaconStart:
                        status ="0"

                    elif iDev< unifiStart:  ## check piBeacon devices
                        try:
                            status		= self.piBeaconDevices[theMAC]["currentStatus"]
                        except:
                            self.getpiBeaconAvailable()
                            self.updatepiBeacons()
                            if len(self.piBeaconDevices) ==0:
                                status ="0"
                            else:
                                try:
                                    status = self.piBeaconDevices[theMAC]["currentStatus"]
                                except:
                                    self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
                                    self.myLog("all",u"error in checkTriggers, indigoID# "+theMAC+u" not in piBeacondevices  :  " + unicode(self.piBeaconDevices)[0:100]+u" ..  is  piBeacon plugin active? " )
                                    status = "0"
                                    del self.piBeaconDevices[theMAC]
                    elif iDev >= unifiStart:  ## check unifi devices
                        try:
                            status		= self.unifiDevices[theMAC]["currentStatus"]
                            #self.myLog("all"," in trigger ndev, status"+ nDev+ "  "+ status)
                        except:
                            self.getUnifiAvailable()
                            self.updateUnifi()
                            if len(self.unifiDevices) ==0:
                                status ="0"
                            else:
                                try:
                                    status = self.unifiDevices[theMAC]["currentStatus"]
                                except:
                                    self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
                                    self.myLog("all",u"error in checkTriggers, indigoID# "+theMAC+u" not in unifidevices  :  " + unicode(self.unifiDevices)[0:100]+u" ..  is  unifi plugin active? " )
                                    del self.unifiDevices[theMAC]
                                    status = "0"
     #				self.myLog("Events","Status from devI: "+theMAC+"-"+status)



                    ## check iFind devcies
                    metersH=-8888888888
                    metersA=-1.
                    if len(evnt["iDeviceName"][nDev]) > 1 and (
                        evnt["iDeviceUseForAway"][nDev] =="1" or
                        evnt["iDeviceUseForHome"][nDev] =="1"): 
                        plug = indigo.server.getPlugin(self.iFindStuffPlugin)  #  get i distance info and may be force a manual update of the distance..
                        if plug.isEnabled():
                            idevD,idevName,idevId = self.getIdandName(evnt["iDeviceName"][nDev])
                            speed				= float(evnt["iSpeed"][nDev])
                            distance			= float(evnt["iDistance"][nDev])
                            pluginUpdateSecs	= float(evnt["iUpdateSecs"][nDev])
                            timeNextUpdate		= float(evnt["itimeNextUpdate"][nDev])
                            distance = max(0.1,distance)
                            metersH = distance  # get the current meters away from home.
                            metersA = distance
                            try:
                                varname=  idevD.name.replace(" ","").replace("'","").encode('ascii', 'ignore').upper()+'FREQ'
                                xx= indigo.variables[varname].value 
                            except:
                                try:
                                    indigo.variable.create(varname,"99")
                                except Exception, e:    
                                    self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
                                    self.myLog("all",u"could not read or create variable  "+varname+" for iFind communication, ignoring iFind communication")
                                    continue
                            
                            
                            nextTimeToCheck= evnt["nextTimeToCheck"][nDev] # set to some default
                            if status !="up":  # if not in IP range use iFind
                                evnt["iMaxSpeed"][nDev]=min(50.,max(abs(speed),evnt["iMaxSpeed"][nDev],1.001) ) 
                                if (distance-float(evnt["distanceHomeLimit"])) > 0:  # not home
                                    if speed < -0.5:	# m / sec moving towards home , not standing, but faster than 0.5m/sec
                                        nextTimeToCheck=  (distance-float(evnt["distanceHomeLimit"]))  / evnt["iMaxSpeed"][nDev]
                                    elif speed < 0.5:	#slow moving
                                        nextTimeToCheck=  (distance-float(evnt["distanceHomeLimit"])) / max(2., min(evnt["iMaxSpeed"][nDev]/2.,5))  # assuming max speed towards/away home is slow ~ 2m/sec
                                    elif speed  <2 : # moving away slowly
                                        nextTimeToCheck=  (distance-float(evnt["distanceHomeLimit"])) / max(1., min(evnt["iMaxSpeed"][nDev]/4.,10))       # assuming max speed away home is < 2m/sec = 7km/h = fast walking speed
                                    
                                    else : # moving away fast > 7 km/h
                                        nextTimeToCheck=  (distance-float(evnt["distanceHomeLimit"])) *2.  # assuming max speed away from home is > 7km/h
                                    self.myLog("iFind",u"ifind after speed calc  nextTimeToCheck: "+str(nextTimeToCheck)+" speed: "+ str(speed)+" iMaxSpeed: "+ str(evnt["iMaxSpeed"][nDev])  )
                                         
                                    nextTimeToCheck = min(813.,nextTimeToCheck) 
                                    nextTimeToCheck = max( 10.,nextTimeToCheck*0.9 ) # between 10 and 720 seconds
                                    evnt["nextTimeToCheck"][nDev]=  nextTimeToCheck

                                else:  # home
                                    pass
                                
                            else:  # in IP range take it slow
                                evnt["iMaxSpeed"][nDev]=1.002
                                if evnt["iFindMethod"][nDev] !="Calculated":
                                    plug.executeAction("refreshFrequencyOff", idevId)
                                evnt["iMaxSpeed"][nDev]=1.004 # reset to walking speed as we are home
                           
                                
                            if distance > 20000.:  # we are far away (> 20km) leave it to the default timing
                                if evnt["iFindMethod"][nDev] !="Calculated":
                                    self.myLog("iFind",u"ifind time : switching method to OFF")
                                    if evnt["iFindMethod"][nDev] !="Calculated":
                                        self.myLog("iFind",u"ifind time : switching method to OFF (2)")
                                        plug.executeAction("refreshFrequencyOff", idevId)
                                        evnt["iFindMethod"][nDev] ="Calculated"
                            
                                            
                            elif distance > float(evnt["distanceHomeLimit"]): ## not FAR AWAY, but not home 
                                    if indigo.variables[varname].value != str(int(nextTimeToCheck)):
                                        indigo.variable.updateValue(varname,str(int(nextTimeToCheck)))
                                    if   nextTimeToCheck < timeNextUpdate -time.time() :
                                        self.myLog("iFind",u"ifind time : switching method to Variable (On)")
                                        plug.executeAction("refreshFrequencyOn", idevId)
                                        evnt["iFindMethod"][nDev] ="Variable"
                                    else:
                                        self.myLog("iFind",u"ifind time : no need to refresh")

                            else:  # we are at home do things slowly ..
                                    if status !="up" :# if the other indicators believe it is away do an iFind update
                                        if time.time() - float(evnt["secondsOfLastOFF"][nDev]) > 600: #after 15 minutes switch back to calculated
                                            if evnt["iFindMethod"][nDev] =="Variable":
                                                evnt["iFindMethod"][nDev] ="Calculated"
                                                self.myLog("iFind",u"ifind time : switching method to OFF (1)")
                                                plug.executeAction("refreshFrequencyOff", idevId)
                                                self.myLog("iFind",u"ifind time : at home, do it slowly (1)")
                                        else:  # check ifind, then set nextTime to 60 secs, see how it works
                                            if evnt["iFindMethod"][nDev] !="Variable":  
                                                evnt["iFindMethod"][nDev] ="Variable"
                                                self.myLog("iFind",u"ifind time : at home, but do a refresh iFind as wifi just turned off  secondsOfLastOFF: " + str(evnt["secondsOfLastOFF"][nDev])+ ";  iUpdateSecs: "+ str(evnt["iUpdateSecs"][nDev]) )
                                                nextTimeToCheck =60 #set to 1 minutes
                                                evnt["nextTimeToCheck"][nDev]=  nextTimeToCheck
                                                if indigo.variables[varname].value != str(int(nextTimeToCheck)): indigo.variable.updateValue(varname,str(int(nextTimeToCheck)))
                                                plug.executeAction("refreshFrequencyOn", idevId)
                                    else:
                                            evnt["iMaxSpeed"][nDev]=1.003
                                            if evnt["iFindMethod"][nDev] !="Calculated":
                                                self.myLog("iFind",u"ifind time : switching method to OFF (2)")
                                                evnt["iFindMethod"][nDev] ="Calculated"
                                                plug.executeAction("refreshFrequencyOff", idevId)
                                            self.myLog("iFind",u"ifind time : at home, do it slowly (2)")


                            self.myLog("iFind",
                                     "ifind time UpdSec: "		+ unicode(int( time.time() - float(pluginUpdateSecs) ))
                                    +";  lastUpdLast: "			+ unicode(int( time.time() - float(evnt["iUpdateSecs"][nDev]) ))
                                    +";  speed: "				+ "%7.3f"%speed
                                    +";  iMaxSpeed: "			+ "%7.3f"%evnt["iMaxSpeed"][nDev]
                                    +";  nextTimeToCheck: "		+ unicode(int(nextTimeToCheck))
                                    +";  timeNextUpdate: "		+ unicode(int(timeNextUpdate -time.time()))
                                    +";  secondsOfLastOFF: "	+ unicode(int(time.time()- float(evnt["secondsOfLastOFF"][nDev])))
                                    +";  newDistance: "			+ unicode(int(distance))
                                    +";  status: "				+ unicode(status	)
                                    +";  iFindMethod: "			+ unicode(evnt["iFindMethod"][nDev]	)
                                    )

                        else:
                            self.myLog("iFind",u"iFind is not enabled, please enable plugin or disable use of iFind in FINGSCAN")
                            metersH=-7777777777
                            metersA=-2.
                    else:
                        metersH=-6666666666
                        metersA=-3.
                    if evnt["iDeviceUseForAway"][nDev] =="1":	 self.metersAway[nDev]	= metersA
                    else:										 self.metersAway[nDev]	= -4.
                    if evnt["iDeviceUseForHome"][nDev] =="1":	 self.metersHome[nDev]	= metersH
                    else:										 self.metersHome[nDev]	= -555555555.

                    if float(self.metersHome[nDev]) >0. and float(self.metersHome[nDev]) <= float(evnt["distanceHomeLimit"]):
                        HomeDist[nDev] = True
                    #self.myLog("iFind",u"ifind  metersHome: "+ unicode(self.metersHome[nDev]) + ";  distanceHomeLimit: "+str(evnt["distanceHomeLimit"])+ ";  HomeDist[nDev]: "+str(HomeDist[nDev]))
                    
                    if (float(self.metersAway[nDev]) >0  and float(self.metersAway[nDev])  <= float(evnt["distanceAwayLimit"])):
                        evnt["secondsOfLastOFF"][nDev] = timeNowm2
                        evnt["timeOfLastOFF"][nDev]= timeNowHMS
                        AwayDist[nDev] = False
                    #self.myLog("iFind",u"ifind  metersAway: "+ unicode(self.metersAway[nDev]) + ";  distanceAwayLimit: "+str(evnt["distanceAwayLimit"])+ ";  AwayDist[nDev]: "+str(AwayDist[nDev]))

                    if status =="up":
                        HomeStat[nDev] = True
                        #evnt["secondsOfLastOFF"][nDev] = timeNowm2
                        #evnt["timeOfLastOFF"][nDev]= timeNowHMS
                    else:
                        AwayStat[nDev] = True
                    AwayTime[nDev] = timeNowm2-float(evnt["secondsOfLastOFF"][nDev])
                    minAwayTime = min(minAwayTime,AwayTime[nDev])
                    maxAwayTime = max(maxAwayTime,AwayTime[nDev])
                    HomeTime[nDev] = timeNowm2-float(evnt["secondsOfLastON"][nDev])
                    minHomeTime = min(minHomeTime,HomeTime[nDev])
                    maxHomeTime = max(maxHomeTime,HomeTime[nDev])



                #self.myLog("Events","minHomeTime "+str(minHomeTime)+ " " + str(HomeTime))
                #self.myLog("Events","minAwayTime "+str(minAwayTime)+ " " + str(AwayTime))
                #self.myLog("Events","Dist: AWAY-"+str(AwayDist)+"-- HOME-"+str(HomeDist))
                #self.myLog("Events","Stat: AWAY-"+str(AwayStat)+"-- HOME-"+str(HomeStat))
    ## all info set, now set final outcome
                oneAway				= False
                allAway				= True
                allHome				= True
                oneHome				= False
                oneHomeTrigger		= False
                oneAwayTrigger		= False
                allHomeTrigger		= False
                allAwayTrigger		= False
                metersAwayForEvent	= 0
                metersHomeForEvent	= 0


                self.myLog("Events",u"Dev#  HomeStat".ljust(15)                         +"HomeTime".ljust(12)           +"HomeDist".ljust(12)          +"AwayStat".ljust(12)         +"AwayTime".ljust(12)           +"AwayDist".ljust(12)           +" oneHome"            +" allHome"             +" oneAway"           +" allAWay",type="EVENT# "+str(nEvent))
                for nDev in evnt["IPdeviceMACnumber"]:
                    if evnt["IPdeviceMACnumber"][nDev] == "0": continue
                    if evnt["IPdeviceMACnumber"][nDev] ==  "": continue
                    evnt["iDeviceAwayDistance"][nDev]= "%5.3f"%self.metersAway[nDev]
                    evnt["iDeviceHomeDistance"][nDev]= "%5.3f"%self.metersHome[nDev]
                    if AwayStat[nDev] and evnt["currentStatusAway"][nDev] == "0" and (minAwayTime < 30 and False):  ### need to fix 
                        self.myLog("all",u"nDev"+ str(nDev)+" AwayStat[nDev]"+ str(AwayStat[nDev])+" evnt[currentStatusAway][nDev]" + str(evnt["currentStatusAway"][nDev])+" minAwayTime" + str(minAwayTime))
                        self.redoAWAY= 10  # increase frequency of up/down test to 1 per second for 10 seconds
    #### away status
                    if evnt["currentStatusAway"][nDev] == "0":
                        if (AwayStat[nDev] and AwayDist[nDev]) :
                            if float(evnt["minimumTimeAway"]) >0.:
                                evnt["currentStatusAway"][nDev]	= "startedTimer"
                                allAway=False  # added , was missing 
                            else:
                                evnt["currentStatusAway"][nDev]	= "AWAY"
                                oneAway = True
                                self.redoAWAY= 0
                            evnt["secondsOfLastOFF"][nDev]= timeNowm2
                            evnt["timeOfLastOFF"][nDev]= timeNowHMS
                        else:
                            allAway=False
                    elif evnt["currentStatusAway"][nDev] == "startedTimer":
                           if (AwayStat[nDev] and AwayDist[nDev]):
                                if AwayTime[nDev] >= float(evnt["minimumTimeAway"]):
                                    evnt["currentStatusAway"][nDev] ="AWAY"
                                else:    
                                    allAway=False
                           else:    
                                evnt["currentStatusAway"][nDev] ="0"
                                allAway=False
                     
                    if evnt["currentStatusAway"][nDev] == "AWAY":
                        if (AwayStat[nDev] and AwayDist[nDev]):
                            oneAway = True
                            if AwayTime[nDev] >= float(evnt["minimumTimeAway"]):
                                oneAwayTrigger =True
                            if minAwayTime >= float(evnt["minimumTimeAway"]):
                                allAwayTrigger =True
                    
                        else:
                            allAway = False
                            evnt["currentStatusAway"][nDev]	= "0"
                            evnt["secondsOfLastOFF"][nDev]= timeNowm2
    #### home status
                    if evnt["currentStatusHome"][nDev] == "0": # was not home
                        if (HomeStat[nDev] or HomeDist[nDev]):
                            evnt["currentStatusHome"][nDev]	= "HOME"
                            evnt["secondsOfLastON"][nDev]= timeNowm2
                            evnt["timeOfLastON"][nDev]= timeNowHMS
                            oneHome = True
                            if minHomeTime >= float(evnt["minimumTimeHome"]):
                                oneHomeTrigger =True
                            if maxHomeTime >= float(evnt["minimumTimeHome"]):
                                allHomeTrigger =True
                        else:
                            allHome=False
                    else:  # it is or was  home
                        if (HomeStat[nDev] or HomeDist[nDev]): # still home: restart timer
                            evnt["timeOfLastON"][nDev]= timeNowHMS
                            evnt["secondsOfLastON"][nDev]= timeNowm2
                            evnt["currentStatusHome"][nDev]	= "HOME"
                            oneHome =True
                            # this is wrong:
                            #if minHomeTime >= float(evnt["minimumTimeHome"]):
                            #    oneHomeTrigger =True
                            #if maxHomeTime >= float(evnt["minimumTimeHome"]):
                            #    allHomeTrigger =True
                        else:
                            evnt["currentStatusHome"][nDev]	= "0"
                            allHome=False
                    self.myLog("Events",str(nDev).rjust(3)+"   " +str(HomeStat[nDev]).ljust(12)+ str(HomeTime[nDev]).ljust(12) + str(HomeDist[nDev]).ljust(12)+ str(AwayStat[nDev]).ljust(12)+ str(AwayTime[nDev]).ljust(12)+ str(AwayDist[nDev]).ljust(12) + str(oneHome).ljust(8)+ str(allHome).ljust(8)+ str(oneAway).ljust(8)+ str(allAway).ljust(8) ,type="EVENT# "+str(nEvent) )


                self.myLog("Events",u"oneHome:" + evnt["oneHome"]+"; allHome:" + evnt["allHome"]+"; oneAway:" + evnt["oneAway"]+"; allAway:" + evnt["allAway"],type="EVENT# "+str(nEvent) )
                if time.time() - self.timeOfStart > 100:
                    if oneHome:
                        if evnt["oneHome"]!= "1" :
                            if oneHomeTrigger:
                                evnt["oneHome"]= "1"
                                self.updatePrefs = True
                                indigo.variable.updateValue("oneHome_"+nEvent,"1")
                                if self.checkTriggerInitialized:
                                    try:indigo.variable.updateValue("FingEventDevChangedIndigoId",str(self.allDeviceInfo[evnt["IPdeviceMACnumber"][oneHomeTrigger]]["deviceId"]))
                                    except: pass
                                    self.triggerEvent("EVENT_"+nEvent+"_oneHome")
                    else:
                        if evnt["oneHome"]!= "0":
                            evnt["oneHome"] ="0"
                            indigo.variable.updateValue("oneHome_"+nEvent,"0")
                            self.updatePrefs = True
                    if allHome:
                        if evnt["allHome"]!= "1":
                            if allHomeTrigger:
                                evnt["allHome"]= "1"
                                self.updatePrefs = True
                                indigo.variable.updateValue("allHome_"+nEvent,"1")
                                if self.checkTriggerInitialized:
                                    try: indigo.variable.updateValue("FingEventDevChangedIndigoId",str(self.allDeviceInfo[evnt["IPdeviceMACnumber"][allHomeTrigger]]["deviceId"]))
                                    except: pass
                                    self.triggerEvent("EVENT_"+nEvent+"_allHome")
                    else:
                        if evnt["allHome"]!= "0":
                            evnt["allHome"] ="0"
                            indigo.variable.updateValue("allHome_"+nEvent,"0")
                            self.updatePrefs = True



                    if allAway:
                        if evnt["allAway"] !="1":
                            if allAwayTrigger:
                                self.updatePrefs = True
                                evnt["allAway"] ="1"
                                indigo.variable.updateValue("allAway_"+nEvent,"1")
                                if self.checkTriggerInitialized:
                                    try: indigo.variable.updateValue("FingEventDevChangedIndigoId",str(self.allDeviceInfo[evnt["IPdeviceMACnumber"][allAwayTrigger]]["deviceId"]))
                                    except: pass
                                    self.triggerEvent("EVENT_"+nEvent+"_allAway")
                    else:
                        if evnt["allAway"] !="0":
                            evnt["allAway"] ="0"
                            indigo.variable.updateValue("allAway_"+nEvent,"0")
                            self.updatePrefs = True

                    if oneAway:
                        if evnt["oneAway"] !="1":
                            if oneAwayTrigger:
                                self.updatePrefs = True
                                evnt["oneAway"] ="1"
                                indigo.variable.updateValue("oneAway_"+nEvent,"1")
                                if self.checkTriggerInitialized:
                                    try: indigo.variable.updateValue("FingEventDevChangedIndigoId",str(self.allDeviceInfo[evnt["IPdeviceMACnumber"][allAwayTrigger]]["deviceId"]))
                                    except: pass
                                    self.triggerEvent("EVENT_"+nEvent+"_oneAway")
                    else:
                        if evnt["oneAway"] !="0":
                            evnt["oneAway"] ="0"
                            indigo.variable.updateValue("oneAway_"+nEvent,"0")
                            self.updatePrefs = True

                if self.debugLevel.find("Events") >-1: self.printEvents(printEvents=nEvent)
    #		self.myLog("Events"," leaving checkTriggers   ---->")

            self.checkTriggerInitialized =True
            
            

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
    

########################################
    def sortIndigoIndex(self):
        try:
            sortFields =[]
            
            ll=0
            for theMAC in self.indigoIpVariableData:
                kk =self.indigoIpVariableData[theMAC]["index"]
                ipCompr =int(self.indigoIpVariableData[theMAC]["ipNumber"].strip().replace(".",""))  # "  192.168.1.5  " --> "  19216815  "
                sortFields.append([ipCompr,kk])  # [[192168110,1],[19216816,2], ....[....]]
                ll+=1
    #			self.myLog("Logic","sort: "+ str(ll) + " " + str(kk) +" " + str(ipCompr))
            sortedIP = sorted(sortFields, key=lambda tup: tup[0])  # sort ip number: tup([0]) as number,

    #		self.myLog("Logic","sort2.0 len: "+ str(len(self.indigoDevicesValues)) )
            for kk in range(ll):
                jj = sortedIP[kk][1]						# old index
    #			self.myLog("Logic","sort2: "+ str(kk) + " " + str(jj) )
                
                newLine = self.indigoDevicesValues[jj]		# from old ipdevice value
                kk00 = self.int2hexFor2Digit(kk+1)							# make it 01 02 ..09 10 11 ..99
                try:
                    indigo.variable.updateValue("ipDevice"+kk00, newLine)  # update indigo with new sorted list
                except:
                    indigo.variable.create("ipDevice"+kk00, newLine,self.indigoVariablesFolderID)  # create new var if it does not exists with new sorted list

            # delete any entry > # of devices
            for kk in range(ll,indigoMaxDevices):
                kk00=self.int2hexFor2Digit(kk+1)						# make it 01 02 ..09 10 11 ..99
                try:
                    indigo.variable.delete("ipDevice"+kk00)
                except:
                    pass
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        return 1





########################################
    def compareToFingIfExpired(self, calledFrom):
        try:
            dateTimeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            for theMAC in self.allDeviceInfo:
                if theMAC in self.ignoredMAC: continue
                    
                update = False
                devI = self.allDeviceInfo[theMAC]
                try:  ## try to find this indigo mac number in  fingdata
                    xxx = self.fingMACNumbers.index(theMAC)
                except:  ## this one is in indigo, but not in the fingdata file, set to exipred if not already done or ignore if better data from wifirouter
                    if self.routerType !="0" and theMAC in self.wifiMacList and self.routerErrorCount==0:
                        if self.allDeviceInfo[theMAC]["setWiFi"] != "Ethernet":
                            if theMAC in self.WiFiChanged:
                                if   self.wifiMacList[theMAC][0] == "Yes":
                                    if self.allDeviceInfo[theMAC]["status"] != "up":
                                            self.allDeviceInfo[theMAC]["status"] = "up"
                                            update = True
                                elif self.allDeviceInfo[theMAC]["status"] == "up":
                                    self.allDeviceInfo[theMAC]["status"] = "down"
                                    update = True
                                elif self.allDeviceInfo[theMAC]["status"] =="down":
                                    self.allDeviceInfo[theMAC]["status"] = "expired"
                                    update = True
                
                    else:
                        if self.allDeviceInfo[theMAC]["expirationTime"] == 0: 
                                update = True
                                self.allDeviceInfo[theMAC]["status"] = "expired"
                        else:
                            if (time.time() - self.allDeviceInfo[theMAC]["lastFingUp"] >  2*self.allDeviceInfo[theMAC]["expirationTime"] ): 
                                if self.allDeviceInfo[theMAC]["status"] != "expired":
                                    update = True
                                    self.allDeviceInfo[theMAC]["status"] = "expired"
                            elif (time.time() - self.allDeviceInfo[theMAC]["lastFingUp"] >  self.allDeviceInfo[theMAC]["expirationTime"] ): 
                                if self.allDeviceInfo[theMAC]["status"] != "down":
                                    update = True
                                    self.allDeviceInfo[theMAC]["status"] = "down"
                    if update:
                        self.allDeviceInfo[theMAC]["timeOfLastChange"] = dateTimeNow
                        self.updateIndigoIpDeviceFromDeviceData(theMAC,["status","timeOfLastChange"])
                        self.updateIndigoIpVariableFromDeviceData(theMAC)
                self.myLog("WiFi",u" fing end..theMAC/wifi/status/: "+theMAC+" -"  + self.allDeviceInfo[theMAC]["status"] )
                
                
            if self.routerType != "0":
                for theMAC in self.wifiMacList:
                    if theMAC not in self.allDeviceInfo:
                        if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
                        self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
                        devI= self.allDeviceInfo[theMAC]
                        devI["ipNumber"]			= "256.256.256.256"
                        devI["timeOfLastChange"]	= str(dateTimeNow)
                        devI["status"]				= "up"
                        devI["nickName"]			= "unidentifiedWiFiDevice"
                        devI["noOfChanges"]			= 1
                        devI["deviceInfo"]			= "unidentified"
                        if devI["setWiFi"] !="Ethernet":
                            devI["WiFi"]			=self.wifiMacList[theMAC][9]
                        devI["usePing"]				= "usePingUP"
                        devI["useWakeOnLanSecs "]	= 0
                        devI["suppressChangeMSG"]	= "show"
                        devI["hardwareVendor"]      = self.getVendortName(theMAC)

                        newIPDevNumber = str(self.indigoEmpty[0])
                        self.myLog("Logic",u"new device added ipDevice" +  newIPDevNumber)
                        
                        self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"])
                        self.updateIndigoIpVariableFromDeviceData(theMAC)


                        ## count down empty space
                        self.indigoIndexEmpty -= 1  # one less empty slot
                        self.indigoEmpty.pop(0) ##  remove first empty from list

                        ## start any triggers if setup
                        try:
                            indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice"+str(newIPDevNumber)+";"+devI["deviceName"])
                        except:
                            indigo.variable.create("ipDevsNewDeviceNo", "ipDevice"+str(newIPDevNumber)+";"+devI["deviceName"],self.indigoVariablesFolderID)
                        self.triggerEvent(u"NewDeviceOnNetwork")

                        try:
                            if self.indigoStoredNoOfDevices != str(self.indigoNumberOfdevices):
                                indigo.variable.updateValue("ipDevsNoOfDevices", str(self.indigoNumberOfdevices))
                        except:
                            indigo.variable.create("ipDevsNoOfDevices", str(indigoNumberOfdevices))

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        return 0
    
    
    
########################################
    def compareToIndigoDeviceData(self,lastUpdateSource="0"):
        try:
            indigoIndexFound =[]
            anyUpdate = 0
            dateTimeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            for kk in range(0,self.fingNumberOfdevices):
                theMAC = self.fingMACNumbers[kk]
                if theMAC in self.ignoredMAC: continue
                dontUseThisOne = False
                if self.fingStatus[kk] != "up":
                    for jj in range(0,self.fingNumberOfdevices):   # sometimes ip numbers are listed twice in fing.data, take the one with "UP"
                        if jj == kk: continue
                        if self.fingMACNumbers[kk] 	!= self.fingMACNumbers[jj]	: continue  # not the same
                        if self.fingStatus[kk] 		== self.fingStatus[jj]		: continue  # same status, should not be, just protecting
                        if self.fingStatus[jj] 		== "up":								# jj is up , kk is not, use jj wait until we are there
                            dontUseThisOne = True
                            break
                        if  theMAC in self.allDeviceInfo:									# and last test if the otehr has the current ip number use jj, not kk
                            if self.allDeviceInfo[theMAC]["ipNumber"] == self.fingIPNumbers[jj]:
                                dontUseThisOne = True
                            break
                if dontUseThisOne: continue
                

                doIndigoUpdate = 0
                if theMAC in self.allDeviceInfo:
                    theAction="exist"
    #				self.myLog("Logic",u" theMAC action: "+theMAC+"/"+theAction )
    #				self.myLog("Logic",str(self.allDeviceInfo[theMAC]))
                else:
                    theAction="new"
    #				self.myLog("Logic",u" theMAC action: "+theMAC+"/"+theAction )
                
                updateStates=[]

                
                if theAction == "exist" :
                    if "setWiFi" not in self.allDeviceInfo[theMAC]:
                        self.allDeviceInfo[theMAC]["setWiFi"] = copy.deepcopy(emptyAllDeviceInfo["setWiFi"])
                    devI= self.allDeviceInfo[theMAC]
                    
                    useFing=True
                    if self.allDeviceInfo[theMAC]["setWiFi"] == "Wifi":
                        useFing=False
                        theStatus = "down"
                    else:
                        theStatus = self.fingStatus[kk]
                        if self.inbetweenPingType!= "0" and theMAC in self.inbetweenPing:
                            if  self.inbetweenPing[theMAC] == "down": theStatus = "down"

                    #if theMAC =="1C:36:BB:97:C0:85": 
                    #    indigo.server.log("exists "+ theStatus+"  "+ str(devI["lastFingUp"]))

                    if theStatus != "up":
                        if theMAC in self.allDeviceInfo and "useWakeOnLanSecs" in self.allDeviceInfo[theMAC] and  self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:
                            self.sendWakewOnLanAndPing(theMAC, nBC= 1,waitForPing=10, countPings=1, waitBeforePing = 0., waitAfterPing = 0.0, calledFrom="compareToIndigoDeviceData")

                    if theStatus == "up":
                        devI["lastFingUp"] = time.time()
                    else:
                        if devI["expirationTime"] != 0 and (time.time() - devI["lastFingUp"] < devI["expirationTime"]): 
                            theStatus = "up"

                    if self.routerType !="0" and self.routerErrorCount ==0:					# check wifi router info if available
                        if devI["setWiFi"] != "Ethernet":									# ignore if set to ethernet
                            if theMAC in self.wifiMacList:
                                associated =self.wifiMacList[theMAC][0]
                                self.myLog("WiFi",u"before theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI["ipNumber"]+" LastUpdateby:"+lastUpdateSource)
                                if associated =="Yes":
                                    if theStatus != "up":
                                        self.fingDate[kk] = str(dateTimeNow)
                                        doIndigoUpdate = 9
                                    if theStatus !="changed": theStatus="up"
                                else:
                                    if theStatus == "up" and lastUpdateSource == "WiFi":
                                        self.fingDate[kk] = str(dateTimeNow)
                                        theStatus = "down"
                                        doIndigoUpdate = 9
        #								self.myLog("WiFi",u"wifi theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI["ipNumber"]+" LastUpdateby:"+lastUpdateSource)
    
                                    #### important !!!!
                                    #fix : add time component > 3 minutes	if theStatus == "up" and lastUpdateSource.find("fing") > -1:
                                    #	devI["WiFi"]=""
                                    #	doIndigoUpdate = 9
                                    #	del self.wifiMacList[theMAC]
                                if theMAC in self.wifiMacList:
                                    if devI["WiFi"] !=self.wifiMacList[theMAC][9]:
                                        devI["WiFi"] =self.wifiMacList[theMAC][9]
                                        doIndigoUpdate = 9
                                if doIndigoUpdate ==9:
                                    updateStates.append("WiFi")
                                self.myLog("WiFi",u"after WiFiF checks theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI["ipNumber"]+" LastUpdateby:"+lastUpdateSource)


                    ## found device, check if anything has changed: ip & status, if changed increment # of changes
                    if devI["status"]!= theStatus:
                        updateStates.append("status")
                        updateStates.append("noOfChanges")
                        doIndigoUpdate = 2
                        devI["noOfChanges"] +=1
                        if theStatus == "up":
                            if devI["ipNumber"].split("-")[0]!= self.fingIPNumbers[kk]:  # split("-") to remove "-changed" string
                                devI["ipNumber"] = self.fingIPNumbers[kk]
                                updateStates.append("ipNumber")
                                doIndigoUpdate = 3
                        if theStatus == "down":
                            if devI["ipNumber"].find("changed")>-1 or devI["ipNumber"].find("double")>-1:
                                devI["ipNumber"] = self.fingIPNumbers[kk]
                                updateStates.append("ipNumber")
                            self.fingDate[kk] = str(dateTimeNow)
                            doIndigoUpdate = 5
                        if theStatus == "changed":
                            doIndigoUpdate = 6
                            updateStates.append("ipNumber")
                            theStatus = "up"
                    #no status change, check if IP number changed
                    else :
                        if theStatus == "up":
                            if devI["ipNumber"].find("changed")>-1 or devI["ipNumber"].find("double")>-1:
                                devI["ipNumber"] = self.fingIPNumbers[kk]
                                updateStates.append("ipNumber")
                                doIndigoUpdate = 8
                            if devI["ipNumber"] != self.fingIPNumbers[kk]:
                                doIndigoUpdate = 7
                                updateStates.append("ipNumber")
                                updateStates.append("noOfChanges")
                                devI["noOfChanges"] +=1
                    devI["status"]	= theStatus
                    devI["ipNumber"]= self.fingIPNumbers[kk]

                    if doIndigoUpdate > 0:
                        if doIndigoUpdate== 6:
                            if theMAC in self.doubleIPnumbers:
                                if len(self.doubleIPnumbers[theMAC]) 	==1: devI["ipNumber"]=self.fingIPNumbers[kk]+ "-changed"
                                elif len(self.doubleIPnumbers[theMAC]) 	>1:	 devI["ipNumber"]=self.fingIPNumbers[kk]+ "-double"
                        dd = self.fingDate[kk]
                        if len(dd) < 5 : dd = str(dateTimeNow)
                        devI["timeOfLastChange"]	=dd
                        self.updateDeviceWiFiSignal(theMAC)
                        updateStates.append("deviceInfo")
                        self.updateIndigoIpDeviceFromDeviceData(theMAC,updateStates)
                        self.updateIndigoIpVariableFromDeviceData(theMAC)

                        if doIndigoUpdate == 3 or doIndigoUpdate == 6 or doIndigoUpdate == 7 :
                            try:
                                indigo.variable.updateValue("ipDevsNewIPNumber", "ipDevice"+self.indigoIpVariableData[theMAC]["ipDevice"]+";"+devI["deviceName"])
                            except:
                                indigo.variable.create("ipDevsNewIPNumber","ipDevice"+self.indigoIpVariableData[theMAC]["ipDevice"]+";"+devI["deviceName"],self.indigoVariablesFolderID)
                            if theMAC in self.doubleIPnumbers:
                                if (len(self.doubleIPnumbers[theMAC])==1 or  (len(self.doubleIPnumbers[theMAC])>1) and  devI["suppressChangeMSG"]=="show"):
                                    self.triggerEvent(u"IPNumberChanged")


                if theAction == "new" :################################# new device, add device to indigo
                    if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
                    self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
                    devI= self.allDeviceInfo[theMAC]
                    devI["ipNumber"]			=self.fingIPNumbers[kk]
                    dd = self.fingDate[kk]
                    if len(dd) < 5 : dd = str(dateTimeNow)
                    ## find a new unique name for device "new-seq#-mac#"
                    sqNumber=0
                    for dNew in indigo.devices.iter("com.karlwachs.fingscan"):
                        if dNew.name.find("new") ==-1: continue
                        xxx= dNew.name.split("-")
                        if len(xxx)< 3: continue
                        try:
                            sqn=int(xxx[1])
                            sqNumber=sqn+1
                        except:
                            continue    
                    
                    devI["timeOfLastChange"]	=dd
                    devI["status"]				="up"
                    devI["nickName"]			="new-"+str(sqNumber)+"-"+theMAC
                    devI["noOfChanges"]			=1
                    if len(self.fingVendor[kk]) < 4:
                        devI["hardwareVendor"]      = self.getVendortName(theMAC)
                    else:
                        devI["hardwareVendor"]		=self.fingVendor[kk]

                    devI["deviceInfo"]			=self.fingDeviceInfo[kk]
                    devI["WiFi"]				=""
                    devI["usePing"]				="usePingUP"
                    devI["useWakeOnLanSecs"]	= 0
                    devI["suppressChangeMSG"]	="show"
                    #if theMAC =="1C:36:BB:97:C0:85": 
                    #    indigo.server.log("new "+ theStatus+"  "+ str(devI["lastFingUp"]))
                    devI["lastFingUp"]	        = time.time()

                    newIPDevNumber = str(self.indigoEmpty[0])
                    self.myLog("Logic",u"new device added ipDevice" +  newIPDevNumber)
                    
                    self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"])
                    self.updateIndigoIpVariableFromDeviceData(theMAC)


                    ## count down empty space
                    self.indigoIndexEmpty -= 1  # one less empty slot
                    self.indigoEmpty.pop(0) ##  remove first empty from list

                    anyUpdate +=1
                    ## start any triggers if setup
                    try:
                        indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice"+str(newIPDevNumber)+";"+devI["deviceName"])
                    except:
                        indigo.variable.create("ipDevsNewDeviceNo", "ipDevice"+str(newIPDevNumber)+";"+devI["deviceName"],self.indigoVariablesFolderID)
                    self.triggerEvent(u"NewDeviceOnNetwork")



            if self.routerType !="0" and lastUpdateSource == "WiFi":
                for theMAC in self.wifiMacList:
                    if theMAC in self.allDeviceInfo: continue
                    if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
                    self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
                    devI= self.allDeviceInfo[theMAC]
                    devI["ipNumber"]			= "254.254.254.254"
                    devI["timeOfLastChange"]	= str(dateTimeNow)
                    devI["status"]				= "up"
                    devI["nickName"]			= "unidentified_WiFi_Device"
                    devI["noOfChanges"]			= 1
                    devI["hardwareVendor"]      = self.getVendortName(theMAC)
                    devI["deviceInfo"]			="unidentified"
                    devI["WiFi"]				= self.wifiMacList[theMAC][9]
                    devI["usePing"]				= ""
                    devI["useWakeOnLanSecs "]	= 0
                    devI["suppressChangeMSG"]	= "show"
                    try:
                        newIPDevNumber = str(self.indigoEmpty[0])
                    except:
                        newIPDevNumber = "1"
                        self.myLog("all",u"new device added indigoEmpty not initialized" +  str(self.indigoEmpty))
                    self.myLog("Logic",u"new device added ipDevice#" +  newIPDevNumber)
                    
                    self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"])
                    self.updateIndigoIpVariableFromDeviceData(theMAC)
                    ## count down empty space
                    self.indigoIndexEmpty -= 1  # one less empty slot
                    self.indigoEmpty.pop(0) ##  remove first empty from list

                    try:
                        indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice"+str(newIPDevNumber)+";"+devI["deviceName"])
                    except:
                        indigo.variable.create("ipDevsNewDeviceNo", "ipDevice"+str(newIPDevNumber)+";"+devI["deviceName"],self.indigoVariablesFolderID)
                    self.triggerEvent(u"NewDeviceOnNetwork")

            try:
                if self.indigoStoredNoOfDevices != str(self.indigoNumberOfdevices):
                    indigo.variable.updateValue("ipDevsNoOfDevices", str(self.indigoNumberOfdevices))
            except:
                indigo.variable.create("ipDevsNoOfDevices", str(indigoNumberOfdevices))

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))


        return 0



########################################
    def getVendortName(self,MAC):
        if self.enableMACtoVENDORlookup !="0" and not self.waitForMAC2vendor:
            self.waitForMAC2vendor = self.M2V.makeFinalTable()
        return  self.M2V.getVendorOfMAC(MAC)

    ########### main loop -- start #########
########################################
    def runConcurrentThread(self):

        self.initialized=1



        self.indigoCommand = "none"
        self.pluginState   = "run"
        ## loop:  get fing data and enter fill indigo variables
        fingNotActiveCounter = 0
        self.totalLoopCounter = 0
        self.routerErrorCount =0
#		observer = Observer()
#		stream = Stream(self.checkLog, self.fingDataDir, file_events=True)
#		observer.start()
#		observer.schedule(stream)
        lastmin=-1
        lastmin5=-1
        lastmin29=-1
        lastmin53=-1
        lastdoWOL=-1
        repeatdoWOL = 5
        self.redoAWAY = 0
        self.sleep(5)
        self.throttlePing = 0
        lastFingActivity = time.time()
        lastFingDATA = lastFingActivity
        rebootMinute = 19 # 19 minutes afetr midnitte, dont do it too close to 00:00 because of other processes might be active

        self.timeOfStart= time.time()
        try:
            while self.quitNOW =="no":
                if self.redoAWAY >0:
                    self.sleep(1)
                    self.redoAWAY -=1
                    self.myLog("Ping",u"redo tests, check if device is back UP: "+ str(self.redoAWAY))
                else:
                    xsleep=max(0.5,self.newSleepTime/10)  ## this is to enable a fast reaction to asynchronous events 
                    nsleep = int(self.newSleepTime /xsleep)
                    tt=time.time()
                    for i in range(nsleep):
                        if self.newSleepTime == 0: break
                        if time.time()-tt > self.newSleepTime: break
                        self.sleep( xsleep )
                    self.newSleepTime = self.sleepTime
                #self.myLog("all","after sleeploop self.redoAWAY "+str(self.redoAWAY) +"  nsleep"+ str(nsleep)+"  self.newSleepTime"+ str(self.newSleepTime))    
                #self.printEvents(printEvents="2")              
                if self.triggerFromPlugin:
                    self.pluginCalled()
                    self.checkTriggers()

                if self.indigoCommand != "none" and self.indigoCommand != "":
                    if self.indigoCommand == "loadDevices": self.doLoadDevices()
                    if self.indigoCommand == "sort": self.doSortData()
                    if self.indigoCommand == "details": self.doDetails()
                    if self.indigoCommand == "ResetEVENTS": 
                        self.resetEvents()
                    if self.indigoCommand == "ResetDEVICES":
                        self.resetDevices()
                        break
                    if self.indigoCommand == "PrintEVENTS":   self.printEvents()
                    if self.indigoCommand == "PrintWiFi":     self.printWiFi()
                    if self.indigoCommand == "PrintpiBeacon": self.printpiBeaconDevs()
                    if self.indigoCommand == "PrintUnifi":    self.printUnifiDevs()
                self.indigoCommand = "none"

                checkTime=datetime.datetime.now().strftime("%H:%M:%S").split(":")
                checkTime[0]=int(checkTime[0])
                checkTime[1]=int(checkTime[1])
                checkTime[2]=int(checkTime[2])
                if lastmin !=checkTime[1] and checkTime[2]>10 :
                    VS.versionCheck(self.pluginId,self.pluginVersion,indigo,14,40,printToLog="log")
                    lastmin =checkTime[1]
                    self.updateDeviceWiFiSignal()
                    self.updateAllIndigoIpDeviceFromDeviceData(["deviceInfo"])
                    self.checkIfDevicesChanged() # check for changed device parameters once a minute .
                    self.checkDEVICES() # complete sync every minutes
                    self.setupEventVariables()
                if lastmin5 !=checkTime[1] and checkTime[1]%5 ==0 and checkTime[1] >0 and checkTime[2]>20 :
                    lastmin5 =checkTime[1]
                    self.setupEventVariables()
                    self.getpiBeaconAvailable()
                    self.updatepiBeacons()
                    self.getUnifiAvailable()
                    self.updateUnifi()
                    
                if lastmin29 !=checkTime[1] and checkTime[1]%29 ==0 and checkTime[1] >0 and checkTime[2]>25 :
                    lastmin29 =checkTime[1]
                    self.updateAllIndigoIpVariableFromDeviceData() # copy any new / changed devices to variables
                    self.cleanUpEvents()
                    self.IDretList=[]
                    self.iDevicesEnabled =False
                    if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
                        for dev in indigo.devices.iter(self.iFindStuffPlugin):
                            if dev.deviceTypeId!="iAppleDeviceAuto": continue
                            self.IDretList.append((dev.id,dev.name))
                            self.iDevicesEnabled =True
                    if self.iDevicesEnabled:
                        self.pluginPrefs["iDevicesEnabled"] =True
                    else:
                        self.pluginPrefs["iDevicesEnabled"] =False

                    self.checkLogFiles()
  




            
                if lastmin53 !=checkTime[1] and checkTime[1]%53 ==0 and checkTime[1] >0 and checkTime[2]>35 :
                    lastmin53 =checkTime[1]
                    self.doInbetweenPing(force=True)
                    self.totalLoopCounter= 500
                    
                if checkTime[0] == 0  and rebootMinute == checkTime[1] and self.totalLoopCounter > 200:
                    self.refreshVariables()
                    self.quitNOW ="reboot after midnight"
                                        


                self.totalLoopCounter +=1
                if self.quitNOW !="no": break
                if self.updatePrefs:
                    self.updatePrefs = False
                    self.pluginPrefs["EVENTS"]	=	json.dumps(self.EVENTS)

                
                if time.time()-lastFingActivity > 280:
                    self.myLog(u"all",u"seems that FING is not active - no change in data, restarting fing, seconds since last change: "+ str(time.time() - lastFingActivity))
                    retCode = self.initFing(1)
                    if retCode ==1:
                        self.myLog(u"all",u"fing restarted successfully")
                        fingNotActiveCounter =0
                        self.sleep(5) ## give it some time
                    else:
                        self.myLog("Logic",u"fing not active, tried to restart fing, did not work, stopping fingscan, may be wrong password \n   in plugins/fingscan/configure:  set password" )
                        self.quitNOW = "yes"
                        break

                self.indigoNeedsUpdate=True
                if self.inbetweenPingType !="0":
                    self.throttlePing -=1
                    if self.throttlePing <0 :
                        if self.doInbetweenPing():
                            if self.indigoNeedsUpdate:
                                self.getIndigoIpDevicesIntoData()
                                self.indigoNeedsUpdate=False
                            self.compareToIndigoDeviceData(lastUpdateSource="ping")
                            self.checkTriggers()


                if time.time() - lastdoWOL > repeatdoWOL:
                    lastdoWOL = time.time()
                    for theMAC in self.allDeviceInfo:
                        devI = self.allDeviceInfo[theMAC]
                        if "useWakeOnLanSecs" in devI and devI["useWakeOnLanSecs"] >0:
                            if time.time() - devI["useWakeOnLanLast"] > devI["useWakeOnLanSecs"]:
                                devI["useWakeOnLanLast"] = time.time()
                                self.sendWakewOnLanAndPing(theMAC, nBC= 1, waitForPing=10, countPings=1, waitBeforePing = 0.01, waitAfterPing = 0.0, calledFrom="loop")


                if self.routerType !="0":
                    self.WiFiChanged = {}
                    errorMsg = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, type=self.routerType)
                    if errorMsg != "ok":
                        self.routerErrorCount+=1
                        if self.routerErrorCount%100 < 3 and self.badWiFiTrigger["trigger"]<1:
                            self.myLog("Ping",u"WiFi Router does not return valid MAC numbers: "+errorMsg[:200])
                            if self.routerErrorCount > 3600:  # about 1 hour
                                self.myLog("all",u"WiFi Router: turning of WiFi Router query, you need to re-enable in configuration after router is back online")
                                self.routerType ="0"

                    else:
                        if self.routerErrorCount >0:
                            self.myLog("WiFi",u"WiFi Router back up again")
                        self.routerErrorCount = 0
                        if 	self.checkIfBadWiFi():
                            self.badWiFiTrigger["trigger"]=10
                            self.myLog("WiFi",u"WiFi signal is weak ")#, triggering external python command "+self.fingDataDir+"pings/doThisWhenWiFiIsBad.py")
                            self.printWiFi()
#							subprocess.Popen(  "/usr/bin/python2.7  '"+self.fingDataDir+"pings/doThisWhenWiFiIsBad.py'", shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                            self.triggerEvent("badWiFi")
                            self.resetbadWifiTrigger()
                            
                        if len(self.WiFiChanged)>0 or self.redoAWAY >0:
                            if self.indigoNeedsUpdate:
                                self.getIndigoIpDevicesIntoData()
                                self.indigoNeedsUpdate=False
                            self.compareToIndigoDeviceData(lastUpdateSource="WiFi")
                            self.compareToFingIfExpired(1)
                            self.checkTriggers()
                        self.oldwifiMacList = copy.deepcopy(self.wifiMacList)
                    self.WiFiChanged = {}
                if self.piBeaconUpDateNeeded:
                    self.checkTriggers()
                    self.piBeaconUpDateNeeded=False
                if self.unifiUpDateNeeded:
                    self.checkTriggers()
                    self.unifiUpDateNeeded=False
                
                retCode =self.getfingLog() ## test log file if new data
                if retCode == 1:
                    self.redoAWAY =0
                    lastFingActivity =time.time()
                    if self.quitNOW !="no": break
                    if self.indigoNeedsUpdate:
                        self.getIndigoIpDevicesIntoData()
                        self.indigoNeedsUpdate=False
                    if self.quitNOW !="no": break
                    self.compareToIndigoDeviceData(lastUpdateSource="fingLog")
                    if self.quitNOW !="no": break
#						retCode = self.getIndigoIpVariablesIntoData()
                    self.checkTriggers()
                    try:
                        if self.debugLevel >0 : indigo.variable.updateValue("ipDevsLastUpdate", time.strftime("%H:%M:%S", time.localtime()) )
                    except:
                        self.quitNOW ="Indigo variable error 9"#  someting must be wrong, restart
                        self.myLog("Ping",u"can not update variable ipDevsLastUpdate  \n  restarting fingscan" )
                        break

                if time.time() - lastFingDATA  >30 or self.redoAWAY >0: ##only check regular data file every 30 secs, then every 1, until any change, ie once per minute
                    retCode = self.testfingError()
                    if self.quitNOW !="no": break

                    retCode = self.getfingData() ## test fing data file if any changes
                    if retCode == 1:
                        self.redoAWAY =0
                        lastFingActivity =time.time()
                        lastFingDATA =time.time()
                        try:
                            indigo.variable.updateValue("ipDevsLastUpdate", time.strftime("%H:%M:%S", time.localtime()) )
                        except Exception, exc:
                            self.quitNOW =" ipDevsLastUpdate can not be updated"#  something must be wrong, restart
                            self.myLog(u"all",u"can not update variable ipDevsLastUpdate  \n  restarting fingscan\n exception code: "+str(exc) )
                            break
                        if self.indigoNeedsUpdate:
                            self.getIndigoIpDevicesIntoData()
                            self.indigoNeedsUpdate=False
                        if self.quitNOW !="no": break
                        retCode = self.compareToIndigoDeviceData(lastUpdateSource="fingData")
                        if self.quitNOW !="no": break
                        retCode = self.compareToFingIfExpired(2)
                        if self.quitNOW !="no": break
                        if not self.indigoInitialized:
                            self.myLog("all",u"FINGSCAN initialized")
                        self.initialized=2
                        self.indigoInitialized = True
#						retCode = self.getIndigoIpVariablesIntoData()
                        self.checkTriggers()


            self.pluginState  = "end"
            self.pluginPrefs["EVENTS"]	=	json.dumps(self.EVENTS)
            self.myLog("all",u"--> while loop break  stopping ...  quitNOW was:" +  self.quitNOW)
            self.quitNOW ="no"
            self.stopConcurrentCounter = 1
############ if there are PING jobs left  kill them
            self.killPing("all")
############ this will tell indigo to stop and restart 
            serverPlugin = indigo.server.getPlugin(self.pluginId)
            serverPlugin.restart(waitUntilDone=False)
            return

            
        except self.StopThread:
            # do any cleanup here
            self.killPing("all")
            self.pluginPrefs["EVENTS"]	    =	json.dumps(self.EVENTS)
            self.pluginPrefs["piBeacon"]	=	json.dumps(self.piBeaconDevices)
            self.pluginPrefs["UNIFI"]	    =	json.dumps(self.unifiDevices)
            self.myLog("all",u"exception StopThread triggered ... stopped,  quitNOW was:" +  self.quitNOW)
            self.quitNOW ="no"
            ############ if there are PING jobs left  kill them
        return








    ############# main program  -- end ###########
    def	updateDeviceWiFiSignal(self,theMACin="all"):
        try:
            if theMACin =="all":
                for theMAC in self.wifiMacList:
                    if theMAC in self.ignoredMAC: continue
                    if theMAC in self.allDeviceInfo:
                        self.allDeviceInfo[theMAC]["WiFi"] =  self.wifiMacList[theMAC][9]
                        if self.wifiMacList[theMAC][0] =="Yes" and self.wifiMacList[theMAC][1] =="Yes" :
                            self.allDeviceInfo[theMAC]["WiFiSignal"] =  ("Sig[dBm]:"+("%4.0f"%self.wifiMacList[theMAC][2]  ).strip()
                                                        +",ave:"+("%4.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))).strip()
                                                        #+",cnt:"+("%8.0f"%self.wifiMacList[theMAC][11]).strip()
                                                        )
                    if self.wifiMacList[theMAC][11] > 9999999: self.resetbadWifiTrigger() # reset counter if tooo big
            else:
                theMAC=theMACin
                if theMAC not in self.ignoredMAC:
                    if theMAC in self.wifiMacList:
                        if theMAC in self.allDeviceInfo:
                            self.allDeviceInfo[theMAC]["WiFi"] =  self.wifiMacList[theMAC][9]
                            if self.wifiMacList[theMAC][0] =="Yes" and self.wifiMacList[theMAC][1] =="Yes" :
                                self.allDeviceInfo[theMAC]["WiFiSignal"] =  (("Sig[dBm]:%4.0f"%self.wifiMacList[theMAC][2]  ).strip()
                                                            +","+("ave:%4.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))).strip()
                                                            #+","+("cnt:%8.0f"%self.wifiMacList[theMAC][11]).strip()
                                                            )
                        if self.wifiMacList[theMAC][11] > 9999999: self.resetbadWifiTrigger() # reset counter if tooo big
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        return


    
##############################################
    def getWifiDevices(self,uid,pwd,ipN,type="ASUS" ):
        resp =""
        try:
            if uid =="": return "error no userid given"
            if pwd =="": return "error no password given"
            if ipN =="": return "error no ipNumber given"
            for theMAC in self.wifiMacList:
                self.wifiMacList[theMAC][0]=""
                self.wifiMacList[theMAC][1]=""
                self.wifiMacList[theMAC][2]=""
                self.wifiMacList[theMAC][3]=""
                self.wifiMacList[theMAC][4]=""
                self.wifiMacList[theMAC][5]=""
                self.wifiMacList[theMAC][6]=""


            #                         full path to curl  timout=3secs   userid  passw           ipnumber  page  changed to 3 secs for mini 
            #ticks= time.time()
            resp= subprocess.Popen("/usr/bin/curl  --max-time 3 -u "+uid+":"+pwd+" 'http://"+ipN+"/Main_WStatus_Content.asp'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            response= resp.communicate()[0]
            resp.stdout.close()
            resp.stderr.close()
            if len(response) < 2 :
                self.wifiErrCounter+=1
                if self.wifiErrCounter > 2:
                    self.myLog("all",u" wifi data received not complete(len=0): "+unicode(response))
                return "error bad return from  curl "+unicode(response)
            self.wifiErrCounter =0
            if type=="MERLIN378_54":
                response2 = response.split("wificlients") # this where the information starts:
                if len(response2) <2:
                        self.myLog("all",u" wifi data received not complete(wificlients): "+unicode(response2))
                        return "error bad return from  curl "+unicode(response2)
                noiseSplit =response.upper().split("\nDATAARRAY")
                if len(noiseSplit) <2:
                        self.myLog("all",u" wifi data received not complete(no nDATAARRAY) "+unicode(response2))
                        return "error bad return from  curl "+unicode(response2)
                    
            else:
                response2 = response.split("\n----------------------------------------\n") # this where the information starts:
                if len(response2) < 3: 				return "error bad return from  curl "+unicode(response2) # no valid data return, or bad password...
                noiseSplit =response.upper().split("NOISE:")
                if len(noiseSplit) < 2: 			return "error bad return from  curl "+unicode(response2) # no valid data return, or bad password...

            fo2 =["","2GHz","5GHz"]
            for i in range(1,3):
                fiveORtwo =fo2[i]
                if type=="MERLIN378_54":
                    nsplit=  noiseSplit[i].split(";")[0].split("= ")
                    if len(nsplit) < 2:
                        self.myLog("WiFi",u" wifi data received not complete (nsplit <2): "+unicode(noiseSplit))
                        continue
                    self.wifiMacAv["noiseLevel"][fiveORtwo] = json.loads(nsplit[1])[3]
    #				self.myLog("WiFi"," wifi noiseLevel "+str(fiveORtwo)+" "+str(noiseSplit[i]))
                else:
                    if len(noiseSplit) > 2:
                        self.wifiMacAv["noiseLevel"][fiveORtwo] = noiseSplit[i].strip(" ").split(" ")[0]
                errorMSG=" "
                if type=="ASUS":			errorMSG =self.parseWIFILogA(response2[i].split("\n\n")[0].split("\n"),fiveORtwo)
                elif type=="MERLIN":		errorMSG =self.parseWIFILogM(response2[i].split("\n\n")[0].split("\n"),fiveORtwo)
                elif type=="MERLIN378_54":	errorMSG =self.parseWIFILogM378(response2[i],fiveORtwo)
                else: return "bad wifi defnition"
                if errorMSG !="ok": 			return errorMSG
                if self.wifiMacAv["numberOfCycles"][fiveORtwo] >3 and self.wifiMacAv["curDev"][fiveORtwo]>0. :
                    if    abs(self.wifiMacAv["curAvSignal"][fiveORtwo] - self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]) > 5.:
                        self.signalDelta["5"][fiveORtwo] +=1
                    elif  abs(self.wifiMacAv["curAvSignal"][fiveORtwo] - self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]) > 2.:
                        self.signalDelta["2"][fiveORtwo] +=1
                    elif  abs(self.wifiMacAv["curAvSignal"][fiveORtwo] - self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]) > 1:
                        self.signalDelta["1"][fiveORtwo] +=1
                    if    self.totalLoopCounter >99999:
                        self.myLog("WiFi",u" wifi signals "+fiveORtwo+": sumSig:%8.0f sumNdev:%8.0f sumNMeas:%8.0f longAv%6.2f longnDevAv%6.2f thisAV:%6.2f thisnMeas:%3.1f del5:%5.0f del2:%5.0f del1:%5.0f"%
                            (self.wifiMacAv["sumSignal"][fiveORtwo]
                            ,self.wifiMacAv["numberOfDevices"][fiveORtwo]
                            ,self.wifiMacAv["numberOfCycles"][fiveORtwo]
                            ,self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]
                            ,self.wifiMacAv["numberOfDevices"][fiveORtwo]/self.wifiMacAv["numberOfCycles"][fiveORtwo]
                            ,self.wifiMacAv["curAvSignal"][fiveORtwo]
                            ,self.wifiMacAv["curDev"][fiveORtwo]
                            ,self.signalDelta["5"][fiveORtwo]
                            ,self.signalDelta["2"][fiveORtwo]
                            ,self.signalDelta["1"][fiveORtwo]))
            delMACs=[]
            for theMAC in self.oldwifiMacList:
                if theMAC not in self.wifiMacList:
                    self.WiFiChanged[theMAC]=self.self.oldwifiMacList[theMAC][0]
                    delMACs.append(theMAC)
                    continue
            for theMAC in delMACs:
                del self.oldwifiMacList[theMAC]
            for theMAC in self.wifiMacList:
                if theMAC not in self.oldwifiMacList:
                    self.WiFiChanged[theMAC]=self.wifiMacList[theMAC][0]
                    self.oldwifiMacList[theMAC] = copy.deepcopy(emptyWiFiMacList)
        
                if self.wifiMacList[theMAC][0] != self.oldwifiMacList[theMAC][0]: self.WiFiChanged[theMAC]=self.wifiMacList[theMAC][0]

                #if self.wifiMacList[theMAC][1] != self.oldwifiMacList[theMAC][1]: self.WiFiChanged[theMAC]=[0]
                #if self.wifiMacList[theMAC][3] != self.oldwifiMacList[theMAC][3]: self.WiFiChanged[theMAC]=[0]
                #if self.wifiMacList[theMAC][4] != self.oldwifiMacList[theMAC][4]: self.WiFiChanged[theMAC]=[0]
                #if self.wifiMacList[theMAC][5] != self.oldwifiMacList[theMAC][5]: self.WiFiChanged[theMAC]=[0]
    
                
                    
            #self.myLog("WiFi"," wifi curl time elapsed: %9.3f " %(time.time()-ticks))
        except  Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e)+" wifi router reponse:"+ unicode(resp))
            return "error "+ unicode(resp)

        return "ok"  # [MACno][MACno,Associated,Authorized,RSSI,PSM,SGI,STBC,Tx rate,Rx rate,Connect Time]], "ok"


##############################################
    def resetbadWifiTrigger(self):
        try:
            for theMAC in self.wifiMacList:
                self.wifiMacList[theMAC][10] =0
                self.wifiMacList[theMAC][11] =0
            self.badWiFiTrigger["numberOfSecondsBad"] =0
            self.wifiMacAv=copy.deepcopy(emptyWifiMacAv)
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return

##############################################
    def checkIfBadWiFi(self):
        try:
            if self.badWiFiTrigger["minNumberOfSecondsBad"] >998: return False
    #		if self.badWiFiTrigger["minNumberOfDevicesBad"] >998: return False
    #		if self.badWiFiTrigger["minSignalDrop"] >998: return False
            candidates =0
            for theMAC in self.wifiMacList:
                if self.wifiMacList[theMAC][0]!="Yes": continue
                if self.wifiMacList[theMAC][1]!="Yes": continue
                if self.wifiMacList[theMAC][9]!="2GHz": continue
                if self.wifiMacList[theMAC][11] < 15: continue
                if (
                    (	(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1.)-self.wifiMacList[theMAC][2])  >   self.badWiFiTrigger["minSignalDrop"]	) 	or
                    (	self.wifiMacList[theMAC][2] <  self.badWiFiTrigger["minWiFiSignal"]		)
                   ): candidates +=1

            if candidates < self.badWiFiTrigger["minNumberOfDevicesBad"]:
                self.badWiFiTrigger["numberOfSecondsBad"] =0
                self.badWiFiTrigger["trigger"] -=1
                return False

            if self.badWiFiTrigger["numberOfSecondsBad"] >0 : # trigger started?
                nSecBad = time.time() -self.badWiFiTrigger["numberOfSecondsBad"]
                if nSecBad%10 == 5:
                    self.myLog("WiFi",u" bad wifi signal for %3.0f seconds"%(nSecBad) )
                if (nSecBad) > self.badWiFiTrigger["minNumberOfSecondsBad"]:
                    # this is the trigger
                    self.badWiFiTrigger["trigger"] =10
                    return True
                else:  # not yet, still waiting
                    self.badWiFiTrigger["trigger"] -=1
                    return False

            # start trigger timer
            self.badWiFiTrigger["numberOfSecondsBad"] = time.time()
            self.badWiFiTrigger["trigger"] -=1
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return False


##############################################
    def parseWIFILogM378(self,wifiLog,fiveORtwo):
    # wdataarray24 = ["2","0","0","-92","8","D8:50:E6:CF:B4:E0","AP"];
    #wificlients24 = [["54:9F:13:3F:95:25","192.168.1.192","iPhone-20","-62","13", "72","  0:24:56"," S AU"],["FC:E9:98:49:BB:B9","192.168.1.155", "Kristins-iPhone","-65","24", "72","  0:37:11","PS AU"],["6C:AD:F8:26:69:9E","192.168.1.242","Chromecast","-50","72", "72","  0:38:00"," STAU"],["F0:7D:68:08:5F:D0","192.168.1.74","<not found>","-68","52", "58","  0:38:02"," STAU"],["28:10:7B:0C:CB:4B","192.168.1.77","<not found>","-72","52", "72","  0:38:03"," STAU"],["F0:7D:68:06:F6:87","192.168.1.71","<not found>","-51","72", "72","  0:38:03"," STAU"],"-1"];
    #dataarray5 = ["5","0","0","-92","149/80","D8:50:E6:CF:B4:E4","AP"];
    #wificlients5 = [["F0:F6:1C:D5:51:16","192.168.1.215","<not found>","-69","24", "243","  0:36:53","PSTAU"],"-1"];

        try:
            self.myLog("WiFi",u"wifiLog:"+ unicode(wifiLog))
            wl= wifiLog.split(";")[0].split("= ")
            if len(wl) < 2:
                self.myLog("all",u"parseWIFILogM378 wifilog data not complete (wl=0): "+ unicode(wifiLog))
                return "error"
            try:
                wlist= json.loads(wl[1])
            except:
                self.myLog("all",u"parseWIFILogM378: wifilog data not complete( Wl json): "+ unicode(wifiLog))
                return "error"


            # now parse
            nDevices = len(wlist)-1
            if nDevices <1: return "ok"
            sumSignal =0.
            nDevConnected=0
            for thisDevice1 in wlist:
                self.myLog("WiFi",u"thisDevice1:"+ unicode(thisDevice1))
                thisDevice=[]

                if thisDevice1 =="-1": continue
                
                theMAC =thisDevice1[0]

                self.myLog("WiFi",u"thisDevice1>>"+ theMAC+"<<  "+str(thisDevice1))
                thisDevice=[]
                if thisDevice1[7].find("A")>-1:			thisDevice.append("Yes")	# associated
                else:									thisDevice.append(" ")
                
                if thisDevice1[7].find("U")>-1:			thisDevice.append("Yes")	# authorized
                else:									thisDevice.append(" ")

                thisDevice.append(thisDevice1[3])									# rssi

                if thisDevice1[7].find("P")>-1:			thisDevice.append("Yes")	# psm
                else:									thisDevice.append("No")

                if thisDevice1[7].find("S")>-1:			thisDevice.append("Yes")	# sgi
                else:									thisDevice.append("No")

                if thisDevice1[7].find("T")>-1:			thisDevice.append("Yes")	# STBC
                else:									thisDevice.append("No")

                thisDevice.append(thisDevice1[4])									# tx rate
                thisDevice.append(thisDevice1[5])									# rx rate
                thisDevice.append(thisDevice1[6])									# connect time
                
                
                try:
                    thisDevice[2] = float(thisDevice[2])
                except:
                    continue
                thisDevice.append(fiveORtwo)
                if theMAC in self.wifiMacList:
                    if self.wifiMacList[theMAC][10] !="":
                        thisDevice.append(float(self.wifiMacList[theMAC][10]))
                        thisDevice.append(float(self.wifiMacList[theMAC][11]))
                    else:
                        thisDevice.append(0.)
                        thisDevice.append(0.)
                else:
                    thisDevice.append(0.)
                    thisDevice.append(0.)
                self.wifiMacList[theMAC]= copy.deepcopy(thisDevice)
                self.wifiMacList[theMAC][10]+= self.wifiMacList[theMAC][2]
                self.wifiMacList[theMAC][11]+= 1



                
                
                if self.wifiMacList[theMAC][0]=="Yes" and self.wifiMacList[theMAC][1]=="Yes" :
                    sumSignal+= self.wifiMacList[theMAC][2]
                    nDevConnected +=1


            if nDevConnected > 0:
                self.wifiMacAv["sumSignal"][fiveORtwo]+= sumSignal
                self.wifiMacAv["numberOfDevices"][fiveORtwo] += nDevConnected
                self.wifiMacAv["curAvSignal"][fiveORtwo]= sumSignal/nDevConnected
                self.wifiMacAv["curDev"][fiveORtwo]= nDevConnected
                self.wifiMacAv["numberOfCycles"][fiveORtwo] +=1

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return  "ok"

##############################################
    def parseWIFILogM(self,wifiLog,fiveORtwo):
        # wifiN =:
        #	tations  (flags: P=Powersave Mode, S=Short GI, T=STBC, A=Associated, U=Authenticated)
        #MAC               IP Address      Name              RSSI    Rx/Tx Rate   Connected Flags
        #FC:E9:98:49:BB:B9 192.168.1.155   Kristins-iPhone  -57dBm   72/72 Mbps   05:43:06  PS AU
                       #FC:E9:98:49:BB:B9 xxx192.168.1.155   xxxKristins-iPhone xxx -57dBmxxx   72xxx/xxx72 xxxMbps   xxx05:43:06  PS AU
                       #MAC               xxxIP Address      xxxName            xxx  RSSI xxx   Rxxxx/xxxTx xxxRate   xxxConnected xxxFlags

        try:
            pointerText = ["MAC   ","IP Address   ","Name   ","  RSSI","   Rx","/","Tx Rate   ","Connected ","Flags"]
            thepointers=[]
    #		self.myLog("WiFi","line:"+ wifiLog[0])
            for pT in range(len(pointerText)):
                p= wifiLog[0].find(pointerText[pT])
                if p ==-1: return "error parsing return string "+pointerText[pT]
                thepointers.append(p)
            thepointers.append(len(wifiLog[0]))
    #		self.myLog("WiFi","line:"+ str(thepointers))

            # records should be ok..
            
            
            # now parse
            nDevices = len(wifiLog)
            if nDevices <1: return "ok"
            sumSignal =0.
            nDevConnected=0
            for line in range(1,nDevices):
    #			self.myLog("WiFi","line:"+ wifiLog[line])
                if len(wifiLog[line])< 20: continue

                thisDevice1=[]
                for p in range(1,len(pointerText)):
                    thisDevice1.append( wifiLog[line][thepointers[p]: min(thepointers[p+1],len(wifiLog[line]))].strip() )
                
                theMAC = wifiLog[line][:17].strip(" ")

                self.myLog("WiFi",u"thisDevice1>>"+ theMAC+"<<  "+str(thisDevice1))
                thisDevice1[7]+="      "
                thisDevice=[]
                if thisDevice1[7].find("A")>-1:			thisDevice.append("Yes")	# associated
                else:									thisDevice.append(" ")
                if thisDevice1[7].find("U")>-1:			thisDevice.append("Yes")	# authorized
                else:									thisDevice.append(" ")
                thisDevice.append(thisDevice1[2])									# rssi
                if thisDevice1[7].find("P")>-1:			thisDevice.append("Yes")	# psm
                else:									thisDevice.append("No")
                if thisDevice1[7].find("S")>-1:			thisDevice.append("Yes")	# sgi
                else:									thisDevice.append("No")
                if thisDevice1[7].find("T")>-1:			thisDevice.append("Yes")	# STBC
                else:									thisDevice.append("No")
                thisDevice.append(thisDevice1[3])									# tx rate
                thisDevice.append(thisDevice1[5].strip(" ").split(" ")[0])			# rx rate  strip the MBps
                thisDevice.append(thisDevice1[6])									# connect time
                
                
                try:
                    thisDevice[2] = float(thisDevice[2][:-3])
                except:
                    continue
                thisDevice.append(fiveORtwo)
                if theMAC in self.wifiMacList:
                    if self.wifiMacList[theMAC][10] !="":
                        thisDevice.append(float(self.wifiMacList[theMAC][10]))
                        thisDevice.append(float(self.wifiMacList[theMAC][11]))
                    else:
                        thisDevice.append(0.)
                        thisDevice.append(0.)
                else:
                    thisDevice.append(0.)
                    thisDevice.append(0.)
                self.wifiMacList[theMAC]= copy.deepcopy(thisDevice)
                self.wifiMacList[theMAC][10]+= self.wifiMacList[theMAC][2]
                self.wifiMacList[theMAC][11]+= 1



                if self.wifiMacList[theMAC][0]=="Yes" and self.wifiMacList[theMAC][1]=="Yes" :
                    sumSignal+= self.wifiMacList[theMAC][2]
                    nDevConnected +=1


            if nDevConnected > 0:
                self.wifiMacAv["sumSignal"][fiveORtwo]+= sumSignal
                self.wifiMacAv["numberOfDevices"][fiveORtwo] += nDevConnected
                self.wifiMacAv["curAvSignal"][fiveORtwo]= sumSignal/nDevConnected
                self.wifiMacAv["curDev"][fiveORtwo]= nDevConnected
                self.wifiMacAv["numberOfCycles"][fiveORtwo] +=1

        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return  "ok"
##############################################
    def parseWIFILogA(self,wifiLog,fiveORtwo):
        
        # wifiN =:
        #						STBC= space Time broad casts
        #						SGI= short guard inetrval:  space between symbols
        #						PSM= Power Save Mode
        #MAC               Associated Authorized    RSSI PSM SGI STBC Tx rate Rx rate Connect Time
        #F8:27:93:59:9D:B2 Yes        Yes         -71dBm Yes Yes No       65M     24M 00:00:02
        #28:10:7B:0C:CB:52 Yes        Yes         -78dBm No  Yes Yes    72.2M   43.3M 06:43:40
        #28:10:7B:0C:CB:4B Yes        Yes         -73dBm No  Yes Yes    72.2M   72.2M 06:43:47
        #B8:E8:56:42:69:FE                        -70dBm No  Yes Yes     585M    234M 00:00:00'
        try:
            pointerText = ["MAC","Associated","Authorized","   RSSI","PSM","SGI","STBC","Tx rate","Rx rate","Connect Time"]
            thepointers=[]
            for pT in range(len(pointerText)):
                p= wifiLog[0].find(pointerText[pT])
                if p ==-1: return "error parsing return string "+pointerText[pT]
                thepointers.append(p)
            thepointers.append(len(wifiLog[0]))

            # records should be ok..
            
            # now parse
            nDevices = len(wifiLog)
            if nDevices <1: return "ok"
            sumSignal =0.
            nDevConnected=0
            for line in range(1,nDevices):
                if len(wifiLog[line])< 5: continue
                thisDevice=[]
                for p in range(1,len(pointerText)):
                    thisDevice.append( wifiLog[line][thepointers[p]: min(thepointers[p+1],len(wifiLog[line]))].strip() )
                theMAC = (wifiLog[line][thepointers[0]: min(thepointers[1],len(wifiLog[line])) ]).strip()
                
                try:
                    thisDevice[2] = float(thisDevice[2][:-3])
                except:
                    continue
                thisDevice.append(fiveORtwo)
                if theMAC in self.wifiMacList:
                    if self.wifiMacList[theMAC][10] !="":
                        thisDevice.append(float(self.wifiMacList[theMAC][10]))
                        thisDevice.append(float(self.wifiMacList[theMAC][11]))
                    else:
                        thisDevice.append(0.)
                        thisDevice.append(0.)
                else:
                    thisDevice.append(0.)
                    thisDevice.append(0.)
                self.wifiMacList[theMAC]= copy.deepcopy(thisDevice)
                self.wifiMacList[theMAC][10]+= self.wifiMacList[theMAC][2]
                self.wifiMacList[theMAC][11]+= 1

                if self.wifiMacList[theMAC][0]=="Yes" and self.wifiMacList[theMAC][1]=="Yes" :
                    sumSignal+= self.wifiMacList[theMAC][2]
                    nDevConnected +=1


            if nDevConnected > 0:
                self.wifiMacAv["sumSignal"][fiveORtwo]+= sumSignal
                self.wifiMacAv["numberOfDevices"][fiveORtwo] += nDevConnected
                self.wifiMacAv["curAvSignal"][fiveORtwo]= sumSignal/nDevConnected
                self.wifiMacAv["curDev"][fiveORtwo]= nDevConnected
                self.wifiMacAv["numberOfCycles"][fiveORtwo] +=1
                
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))

        return  "ok"


##############################################
    def checkWIFIinfo(self):
        try:
            for mac in self.wifiMacList:
                self.wifiMacList[mac]=copy.deepcopy(emptyWiFiMacList)
            if self.routerType !="0":
                errorMSG = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn,type=self.routerType)
                if errorMSG !="ok":
                    self.myLog("WiFi",u"Router wifi not reachable, userid password or ipnumber wrong?\n"+ unicode(errorMSG))
                    return
                else:
                    self.myLog("WiFi",u"Router wifi data ok")
            else:
                self.routerUID	= ""
                self.routerPWD	= ""
                self.routerIPn	= ""


        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return



##############################################
    def checkDEVICES(self):
    #		self.myLog("Logic",u"checking devices")
    #					emptyAllDeviceInfo={"00:00:00:00:00:00":{"ipNumber":"0.0.0.0","timeOfLastChange":"timeOfLastChange","status":"down","nickName":"iphonexyz":"noOfChanges":"0", "hardwareVendor":"", "deviceInfo":"","WiFi":"","deviceId":0,"deviceName":"","devExists":0}}
        try:
            for theMAC in self.allDeviceInfo:
                self.allDeviceInfo[theMAC]["devExists"]=0

            for dev in indigo.devices.iter("com.karlwachs.fingscan"):
                devID=str(dev.id)
                theStates = dev.states.keys()
    #			self.myLog("Logic",u"device testing: "+dev.name)
    #			self.myLog("Logic",u"device states: MAC-"+str(theStates))
                
                if "MACNumber" in theStates:
                    anyUpdate = False
                    theMAC = dev.states["MACNumber"]
                    if theMAC =="": continue
                    if not theMAC in self.allDeviceInfo: continue
                    devI=self.allDeviceInfo[theMAC]
                    devI["deviceId"]	=dev.id
                    if dev.name != devI["deviceName"]:
                        devI["nickName"] = dev.name
                        devI["deviceName"]	=dev.name
                        
                    if theMAC in self.wifiMacList:
                        self.updateDeviceWiFiSignal(theMAC)
                        dev.description = theMAC+"-"+devI["WiFi"]+"-"+devI["WiFiSignal"]
                        dev.replaceOnServer()
                        #dev.updateStateOnServer("WiFi",				devI["WiFi"])
                        self.addToStatesUpdateList(str(dev.id),"WiFi",				devI["WiFi"])
                        try:
                            string ="%5.1f"%self.wifiMacList[theMAC][2]
                        except:
                            string =str(self.wifiMacList[theMAC][2])
                        
                        #dev.updateStateOnServer("WiFiSignal",string)
                        self.addToStatesUpdateList(str(dev.id),"WiFiSignal",string)
                    
                    if dev.states["ipNumber"] != devI["ipNumber"]:
                        #dev.updateStateOnServer("ipNumber",			devI["ipNumber"])
                        self.addToStatesUpdateList(str(dev.id),"ipNumber",			devI["ipNumber"])
                        anyUpdate=True
                    if dev.states["status"] != devI["status"]:
                        #dev.updateStateOnServer("status",			devI["status"])
                        self.addToStatesUpdateList(str(dev.id),"status",			devI["status"])
                        anyUpdate=True
                    if dev.states["nickName"] != devI["nickName"]:
                        #dev.updateStateOnServer("nickName",			devI["nickName"])
                        self.addToStatesUpdateList(str(dev.id),"nickName",			devI["nickName"])
                        anyUpdate=True
                    if unicode(dev.states["noOfChanges"]) != unicode(devI["noOfChanges"]):
                        #dev.updateStateOnServer("noOfChanges",		int(devI["noOfChanges"]) )
                        self.addToStatesUpdateList(str(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
                        anyUpdate=True
                    if dev.states["hardwareVendor"] !=devI["hardwareVendor"]:
                        #dev.updateStateOnServer("hardwareVendor",	devI["hardwareVendor"])
                        self.addToStatesUpdateList(str(dev.id),"hardwareVendor",	devI["hardwareVendor"])
                        anyUpdate=True
                    if dev.states["deviceInfo"] !=devI["deviceInfo"]:
                        #dev.updateStateOnServer("deviceInfo",		devI["deviceInfo"])
                        self.addToStatesUpdateList(str(dev.id),"deviceInfo",		devI["deviceInfo"])
                        anyUpdate=True
                    if dev.states["WiFi"] !=devI["WiFi"]:
                        #dev.updateStateOnServer("WiFi",				devI["WiFi"])
                        self.addToStatesUpdateList(str(dev.id),"WiFi",				devI["WiFi"])
                        anyUpdate=True
                    if "created" in dev.states and len(dev.states["created"]) < 10:
                        self.addToStatesUpdateList(str(dev.id),"created",		datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        anyUpdate=True
                    usePing = devI["usePing"]
                    if  str(devI["useWakeOnLanSecs"]) !="0":
                        usePing +="-WOL:"+str(devI["useWakeOnLanSecs"])
                    if "usePing-WOL" in dev.states:
                        if dev.states["usePing-WOL"] !=usePing:
                            anyUpdate=True
                            #dev.updateStateOnServer("usePing",			devI["usePing"])
                            self.addToStatesUpdateList(str(dev.id),"usePing-WOL",			usePing)
                    if "suppressChangeMSG" in dev.states:
                        if dev.states["suppressChangeMSG"] != devI["suppressChangeMSG"]:
                            anyUpdate=True
                            #dev.updateStateOnServer("suppressChangeMSG",devI["suppressChangeMSG"])
                            self.addToStatesUpdateList(str(dev.id),"suppressChangeMSG",devI["suppressChangeMSG"])
                            
                    if "lastFingUp" in dev.states:
                        if dev.states["lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])):
                            anyUpdate=True
                            #dev.updateStateOnServer("suppressChangeMSG",devI["suppressChangeMSG"])
                            self.addToStatesUpdateList(str(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])))
                            
                

                    if anyUpdate:
    #					self.myLog("all",u"state updates needed")
                        #dev.updateStateOnServer("timeOfLastChange",	devI["timeOfLastChange"])
                        self.addToStatesUpdateList(str(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
    #				else:
    #					self.myLog("all",u"state updates NOT  needed")




                    pad = self.padStatusForDevListing(devI["status"])

                    if dev.states["statusDisplay"] != (devI["status"]).ljust(pad)+devI["timeOfLastChange"]:
    #					self.myLog("all",u"statusDisplay updates needed")
                        #dev.updateStateOnServer("statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
                        self.addToStatesUpdateList(str(dev.id),"statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
                    self.executeUpdateStatesList()
    #				else:
    #					self.myLog("all",u"statusDisplay updates NOT  needed")


                    try:
                        props = dev.pluginProps
                        if props["address"] != self.formatiPforAddress(devI["ipNumber"]):
                            if props["address"].split("-")[0] != self.formatiPforAddress(devI["ipNumber"]).split("-")[0] :
#							if props["address"].strip("-changed") != self.formatiPforAddress(devI["ipNumber"]).strip("-changed") :
                                if "suppressChangeMSG" in dev.states:
                                    if dev.states["suppressChangeMSG"] =="show":
                                        if theMAC in self.doubleIPnumbers:
                                            if len(self.doubleIPnumbers[theMAC]) ==1:
                                                self.myLog("all",u"IPNumber changed,  old: "+ str(props["address"])+ "; new: "+ str(self.formatiPforAddress(devI["ipNumber"]))+ " for device MAC#: "+theMAC +" to switch off changed message: edit this device and select no msg")
                                            else:
                                                self.myLog("all",u"Multiple IPNumbers for device MAC#: "+theMAC+" -- "+ str(self.doubleIPnumbers[theMAC])+" to switch off changed message: edit this device and select no msg")
                                        else:
                                                self.myLog("all",u"IPNumber changed,  old: "+ str(props["address"])+ "; new: "+ str(self.formatiPforAddress(devI["ipNumber"]))+ " for device MAC#: "+theMAC+" to switch off changed message: edit this device and select no msg")

                            props["address"]=self.formatiPforAddress(devI["ipNumber"])
                            dev.replacePluginPropsOnServer(props)
    #					else:
    #						self.myLog("all",u"address updates NOT  needed"å)
                    except:
                        self.myLog("Ping",u"props check did not work")
                    devI["devExists"]	=1

            for theMAC in self.allDeviceInfo:
                if theMAC =="": continue
                devI = self.allDeviceInfo[theMAC]
                if devI["devExists"] == 0 and self.acceptNewDevices and theMAC not in self.ignoredMAC:

    #				self.myLog("Logic",u" creating device "+str(devI))
                    try:
                        if devI["nickName"] !="iphone-xyz" and devI["nickName"] !="":
                            theName=devI["nickName"]
                            try:
                                dev = indigo.devices[theName]
                                test= dev.id
                                theName = "MAC_"+theMAC
                            except:
                                theName=devI["nickName"]
                        else:
                            theName = "MAC_"+theMAC
                        indigo.device.create(
                            protocol=indigo.kProtocol.Plugin,
                            address=self.formatiPforAddress(devI["ipNumber"]),
                            name=theName,
                            description=theMAC,
                            pluginId="com.karlwachs.fingscan",
                            deviceTypeId="IP-Device",
                            props = {"setUsePing":"doNotUsePing","setuseWakeOnLan":0,"setExpirationTime":0},
                            folder=self.indigoDeviceFolderID
                            )
                        dev = indigo.devices[theName]
                        self.addToStatesUpdateList(str(dev.id),"MACNumber",		theMAC)
                        self.addToStatesUpdateList(str(dev.id),"ipNumber",			devI["ipNumber"])
                        self.addToStatesUpdateList(str(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
                        self.addToStatesUpdateList(str(dev.id),"status",			devI["status"])
                        self.addToStatesUpdateList(str(dev.id),"nickName",			devI["nickName"])
                        self.addToStatesUpdateList(str(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
                        self.addToStatesUpdateList(str(dev.id),"hardwareVendor",	devI["hardwareVendor"])
                        self.addToStatesUpdateList(str(dev.id),"deviceInfo",		devI["deviceInfo"])
                        self.addToStatesUpdateList(str(dev.id),"suppressChangeMSG", devI["suppressChangeMSG"])
                        self.addToStatesUpdateList(str(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
                        self.addToStatesUpdateList(str(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
                        if theMAC in self.wifiMacList:
                            self.addToStatesUpdateList(str(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])

                        self.updateDeviceWiFiSignal(theMAC)
                        usePing = devI["usePing"]
                        if  str(devI["useWakeOnLanSecs"]) !="0":
                            usePing +="-WOL:"+str(devI["useWakeOnLanSecs"])
                        if "usePing-WOL" in dev.states: self.addToStatesUpdateList(str(dev.id),"usePing-WOL",			usePing)
                        self.addToStatesUpdateList(str(dev.id),"WiFi",				devI["WiFi"])
                        pad = self.padStatusForDevListing(devI["status"])
                        self.addToStatesUpdateList(str(dev.id),"statusDisplay",	devI["status"].ljust(pad)+devI["timeOfLastChange"])
                        self.addToStatesUpdateList()
                        devI["deviceId"]	=dev.id
                        devI["deviceName"]	=dev.name
                        devI["devExists"]	=1
                        if devI["WiFi"] !="":
                            dev.description = theMAC+"-"+devI["WiFi"]+"-"+devI["WiFiSignal"]
                            dev.replaceOnServer()
                    except:
                        pass
                        
                try:
                    if self.wifiMacAv["curAvSignal"]["2GHz"] !=0.:
                        indigo.variable.updateValue("averageWiFiSignal_2GHz", "%5.1f"%self.wifiMacAv["curAvSignal"]["2GHz"] )
                    if self.wifiMacAv["curAvSignal"]["5GHz"] !=0.:
                        indigo.variable.updateValue("averageWiFiSignal_5GHz", "%5.1f"%self.wifiMacAv["curAvSignal"]["5GHz"] )
                except:
                    pass
            self.executeUpdateStatesList()        
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
            
        return

##############################################
    def checkIfDevicesChanged(self):
        try:
    #		self.myLog("Logic",u" check if devices changed..")
            for dev in indigo.devices.iter("com.karlwachs.fingscan"):
                #if  dev.pluginId.find("com.karlwachs.fingscan") == -1 :continue
                devID=str(dev.id)
                theStates = dev.states.keys()
                update = 0
                if "MACNumber" in theStates:
                    theMAC = dev.states["MACNumber"]
                    if theMAC =="": continue
                    if not theMAC in self.allDeviceInfo: continue
                    devI=self.allDeviceInfo[theMAC]
    #				self.myLog("Logic",u" checking MAC/values: "+theMAC+":"+ str(devI))
                    devI["deviceId"]	=dev.id
                    if dev.name != devI["deviceName"]:
                        update = 1
                        devI["nickName"] 	= dev.name
                        devI["deviceName"]	= dev.name
                        #dev.updateStateOnServer("nickName",	devI["nickName"])
                        self.addToStatesUpdateList(str(dev.id),"nickName",	devI["nickName"])
                    if dev.states["hardwareVendor"] != devI["hardwareVendor"]:
                        devI["hardwareVendor"]		=dev.states["hardwareVendor"]
                        update = 2
                    if dev.states["deviceInfo"] != devI["deviceInfo"]:
                        devI["deviceInfo"]			=dev.states["deviceInfo"]
                    if dev.states["WiFi"] != devI["WiFi"]:
                        test 					=dev.states["WiFi"]
                        if test ==0:devI["WiFi"]=""
                        else:		devI["WiFi"]=dev.states["WiFi"]
                        update = 3
                if update>0:
    #				self.myLog("Logic",u" updating MAC: "+theMAC)
                    self.updateIndigoIpVariableFromDeviceData(theMAC)
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return

##############################################
    def updateAllIndigoIpDeviceFromDeviceData(self,statesToUdate=["all"]):
        devcopy = copy.deepcopy(self.allDeviceInfo)
        for theMAC in devcopy:
            if theMAC in self.ignoredMAC: continue
            self.updateIndigoIpDeviceFromDeviceData(theMAC,statesToUdate)
##############################################
    def updateIndigoIpDeviceFromDeviceData(self,theMAC,statesToUpdate,justStatus=""):
#		self.myLog("Logic",u"updating dev and states: "+ theMAC+"/"+str(statesToUpdate))
        if theMAC in self.ignoredMAC: return
        try:
            try:
                devI=self.allDeviceInfo[theMAC]
            except:
                self.myLog(u"all",u"deleteIndigoIpDevicesData: MAC Number: "+ theMAC+" information does not exist in allDeviceInfo")
                return
            try:
                devId =devI["deviceId"]
                dev = indigo.devices[devId]
                if justStatus!="": # update only status for quick turn around
                    #dev.updateStateOnServer("status",justStatus)
                    self.addToStatesUpdateList(str(dev.id),"status",justStatus)
                    pad = self.padStatusForDevListing(justStatus)
                    #dev.updateStateOnServer("statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", localtime()))
                    self.addToStatesUpdateList(str(dev.id),"statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    if "lastFingUp" in dev.states:
                        if dev.states["lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])):
                            self.addToStatesUpdateList(str(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])))
                    self.executeUpdateStatesList()
                    self.allDeviceInfo[theMAC]["status"] =justStatus
                    return
            except:
    # create new device
                name="MAC-"+theMAC,
                if "nickName" in devI:
                    if devI["nickName"] !="": 	name =devI["nickName"]
                    if True or self.acceptNewDevices:
                        try:
                            indigo.device.create(
                                protocol=indigo.kProtocol.Plugin,
                                address=self.formatiPforAddress(devI["ipNumber"]),
                                name=name,
                                description=theMAC,
                                pluginId="com.karlwachs.fingscan",
                                deviceTypeId="IP-Device",
                                props = {"setUsePing":"doNotUsePing","setuseWakeOnLan":0,"setExpirationTime":0},
                                folder=self.indigoDeviceFolderID
                                )
                        except:
                            pass

                        dev = indigo.devices[name]
                        self.addToStatesUpdateList(str(dev.id),"MACNumber",		theMAC)
                        self.addToStatesUpdateList(str(dev.id),"ipNumber",			devI["ipNumber"])
                        self.addToStatesUpdateList(str(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
                        self.addToStatesUpdateList(str(dev.id),"status",			devI["status"])
                        self.addToStatesUpdateList(str(dev.id),"nickName",			devI["nickName"])
                        self.addToStatesUpdateList(str(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
                        self.addToStatesUpdateList(str(dev.id),"hardwareVendor",	devI["hardwareVendor"])
                        self.addToStatesUpdateList(str(dev.id),"deviceInfo",		devI["deviceInfo"])
                        self.addToStatesUpdateList(str(dev.id),"WiFi",				devI["WiFi"])
                        self.addToStatesUpdateList(str(dev.id),"usePing-WOL",		devI["usePing"]+"-"+str(devI["useWakeOnLanSecs"]))
                        self.addToStatesUpdateList(str(dev.id),"suppressChangeMSG", devI["suppressChangeMSG"])
                        self.addToStatesUpdateList(str(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
                        self.addToStatesUpdateList(str(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
                        if theMAC in self.wifiMacList:
                            self.addToStatesUpdateList(str(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])
                
                        pad = self.padStatusForDevListing(devI["status"])
                        self.addToStatesUpdateList(str(dev.id),"statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
                        devI["deviceId"]	=dev.id
                        devI["deviceName"]	=dev.name
                        devI["devExists"]	=1
                        self.executeUpdateStatesList()

                return
            
            if len(statesToUpdate)>0:
                anyUpdate=False
    # update old device
                if "ipNumber" in statesToUpdate or statesToUpdate[0]=="all":
                    if dev.states["ipNumber"] !=devI["ipNumber"]:
                        self.addToStatesUpdateList(str(dev.id),"ipNumber",			devI["ipNumber"])
                        anyUpdate=True
                if "status" in statesToUpdate or statesToUpdate[0]=="all":
                    if dev.states["status"] !=devI["status"]:
                        self.addToStatesUpdateList(str(dev.id),"status",			devI["status"])
                        anyUpdate=True

                if "nickName" in statesToUpdate or statesToUpdate[0]=="all":
                    if dev.states["nickName"] !=devI["nickName"]:
                        self.addToStatesUpdateList(str(dev.id),"nickName",			devI["nickName"])
                        anyUpdate=True
                if "noOfChanges" in statesToUpdate or statesToUpdate[0]=="all":
                    if unicode(dev.states["noOfChanges"]) != unicode(devI["noOfChanges"]):
                        self.addToStatesUpdateList(str(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
                        anyUpdate=True
                if "hardwareVendor" in statesToUpdate or statesToUpdate[0]=="all":
                    if dev.states["hardwareVendor"] !=devI["hardwareVendor"]:
                        self.addToStatesUpdateList(str(dev.id),"hardwareVendor",	devI["hardwareVendor"])
                        anyUpdate=True
                if "deviceInfo" in statesToUpdate or statesToUpdate[0]=="all":
                    if dev.states["deviceInfo"] !=devI["deviceInfo"]:
                        self.addToStatesUpdateList(str(dev.id),"deviceInfo",		devI["deviceInfo"])
                        anyUpdate=True
                if "WiFi" in statesToUpdate or statesToUpdate[0]=="all":
                    if dev.states["WiFi"] !=devI["WiFi"]:
                        self.addToStatesUpdateList(str(dev.id),"WiFi",				devI["WiFi"])
                        if theMAC in self.wifiMacList:
                            self.addToStatesUpdateList(str(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])
                        anyUpdate=True

                usePing = devI["usePing"]
                if  str(devI["useWakeOnLanSecs"]) !="0":
                    usePing +="-WOL:"+str(devI["useWakeOnLanSecs"])
                if "usePing-WOL" in statesToUpdate or statesToUpdate[0]=="all":
                    if "usePing-WOL" in dev.states:
                        if dev.states["usePing-WOL"] != usePing:
                            anyUpdate=True
                            self.addToStatesUpdateList(str(dev.id),"usePing-WOL",			usePing)
                if "suppressChangeMSG" in statesToUpdate or statesToUpdate[0]=="all":
                    if "suppressChangeMSG" in dev.states:
                        if dev.states["suppressChangeMSG"] !=devI["suppressChangeMSG"]:
                            anyUpdate=True
                            self.addToStatesUpdateList(str(dev.id),"suppressChangeMSG",			devI["suppressChangeMSG"])

                if anyUpdate:
    #				self.myLog("all",u"state updates needed")
                    self.addToStatesUpdateList(str(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
    #			else:
    #				self.myLog("all",u"state updates NOT  needed")

                if statesToUpdate[0]=="all" or "status" in statesToUpdate or "ipNumber" in statesToUpdate or "WiFi" in statesToUpdate:
                    pad = self.padStatusForDevListing(devI["status"])
                    if (devI["status"]).ljust(pad)+devI["timeOfLastChange"] !=dev.states["statusDisplay"]:
                        self.addToStatesUpdateList(str(dev.id),"statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
                    props = dev.pluginProps
                    try:
                        if props["address"] != self.formatiPforAddress(devI["ipNumber"]):
                            if "suppressChangeMSG" in dev.states:
                                if dev.states["suppressChangeMSG"] =="show":
                                    self.myLog("all",u"MAC#:"+theMAC  +" -- old IP: "+ str(props["address"])+ ";  new IP number: "+ str(self.formatiPforAddress(devI["ipNumber"]))+" to switch off changed message: edit this device and select no msg")
                            props["address"]=self.formatiPforAddress(devI["ipNumber"])
                            dev.replacePluginPropsOnServer(props)
                    except:
                        self.myLog("Ping",u"props check did not work")

                devI["deviceId"]		=dev.id
                devI["deviceName"]		=dev.name
                devI["devExists"]		=1


                self.executeUpdateStatesList()


                if theMAC in self.wifiMacList or "WiFi" in statesToUpdate:
                    self.updateDeviceWiFiSignal()
                    if devI["WiFi"] =="":
                        dev.description = theMAC
                    else:
                        dev.description = theMAC+"-"+devI["WiFi"]+"-"+devI["WiFiSignal"]
                    dev.replaceOnServer()


        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return
##############################################
    def deleteIndigoIpDevicesData(self,theMACin):  # do this once in the beginning..
        try:
            theList=[]
            if theMACin =="all":
                for theMAC in self.allDeviceInfo:
                    theList.append(theMAC)
            else:
                theList.append(theMACin)

    #		self.myLog("Logic",u" list of devices to be deleted: %s"%theList)

            for theMAC in theList:
                try:
                    devI=self.allDeviceInfo[theMAC]
                    devID =devI["deviceId"]
    #				self.myLog("Logic",u"deleting device information for theMAC/deviceName "+ theMAC+"/"+str(self.allDeviceInfo[theMAC]["deviceName"]))
                    indigo.device.delete(devID)
                except:
                    self.myLog("Ping",u"deleteIndigoIpDevicesData: theMAC/deviceID/deviceName"+ theMAC+"/"+str(devID)+"/"+str(self.allDeviceInfo[theMAC]["deviceName"])+" device does not exist")
                
                try:
                    devV=self.indigoIpVariableData[theMAC]
                    indigo.variable.delete("ipDevice"+devV["ipDevice"])
                except:
                    self.myLog("Ping",u"deleteIndigoIpDevicesData: theMAC "+ theMAC+ " information does not exist in indigoIpVariableData")


                try:
                    theName= devI["deviceName"]
                    del self.allDeviceInfo[theMAC]
                except:
                    self.myLog("Ping",u"deleteIndigoIpDevicesData: name/MAC "+ theName+"/"+theMAC+" information does not exist in allDeviceInfo")

    #			self.myLog("Logic",u"deleted device MAC: "+theMAC)

            self.getIndigoIpVariablesIntoData()
        except Exception, e:
            self.myLog("all",u"error in  Line '%s' ;  error='%s'" % (sys.exc_traceback.tb_lineno, e))
        return

##############################################
    def getIndigoIpDevicesIntoData(self):  # do this once in the beginning..
    
        try:
            theMAC=""
            for dev in indigo.devices.iter("com.karlwachs.fingscan"):
                if not dev.enabled: continue
                theStates = dev.states.keys()
                if "MACNumber" in theStates:
                    theMAC = dev.states["MACNumber"]
                    if theMAC =="": continue
                    update =0
                    if not theMAC in self.allDeviceInfo:
                        self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
                        update=5
                    devI=self.allDeviceInfo[theMAC]
                    props = dev.pluginProps
                    if dev.name != devI["deviceName"]:
                        update = 1
                        devI["nickName"] 	= dev.name
                        devI["deviceName"]	= dev.name
                        #dev.updateStateOnServer("nickName",	devI["nickName"])
                        self.addToStatesUpdateList(str(dev.id),"nickName",	devI["nickName"])
                    if dev.states["hardwareVendor"] != devI["hardwareVendor"]:
                        devI["hardwareVendor"]		= dev.states["hardwareVendor"]
                        update = 2
                    if dev.states["deviceInfo"] != devI["deviceInfo"]:
                        devI["deviceInfo"]		= dev.states["deviceInfo"]
                        update = 3
                    devI["ipNumber"]			= dev.states["ipNumber"]
                    devI["timeOfLastChange"]	= dev.states["timeOfLastChange"]
                    devI["status"]				= dev.states["status"]
                    devI["nickName"]			= dev.states["nickName"]
                    devI["noOfChanges"]			= int(dev.states["noOfChanges"])
                    devI["hardwareVendor"]		= dev.states["hardwareVendor"]
                    devI["deviceInfo"]			= dev.states["deviceInfo"]
                    try:    devI["lastFingUp"]	= time.mktime( datetime.datetime.strptime(dev.states["lastFingUp"],"%Y-%m-%d %H:%M:%S").timetuple()  )
                    except: devI["lastFingUp"]	= time.time()
                    if "setWiFi" not in devI:   devI["setWiFi"] =copy.deepcopy(emptyAllDeviceInfo["setWiFi"])
                    devI["WiFi"]				= dev.states["WiFi"]
                    devI["deviceId"]			= dev.id
                    devI["deviceName"]			= dev.name
                    devI["devExists"]			= 1

                    if "setUsePing"      in props: 
                        devI["usePing"]           = props["setUsePing"]
                    else:
                        devI["usePing"]           = "doNotUsePing"

                    if "setuseWakeOnLan" in props: 
                        devI["useWakeOnLanSecs"]  = int(props["setuseWakeOnLan"])
                    else:
                        devI["useWakeOnLanSecs"]  = 0

                    if "setExpirationTime" in props: 
                        devI["expirationTime"]  = float(props["setExpirationTime"])
                    else:
                        devI["expirationTime"]  = 0


                    if "suppressChangeMSG" in dev.states:
                        devI["suppressChangeMSG"]			=dev.states["suppressChangeMSG"]
                    else:
                        devI["suppressChangeMSG"]			="show"
                if update>0:
    #				self.myLog("Logic",u" updating MAC: "+theMAC)
                    self.updateIndigoIpVariableFromDeviceData(theMAC)
                self.executeUpdateStatesList()    

        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.myLog("all",u"MAC#                           "+ theMAC)
            try:
                self.myLog("all",u" indigoIpVariableData:     "+unicode(self.indigoIpVariableData[theMAC]))
            except:
                self.myLog("all",u" indigoIpVariableData: all "+unicode(self.indigoIpVariableData))
            try:
                self.myLog("all",u" allDeviceInfo:            "+ unicode(self.allDeviceInfo[theMAC]))
            except:
                self.myLog("all",u" allDeviceInfo:  all       "+ unicode(self.allDeviceInfo))
        return
########################################
    def updateAllIndigoIpVariableFromDeviceData(self):
        for theMAC in self.allDeviceInfo:
            self.updateIndigoIpVariableFromDeviceData(theMAC)

########################################
    def updateIndigoIpVariableFromDeviceData(self,theMAC):
        try:
            if theMAC in self.ignoredMAC: return 
            if theMAC in self.indigoIpVariableData:
                devV =self.indigoIpVariableData[theMAC]
            else:
                self.indigoIpVariableData[theMAC] = copy.deepcopy(emptyindigoIpVariableData)
                devV =self.indigoIpVariableData[theMAC]
                try:
                    devV["ipDevice"] = str(self.indigoEmpty[0])
                except:
                    self.myLog("all", u"updateIndigoIpVariableFromDeviceData indigoEmpty not initialized" +str(self.indigoEmpty))
                    self.myLog("all", u"updateIndigoIpVariableFromDeviceData theMAC# " +unicode(theMAC))
                    self.myLog("all", u"updateIndigoIpVariableFromDeviceData indigoIpVariableData" +unicode(self.indigoIpVariableData[theMAC]))
                    devV["ipDevice"] = "1"
                self.indigoNumberOfdevices +=1
                devV["index"] = self.indigoNumberOfdevices-1
                self.indigoIndexEmpty -= 1  # one less empty slot
                self.indigoEmpty.pop(0) ##  remove first empty from list


            devI=self.allDeviceInfo[theMAC]
            updstr  =self.padMAC(theMAC)
            updstr +=";"+self.padIP(devI["ipNumber"])
            updstr +=";"+self.padDateTime(devI["timeOfLastChange"])
            updstr +=";"+devI["status"]
            updstr +=";"+self.padStatus(devI["status"])+self.padNoOfCh(devI["noOfChanges"])
            updstr +=";"+self.padNickName(devI["nickName"])
            updstr +=";"+self.padVendor(devI["hardwareVendor"])
            updstr +=";"+self.padDeviceInfo(devI["deviceInfo"])
            updstr +=";"+devI["WiFi"].rjust(5)
            updstr +=";"+devI["WiFiSignal"].rjust(10)
            updstr +=";"+(devI["usePing"]+"-"+str(devI["useWakeOnLanSecs"])).rjust(13)+";"
            theValue = updstr.split(";")

            devV["ipNumber"]			=theValue[1].strip()
            devV["timeOfLastChange"]	=theValue[2].strip()
            devV["status"]				=theValue[3].strip()
            try:
                devV["noOfChanges"]		=int(theValue[4].strip())
            except:
                devV["noOfChanges"]		=0
            devV["nickName"]			=theValue[5].strip()
            devV["hardwareVendor"]		=theValue[6].strip()
            devV["deviceInfo"]			=theValue[7].strip()
            devV["WiFi"]				=theValue[8].strip()
            devV["usePing"]				=theValue[9].strip()


            diff = False
            try:
                curr = indigo.variables["ipDevice"+devV["ipDevice"]].value.split(";")
            except:
                self.myLog("all",u" updating ipDevice "+devV["ipDevice"]+" does not exist , (re)creating")
                
                curr =[]
            
            old = updstr.split(";")
            if len(old) ==len(curr):
                for i in range(len(curr)):
                    if i==2: continue# skip the date field.
                    if curr[i] != old[i]:
    #					self.myLog("all",u" updating ipDevice "+devV["ipDevice"]+"  "+curr[i]+"!="+old[i])
                        diff= True
                        break
            else:
                diff=True
            if diff:
                try:
                    indigo.variable.updateValue("ipDevice"+devV["ipDevice"], updstr)
                except:
                    indigo.variable.create("ipDevice"+devV["ipDevice"], updstr,self.indigoVariablesFolderID)
    #		else:
    #			self.myLog("all",u"not updating ipDevice"+devV["ipDevice"])

        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.myLog("all",u"MAC#                           "+ theMAC)
            try:
                self.myLog("all",u" indigoIpVariableData:     "+unicode(self.indigoIpVariableData[theMAC]))
            except:
                self.myLog("all",u" indigoIpVariableData: all "+unicode(self.indigoIpVariableData))
            try:
                self.myLog("all",u" allDeviceInfo:            "+ unicode(self.allDeviceInfo[theMAC]))
            except:
                self.myLog("all",u" allDeviceInfo:  all       "+ unicode(self.allDeviceInfo))


        return 0






########################################
    def updateallDeviceInfofromVariable(self):


        try:
            for theMAC in self.indigoIpVariableData:
                devV =self.indigoIpVariableData[theMAC]
                if not theMAC in self.allDeviceInfo:
                    self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
                devI=self.allDeviceInfo[theMAC]
                devI["ipNumber"]			=devV["ipNumber"].strip()
                devI["timeOfLastChange"]	=devV["timeOfLastChange"].strip()
                devI["status"]				=devV["status"].strip()
                try:
                    devI["noOfChanges"]		=int(devV["noOfChanges"])
                except:
                    devI["noOfChanges"]		=0
                devI["nickName"]			=devV["nickName"].strip()
                devI["hardwareVendor"]		=devV["hardwareVendor"].strip()
                devI["deviceInfo"]			=devV["deviceInfo"].strip()
                if "WiFi" not in devV:
                    devI["WiFi"]			=""
                else:
                    devI["WiFi"]			=devV["WiFi"].strip()
                    
                devI["usePing"]			="usePing"
                devI["usePing"]		    = ""
                devI["useWakeOnLanSecs"]	= 0
                if "usePing"  in devV:
                    usePing = (devV["usePing"].strip()).split("-")
                    devI["usePing"]			 = usePing[0]
                    if len(usePing) == 2:
                        devI["useWakeOnLanSecs"] = int(usePing[1])
                        
                if "deviceId" not in devI: 		devI["deviceId"]=""
                if "deviceName" not in devI: 	devI["deviceName"]=""

        except  Exception, e:
            self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.myLog("all",u"MAC# "+ theMAC+" indigoIpVariableData: "+unicode(self.indigoIpVariableData[theMAC]))
            self.myLog("all",u"MAC# "+ theMAC+" allDeviceInfo:        "+ unicode(self.allDeviceInfo[theMAC]))

        return 0



    ####################  utilities -- start  #######################

########################################
    def padStatusForDevListing(self,status):
        if	 status == "up": 		return 11
        elif status == "expired":	return 8
        elif status == "down":		return 9
        elif status == "changed":	return 8
        elif status == "double":	return 8
        else: 						return 10
########################################
    def column(self,matrix, i):
        return [row[i] for row in matrix]
    
########################################
    def padDateTime(self,xxx):
        return "   "+xxx+"   "
    
########################################
    def padVendor(self,ddd):
        ddd= ddd.replace("\n","")
        theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
        blanks = " "
        for kk in range(1,theNumberOfBlanks):
            blanks += " "
        return "  "+ddd+blanks
    
########################################
    def padDeviceInfo(self,ddd):
        ddd= ddd.replace("\n","")
        theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
        blanks = " "
        for kk in range(1,theNumberOfBlanks):
            blanks += " "
        return "  "+ddd+blanks
    
########################################
    def padIP(self,xxx):
        ddd =len(xxx)
        pad = "   "
        if ddd == 11:	pad = "       "
        if ddd == 12:	pad = "     "
        return "   "+xxx+pad
    
########################################
    def padNickName(self,ddd):
        theNumberOfBlanks =min(32,max(0,(17-len(ddd))*2))
        blanks = "   "
        for kk in range(1,theNumberOfBlanks):
            blanks += " "
        return "   "+ddd+blanks
    
########################################
    def padNoOfCh(self,xxx):
        xxx=int(xxx)
        if xxx < 10       : return "    "+str(xxx)+"               "
        if xxx < 100      : return "    "+str(xxx)+"             "
        if xxx < 1000     : return "    "+str(xxx)+"           "
        if xxx < 10000    : return "    "+str(xxx)+"         "
        return "    "+str(xxx)+"       "
    
    
########################################
    def padStatus(self,xxx):
        if xxx == "up"     : return "       "
        if xxx == "down"   : return "   "
        if xxx == "expired": return ""
        if xxx == "changed": return ""
        if xxx == "double" : return " "
        return " "
    
########################################
    def padMAC(self,xxx):
        yyy =str(xxx)
        NofA = yyy.count("A")
        NofB = yyy.count("B")
        NofC = yyy.count("C")
        NofD = yyy.count("D")
        NofE = yyy.count("E")
        NofF = yyy.count("F")
        NofN = 12 - NofA - NofB - NofC - NofD - NofE - NofF
        Ascal = 9
        Bscal = 7.5
        Cscal = 9
        Dscal = 9.9
        Escal = 6.9
        Fscal = 6.9
        Nscal = 8.0
        theScale = NofA * Ascal + NofB * Bscal + NofC * Cscal + NofD * Dscal + NofE * Escal + NofF * Fscal + NofN * Nscal
        ##12*ee --> 12*dd = 12 blanks  difference --> 78 --> 120:  44/12 = 3.5
        theNumberOfBlanks = int(((115 - theScale) / 3.5))
        theNumberOfBlanks =min(10,max(0,theNumberOfBlanks))
        
        blanks = "    "
        for kk in range(1,theNumberOfBlanks):
            blanks += " "
        return yyy+blanks
##############################################
    def formatiPforAddress(self,ipN):
        ips = ipN.split(".")
        digit = ips[3].split("-")[0]
        if   int(digit) < 10:	last = "00"
        elif int(digit) < 100:	last = "0"
        else: last =""
        ips[3] = last+digit
        if "changed" in ipN:
            ips[3]+="-changed"
        elif "double" in ipN:
            ips[3]+="-double"
        else:
            ips[3]+="        "
        return ".".join(ips)
    ####################  utilities -- end #######################
    def checkTimeZone (self,InfoTimeStamp):
        InfoTimeStampSecs=  float(int(time.mktime(InfoTimeStamp)))
        deltaSecs = InfoTimeStampSecs- time.time()
        hours = int(deltaSecs/3600.)
        if deltaSecs > 100: # time zone left of us, should be ~ same, can't be positive  +100==> other timezone, if delayed by > 3500 secs its wrong
            InfoTimeStampSecs -= hours*3600
        elif deltaSecs < -3500: # timezone right of us min delay for one hour timezone diff: = 0 secs = -1 hour, so if its delayed by 3500 secs its wrong
            InfoTimeStampSecs += hours*3600
        return InfoTimeStampSecs


    ####-----------------  check logfile sizes ---------
    def checkLogFiles(self):
        try:
            fn = self.logFile.split(".log")[0]
            if os.path.isfile(fn + ".log"):
                fs = os.path.getsize(fn + ".log")
                self.myLog("Logic", "checking logfile size ...")
                if fs > 30000000:  # 30 Mbyte
                    self.myLog("Logic", "     ... reset logfile due to size")
                    if os.path.isfile(fn + "-1.log"):
                        os.remove(fn + "-1.log")
                    os.rename(fn + ".log", fn + "-1.log")
                else:
                    self.myLog("Logic", "     ...  size ok")

        except  Exception, e:
            if len(unicode(e)) > 5:
                indigo.server.log( u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e))

     ####----------------- logfile  ---------
    def myLog(self, msgLevel, text, type=""):
        if msgLevel == "": return

        try:
            if not self.logFileActive :
                    if msgLevel == "smallErr":
                        indigo.server.log(u"--------------------------------------------------------------")
                        indigo.server.log(text)
                        indigo.server.log(u"--------------------------------------------------------------")
                        return

                    if msgLevel == "bigErr":
                        self.errorLog(u"----------------------------------------------------------------------------------")
                        self.errorLog(text)
                        self.errorLog(u"----------------------------------------------------------------------------------")
                        return

                    if msgLevel == "all":
                        if type == "":
                            indigo.server.log(text)
                        else:
                            indigo.server.log(text, type=type)
                        return

                    if self.debugLevel == "all":
                        if type == "":
                            indigo.server.log(text)
                        else:
                            indigo.server.log(text, type=type)
                        return


                    if self.debugLevel.find(msgLevel) >-1:
                        if type == "":
                            indigo.server.log(text)
                        else:
                            indigo.server.log(text, type=type)
                        return

                    return


            else:

                try:
                    f =  open(self.logFile,"a")
                except  Exception, e:
                    indigo.server.log(u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e))
                    try:
                        f.close()
                    except:
                        pass
                    return
                if msgLevel == "smallErr":
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    f.write(u"--------------------------------------------------------------\n")
                    f.write((ts+u" ".ljust(12)+u"-"+text+u"\n").encode("utf8"))
                    f.write(u"--------------------------------------------------------------\n")
                    f.close()
                    return

                if msgLevel == "bigErr":
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    f.write(u"==================================================================================\n")
                    f.write((ts+u" "+u" ".ljust(12)+u"-"+text+u"\n").encode("utf8"))
                    f.write(u"==================================================================================\n")
                    f.close()
                    return

                if  msgLevel == "all":
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    if type == u"":
                        f.write((ts+u" "+u" ".ljust(12)+u"-" + text + u"\n").encode("utf8"))
                    else:
                        f.write((ts+" "+type.ljust(12) +u"-" + text + u"\n").encode("utf8"))
                    f.close()
                    return

                if self.debugLevel == "all":
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    if type == "":
                        f.write((ts+u" "+u" ".ljust(12)+u"-" + text + u"\n").encode("utf8"))
                    else:
                        f.write((ts+u" "+type.ljust(12)+u"-" + text + u"\n").encode("utf8"))
                    f.close()
                    return

                if  self.debugLevel.find(msgLevel) >-1:
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    if type == u"":
                        f.write((ts+u" "+u" ".ljust(12)  +u"-" + text + u"\n").encode("utf8"))
                    else:
                        f.write((ts+u" "+type.ljust(12) + u"-" + text + u"\n").encode("utf8"))
                    f.close()
                    return

                f.close()
                return

        except  Exception, e:
            if len(unicode(e)) > 5:
                indigo.server.log(u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e))
                indigo.server.log(str(msgLevel)+"  "+text)


####----------------- get path to indigo programs ---------
    def getIndigoPath(self):
        return
        found=False
        indigoVersion = 0
        for indi in range(5,100):  # we are optimistic for the future of indigo, starting with V5
            if found:
                if os.path.isdir("/Library/Application Support/Perceptive Automation/Indigo "+str(indi)): continue
                else:
                    indigoVersion = indi-1
                    break
            else:
                if os.path.isdir("/Library/Application Support/Perceptive Automation/Indigo "+str(indi)): found = True

        self.indigoPath	=	"/Library/Application Support/Perceptive Automation/Indigo "+str(indigoVersion)+"/"

    def addToStatesUpdateList(self,devId,key,value):
        try:

            if devId in self.updateStatesList: 
                if key in self.updateStatesList[devId]:
                    if value != self.updateStatesList[devId][key]:
                        self.updateStatesList[devId][key]=value
                    return
            else:  self.updateStatesList[devId]={}      
            self.updateStatesList[devId][key] = value

        except  Exception, e:
            if len(unicode(e))  > 5 :
                self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
            self.updateStatesList={}

    def executeUpdateStatesList(self,newStates=""):
        try:
            if len(self.updateStatesList) ==0: return
            for devId in self.updateStatesList:
                if len(self.updateStatesList[devId]) > 0:
                    dev =indigo.devices[int(devId)]
                    actualChanged = []
                    for key in self.updateStatesList[devId]:
                        value = self.updateStatesList[devId][key]
                            
                        if  newStates == "":
                            if value != dev.states[key]:
                                actualChanged.append({"key":key,"value":value})
                        else:            
                            if value != newStates[key]:
                                newStates[key] = value
                        if key == "status":
                            if value in [u"up","ON"] :
                                dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
                            elif value in [u"down",u"off"]:
                                dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
                            elif value in [u"expired","REC"] :
                                dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)

                    if  newStates == "":
                        self.updateStatesList[devId]={}           
                        if actualChanged !=[]:
                            #indigo.server.log("%14.3f"%time.time()+"  "+dev.name.ljust(25)  + unicode(actualChanged)) 
                            dev.updateStatesOnServer(actualChanged)
            if  newStates != "":  
                return newStates              
        except  Exception, e:
            if len(unicode(e))  > 5 :
                self.myLog("all", u"in Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e) )
