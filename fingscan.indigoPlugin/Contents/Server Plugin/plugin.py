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
import traceback
import platform
import MAC2Vendor
from checkIndigoPluginName import checkIndigoPluginName 

try:
	import json
except:
	import simplejson as json


import copy
import math
import shutil
import cProfile
import pstats
import logging

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
	"nickName": "",
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
	"udeviceInfo": "",
	"variableName": "",
	"ipDevice": "00",
	"index": 0,
	"WiFi": "",
	"WiFiSignal": "0",
	"usePing": "",
	"suppressChangeMSG": "show"
	}
emptyEVENT ={#              -including Idevices option-------------                                                                                                                                            ----------  ------------pi beacons---------------------                   --------------  unifi ---------------------
	"IPdeviceMACnumber"    :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"timeOfLastON"         :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"timeOfLastOFF"        :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"secondsOfLastON"      :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"secondsOfLastOFF"    :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"currentStatusHome"   :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"currentStatusAway"   :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"iDeviceUseForHome"   :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"iDeviceUseForAway"   :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"iDeviceAwayDistance" :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"iDeviceHomeDistance" :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"iDeviceName"         :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"iDistance"           :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"iSpeed"              :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"iUpdateSecs"         :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"iDistanceLast"       :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"iSpeedLast"          :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"iUpdateSecsLast"     :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"itimeNextUpdate"	   :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"iMaxSpeed"	       :{"{}".format(i):1.0 for i in range(1,nOfDevicesInEvent)},
	"iFindMethod"         :{"{}".format(i):""  for i in range(1,nOfDevicesInEvent)},
	"nextTimeToCheck"	   :{"{}".format(i):1.0 for i in range(1,nOfDevicesInEvent)},
	"oneAway": "0",
	 "allAway": "0",
	 "nAway": 0,
	 "allHome": "0",
	 "oneHome": "0",
	 "nHome": 0,
	 "distanceAwayLimit": 66666.,
	 "distanceHomeLimit": -1,
	 "minimumTimeAway": 300,
	 "minimumTimeHome": 0,
	 "enableDisable": "0",
	 "dataFormat": "3.0",
	 "maxLastTimeUpdatedDistanceMinutes": 900
	}
emptyWiFiMacList=["x", "x","", "x", "x","","","","","","",""]
indigoMaxDevices = 1024
emptyWifiMacAv={"sumSignal":{"2GHz":0., "5GHz":0.}, "numberOfDevices":{"2GHz":0., "5GHz":0.}, "curAvSignal":{"2GHz":0., "5GHz":0.}, "curDev":{"2GHz":0., "5GHz":0.}, "numberOfCycles":{"2GHz":0., "5GHz":0.}, "noiseLevel":{"2GHz": "0", "5GHz": "0"}}
_debAreas = ["Logic", "Ping", "Wifi", "Events", "piBeacon", "Unifi", "BC", "Special", "StartFi", "all"]

kDefaultPluginPrefs = {
				"network":					"192.168.1.0",
				"netwType":					"24",
				"ipDevices":				"",
				"acceptNewDevices":			"1",
				"enablepiBeaconDevices":	"0",
				"enablepiUnifiDevices":		"0",
				"enableBroadCastEvents":	"0",
				"routerType":				"0",
				"routerIPn":				"0",
				"routerUID":				"0",
				"routerType":				"0",
				"minWiFiSignal":			"0",
				"minSignalDrop":			"0",
				"minNumberOfDevicesBad":	"0",
				"password":					"your router password here",
				"sleepTime":				"1",
				"inbetweenPingType":		"1",
				"sleepTime":				"1",
				"debugLogic":				False,
				"debugPing":				False,
				"debugWifi":				False,
				"debugEvents":				False,
				"debugpiBeacon":			False,
				"debugUnifi":				False,
				"debugBC":					False,
				"debugStartFi":				False,
				"debugSpecial":				False,
				"debugall":					False,
				"do_cProfile":				"on/off/print"
				}


################################################################################
class Plugin(indigo.PluginBase):

####-----------------             ---------
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		
		self.pluginShortName 			= "fing"

 
###############  common for all plugins ############
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split("Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split("."))
		self.indigoVersion 				= float(major)+float(minor)/10.
		self.indigoRelease 				= release

		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= "init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser("~")
		self.userIndigoDir				= self.MAChome + "/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+"Preferences/Plugins/"+self.pluginId+"/"
		self.indigoPluginDirOld			= self.userIndigoDir + self.pluginShortName+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +"/plugin.log"

		formats=	{   logging.THREADDEBUG: "%(asctime)s %(msg)s",
						logging.DEBUG:       "%(asctime)s %(msg)s",
						logging.INFO:        "%(asctime)s %(msg)s",
						logging.WARNING:     "%(asctime)s %(msg)s",
						logging.ERROR:       "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:    "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: "%Y-%m-%d %H:%M:%S",		# 5
						logging.DEBUG:       "%Y-%m-%d %H:%M:%S",		# 10
						logging.INFO:        "%Y-%m-%d %H:%M:%S",		# 20
						logging.WARNING:     "%Y-%m-%d %H:%M:%S",		# 30
						logging.ERROR:       "%Y-%m-%d %H:%M:%S",		# 40
						logging.CRITICAL:    "%Y-%m-%d %H:%M:%S" }		# 50
		formatter = LevelFormatter(fmt= "%(msg)s", datefmt= "%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger("Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.INFO)

		self.indiLOG.log(20, "initializing  ... ")
		self.indiLOG.log(20, "path To files:          =================")
		self.indiLOG.log(10, "indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(10, "installFolder           {}".format(self.indigoPath))
		self.indiLOG.log(10, "plugin.py               {}".format(self.pathToPlugin))
		self.indiLOG.log(10, "indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(20, "detailed logging        {}".format(self.PluginLogFile))
		self.indiLOG.log(20, "testing logging levels, for info only: ")
		self.indiLOG.log( 0, "logger  enabled for     0 ==> TEST ONLY ")
		self.indiLOG.log( 5, "logger  enabled for     THREADDEBUG    ==> TEST ONLY ")
		self.indiLOG.log(10, "logger  enabled for     DEBUG          ==> TEST ONLY ")
		self.indiLOG.log(20, "logger  enabled for     INFO           ==> TEST ONLY ")
		self.indiLOG.log(30, "logger  enabled for     WARNING        ==> TEST ONLY ")
		self.indiLOG.log(40, "logger  enabled for     ERROR          ==> TEST ONLY ")
		self.indiLOG.log(50, "logger  enabled for     CRITICAL       ==> TEST ONLY ")
		self.indiLOG.log(10, "Plugin short Name       {}".format(self.pluginShortName))
		self.indiLOG.log(10, "my PID                  {}".format(self.myPID))	 
		self.indiLOG.log(10, "Achitecture             {}".format(platform.platform()))	 
		self.indiLOG.log(10, "OS                      {}".format(platform.mac_ver()[0]))	 
		self.indiLOG.log(10, "indigo V                {}".format(indigo.server.version))	 
		self.indiLOG.log(10, "python V                {}.{}.{}".format(sys.version_info[0], sys.version_info[1] , sys.version_info[2]))	 

		self.pythonPath = ""
		if sys.version_info[0] >2:
			if os.path.isfile("/Library/Frameworks/Python.framework/Versions/Current/bin/python3"):
				self.pythonPath				= "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
		if self.pythonPath == "":
				self.indiLOG.log(40, "FATAL error:  python versions 3.x is not installed  ==>  stopping {}".format(self.pluginId))
				self.quitNOW = "python 3 not installed"
				exit()
		self.indiLOG.log(20, "using '{}' for utily programs".format(self.pythonPath))
###############  END common for all plugins ############

		return
####-----------------             ---------
	def __del__(self):
		indigo.PluginBase.__del__(self)


###########################     INIT    ## START ########################
	
####----------------- @ startup set global parameters, create directories etc ---------
	def startup(self):

		if not checkIndigoPluginName(self, indigo): 
			exit() 

		try:
			self.checkcProfile()

			self.debugLevel			= []
			for d in _debAreas:
				if self.pluginPrefs.get("debug"+d, False): self.debugLevel.append(d)
			self.indiLOG.log(20, "debug settings :{} ".format(self.debugLevel))

############ directory & file names ...
			self.fingDataFileName0			= "fing.data"
			self.fingLogFileName0			= "fing.log"
			self.fingErrorFileName0			= "fingerror.log"
			self.fingServicesFileName0		= "fingservices.json"
			self.fingServicesLOGFileName0	= "fingservices.log"
			self.fingDataFileName			= self.indigoPreferencesPluginDir+self.fingDataFileName0	
			self.fingLogFileName			= self.indigoPreferencesPluginDir+self.fingLogFileName0 
			self.fingErrorFileName			= self.indigoPreferencesPluginDir+self.fingErrorFileName0 
			self.fingServicesFileName		= self.indigoPreferencesPluginDir+self.fingServicesFileName0 
			self.fingServicesLOGFileName	= self.indigoPreferencesPluginDir+self.fingServicesLOGFileName0
			self.fingServicesOutputFileName	= self.indigoPreferencesPluginDir+"fingservices.txt"
			self.ignoredMACFile				= self.indigoPreferencesPluginDir+"ignoredMAC"
			self.fingPasswordFileName		= self.indigoPreferencesPluginDir+"parameter"
			self.fingSaveFileName			= self.indigoPreferencesPluginDir+"fingsave.data"
			self.fingEXEpath				= "/usr/local/bin/fing"

			if not os.path.isdir(self.indigoPreferencesPluginDir):
				self.indiLOG.log(20, " creating plugin prefs directory:{}".format(self.indigoPreferencesPluginDir))
				os.mkdir(self.indigoPreferencesPluginDir)
			if not os.path.isdir(self.indigoPreferencesPluginDir+"pings"):
				os.mkdir(self.indigoPreferencesPluginDir+"pings")
			if not os.path.isdir(self.indigoPreferencesPluginDir+"mac2Vendor"):
				os.mkdir(self.indigoPreferencesPluginDir+"mac2Vendor")
			if os.path.exists(self.indigoPluginDirOld+"fing.data"):
				indigo.server.log(" moving "+ "cp -R " + self.indigoPluginDirOld+"* '" + self.indigoPreferencesPluginDir+"'" )
				os.system("cp -R " + self.indigoPluginDirOld+"* '" + self.indigoPreferencesPluginDir+"'" )




			self.savePrefs 					= 0
			self.updateStatesList			= {}
			self.updatePrefs				= False
			self.fingDataModTimeOLD			= 0
			self.fingDataModTimeNEW			= 0
			self.fingData					= []
			self.fingIPNumbers				= []
			self.fingMACNumbers				= []
			self.fingDate					= []
			self.fingVendor					= []
			self.fingDeviceInfo				= []
			self.fingNumberOfdevices		= 0
			self.fingLogFileSizeold			= 0
			self.fingLogFileSizeNEW			= 0
			self.doubleIPnumbers			= {}
			self.pingJobs					= {}
			self.inbetweenPing				= {}
			self.excludeMacFromPing			= {}
			self.iDevicesEnabled			= False
			self.ipDevsPasswordMode			= 5
			self.indigoStoredNoOfDevices	= 0
			self.fingDataErrorCount			= 0
			self.fingDataErrorCount2		= 0
			self.finglogerrorCount			= 0
			self.fingRestartCount			= 0
			self.myPID						= "{}".format(os.getpid())
			self.theServices				= []
			self.indigoInitialized			= False
			self.stopConcurrentCounter		= 0
			self.doNOTupdate				= False
			self.piBeaconUpDateNeeded		= False
			self.unifiUpDateNeeded			= False
			self.allDeviceInfo				= {}
			self.wifiMacList				= {}
			self.oldwifiMacList				= {}
			self.wifiMacAv					= copy.deepcopy(emptyWifiMacAv)
			self.triggerList				= []
			self.EVENTS						= {}
			self.indigoVariablesFolderID	= 0
			self.passwordOK					= "no"
			self.yourPassword				= ""
			self.quitNOW					= "no"
			self.WiFiChanged 				= {}
			self.wifiErrCounter				= 0
			self.callingPluginName			= []
			self.callingPluginCommand		= []
			self.triggerFromPlugin			= False

			self.executionMode				= "noInterruption"  ## interrupted by plugin/fingscan/configuration
			self.signalDelta				= {"5":{"2GHz":0,"5GHz":0},"2":{"2GHz":0,"5GHz":0},"1":{"2GHz":0,"5GHz":0}}
			self.theNetwork					= "0.0.0.0"

		except Exception:
			self.logger.error("", exc_info=True)


		self.startTime = time.time()


		return


####----------------- @ startup set global parameters, ---------
	def initConfig(self):

		try:

############ startup message
			 
			indigo.server.log("FINGSCAN--   initializing     will take ~ 2 minutes..")

############ set basic parameters to default before we use them

			try: self.enableBroadCastEvents  = self.pluginPrefs.get("enableBroadCastEvents","0")
			except: self.enableBroadCastEvents = "0"
			self.sendBroadCastEventsList    = []


########### try to setup folders, create directories if they do not exist
			try:
				ret = self.readPopen("mkdir '"+  self.indigoPreferencesPluginDir + "'  > /dev/null 2>&1 &")
				ret = self.readPopen("mkdir '"+  self.indigoPreferencesPluginDir+"pings'" + "  > /dev/null 2>&1 &")
			except:
				pass

			
############ if there are PING jobs left from last run, kill them
			self.killPing("all")
			
			
############ get plugin prefs parameters
			
			self.inbetweenPingType = self.pluginPrefs.get("inbetweenPingType", "0")
			self.sleepTime = int(self.pluginPrefs.get("sleepTime", 1))
			self.newSleepTime = self.sleepTime


############ get & setup WiFi parameters
			self.badWiFiTrigger = {"minSignalDrop":10, "numberOfSecondsBad":0, "minNumberOfDevicesBad":3, "minNumberOfSecondsBad":200, "minWiFiSignal":-90, "trigger":0}
			try:
				self.badWiFiTrigger["minSignalDrop"]			= float(self.pluginPrefs.get("minSignalDrop"		 ,self.badWiFiTrigger["minSignalDrop"]))
				self.badWiFiTrigger["minNumberOfDevicesBad"]	= float(self.pluginPrefs.get("minNumberOfDevicesBad",self.badWiFiTrigger["minNumberOfDevicesBad"]))
				self.badWiFiTrigger["minNumberOfSecondsBad"]	= float(self.pluginPrefs.get("minNumberOfSecondsBad",self.badWiFiTrigger["minNumberOfSecondsBad"]))
				self.badWiFiTrigger["minWiFiSignal"]			= float(self.pluginPrefs.get("minWiFiSignal"		 ,self.badWiFiTrigger["minWiFiSignal"]))
			except:
				self.indiLOG.log(30, "leaving WiFi parameters at default, not configured in 'fingscan/Configure...'")

			self.initIndigoParms()

############ get network info

			try:
				self.netwType   = "{}".format(int(self.pluginPrefs.get("netwType", "24")))
			except:
				self.netwType = "24"
			if "{}".format(self.netwType) ==  "8":
				self.netwType = "24"
			
			self.theNetwork         = self.pluginPrefs.get("network", "192.168.1.0")
			if not self.isValidIP(self.theNetwork):
				self.theNetwork ="192.168.1.0"

			try: 
				aa = self.theNetwork+"/"+self.netwType
				self.netwInfo = self.IPCalculator(self.theNetwork, self.netwType)
			except Exception as e:
				self.logger.error("", exc_info=True)
				self.netwInfo = {'netWorkId': '192.168.1.0', 'broadcast': '192.168.1.255', 'netMask': '255.255.255.0', 'maxHosts': 254, 'hostRange': '192.168.1.1 - 192.168.1.254'}
			self.indiLOG.log(20, "network info: {}, netwType:{}".format(self.netwInfo, self.netwType))
			self.broadcastIP = self.netwInfo["broadcast"]

			self.pluginPrefs["network"]  	= self.theNetwork
			self.pluginPrefs["netwType"] 	= self.netwType


			self.acceptNewDevices = self.pluginPrefs.get("acceptNewDevices", "0") == "1"
			self.getIgnoredMAC()

############ get password
			self.passwordOK = "0"
			self.indiLOG.log(20, "getting password")
			test = self.getPWD("fingscanpy")
			if self.pluginPrefs.get("passwordMethod", "keyChain") == "prefs":
				self.yourPassword = self.pluginPrefs.get("password", "")
				if self.yourPassword == "":
					self.indiLOG.log(40, "password error please enter password in configuration menu, otherwise FING can not be started ")
					self.sleep(20)
					self.quitNOW = "wait noPassword"
				else:
					self.passwordOK = "2"
			else:
				if test == "0":  # no password stored in keychain, check config file
					self.yourPassword = self.pluginPrefs.get("password", "yourPassword")

					if True:												self.passwordOK = "1"  # a password has been entered before
					if self.yourPassword == "yourPassword": 				self.passwordOK = "0"  # nothing changed from the beginning
					if self.yourPassword == "password is already stored":	self.passwordOK = "2"  ## password was entered and was stored into keychain

				
					if self.passwordOK == "1":
						self.storePWD(self.yourPassword, "fingscanpy")
						self.pluginPrefs["password"] = "password is already stored"  # set text to everything ok ...
						self.passwordOK = "2"
			
					## wait for password

					if self.passwordOK == "0":
						for ii in range(10):
							self.indiLOG.log(40, "no password entered:  please do plugin/fingscan/configure and enter your password ")
							self.sleep(5)
							if self.passwordOK != "1": break
					## password entered, check if it is NOW in keychain

					test = self.getPWD("fingscanpy")
					if test != "0":	## password is in keychain
						self.pluginPrefs["password"] = "password is already stored"  # set text to everything ok ...
						self.yourPassword = test
						self.passwordOK = "2"
						self.quitNOW = "no"

					else:  ## no password in keychain error exit, stop plugin
						self.passwordOK = "0"
						self.pluginPrefs["password"] = "yourPassword"  # set text enter password
						self.indiLOG.log(40, "password error please enter password in configuration menu, otherwise FING can not be started ")
						self.sleep(20)
						self.quitNOW = "wait noPassword"

				else:  # password is in keychain, done
					self.yourPassword = test
					self.pluginPrefs["password"] = "password is already stored"  # set text to everything ok ...
					self.quitNOW = "no"
					self.passwordOK = "2"
			self.pluginPrefs["password"] = self.yourPassword	
			self.pluginPrefs["passwordMethod"] = "prefs"

			self.indiLOG.log(20, "get password done;  checking if FING is installed ")

############ install FING executables, set rights ... 
			self.setupFingPgm()
	
############ get WIFI router info if available
			self.routerType	= self.pluginPrefs.get("routerType","0")
			self.routerPWD	= ""
			self.routerUID	= ""
			self.routerIPn	= ""
			if self.routerType != "0":
				self.routerUID	= self.pluginPrefs.get("routerUID", "0")
				self.routerIPn	= self.pluginPrefs.get("routerIPn", "0")
				
				test = self.getPWD("fingrt")
				if test != "0":
					self.routerPWD	= test
				else:
					self.routerType = "0"
					self.routerPWD	= ""

				self.checkWIFIinfo()

############ kill old pending PING jobs
			self.killPing("all")

############ here we get stored setup etc
			self.refreshVariables()
			self.getIndigoIpVariablesIntoData()		# indigo variable data to  into self.indigoIpVariableData
			self.updateallDeviceInfofromVariable()	# self.indigoIpVariableData  to self.allDeviceInfo
			self.getIndigoIpDevicesIntoData()       # indigo dev data to self.allDeviceInfo
			self.checkDEVICES()
			self.checkIfDevicesChanged()
			self.updateAllIndigoIpVariableFromDeviceData()
			self.indiLOG.log(20, "loaded indigo data")




############ for triggers:
			self.currentEventN = "0"
			try:
				xxx = ""
				xxx = self.pluginPrefs["EVENTS"]
				self.EVENTS=json.loads(xxx)
			except:
				self.EVENTS = {}
				self.indiLOG.log(30, "empty or bad read of EVENT from prefs file: len(data): {}; \ndata: {} .. {}".format(len(xxx), xxx[0:100],xxx[-100:]) )

			timeNow = time.time()
			self.checkTriggerInitialized =False
		  



############ check if FMID is enabled
			self.IDretList=[]
			self.iFindStuffPlugin = "com.corporatechameleon.iFindplugBeta"
			self.checkIfiFindisEnabled()

############ en/ disable mac to vendor lookup
		
			self.enableMACtoVENDORlookup    = self.pluginPrefs.get("enableMACtoVENDORlookup", "21")
			try: int(self.enableMACtoVENDORlookup)
			except: self.enableMACtoVENDORlookup = "0"
			self.waitForMAC2vendor = False
			if self.enableMACtoVENDORlookup != "0":
				self.M2V = MAC2Vendor.MAP2Vendor(pathToMACFiles=self.indigoPreferencesPluginDir+"mac2Vendor/", refreshFromIeeAfterDays = self.enableMACtoVENDORlookup, myLogger = self.indiLOG.log)
				self.waitForMAC2vendor = self.M2V.makeFinalTable(quiet=True)


############ check for piBeacon plugin devcies
			try:
				self.piBeaconDevices=json.loads(self.pluginPrefs["piBeacon"])
			except:
				self.piBeaconDevices = {}
			self.cleanUppiBeacon()


			self.enablepiBeaconDevices = self.pluginPrefs.get("enablepiBeaconDevices","0")
			self.piBeaconIsAvailable = False
			self.piBeaconDevicesAvailable = []
			self.getpiBeaconAvailable()
			if self.piBeaconIsAvailable:
				self.pluginPrefs["piBeaconEnabled"] = True
				self.updatepiBeacons()
			else:
				self.pluginPrefs["piBeaconEnabled"] = False
############ check for UNIFI plugin devcies
			try:
				self.unifiDevices=json.loads(self.pluginPrefs["UNIFI"])
			except:
				self.unifiDevices = {}
			self.cleanUpUnifi()
			self.enableUnifiDevices = self.pluginPrefs.get("enableUnifiDevices","0")
			self.unifiAvailable = False
			self.unifiDevicesAvailable = []
			self.getUnifiAvailable()
			if self.unifiAvailable:
				self.pluginPrefs["unifiEnabled"] = True
				self.updateUnifi()
			else:
				self.pluginPrefs["unifiEnabled"] = False



############ setup mac / devname /number selection list
			self.IPretList=[]
			for theMAC in self.allDeviceInfo:
				theString = self.allDeviceInfo[theMAC]["deviceName"] +"-" +self.allDeviceInfo[theMAC]["ipNumber"] + "-"+theMAC
				self.IPretList.append(( theMAC,theString ))
			self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
			self.IPretList.append((1, "Not used"))


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
			self.indiLOG.log(20, "Initializing parameters for FING")
			retCode = self.initFing(1)
			if retCode != 1:
				self.indiLOG.log(40, " FING not running... quit")
				self.quitNOW = "FING not running; wait with reboot"
				self.passwordOK = "0"
			else:
				pass

############ print info to indigo logfile
			self.printConfig()
			self.printEvents()
			if self.routerType != "0":
				errorMSG = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, rType=self.routerType)
				if errorMSG != "ok":
					self.indiLOG.log(40, "Router wifi not reachable, userid, password or ipnumber wrong?\n{}".format(errorMSG))
				self.printWiFi()
			self.printpiBeaconDevs()
			self.printUnifiDevs()
			

############ try to find hw vendor 
			self.indiLOG.log(20, "getting vendor info ")
			self.MacToNamesOK = True
			for theMAC in self.allDeviceInfo:
				for item in emptyAllDeviceInfo:
					if item not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC][item] = copy.copy(emptyAllDeviceInfo[item])

				if not self.MacToNamesOK: continue 
				update = 0
				if self.allDeviceInfo[theMAC]["hardwareVendor"].find("\n") >-1: 
					update = 1
					self.allDeviceInfo[theMAC]["hardwareVendor"] = self.allDeviceInfo[theMAC]["hardwareVendor"].strip("\n").strip()
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "{:}  devID:{:>15d} existingVendor >>{:}<<".format(theMAC, self.allDeviceInfo[theMAC]["deviceId"], self.allDeviceInfo[theMAC]["hardwareVendor"]) )
				if self.allDeviceInfo[theMAC]["deviceId"] !=0:             
					if len(self.allDeviceInfo[theMAC]["hardwareVendor"]) < 3 or  (self.allDeviceInfo[theMAC]["hardwareVendor"].find("<html>")) > -1 :
						vend = self.getVendortName(theMAC)
						if vend == None: vend = ""
						if self.decideMyLog("Logic"): self.indiLOG.log(10, "{}  Vendor info  >>{}<<".format(theMAC,vend ) )
						if vend != ""  or self.allDeviceInfo[theMAC]["hardwareVendor"].find("<html>") > -1: 
							update = 2

				if update > 0:
					if update == 1: 
						vend = self.allDeviceInfo[theMAC]["hardwareVendor"].strip("\n")
						if vend == None: vend = ""
					try: 
						self.indiLOG.log(10, " updating :{}  {}  to >>{}<<".format(theMAC, self.allDeviceInfo[theMAC]["deviceId"], vend))
						self.allDeviceInfo[theMAC]["hardwareVendor"]  = vend
						dev = indigo.devices[self.allDeviceInfo[theMAC]["deviceId"]]
						dev.updateStateOnServer("hardwareVendor",vend)
					except Exception as e:
						self.logger.error("", exc_info=True)
						
			self.MacToNamesOK = True
				

		except Exception as e:
				self.logger.error("", exc_info=True)
				self.quitNOW = "restart required; {}".format(e) 
				self.sleep(20)


		return


########################################
	def setupFingPgm(self):
		try:

			#paths for fing executables files to be installed
			if self.passwordOK == "2": 
				try:
					ret, err = self.readPopen("echo '"+self.yourPassword+ "' | sudo -S  /bin/mkdir /usr/local/  ")
					if len(ret) > 1 and ret.find("File exists") ==-1 :
						self.indiLOG.log(20, "mk fing dir:   "+ret.strip("\n"))
						if ret.find("incorrect password") >-1  or ret.find("Sorry, try again") >-1: 
							self.indiLOG.log(30, "please corrrect password in config and reload plugin , skipping fing install")
							self.passwordOK = "0"
							self.sleep(2)
				except:
					pass

				cmd = "cd '"+self.indigoPreferencesPluginDir+"'; echo '"+self.yourPassword+ "' | sudo /usr/sbin/chown "+self.MACuserName+" *"
				os.system(cmd) 
				cmd = "cd '"+self.indigoPreferencesPluginDir+"'; echo '"+self.yourPassword+ "' | sudo /bin/chmod -R 777 *"
				os.system(cmd) 
				if not os.path.isfile(self.fingDataFileName):
					subprocess.Popen( "echo 0 > '"+ self.fingDataFileName+ "' &",shell=True )
					self.sleep(0.2)
					if not os.path.isfile(self.fingDataFileName):
						self.indiLOG.log(40, "could not create file: "+self.fingDataFileName+" stopping program")
						#self.quitNOW = "directory /  file problem"
						#return


			if self.passwordOK == "2": 
				# set proper attributes for catalina 
				ret, err = self.readPopen("echo '"+self.yourPassword+ "' | sudo -S /usr/bin/xattr -rd com.apple.quarantine '"+self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/fing'")

				### set proper attributes for >= catalina OS 
				cmd = "echo '"+self.yourPassword+ "' | sudo -S /usr/bin/xattr -rd com.apple.quarantine '"+self.fingEXEpath+"'"
				ret, err = self.readPopen(cmd)
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "setting attribute for catalina+  with:  {}".format(cmd))
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "setting attribute for catalina+  result:{}".format(ret))
				cmd = "echo '"+self.yourPassword+ "' | sudo -S /usr/bin/xattr -rd com.apple.quarantine  /usr/local/lib/fing/*"
				ret, err = self.readPopen(cmd)
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "setting attribute for catalina+  with:  {}".format(cmd))
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "setting attribute for catalina+  result:{}".format(ret))
				self.indiLOG.log(20, "fing install check done")

				self.opsys, self.fingVersion = self.checkVersion()
				if self.opsys >= 10.15 and self.fingVersion < 5 and self.fingVersion >0 :
					self.indiLOG.log(50, "\nmiss match version of opsys:{} and fing:{} you need to upgrade / install FING to 64 bit version (>=5). Download from\nhttps://www.fing.com/products/development-toolkit  use OSX button"+\
					 "\nor use\nCLI_macOSX_5.4.0.zip\n included in the plugin download to install\nthen delete fing.log and fing.data in the indigo preference directory and reload the plugin".format(self.opsys, self.fingVersion))
					for ii in range(1000):			
						time.sleep(2)
				if self.fingVersion  ==-1 :
					self.indiLOG.log(50, "\nmiss match version of opsys:{} and fing:{} you need to upgrade / imstall FING to 64 bit version (>=5). Download from\nhttps://www.fing.com/products/development-toolkit  use OSX button")
					self.indiLOG.log(50, "or use\nCLI_macOSX_5.4.0.zip\n included in the plugin download to install\nthen delete fing.log and fing.data in the indigo preference directory and reload the plugin".format(self.opsys, self.fingVersion))
					self.indiLOG.log(50, "\n and try:")
					self.indiLOG.log(50, "sudo /usr/bin/xattr -rd com.apple.quarantine  /usr/local/lib/fing/*")
					self.indiLOG.log(50, "sudo /usr/bin/xattr -rd com.apple.quarantine  /usr/local/bin/fing")
					for ii in range(1000):			
						time.sleep(2)
			
		except Exception as e:
			self.logger.error("", exc_info=True)
		return	


########################################
	def checkVersion(self):
		import platform
		try:
			opsys		= platform.mac_ver()[0].split(".")
			opsys		= float(opsys[0]+"."+opsys[1])
			cmd 		= "echo '"+self.yourPassword+ "' | sudo -S "+self.fingEXEpath+" -v"
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "testing versiosn w  {}".format(cmd))
			ret, err = self.readPopen(cmd)
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "testing verions w  {} ==> {} - {}, opsys:{}".format(cmd, ret, err, opsys))
			ret 		= ret.strip("\n").split(".")
			if len(ret) > 1:
				fingVersion	= float(ret[0]+"."+ret[1])
			else:
				self.indiLOG.log(40, "error in get fing version#: seems that either {} in not installed or password>>{}<< not correct,\nreturned text from fing probe:{}:  {}-{}".format(self.fingEXEpath, self.yourPassword, cmd, ret, err))
				fingVersion	= -1.0
			return opsys, fingVersion
		except Exception:
			self.logger.error("", exc_info=True)
		return 0, -1.0			


########################################
	def refreshVariables(self):
		try:    indigo.variable.create("ipDevsLastUpdate", "",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create("ipDevsLastDevChangedIndigoName", "",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create("ipDevsNewDeviceNo", "",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create("ipDevsNewIPNumber", "",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create("ipDevsNoOfDevices", "",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create("ipDevsOldNewIPNumber", "", "")	
		except: pass
		return
		
########################################
	def setupEventVariables(self,init=False):
		try:
			try:
				indigo.variables.folder.create("FINGscanEvents")
				self.indiLOG.log(20, "FINGscanFolder folder created")
			except:
				pass
			self.FINGscanFolderID = indigo.variables.folders["FINGscanEvents"].id
			for i in self.EVENTS:
				try: 	indigo.variable.create("allHome_{}".format(i), "",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create("oneHome_{}".format(i), "",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create("nHome_{}".format(i), "",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create("allAway_{}".format(i), "",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create("oneAway_{}".format(i), "",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create("nAway_{}".format(i), "",folder=self.FINGscanFolderID)
				except:	pass

			
			try:
				indigo.variable.create("FingEventDevChangedIndigoId",folder=self.FINGscanFolderID)
			except: pass



			for nEvent in self.EVENTS:
				evnt = self.EVENTS[nEvent]
				if "oneHome" not in evnt: continue
				xx =  "{}".format(indigo.variables["oneHome_"+nEvent].value)
				if evnt["oneHome"]  !=  xx:                	indigo.variable.updateValue("oneHome_"+nEvent,evnt["oneHome"])
				xx =  "{}".format(indigo.variables["allHome_"+nEvent].value)
				if evnt["allHome"]  !=  xx:               		indigo.variable.updateValue("allHome_"+nEvent,evnt["allHome"])
				xx =  "{}".format(indigo.variables["allHome_"+nEvent].value)
				if evnt["nHome"]  !=  xx:                  	indigo.variable.updateValue("nHome_"+nEvent,"{}".format(evnt["nHome"]))
				xx =  "{}".format(indigo.variables["oneAway_"+nEvent].value)
				if evnt["oneAway"]  !=  xx:                  	indigo.variable.updateValue("oneAway_"+nEvent,evnt["oneAway"])
				xx =  "{}".format(indigo.variables["allAway_"+nEvent].value)
				if evnt["allAway"]  !=  xx:             		indigo.variable.updateValue("allAway_"+nEvent,evnt["allAway"])
				xx =  "{}".format(indigo.variables["nAway_"+nEvent].value)
				if evnt["nAway"]  !=  xx:                    	indigo.variable.updateValue("nAway_"+nEvent,"{}".format(evnt["nAway"]))
		except Exception:
			self.logger.error("", exc_info=True)
		return




########################################
	def sendWakewOnLanAndPing(self, MAC, nBC= 2, waitForPing=500, nPings=1, countPings=1, waitBeforePing = 0.5, waitAfterPing = 0.5, calledFrom=""):
		self.sendWakewOnLan(MAC, calledFrom=calledFrom)
		if nBC == 2:
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
			Wait = "-W {}".format(waitForPing)
		Count = "-c 1"
		if countPings != "":
			Count = "-c {}".format(countPings)
		if nPings == 1:
			waitAfterPing =0.

		retCode = 1
		for nn in range(nPings):            
			retCode = subprocess.call('/sbin/ping -o {} {} -q {} >/dev/null'.format(Wait, Count, ipN),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # "call" will wait until its done and deliver retcode 0 or >0
			if self.decideMyLog("Ping"): self.indiLOG.log(10, "ping resp:{}: {}".format(ipN, retCode) )
			if retCode ==0: return 0
			if nn != nPings-1: self.sleep(waitAfterPing)
		return retCode

########################################
	def sendWakewOnLan(self, MAC, calledFrom=""):
		try:
			data = ''.join(['FF' * 6, MAC.replace(':', '') * 16])
			if self.decideMyLog("Ping"): self.indiLOG.log(10, "sendWakewOnLan for {};  called from {};  bc ip: {}".format(MAC, calledFrom, self.broadcastIP) )
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			if sys.version_info[0] >2:
				sock.sendto(bytes.fromhex(data), (self.broadcastIP, 9))
			else:
				sock.sendto(data.decode("hex"), (self.broadcastIP, 9))
		except Exception as e:
			self.logger.error("sendWakewOnLan for {};  called from {};  bc ip: {}".format(MAC, calledFrom, self.broadcastIP), exc_info=True)

########################################
	def checkIfiFindisEnabled(self):
		try:
			self.iDevicesEnabled =False
			self.getiFindFile()
			if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
				for dev in indigo.devices.iter(self.iFindStuffPlugin):
					#if  dev.pluginId.find(self.iFindStuffPlugin) == -1 :continue
					if dev.deviceTypeId!= "iAppleDeviceAuto": continue
					self.iDevicesEnabled =True
					self.pluginPrefs["iDevicesEnabled"] =True
					return
			self.pluginPrefs["iDevicesEnabled"] =False
		except Exception:
			self.logger.error("", exc_info=True)
		return

########################################
	def getiFindFile(self):
		try:
			line, err = self.readPopen("ls '{}Preferences/Plugins/' | grep  '{}' | grep -v grep".format(self.indigoPath, iFindPluginMinText))
			if len(line) > 0:
				self.iFindStuffPlugin = line.split(".indiPref")[0]
			self.indiLOG.log(20, "ifind plugin: {}".format(self.iFindStuffPlugin))

		except Exception:
			self.logger.error("", exc_info=True)
		return
########################################
	def getpiBeaconAvailable(self):
		try:
			self.piBeaconDevicesAvailable=[]
			if  indigo.server.getPlugin("com.karlwachs.piBeacon").isEnabled():
				for dev in indigo.devices.iter("com.karlwachs.piBeacon"):
						self.piBeaconIsAvailable =True
						if "Pi_0_Signal" in dev.states and "status" in dev.states: # only interested in iBeacons
							self.piBeaconDevicesAvailable.append((dev.id, dev.name))
							if dev.states["status"] == "up" or dev.states["status"] == "1":
															status= "up"
							else:                           status= "0"
							if "{}".format(dev.id) not in self.piBeaconDevices:
								self.piBeaconDevices["{}".format(dev.id)]={"currentStatus":status,"lastUpdate":time.time(),"name":dev.name,"used": "0"}
							else:
								self.piBeaconDevices["{}".format(dev.id)]["name"]=dev.name
								self.piBeaconDevices["{}".format(dev.id)]["currentStatus"]=status
							
			## remove devices that do not exist anymore
			delList=[]
			list="{}".format(self.piBeaconDevicesAvailable)
			for nDev in self.piBeaconDevices:
				if list.find(nDev)==-1 : delList.append(nDev)
			for d in delList:
				del self.piBeaconDevices[d] 
			self.piBeaconDevicesAvailable= sorted(self.piBeaconDevicesAvailable, key=lambda tup: tup[1])    
			self.piBeaconDevicesAvailable.append((1, "do not use"))
		except Exception:
			self.logger.error("", exc_info=True)
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
							if dev.states["status"] == "up" or dev.states["status"] == "1":
															state = "up"
							else:                           state = "0"
							if "{}".format(dev.id) not in self.unifiDevices:
								self.unifiDevices["{}".format(dev.id)] = {"currentStatus": "0", "lastUpdate":time.time(), "name":dev.name, "used": "0"}
							else:
								self.unifiDevices["{}".format(dev.id)]["name"] = dev.name
								self.unifiDevices["{}".format(dev.id)]["currentStatus"] = state
			## remove devices that do not exist anymore
			#self.indiLOG.log(30,"{}".format(self.unifiDevicesAvailable))
			#self.indiLOG.log(30,"{}".format(self.unifiDevices))
			delList=[]
			list="{}".format(self.unifiDevicesAvailable)
			for nDev in self.unifiDevices:
				if list.find(nDev)==-1 : delList.append(nDev)
			for d in delList:
				del self.unifiDevices[d]
			self.unifiDevicesAvailable= sorted(self.unifiDevicesAvailable, key=lambda tup: tup[1])                
			self.unifiDevicesAvailable.append((1, "do not use"))
		except Exception:
			self.logger.error("", exc_info=True)
		return


########################################
	def printConfig(self):
		try:
			self.indiLOG.log(10, "settings:  iDevicesEnabled              {}".format(self.iDevicesEnabled))
			self.indiLOG.log(10, "settings:  inbetweenPingType            {}".format(self.inbetweenPingType))
			self.indiLOG.log(10, "settings:  wifiRouter                   {}".format(self.routerType))
			self.indiLOG.log(10, "settings:  wait seconds between cycles  {}".format(self.sleepTime))
			self.indiLOG.log(10, "settings:  password entered             {}".format(self.passwordOK=="2"))
			self.indiLOG.log(10, "settings:  debugLevel                   {}".format(self.debugLevel))
			try:
				nwP= self.theNetwork.split(".")
				self.indiLOG.log(10, "settings:  FINGSCAN will scan Network    broadCast{} ".format(self.broadcastIP))
			except:
				pass
			self.indiLOG.log(20, "\n")
		except Exception:
			self.logger.error("", exc_info=True)


########################################
	def deviceDeleted(self,dev):
		try:
			devID= dev.id
			for theMAC in self.allDeviceInfo:
				if self.allDeviceInfo[theMAC]["deviceId"] ==dev.id:
					self.deleteIndigoIpDevicesData(theMAC)
					return
		except Exception:
			self.logger.error("", exc_info=True)

########################################
	def deviceStartComm(self, dev):
		try:
			if self.pluginState == "init":
				dev.stateListOrDisplayStateIdChanged()  # update device.xml info if changed
			else:
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "dev start called for "+dev.name)
			return
		except Exception:
			self.logger.error("", exc_info=True)
	
########################################
	def deviceStopComm(self, dev):
		if self.pluginState != "init":
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "dev Stop called for "+dev.name)
		
		
########################################
	def intToBin(self,iNumber):
		try:
			nBinString=""
			for i in range(17):
				j=16-i
				k=int(math.pow(2,j))
				if iNumber >=k:
					iNumber -= k
					nBinString  += "1"
				else:nBinString += "0"
			return nBinString
		except Exception:
			self.logger.error("", exc_info=True)


########################################
	def shutdown(self):
		self.indiLOG.log(30, "shutdown called")
		retCode = self.killFing("all")
		retCode = self.killPing("all")


########################################
	def stopConcurrentThread(self):
		self.stopConcurrentCounter +=1
		self.indiLOG.log(30, "stopConcurrentThread called " + "{}".format(self.stopConcurrentCounter))
		if self.stopConcurrentCounter ==1:
			self.stopThread = True


########################################
	def CALLBACKIPdeviceMACnumber1(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "1")
	def CALLBACKIPdeviceMACnumber2(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "2")
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
		return self.CALLBACKIPdevice(valuesDict, "10")
	def CALLBACKIPdeviceMACnumber11(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "11")
	def CALLBACKIPdeviceMACnumber12(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "12")
	def CALLBACKIPdeviceMACnumber13(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "13")
	def CALLBACKIPdeviceMACnumber14(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "14")
	def CALLBACKIPdeviceMACnumber15(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "15")
	def CALLBACKIPdeviceMACnumber16(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "16")
	def CALLBACKIPdeviceMACnumber17(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "17")
	def CALLBACKIPdeviceMACnumber18(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "18")
	def CALLBACKIPdeviceMACnumber19(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "19")
	def CALLBACKIPdeviceMACnumber20(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "20")
	def CALLBACKIPdeviceMACnumber21(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict, "21")

########################################
	def CALLBACKIPdevice(self, valuesDict,nDev):
		try:
			self.currentEventN="{}".format(valuesDict["selectEvent"])
			if self.currentEventN == "0":
				return valuesDict
			imac= valuesDict["IPdeviceMACnumber"+nDev]
			if imac == "0" or imac== "1" or imac == "":
				valuesDict["iDevicesEnabled"+nDev] =False
				return valuesDict
				
			if self.iDevicesEnabled:
				valuesDict["iDevicesEnabled"+nDev] =True
			else:
				valuesDict["iDevicesEnabled"+nDev] =False
				valuesDict["iDevicesEnabled"+nDev+"a"] =False
			
		
		except Exception:
			self.logger.error("", exc_info=True)
		return valuesDict


########################################
	def CALLBACKIdevice1Selected(self, valuesDict,typeId=""):
		return self.CALLBACKIdeviceSelected(valuesDict, "1")
	def CALLBACKIdevice2Selected(self, valuesDict,typeId=""):
		return self.CALLBACKIdeviceSelected(valuesDict, "2")
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
###		self.indiLOG.log(20, "currentEventN{}".format(self.currentEventN)+"  ndev{}".format(nDev)+"  iDeviceName"+valuesDict["iDeviceName"+nDev])
		try:
			if self.currentEventN == "0":
				return valuesDict
			if self.iDevicesEnabled:
				if 	not ( valuesDict["iDeviceName"+nDev] =="1" or valuesDict["iDeviceName"+nDev] ==""):
					valuesDict["iDevicesEnabled"+nDev+"a"] =True
				else:
					valuesDict["iDevicesEnabled"+nDev+"a"] =False
			else:
				valuesDict["iDevicesEnabled"+nDev+"a"] =False
		
		except Exception:
			self.logger.error("", exc_info=True)
		return valuesDict


########################################
	def CALLBACKevent(self, valuesDict,typeId=""):

		try:
			self.getUnifiAvailable()
			self.getpiBeaconAvailable()
			
			self.currentEventN="{}".format(valuesDict["selectEvent"])
			#self.indiLOG.log(20, "CALLBACKevent currentEventN = " +self.currentEventN)
			if self.currentEventN == "0":
				errorDict = valuesDict
				return valuesDict
			
			if not self.currentEventN in self.EVENTS:
				self.EVENTS[self.currentEventN]= copy.deepcopy(emptyEVENT)
				
			for nDev in self.EVENTS[self.currentEventN]["IPdeviceMACnumber"]:
				#self.indiLOG.log(20, "CALLBACKevent checking  nDev:"+nDev+ ";  self.EVENTS[self.currentEventN][IPdeviceMACnumber][nDev]:{}".format(self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]) )
				valuesDict["IPdeviceMACnumber"+nDev]	=	self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]
				valuesDict["iDeviceName"+nDev]	        =	self.EVENTS[self.currentEventN]["iDeviceName"][nDev]
				#if nDev== "1": self.indiLOG.log(20, "CALLBACKevent  IPdeviceMACnumber= " +valuesDict["IPdeviceMACnumber"+nDev])
				#idevD,idevName,idevId = self.getIdandName("{}".format(self.EVENTS[self.currentEventN]["iDeviceName"][nDev]))
				#if idevName != "0":
				#    valuesDict["iDeviceName"+nDev]			=	"{}".format(idevId)
				valuesDict["iDeviceUseForHome"+nDev]	=	self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]
				valuesDict["iDeviceUseForAway"+nDev]	=	self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]
				imac= valuesDict["IPdeviceMACnumber"+nDev]
				if imac == "0" or imac== "1" or imac == "":
					valuesDict["iDevicesEnabled"+nDev] =False
				else:
					if self.iDevicesEnabled and (self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev] == "1" or self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev] == "1"):
						valuesDict["iDevicesEnabled"+nDev] =True
						valuesDict["iDevicesEnabled"+nDev+"a"] = True
					else:
						valuesDict["iDevicesEnabled"+nDev] = False
						valuesDict["iDevicesEnabled"+nDev+"a"] = False

		
			valuesDict["minimumTimeHome"]				    	=	"{}".format(int(float(self.EVENTS[self.currentEventN]["minimumTimeHome"])))
			valuesDict["minimumTimeAway"]				    	=	"{}".format(int(float(self.EVENTS[self.currentEventN]["minimumTimeAway"])))
			valuesDict["distanceAwayLimit"]				    =	"{}".format(int(float(self.EVENTS[self.currentEventN]["distanceAwayLimit"])))
			valuesDict["distanceHomeLimit"]				    =	"{}".format(int(float(self.EVENTS[self.currentEventN]["distanceHomeLimit"])))
			valuesDict["maxLastTimeUpdatedDistanceMinutes"]	=   "{}".format(int(float(self.EVENTS[self.currentEventN]["maxLastTimeUpdatedDistanceMinutes"])))
			valuesDict["enableDisable"]					    =	self.EVENTS[self.currentEventN]["enableDisable"]

			if self.iDevicesEnabled:	valuesDict["iDevicesEnabled"]   = True
			else:						valuesDict["iDevicesEnabled"]   = False
				
				
			if self.piBeaconIsAvailable:	
				valuesDict["piBeaconEnabled"]     = True
				for npiBeacon in ("25", "26", "27", "28", "29"):
					valuesDict["IPdeviceMACnumber"+npiBeacon]=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]
			else:	
				valuesDict["piBeaconEnabled"]     = False

			if self.unifiAvailable:	
				valuesDict["unifiEnabled"]     = True
				for nUnifi in ("30","31","32","33","34"):
					valuesDict["IPdeviceMACnumber"+nUnifi]=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]
			else:	
				valuesDict["unifiEnabled"]     = False

		
		except Exception:
			self.logger.error("", exc_info=True)
		#self.indiLOG.log(20, "CALLBACKevent valuesDict:{}".format(valuesDict))
		self.updatePrefs = True
		return valuesDict

########################################
	def doPing(self, theMAC):
		try:
			ipn= self.allDeviceInfo[theMAC]["ipNumber"]
			ret, err = self.readPopen('/sbin/ping -c3 '+ipn)
			if self.decideMyLog("Ping"): self.indiLOG.log(10, "pinging device "+ self.allDeviceInfo[theMAC]["deviceName"]+" " +self.allDeviceInfo[theMAC]["ipNumber"])
			lines = ret.split("\n")
			for line in lines:
				if self.decideMyLog("Ping"): self.indiLOG.log(10,"{}".format(line))
		except Exception:
			self.logger.error("", exc_info=True)

########################################
	def pingCALLBACKaction(self, action):

		theMAC= action.props["pingIpDevice"]
		self.doPing(theMAC)



		
########################################
	def actionFromCALLBACKaction(self, action):
		#if self.decideMyLog("iFind"): self.indiLOG.log(10, " actionFromCALLBACK --{}".format(action))
		try:
			self.callingPluginName.append(action.props["from"])
			self.callingPluginCommand.append(action.props["msg"])
		except:
			pass
			self.indiLOG.log(40,  "actionFrom no plugin call back given" )
			return
		self.triggerFromPlugin=True
		return

########################################
	def piBeaconUpdateCALLBACKaction(self, action):
		#if self.decideMyLog("piBeacon"): self.indiLOG.log(10, " self.piBeaconDevices {}".format(self.piBeaconDevices))
		try:
			if "deviceId" in  action.props:
				for devId in action.props["deviceId"]:
					devS="{}".format(devId)
					if devS not in self.piBeaconDevices:
						if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "piBeacon deviceId not used in fingscan: "+devS)
						continue
					dev=indigo.devices[int(devId)]
					mdevName=dev.name
					try:
						try:
							status= dev.states["status"].lower()
							if status == "1": status= "up"
						except:
							status = "notAvail"
						
						if self.decideMyLog("piBeacon"): self.indiLOG.log(10, " devName "+mdevName+"  Status "+status )
						if self.piBeaconDevices[devS]["currentStatus"] !=status:
							if self.piBeaconDevices[devS]["used"] == "1":
								self.newSleepTime=0.
								self.piBeaconUpDateNeeded = True
							self.piBeaconDevices[devS]["lastUpdate"] = time.time()
						self.piBeaconDevices[devS]["currentStatus"] = status
						self.piBeaconDevices[devS]["name"] = mdevName
					except:
						if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "status data not ready:{}".format(status))
		
			else:
				if self.decideMyLog("piBeacon"): self.indiLOG.log(10, " error from piBeacon, deviceId not in action: {}".format(action))
				return
		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "{}".format(action))
			return
		self.pluginPrefs["piBeacon"]	=	json.dumps(self.piBeaconDevices)
		return
		

########################################
	def UnifiUpdateCALLBACKaction(self, action):
		if self.decideMyLog("Unifi"): self.indiLOG.log(10, "self.unifiDevices {}".format(self.unifiDevices))
		try:
			if "deviceId" in  action.props:
				for devId in action.props["deviceId"]:
					devS="{}".format(devId)
					if devS not in self.unifiDevices:
						if self.decideMyLog("Unifi"): self.indiLOG.log(10, "unifi deviceId not used in fingscan: "+devS)
						continue
					dev=indigo.devices[int(devId)]
					mdevName=dev.name
					try:
						try:
							status= dev.states["status"]
						except:
							status = "notAvail"
						
						if self.decideMyLog("Unifi"): self.indiLOG.log(10, " devName "+mdevName+"  status "+status )
						if self.unifiDevices[devS]["currentStatus"] !=status:
							if self.unifiDevices[devS]["used"] == "1":
								self.newSleepTime=0.
								self.unifiUpDateNeeded=True
							self.unifiDevices[devS]["lastUpdate"] = time.time()
						self.unifiDevices[devS]["currentStatus"] = status
						self.unifiDevices[devS]["name"] = mdevName
					except:
						if self.decideMyLog("Unifi"): self.indiLOG.log(10, "status data not ready:"+status)
		
			else:
				if self.decideMyLog("Unifi"): self.indiLOG.log(10, " error from unifi, deviceId not in action: {}".format(action))
				return
		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "{}".format(action))
			return
		self.pluginPrefs["UNIFI"]	=	json.dumps(self.unifiDevices)
		return


########################################
	def updatepiBeacons(self):
		try:
			status = "not initialized"
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
						if status == "1": status = "up"
					except:
						status = "notAvail"

					if currentState !=status:
						if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "updating piBeacon:  devName "+mdevName+"  status "+status)
						self.piBeaconUpDateNeeded=True
						self.piBeaconDevices[deviceId]["currentStatus"]= status
						self.piBeaconDevices[deviceId]["lastUpdate"] 	= time.time()
						self.piBeaconDevices[deviceId]["name"] 		= mdevName
						if self.piBeaconDevices[devS]["used"] == "1":
							self.newSleepTime=0.
				except:
						if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "updating piBeacon:  devName {}".format(mdevName)+"  status {}".format(status) +" not ready"  )
	
		
		except Exception:
			self.logger.error("", exc_info=True)
			self.piBeaconDevices={}
		return

########################################
	def updateUnifi(self):
		try:
			Presence = "not initialized"
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
						Status = "notAvail"

					if currentState !=Presence:
						if self.decideMyLog("Unifi"): self.indiLOG.log(10, "updating unifi:  devName "+mdevName+"  Status "+Status)
						self.unifiUpDateNeeded=True
						self.unifiDevices[deviceId]["currentStatus"] = Status
						self.unifiDevices[deviceId]["lastUpdate"] 	= time.time()
						self.unifiDevices[deviceId]["name"] 		= mdevName
						if self.unifiDevices[devS]["used"] == "1":
							self.newSleepTime=0.
				except:
						if self.decideMyLog("Unifi"): self.indiLOG.log(10, "updating unifi:  devName {}".format(mdevName)+"  Status {}".format(Status) +" not ready"  )
	
		
		except Exception:
			self.logger.error("", exc_info=True)
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
	def filterIgnoredMACs(self, filter= "self", valuesDict=None, typeId="", targetId=0):
		retList =[]
		for theMAC in self.ignoredMAC:
			retList.append((theMAC,self.ignoredMAC[theMAC]))
		retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text
		return retList
########################################
	def filterNotIgnoredMACs(self, filter= "self", valuesDict=None, typeId="", targetId=0):
		retList =[]
		for theMAC in self.allDeviceInfo:
			if theMAC not in self.ignoredMAC:
				retList.append((theMAC,theMAC+"-"+self.allDeviceInfo[theMAC]["deviceName"]+"-"+self.allDeviceInfo[theMAC]["ipNumber"]))
		retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text
		return retList

########################################
	def filterListIpDevices(self, filter= "self", valuesDict=None, typeId="", targetId=0):
		retList =[]
		for theMAC in self.allDeviceInfo:
			devI=self.allDeviceInfo[theMAC]
			retList.append((theMAC,devI["deviceName"]+"-"+devI["ipNumber"]+"-"+devI["status"]))

		retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text

		return retList


########################################
	def selectiDeviceFilter(self, filter= "self", valuesDict=None,typeId=""):
		try:
			self.IDretList=[]
			if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
				self.iDevicesEnabled = True
				for dev in indigo.devices.iter(self.iFindStuffPlugin):
					if dev.deviceTypeId != "iAppleDeviceAuto": continue
					self.IDretList.append((dev.id,dev.name))
				self.IDretList	= sorted(self.IDretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
				self.IDretList.append((1, "do not use iDevice"))
			else:
				self.iDevicesEnabled = False
			#self.indiLOG.log(20, "selectiDeviceFilter called" )
			
			return self.IDretList
		except Exception as e:
			self.indiLOG.log(40,  "in Line '%s' has error='%s'" % (sys.exc_info()[2].tb_lineno, e) )

	   

########################################
	def IPdeviceMACnumberFilter(self, filter= "self", valuesDict=None,typeId=""):
		try:
			self.IPretList=[]
			for theMAC in self.allDeviceInfo:
				devI=self.allDeviceInfo[theMAC]
				theString = devI["deviceName"]+"-"+devI["ipNumber"]+"-"+theMAC
				self.IPretList.append(( theMAC,theString ))
			self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
			self.IPretList.append((1, "Not used"))
		except Exception:
			self.logger.error("", exc_info=True)
		#self.indiLOG.log(20, "IPdeviceMACnumberFilter called" )
		return self.IPretList


########################################
	def piBeaconFilter(self, filter= "self", valuesDict=None,typeId=""):
		#self.indiLOG.log(20, "piBeaconFilter called" )
		try:
			retList =copy.deepcopy(self.piBeaconDevicesAvailable)
		except Exception:
			self.logger.error("", exc_info=True)
			return [(0,0)]
		return retList

########################################
	def unifiFilter(self, filter= "self", valuesDict=None,typeId=""):
		#self.indiLOG.log(20, "unifiFilter called" )
		try:
			retList =copy.deepcopy(self.unifiDevicesAvailable)
		except Exception:
			self.logger.error("", exc_info=True)
			return [(0,0)]
		return retList


########################################
	def buttonConfirmDevicesCALLBACK(self, valuesDict,typeId=""):
		errorDict=indigo.Dict()

		try:
			self.currentEventN="{}".format(valuesDict["selectEvent"])
			if self.currentEventN == "0" or  self.currentEventN =="":
	#			errorDict = valuesDict
				return valuesDict


	########  do piBeacon stuff needed later in EVENTS
			for npiBeacon in ("22", "23", "24", "25", "26", "27", "28", "29"):
				mId="{}".format(valuesDict["IPdeviceMACnumber"+npiBeacon])
				if mId == "0":
					mId = self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]
				elif mId == "1":
					mId = ""

				self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]	= mId
				if mId != "" and mId != "0"and mId != "1":
					try:
						mdevName=indigo.devices[int(mId)].name
						if mId not in self.piBeaconDevices:
							if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "piBeacon mId 3 {}".format(mId) + "  {}".format(npiBeacon))
					except:
						pass


			## clean up piBeacon list
			keep=[]
			for nEvent in self.EVENTS:
				for npiBeacon in ("25", "26", "27", "28", "29"):
					mId=self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][npiBeacon]
					if  mId !="" and mId != "0":
						keep.append(mId)

			deleteM=[]
			for piBeaconId in self.piBeaconDevices:
				if piBeaconId not in keep: deleteM.append(piBeaconId)
			for piBeaconId in deleteM:
				del self.piBeaconDevices[piBeaconId]



	########  do unifi stuff needed later in EVENTS
			for nUnifi in ("30", "31", "32", "33", "34"):
				mId="{}".format(valuesDict["IPdeviceMACnumber"+nUnifi])
				if mId == "0":
					mId = self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]
				elif mId == "1":
					mId = ""

				self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nUnifi]	= mId
				if mId !="" and mId !="0"and mId != "1":
					try:
						mdevName=indigo.devices[int(mId)].name
						if mId not in self.piBeaconDevices:
							if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "unifi mId 3 {}".format(mId) + "  {}".format(nUnifi))
					except:
						pass


			## clean up unifi list
			keep=[]
			for nEvent in self.EVENTS:
				for nUnifi in ("30", "31", "32", "33", "34"):
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
					valuesDict["IPdeviceMACnumber"+nDev]	= "0"
					if iDev <= nOfIDevicesInEvent:
						valuesDict["iDeviceName"+nDev]			= ""
						valuesDict["iDeviceUseForHome"+nDev]	= "0"
						valuesDict["iDeviceUseForAway"+nDev]	= "0"
				valuesDict["DeleteEvent"] 		= False
				valuesDict["distanceAwayLimit"]	= "{}".format(copy.deepcopy(emptyEVENT["distanceAwayLimit"]))
				valuesDict["distanceHomeLimit"]	= "{}".format(copy.deepcopy(emptyEVENT["distanceHomeLimit"]))
				valuesDict["minimumTimeAway"]	= "{}".format(copy.deepcopy(emptyEVENT["minimumTimeAway"]))
				valuesDict["enableDisable"] 	= False
				self.EVENTS[self.currentEventN] = copy.deepcopy(emptyEVENT)
				self.currentEventN = "0"
				valuesDict["selectEvent"] = "0"
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
				else:   self.EVENTS[self.currentEventN]["maxLastTimeUpdatedDistanceMinutes"] =float(emptyEVENT["maxLastTimeUpdatedDistanceMinutes"]);errorDict["maxLastTimeUpdatedDistanceMinutes"]="{}".format(emptyEVENT["maxLastTimeUpdatedDistanceMinutes"])

			for lDev in range(1,nOfDevicesInEvent+1):
				nDev= "{}".format(lDev)
				if "IPdeviceMACnumber"+nDev not in valuesDict: continue
				selectedMAC = valuesDict["IPdeviceMACnumber"+nDev]
				if selectedMAC == "1" or selectedMAC == "":
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
					idevName = "0" # default, dont change..


					if  self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]!= selectedMAC:
						self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev] = selectedMAC


					if self.iDevicesEnabled:
						if not ("{}".format(valuesDict["iDeviceName"+nDev]) =="1" or "{}".format(valuesDict["iDeviceName"+nDev]) == "0" or "{}".format(valuesDict["iDeviceName"+nDev]) == "-1"):
							idevD,idevName,idevId = self.getIdandName(valuesDict["iDeviceName"+nDev])
							self.EVENTS[self.currentEventN]["iDeviceName"][nDev]= "{}".format(idevId)

							if valuesDict["iDeviceUseForHome"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	= "0";errorDict["iDeviceUseForHome"]=emptyEVENT["iDeviceUseForHome"]
							else:										self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	=valuesDict["iDeviceUseForHome"+nDev]

							if valuesDict["iDeviceUseForAway"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	= "0";errorDict["iDeviceUseForAway"]=emptyEVENT["iDeviceUseForAway"]
							else:										self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	=valuesDict["iDeviceUseForAway"+nDev]

						elif "{}".format(valuesDict["iDeviceName"+nDev]) =="1" or "{}".format(valuesDict["iDeviceName"+nDev]) =="-1":
							idevName = ""
						else:
							if valuesDict["iDeviceUseForHome"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	= "0";errorDict["iDeviceUseForHome"]=emptyEVENT["iDeviceUseForHome"]
							else:										self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	=valuesDict["iDeviceUseForHome"+nDev]

							if valuesDict["iDeviceUseForAway"+nDev]=="":self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	= "0";errorDict["iDeviceUseForAway"]=emptyEVENT["iDeviceUseForAway"]
							else:										self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	=valuesDict["iDeviceUseForAway"+nDev]
						if  idevName == "" :
							self.EVENTS[self.currentEventN]["iDeviceName"][nDev]	    = ""
							self.EVENTS[self.currentEventN]["iDeviceUseForHome"][nDev]	=  "0"
							self.EVENTS[self.currentEventN]["iDeviceUseForAway"][nDev]	=  "0"





			valuesDict["EVENTS"]	=	json.dumps(self.EVENTS)


			valuesDict["piBeacon"]	=	json.dumps(self.piBeaconDevices)
			if self.decideMyLog("piBeacon"): self.indiLOG.log(10, "self.piBeaconDevices  {}".format(self.piBeaconDevices))
			if valuesDict["piBeaconEnabled"]: self.updatepiBeacons()

			valuesDict["UNIFI"]	=	    json.dumps(self.unifiDevices)
			if self.decideMyLog("Unifi"): self.indiLOG.log(10, "self.unifiDevices  {}".format(self.unifiDevices))
			if valuesDict["unifiEnabled"]: self.updateUnifi()

			self.savePrefs = 1
		except Exception:
			self.logger.error("", exc_info=True)
		if len(errorDict) > 0: return  valuesDict, errorDict
		return  valuesDict




########################################
	def validatePrefsConfigUi(self, valuesDict):
		try:
			self.updatePrefs =True
			rebootRequired   = False
			
			self.debugLevel			= []
			for d in _debAreas:
				if "debug"+d in valuesDict and valuesDict["debug"+d]: self.debugLevel.append(d)

			self.enableBroadCastEvents  = valuesDict["enableBroadCastEvents"]
			if self.enableBroadCastEvents not in ["0","all","individual"]:
				self.enableBroadCastEvents  = "0"

			xx   = valuesDict["indigoDevicesFolderName"]
			if xx != self.indigoDevicesFolderName:
				self.indigoDevicesFolderName    = xx
				try:
					indigo.devices.folder.create(self.indigoDevicesFolderName)
					self.indiLOG.log(20,self.indigoDevicesFolderName+ " folder created")
				except:
					pass
				self.indigoDeviceFolderID = indigo.devices.folders[self.indigoDevicesFolderName].id

			xx   = valuesDict["indigoVariablesFolderName"]
			if xx != self.indigoVariablesFolderName:
				self.indigoVariablesFolderName    = xx
				if self.indigoVariablesFolderName not in indigo.variables.folders:
					self.indigoVariablesFolderID=indigo.variables.folder.create(self.indigoVariablesFolderName).id
					self.indiLOG.log(20,self.indigoVariablesFolderName+ " folder created")
				else:
					self.indigoVariablesFolderID=indigo.variables.folders[self.indigoVariablesFolderName].id

			
			
	## password handiling
			testi = valuesDict["inbetweenPingType"]
			try:
				testT = int(valuesDict["sleepTime"])
			except:
				testT = 5
			if testi != self.inbetweenPingType or testT != self.sleepTime:
				self.inbetweenPing={}
				self.killPing("all")
			self.inbetweenPingType = testi
			self.sleepTime = int(testT)

			netwT   = valuesDict["netwType"]
			network = valuesDict["network"]
			try:    "{}".format(int(netwT))
			except: netwT = "24"

			if not self.isValidIP(network):
				ok = False
			else:
				ok = True


			if ok and (self.netwType != netwT or network != self.theNetwork) :
				self.quitNOW = "new Network"
				self.theNetwork = network
				self.netwType   = netwT
				valuesDict["netwType"]	= self.netwType
				valuesDict["network"]	= self.theNetwork
				self.netwInfo			= self.IPCalculator(self.theNetwork, self.netwType)
				self.broadcastIP		= self.netwInfo["broadcast"]
				self.netwInfo = {'netWorkId': '192.168.1.0', 'broadcast': '192.168.1.255', 'netMask': '255.255.255.0', 'maxHosts': 254, 'hostRange': '192.168.1.1 - 192.168.1.254'}
				self.indiLOG.log(30, "network setings changed, will auto restart plugin in a minute  new defs: {}".format(self.netwInfo))

			self.yourPassword = valuesDict["password"]
			self.passwordOK = "2"

			self.routerType = valuesDict["routerType"]
			if self.routerType != "0":
				try:
					rtPW = valuesDict["routerPWD"]
					if rtPW == "your router password here":
						self.routerPWD	= ""
						self.routerType = "0"
					elif rtPW == "password is already stored":
						self.routerPWD = self.getPWD("fingrt")
					else:
						self.routerPWD	= rtPW
						self.storePWD(rtPW, "fingrt")
						valuesDict["routerPWD"] = "password is already stored"
					self.routerUID	= valuesDict["routerUID"]
					self.routerIPn	= valuesDict["routerIPn"]
					self.badWiFiTrigger["minSignalDrop"]			= float(valuesDict["minSignalDrop"])
					self.badWiFiTrigger["minNumberOfDevicesBad"]	= float(valuesDict["minNumberOfDevicesBad"])
					self.badWiFiTrigger["minNumberOfSecondsBad"]	= float(valuesDict["minNumberOfSecondsBad"])
					self.badWiFiTrigger["minWiFiSignal"]			= float(valuesDict["minWiFiSignal"])
				except:
					self.routerType =0
					if self.decideMyLog("WiFi"): self.indiLOG.log(10, " router variables not initialized, bad data entered ")
		
				self.checkWIFIinfo()
				self.checkIfBadWiFi()
				self.checkDEVICES()
			else:
				self.wifiMacList={}
				self.oldwifiMacList={}
				valuesDict["wifiMacList"] = ""



			if self.enableMACtoVENDORlookup != valuesDict["enableMACtoVENDORlookup"] and self.enableMACtoVENDORlookup == "0":
				rebootRequired                         = True
			self.enableMACtoVENDORlookup               = valuesDict["enableMACtoVENDORlookup"]

			self.acceptNewDevices = valuesDict["acceptNewDevices"] == "1"

	# clean up empty events
			self.cleanUpEvents()
	# save to indigo
			valuesDict["EVENTS"]	=	json.dumps(self.EVENTS)
			valuesDict["UNIFI"]	=	json.dumps(self.unifiDevices)
			valuesDict["piBeacon"]	=	json.dumps(self.piBeaconDevices)

			self.printWiFi()
			self.printConfig()

		except Exception:
			self.logger.error("", exc_info=True)
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
				self.updateIndigoIpDeviceFromDeviceData(theMAC,["hardwareVendor", "deviceInfo", "WiFi", "usePing", "suppressChangeMSG"])
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
				nev= "{}".format(n)
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
					nDev= "{}".format(i)
					if nDev not in self.EVENTS[n]["IPdeviceMACnumber"]:
						for prop in emptyEVENT:
							try:
								self.EVENTS[n][prop][nDev]		= copy.deepcopy(emptyEVENT[prop]["1"])
							except: 
								pass                               
												
					if int(nDev) >= piBeaconStart:#  here the mac number is the indigo device # , remove it if the indigo device is gone
						if self.EVENTS[n]["IPdeviceMACnumber"][nDev] != "" and self.EVENTS[n]["IPdeviceMACnumber"][nDev] != "0":
							try:
								indigo.devices[int(self.EVENTS[n]["IPdeviceMACnumber"][nDev])]
							except Exception as e:
								self.logger.error("cleanupEVENTS:  please remove device from EVENTS as indigo device does not exist: {}".format(self.EVENTS[n]["IPdeviceMACnumber"][nDev]) , exc_info=True)
								continue
								# dont auto delete let user remove from event listing
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
					lDev="{}".format(lll)
					idevD,idevName,idevId = self.getIdandName(self.EVENTS[nev]["iDeviceName"][lDev])
					self.EVENTS[nev]["iDeviceName"][lDev]= "{}".format(idevId)
					
		except Exception:
			self.logger.error("", exc_info=True)
			
########################################
	def	resetEvents(self):
		try:
			self.EVENTS = {}
			self.cleanUpEvents()
			self.pluginPrefs["EVENTS"]	= json.dumps(self.EVENTS)
			indigo.server.savePluginPrefs() 
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "ResetEVENTS done")
		except Exception:
			self.logger.error("", exc_info=True)
		return
########################################
	def	resetDevices(self):
		try:
			List =[]
			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				#if dev.pluginId.upper().find("FINGSCAN")>-1:  # put your plugin name here
					List.append((dev.id,dev.name))
			self.indiLOG.log(30, "deleting devices:{}".format(List))
			for devId in List:
				indigo.device.delete(devId[0])
	#		self.quitNOW = "loading data from file after Device reset"

			if not os.path.exists(self.fingSaveFileName):
				self.writeToFile()
			else:
				shutil.copy(self.fingSaveFileName,self.fingSaveFileName+"{}".format(time.time()))
				
			self.doLoadDevices()


			if self.decideMyLog("WiFi"): self.indiLOG.log(30, "ResetDEVICES done")
		except Exception:
			self.logger.error("", exc_info=True)
		return

########################################
	def printEvents(self,printEvents="all"):
		try:
			if len(self.EVENTS) == 0:
				self.indiLOG.log(20, "printEvents: no EVENT defined \n")
				return


			out ="\nEVENT defs:::::::::::::::::: Start :::::::::::::::::\n"
			eventsToPrint=[]
			if printEvents == "all":
				for i in range(1,nEvents+1):
					eventsToPrint.append("{}".format(i))
			else:
				eventsToPrint.append(printEvents)
			eventsToPrint=sorted(eventsToPrint)
			
			timeNowSecs = "{}".format(int(time.time()))
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
				out+= "EVENT:------------- "+nEvent.rjust(2)+"  --------------------------------------------------------------------------------------------------"+"\n"
				for iDev in range(1,nOfDevicesInEvent+1):
					if iDev not in listOfDevs: continue
					nDev = "{}".format(iDev)
					#sout+= "{}".format(evnt["IPdeviceMACnumber"]))
					try:
						theMAC = evnt["IPdeviceMACnumber"][nDev]
					except:
						continue
					
					if int(nDev) < piBeaconStart:
						try:
							devI = self.allDeviceInfo[theMAC]
						except: 
							out = "{}  is not defined, please remove from event# {}".format(theMAC, nEvent)
							continue
						out+= "dev#: {}".format(nDev).rjust(2)+" -- devNam:"+devI["deviceName"].ljust(25)[:25] +" -- MAC#:"+theMAC+" -- ip#:"+devI["ipNumber"].ljust(15)+" -- status:"+devI["status"].ljust(8)+" -- WiFi:"+devI["WiFi"]+"\n"
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
								out+= " piBeacon device IndigoID# "+theMAC+ " does not exist, check you piBeacon plugin" +"\n"
								continue
						status= self.piBeaconDevices[theMAC]["currentStatus"]
						out+= "dev#: {}".format(nDev)+" -- devNam:"+name.ljust(25)[:25] +" -- IND#:"+theMAC.ljust(17)+" --     "+" ".ljust(15)+" -- status:"+status.ljust(8)+"\n"
					else:
						try:
							name= 	self.unifiDevices[theMAC]["name"]
						except:
							self.getUnifiAvailable()
							self.updateUnifi()
							try:
								name= 	self.unifiDevices[theMAC]["name"]
							except:
								self.indiLOG.log(40, " unifi device IndigoID# {} does not exist, check your unifi plugin".format(theMAC) )
								continue
						status= self.unifiDevices[theMAC]["currentStatus"]
						out+= "dev#: {}".format(nDev)+" -- devNam:{:25} -- IND#:{:17} --     {:15} -- status:{:8}\n".format(name[:25], theMAC, " ",status)
					


				out+= self.printEventLine("currentStatusHome"	 		, "currentStatusHome"		,nEvent,listOfDevs)
				out+= self.printEventLine("currentStatusAway"	 		, "currentStatusAway"		,nEvent,listOfDevs)
				if prntDist:
					out+= self.printEventLine("iDeviceName"				, "iDevice Name"				,nEvent,listOfDevs)
					out+= self.printEventLine("iDeviceUseForHome"		, "iDeviceUseForHome"		,nEvent,listOfDevs)
					out+= self.printEventLine("iDeviceUseForAway"		, "iDeviceUseForAway"		,nEvent,listOfDevs)
					out+= self.printEventLine("iDeviceAwayDistance"		, "iDeviceCurrntAwayDist"	,nEvent,listOfDevs)
					out+= self.printEventLine("iDeviceHomeDistance"		, "iDeviceCurrntHomeDist"	,nEvent,listOfDevs)
				out+= self.printEventLine("timeOfLastOFF"				, "time WhenLast DOWN"		,nEvent,listOfDevs)
				out+= self.printEventLine("timeOfLastON"				, "time WhenLast UP"			,nEvent,listOfDevs)
				out+= self.printEventLine("secondsOfLastON"				, "seconds WhenLast UP"		,nEvent,listOfDevs)
				out+= self.printEventLine("secondsOfLastOFF"			, "seconds WhenLast DOWN"	,nEvent,listOfDevs)
				if prntDist:
					pass
					#self.printEventLine("iDeviceInfoTimeStamp"	,"iDeviceInfoTimeStamp"		,nEvent,listOfDevs)
				out+=   	"Time right now:          :"+timeNowHMS.rjust(12)+"\n"
				out+=   	"ALL Devices         Home :{}".format(evnt["allHome"]).rjust(12)+"  -- reacts after minTimeNotHome"+"\n"
				out+=   	"AtLeast ONE Device  Home :{}".format(evnt["oneHome"]).rjust(12)+"  -- reacts after minTimeNotHome"+"\n"
				out+=   	"n Devices           Home :{}".format(evnt["nHome"]).rjust(12)  +"  -- reacts after minTimeNotHome"+"\n"
				out+=   	"ALL Devices         Away :{}".format(evnt["allAway"]).rjust(12)+"  -- reacts minTimeAway bf Trig"+"\n"
				out+=   	"AtLeast ONE Device  Away :{}".format(evnt["oneAway"]).rjust(12)+"  -- reacts minTimeAway bf Trig"+"\n"
				out+=   	"n Devices           Away :{}".format(evnt["nAway"]).rjust(12)  +"  -- reacts minTimeAway bf Trig"+"\n"
				if prntDist:
					out+=	"minDist.toBeAway         :{}".format("%5.2f"%float(evnt["distanceAwayLimit"])).rjust(12)+"\n"
					out+=	"minDist.toBeNotHome      :{}".format("%5.2f"%float(evnt["distanceHomeLimit"])).rjust(12)+"\n"
					out+=	"max age of dist info     :{}".format(evnt["maxLastTimeUpdatedDistanceMinutes"]).rjust(12)+"\n"
				out+=		"minTimeAway bf Trig      :{}".format("%5.0f"%float(evnt["minimumTimeAway"])).rjust(12)+"\n"
				out+= 		"minTimeNotHome bf re-Trig:{}".format("%5.0f"%float(evnt["minimumTimeHome"])).rjust(12)+"\n"
				out+= 		"Event enabled            :{}".format(evnt["enableDisable"]).rjust(12)+"\n"
				out+=		"dataFormat               :{}".format(evnt["dataFormat"]).rjust(12)+"\n"
			out+=			"EVENT defs:::::::::::::::::: END ::::::::::::::::::"
			self.indiLOG.log(20, out+"\n")
		except Exception:
			self.logger.error("", exc_info=True)
		return
########################################
	def printEventLine(self, name,nameText,nEvent,listOfDevs):
		out=""
		try:
			list ="" 
			for iDev in range(1,nOfDevicesInEvent+1):
				if iDev not in listOfDevs: continue
				nDev = "{}".format(iDev)
				if name == "secondsOfLastON" or  name == "secondsOfLastOFF" :
					list += "#"+nDev.rjust(2)+":{}".format( int(time.time()) - int(self.EVENTS[nEvent][name][nDev]) ).rjust(15)+"  "
				elif name == "iDeviceName" :
					idevD,idevName,idevId = self.getIdandName("{}".format(self.EVENTS[nEvent][name][nDev]))
					list += "#"+nDev.rjust(2)+":"+idevName.rjust(15)+"  "
				else:
					list += "#"+nDev.rjust(2)+":{}".format(self.EVENTS[nEvent][name][nDev]).rjust(15)+"  "
			out = (nameText+":").ljust(22) + list.strip("  ")
		except Exception as e:
			self.logger.error("{}".format(self.EVENTS[nEvent]), exc_info=True)
		return out+"\n"

#		self.indiLOG.log(10, "<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )
########################################
	def	printWiFi(self,printWiFi= "all"):
		return 
		out ="\n"
		try:
			if len(self.wifiMacList) ==0:
				self.indiLOG.log(20, "printWiFi: no WiFi devices defined")
				return
			if self.routerType !=0:
				self.updateDeviceWiFiSignal()
				out+= "WiFi info router type:{}-- IP#/page: {}   .....ACTIVE Wifi device list:\n".format(self.routerType, self.routerIPn)
				out+= "---- MAC # ------ ---- device Name ----- ------ ip# ----- -WiFi- -Signal- -aveSign -Associated Authorized\n"
				self.printWiFiDevs("5GHz",Header=True)
				self.printWiFiDevs("2GHz")
				self.printWiFiDevs("")
				out+= "\n"
				#out+= self.printWiFiAve("2GHz",Header=True)
				#out+= self.printWiFiAve("5GHz")
				out+= "\n"
				out+= "settings for badWiFiSignalTrigger "+ "\n"
				out+= " minNumberOfSecondsBad: {5.1f}\n".format(self.badWiFiTrigger["minNumberOfSecondsBad"])
				out+= " minNumberOfDevicesBad: {5.1f}\n".format(self.badWiFiTrigger["minNumberOfDevicesBad"])
				out+= " minSignalDrop:         {5.1f}\n".format(self.badWiFiTrigger["minSignalDrop"])
				out+= " minWiFiSignal:         {5.1f}\n".format(self.badWiFiTrigger["minWiFiSignal"])
				out+= "-------------------------------------------------------------------------------------------------------- "+ "\n"
				self.indiLOG.log(10,out)
		except Exception:
			self.logger.error("", exc_info=True)

		return
########################################
	def printpiBeaconDevs(self):
		try:
			## refresh piBeacon cokkies
			self.getpiBeaconAvailable()
			if len(self.piBeaconDevices) ==0: return
			out = "\n"
			
			out+= "===      piBeacon devices  available  to fingscan    ===        START"+"\n"
			#				 123456789012345678901234567890123412345678123456789012
			out+= "--Device Name------        indigoID--    --Status  lastUpdate  used"+"\n"
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
						theString+= "{}".format(lastUpdate).rjust(12)
						theString+= self.piBeaconDevices[theMAC]["used"].rjust(6)
					
						out+= theString + "\n"
					except:
						self.indiLOG.log(40, " data wrong for {}".format(theMAC) +"    {}".format(self.piBeaconDevices))
			out+= "===      piBeacon devices  available  to fingscan    ===        END"+"\n"
			self.indiLOG.log(10,out)
	
		except Exception:
			self.logger.error("", exc_info=True)

########################################
	def printUnifiDevs(self):
		try:
			## refresh piBeacon cokkies
			self.getUnifiAvailable()
			if len(self.unifiDevices) ==0: return
			out = "\n"
			out+= "===      Unifi   devices  available  to fingscan    ===        START"+"\n"
			#				 123456789012345678901234567890123412345678123456789012
			out+= "--Device Name------        indigoID--    --Status  lastUpdate  used"+"\n"
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
						theString+= "{}".format(lastUpdate).rjust(12)
						theString+= self.unifiDevices[theMAC]["used"].rjust(6)
						out+= theString + "\n"
						
					except Exception as e:
						self.logger.error(" data wrong for {}".format(theMAC) +"    {}".format(self.unifiDevices[theMAC]), exc_info=True)
			out+= "===      unifi devices  available  to fingscan    ===        END"
			self.indiLOG.log(10,out)
	
		except Exception:
			self.logger.error("", exc_info=True)


########################################
	def printWiFiDevs(self, ghz,Header=False):
		out =""
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
						theString+= "  {}".format(self.wifiMacList[theMAC][2]).ljust(7)
					try:
						theString+= "   %7.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))
					except:
						theString+= "   0      "
					theString+= "  "	+self.wifiMacList[theMAC][0].rjust(7)
					theString+= "    "	+self.wifiMacList[theMAC][1].rjust(7)
					if devI["deviceName"].find("unidentifiedWiFiDevice") > -1:
						theString += " some times devices with wifi AND ethernet show this behaviour"
					out+= theString+"\n"
				else:
					out+= theMAC+" -device is expired, not in dev list any more- {}".format(self.wifiMacList[theMAC]) +" some times devices with wifi AND ethernet show this behaviour"+"\n"
		except Exception:
			self.logger.error("", exc_info=True)
		return out
########################################
	def printWiFiAve(self, ghz,Header=False):
		out=""
		try:
			if Header: out+= "overall WiFi stats:"+"\n"
			out+= " "+ghz+": ave.Signal[dBm]%4.0f,  curr.Signal:%4.0f,  NumberOfMeasurements:%6.0f,  NumberOfCycles:%6.0f, ave.NumberofDevices:%2.0f, curr.NumberOfDevicesConnected:%2.0f,  noiseLevel: %s"\
				%( (self.wifiMacAv["sumSignal"][ghz]/max(1.0,self.wifiMacAv["numberOfDevices"][ghz]))
				 , self.wifiMacAv["curAvSignal"][ghz]
				 , self.wifiMacAv["numberOfDevices"][ghz]
				 , self.wifiMacAv["numberOfCycles"][ghz]
				 , self.wifiMacAv["numberOfDevices"][ghz]/max(1.0,self.wifiMacAv["numberOfCycles"][ghz])
				 , self.wifiMacAv["curDev"][ghz]
				 , self.wifiMacAv["noiseLevel"][ghz])
				 
		except Exception:
			self.logger.error("", exc_info=True)
		return out+"\n"
		

##### execute triggers:

######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

	def triggerStartProcessing(self, trigger):
#		if self.decideMyLog("WiFi"): self.indiLOG.log(10, "<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )iDeviceHomeDistance
		self.triggerList.append(trigger.id)
#		if self.decideMyLog("WiFi"): self.indiLOG.log(10, "exiting triggerStartProcessing -->>")

	def triggerStopProcessing(self, trigger):
#		if self.decideMyLog("WiFi"): self.indiLOG.log(10, "<<-- entering triggerStopProcessing: %s (%d)" % (trigger.name, trigger.id))
		if trigger.id in self.triggerList:
#			if self.decideMyLog("WiFi"): self.indiLOG.log(10, "TRIGGER FOUND")
			self.triggerList.remove(trigger.id)
#		if self.decideMyLog("WiFi"): self.indiLOG.log(10, "exiting triggerStopProcessing -->>")

	#def triggerUpdated(self, origDev, newDev):
	#	self.logger.log(4, "<<-- entering triggerUpdated: %s" % origDev.name)
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

	def triggerEvent(self, eventId):
		try:
			if self.decideMyLog("Events"): self.indiLOG.log(10, "triggerEvent: %s " % eventId)
			for trigId in self.triggerList:
				trigger = indigo.triggers[trigId]
				if self.decideMyLog("Events"): self.indiLOG.log(10, "testing trigger id: {}".format(trigId).rjust(12)+"; eventId:{}".format(eventId).rjust(12)+";  {}".format(trigger.pluginTypeId))
				if trigger.pluginTypeId == eventId:
					if self.decideMyLog("Events"): self.indiLOG.log(10, "firing trigger id : {}".format(trigId))
					indigo.trigger.execute(trigger)
		except Exception:
			self.logger.error("", exc_info=True)
		return






####################


	####################  startup / config methods  #######################

########################################
	def storePWD(self,passw,name):
		try:
			## store pwd into keychain
			storePassword = "&a3"+passw[::-1]+"#5B"  # fist reverse password, then add 4 char before and after,
			ret, err = self.readPopen("/usr/bin/security add-generic-password -a fingscanpy -w \'"+ storePassword+"\' -s "+name+" -U")
			return
		except Exception:
			self.logger.error("", exc_info=True)

########################################
	def getPWD(self,name):
		try:
			## get pwd from keychain
			ret, storePassword = self.readPopen(["security", "find-generic-password", "-gl",name])
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "password entered (&a3reversed#5B)=" +"{}".format(storePassword))
			try:
				storePassword.index("password")  # if the return text contains "password" its ok, continue
				storePassword= "{}".format(storePassword).split('"')[1]
				return storePassword[3:-3][::-1] ## 1. drop fist and last 3 characaters, then reverse string
			except:  # bad return, no password stored, return "0"
				return "0"
		except Exception:
			self.logger.error("", exc_info=True)


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
			if self.decideMyLog("WiFi"): self.indiLOG.log(10, " device selected:{}".format(devId)+"/"+devName)
		else:
			if self.decideMyLog("WiFi"): self.indiLOG.log(10, " device selected:"+ " all")
			
		return True
########################################
	def pickDeviceFilter(self,filter=None,valuesDict=None,typeId=0):
		retList =[]
		for dev in indigo.devices.iter("com.karlwachs.fingscan"):
#			if self.decideMyLog("WiFi"): self.indiLOG.log(10,dev.pluginId+" "+dev.name)
			#if dev.pluginId.upper().find("FINGSCAN")>-1:  # put your plugin name here
#				if self.decideMyLog("WiFi"): self.indiLOG.log(10, " adding "+dev.name)
				retList.append((dev.id,dev.name))
		retList.append((0, "all devices"))
		return retList
########################################
	def triggerEventCALLBACK(self,valuesDict,typeId):
		self.indiLOG.log(20, "received trigger event from menu: {}".format(valuesDict))
		self.triggerEvent(valuesDict["triggerEvent"])
		return



########### menue in and out ###########
	def getMenuActionConfigUiValues(self, menuId):
		#indigo.server.log('Called getMenuActionConfigUiValues(self, menuId):')
		#indigo.server.log('     (' + "{}".format(menuId) + ')')

		valuesDict = indigo.Dict()
		valuesDict["selectEvent"] = "0"  
		errorMsgDict = indigo.Dict()
		return (valuesDict, errorMsgDict)
########################################
	def inpPrintEVENTS(self):
		self.indigoCommand = "PrintEVENTS"
		self.indiLOG.log(20, "command: Print EVENTS and configuration")
		return

########################################
	def inpPrintWiFi(self):
		self.indigoCommand = "PrintWiFi"
		self.indiLOG.log(20, "command: Print WiFi information and configuration")
		return
########################################
	def inpPrintpiBeacon(self):
		self.indigoCommand = "PrintpiBeacon"
		self.indiLOG.log(20, "command: Print piBeacon information")
		return
########################################
	def inpPrintUnifi(self):
		self.indigoCommand = "PrintUnifi"
		self.indiLOG.log(20, "command: Print unifi information")
		return


########################################
	def inpResetEVENTS(self):
		self.indigoCommand = "ResetEVENTS"
		self.indiLOG.log(20, "command: ResetEVENTS")
		return
########################################
	def inpResetDEVICES(self):
		self.indigoCommand = "ResetDEVICES"
		self.indiLOG.log(20, "command: ResetDEVICES")
		return
########################################  not used anymore
	def inpEVENTAway1(self):
		self.indigoCommand = "EVENT_Away_1"
		self.indiLOG.log(20, "command: EVENT_Away_1")
		return
########################################  not used anymore
	def inpEVENTHome1(self):
		self.indigoCommand = "EVENT_Home_1"
		self.indiLOG.log(20, "command: EVENT_Home_1")
		return

########################################
	def inpSaveData(self):
		self.indigoCommand = "save"
		self.indiLOG.log(20, "command: save")
		retCode = self.writeToFile()
		self.indigoCommand = "none"
		self.indiLOG.log(20, "save done")
		return
		

########################################
	def inpLoadDevices(self):
		self.indigoCommand = "loadDevices"
		self.indiLOG.log(20, "command: loadDevices")
		return


########################################
	def inpSortData(self):
		self.indigoCommand = "sort"
		self.indiLOG.log(20, "command: sort")
		return

########################################
	def inpDetails(self):
		self.indigoCommand = "details"
		self.indiLOG.log(20, "command: log IP-Services of your network")
		return

########################################
	def inpSoftrestart(self):
		self.quitNOW = "softrestart"
		self.indiLOG.log(20, "command: softrestart")
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
			self.indiLOG.log(20, "       restore done")
		except Exception:
			self.logger.error("", exc_info=True)
		return


########################################
	def doSortData(self):
		self.indiLOG.log(20, "sorting ipDevices with IP Numbers")
		retCode = self.getIndigoIpVariablesIntoData()
		retCode = self.sortIndigoIndex()
		retCode = self.getIndigoIpVariablesIntoData()
		self.indiLOG.log(20, " sorting  done")
		return

########################################
	def doDetails(self):

		self.indiLOG.log(10, "starting log IP-Services of your network, might take several minutes, it will test each port on each ip-device, output to plugin.log and:{}".format(self.fingServicesOutputFileName))
		## ask fing to produce details list of services per ip number
		ret=""
## cd '/Library/Application Support/Perceptive Automation/Indigo 7.4/Preferences/Plugins/com.karlwachs.fingscan/';echo 'your osx password here.. no quotes' | sudo -S /usr/local/bin/fing  -s 192.168.1.0/24 -o json,fingservices.json > fingservices.log
		try:

			cmd ="echo '" +self.yourPassword + "' | sudo -S /bin/rm '"+self.fingServicesFileName+"'"
			ret, err = self.readPopen(cmd)
			if self.decideMyLog("Special"): self.indiLOG.log(10, " del cmd: {}, ret: {}- {}".format(cmd, ret, err) )
			if self.opsys >= 10.15:
				cmd ="cd '"+self.indigoPreferencesPluginDir+"';echo '"+self.yourPassword+"' | sudo -S "+self.fingEXEpath+"  -s "+self.theNetwork+"/{}".format(self.netwType)+" -o json > "+self.fingServicesFileName0
			else:
				cmd ="cd '"+self.indigoPreferencesPluginDir+"';echo '"+self.yourPassword+"' | sudo -S "+self.fingEXEpath+"  -s "+self.theNetwork+"/{}".format(self.netwType)+" -o json,"+self.fingServicesFileName0+" > "+self.fingServicesLOGFileName0
		

			self.indiLOG.log(20, "fing network scan: "+self.theNetwork+"/{}".format(self.netwType))
			if self.decideMyLog("Special"): self.indiLOG.log(10, "fing under opsys: {} command: {}".format(self.opsys, cmd) )
			ret, err = self.readPopen(cmd)
			

		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "  fing details failed: fing returned an error: {}- err".format(ret, err))
			return

		## read fing output file
		fingOut = ""
		try:
			f = open(self.fingServicesFileName,"r")
			fingOut = f.read()
			f.close()
			#self.indiLOG.log(20, "  json fingOut {}".format(fingOut))
			if fingOut.find("> Service scan starting.") > -1:
				ff = fingOut.find("\n[") 
				fingOut = fingOut[ff+1:]
		except Exception as e:
			self.logger.error("  fing details failed , output file: {}".format(fingOut), exc_info=True)
			return
			
		## now get the list into theServices
		try:
		
			self.theServices=json.loads(fingOut.replace(",},","},").replace("},]","}]").replace("':",'":').replace(":'",':"').replace("','",'","').replace("{'",'{"').replace("'}",'"}'))
		except:
			self.indiLOG.log(40, "  fing details failed: json command went wrong ")
			self.indiLOG.log(40, "{}".format(fingOut))
			return
		
		retCode = self.getIndigoIpVariablesIntoData()  ## refresh indigo data

		out =""
		out+="IP-Device Number, Name, Vendor,.."+"IP-Device port scan on  "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

##self.fingServicesOutputFileName
####
# now put the results into the logfile
		theLength1 = len(self.theServices)
		macIndex=[]
		for ii in range(0,theLength1):
			ipNo ="{}".format(self.theServices[ii]["Address"])
				
			scanResult ="{}".format(self.theServices[ii]["ScanResult"])
			## have all indexes , merge indigo and fing info
			
			if scanResult != "OK": continue
			try:
				theMAC ="{}".format(self.theServices[ii]["HardwareAddress"])
				if len(theMAC) < 16 : continue
				macIndex.append(theMAC)
				devV= self.indigoIpVariableData[theMAC]
				n1=devV["nickName"].strip()
				n2=devV["hardwareVendor"].strip()
				n3=devV["deviceInfo"].strip()
				if n3== "-":n3=""
				nickname= (n1+" "+n2+" "+n3).strip()
			except:
				nickname= ""
				theMAC= ""
#				fout.write("IP-Device Number, Name, Vendor,..." +" "+"------------------------------------------------------------------------ "+"\n")
			out+= "IP-Device Number, Name, Vendor,..."+"------------------------------------------------------------------------ "+"\n"
			theLength2 = len(self.theServices[ii]["Services"])
			if theLength2 >0:
				out+= "IP-Device Number, Name, Vendor,..."+ self.theServices[ii]["Address"].ljust(17)+theMAC+" "+self.theServices[ii]["Hostname"].ljust(24)+nickname.ljust(35)+"firewall:" + "{}".format(self.theServices[ii]["FirewallDetected"])+"\n"
				for kk in range(0,theLength2):
					out+= "..... service Port, Name, Comment:" +"    {}".format(self.theServices[ii]["Services"][kk]["Port"]).ljust(7)+ "{}".format(self.theServices[ii]["Services"][kk]["Name"]).ljust(18)	+"{}".format(self.theServices[ii]["Services"][kk]["Description"])+"\n"
			else:
				out+= "IP-Device Number, Name, Vendor,..."+self.theServices[ii]["Address"].ljust(17)+theMAC+" "+self.theServices[ii]["Hostname"].ljust(24)+nickname.ljust(35)+"firewall:" + "{}".format(self.theServices[ii]["FirewallDetected"])+"\n"
				out+= "..... service Port, Name, Comment:" +"    "+ "00000  Port Responding   No Answer from Device"+"\n"
	
# not found in fing scan use indigo data only
		out+= "IP-Device Number, Name, Vendor,..."+"------------------------------------------------------------------------ "+"\n"
		out+= "IP-Device Number, Name, Vendor,..."+"no FING info for devices: "+"\n"
		for theMAC in self.indigoIpVariableData:
			try:
				macIndex.index(theMAC) # if this ok, it was done already
				continue
			except:
				devI= self.allDeviceInfo[theMAC]
				n1=devI["nickName"].strip()
				n2=devI["hardwareVendor"].strip()
				n3=devI["deviceInfo"].strip()
				n4= "status: "+devI["status"].strip()
				if n3 == "-":n3=""
				nickname= (n1+" "+n2+" "+n3)
				out+= "IP-Device Number, Name, Vendor,..."+ devI["ipNumber"].ljust(17)+theMAC.ljust(19)+n4.ljust(17)+nickname+"\n"
		out+= "IP-Device Number, Name, Vendor,..."+"------------------------------------------------------------------------ "
		self.indiLOG.log(20,out+"         log IP-Services of your network, .......  done")
		fout=open(self.fingServicesOutputFileName,"w")
		fout.write(out.encode("utf8"))
		fout.close()
		return
	
	
########################################
	def writeToFile(self):
		
		self.indiLOG.log(20, "saving indigo data to file")
		f = open ( self.fingSaveFileName , "w")
		nwrite= min( len(self.indigoDevicesNumbers),self.indigoNumberOfdevices )
		for kk in range(nwrite):
				writestring = "{}".format(self.indigoDevicesNumbers[kk] )+";"+self.indigoDevicesValues[kk]+"\n"
				f.write(writestring.encode("utf8"))
		f.close()
		self.indiLOG.log(20, " saved")
		
		return 0


########################################
	def readFromFile(self):
		self.indiLOG.log(20, "restore indigo data from file")
		f= open ( self.fingSaveFileName , "r")
		lastD=0
		self.indigoDevicesNumbers = []
		for line in f.readlines():
			ipDevNumber = line[:2]
			if len(ipDevNumber) >1 :
				lastD+=1
				kk00=self.int2hexFor2Digit(lastD)
				self.indigoDevicesNumbers.append(kk00)

				self.indiLOG.log(20, " create re-store indigo data from file")
				try:
					test = indigo.variable.updateValue("ipDevice"+kk00,line[3:])
					self.indiLOG.log(20, " updated variable:"+kk00 )
				except:
					test = indigo.variable.create("ipDevice"+kk00,line[3:],folder=self.indigoVariablesFolderID)
					self.indiLOG.log(20, " created variable:"+kk00+" folder:{}".format(self.indigoVariablesFolderID))
		f.close()
		test = indigo.variable.updateValue("ipDevsNoOfDevices","{}".format(lastD))
		
		for kk in range(lastD,indigoMaxDevices):
			kk00 = self.int2hexFor2Digit(kk+1)						# make it 01 02 ..09 10 11 ..99
			try:
				indigo.variable.delete("ipDevice"+kk00)  # delete any entry > # of devices
			except:
				pass
				
		return 0
	
########################################
	def int2hexFor2Digit(self,numberIn):
		if numberIn < 10: return "0{}".format(numberIn)
		if numberIn <100: return "{}".format(numberIn)
		nMod = "{}".format(numberIn%100)
		if len(nMod) <2: nMod = "0"+nMod  # 105 ==> A05; 115 ==> A15 205 ==> B05;  215 ==> B15
		x = numberIn//100
		if x ==1: return "A"+nMod
		if x ==2: return "B"+nMod
		if x ==3: return "C"+nMod
		if x ==4: return "D"+nMod
		if x ==5: return "E"+nMod
		return "F"+nMod


########################################
	def getIgnoredMAC(self):
		self.ignoredMAC = {}
		xx = ""
		try:
			f = open (self.ignoredMACFile , "r")
			xx = json.loads(f.read())
			f.close()
			# now make it all upper case
			for mm in xx:
				self.ignoredMAC[mm.upper()] = 1
		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "getIgnoredMAC file read:{}".format(xx))
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


		self.indigoDevicesFolderName  = self.pluginPrefs.get("indigoDevicesFolderName",   "ipDevices")
		if len(self.indigoDevicesFolderName)   < 2: self.indigoDevicesFolderName    = "ipDevices"
		
		try:
			indigo.devices.folder.create(self.indigoDevicesFolderName)
			self.indiLOG.log(20,self.indigoDevicesFolderName+ " folder created")
		except:
			pass
		self.indigoDeviceFolderID = indigo.devices.folders[self.indigoDevicesFolderName].id
		self.pluginPrefs["indigoDeviceFolderID"] = self.indigoDeviceFolderID


		self.indigoVariablesFolderName = self.pluginPrefs.get("indigoVariablesFolderName", "IP devices")
		if len(self.indigoVariablesFolderName) < 2: self.indigoVariablesFolderName  = "IP devices"
		if self.indigoVariablesFolderName not in indigo.variables.folders:
			self.indigoVariablesFolderID=indigo.variables.folder.create(self.indigoVariablesFolderName).id
			self.indiLOG.log(20,self.indigoVariablesFolderName+ " folder created")
		else:
			self.indigoVariablesFolderID=indigo.variables.folders[self.indigoVariablesFolderName].id

		self.pluginPrefs["indigoVariablesFolderName"] = self.indigoVariablesFolderName
			   
				
		try:
			test = indigo.variable.create("ipDevice00", "MAC-Number                ;     IP-Number       ;   Time-Of-Last-Change   ;Status;     N.of-Ch.    ;   Nick-Name                 ;   Hardware-Vendor        ;   DeviceInfo               ; WiFi  ;   usePing",self.indigoVariablesFolderID)
		except:
			test = indigo.variable.updateValue("ipDevice00", "MAC-Number                ;     IP-Number       ;   Time-Of-Last-Change   ;Status;     N.of-Ch.    ;   Nick-Name                 ;   Hardware-Vendor        ;   DeviceInfo               ;  WiFi  ;   usePing")
		try:
			test = indigo.variable.create("ipDevsLastUpdate", "1",self.indigoVariablesFolderID)	;
		except:
			pass
		try:
			test = indigo.variable.create("ipDevsNewIPNumber", "1",self.indigoVariablesFolderID)	;
		except:
			pass
		try:
			test = indigo.variable.create("ipDevsNoOfDevices", "0",self.indigoVariablesFolderID)	;
		except:
			pass
		try:
			test = indigo.variable.create("ipDevsNewDeviceNo", "0",self.indigoVariablesFolderID)	;
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsCommand", "-- not used anymore can be deleted --")	;
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsPid", "-- not used anymore can be deleted --")		;
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsFormat", "-- not used anymore can be deleted --")	;
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsDoNotAsk", "-- not used anymore can be deleted --");
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsPasswordMode", "-- not used anymore can be deleted --");
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsDebug", "-- not used anymore can be deleted --")	;
		except:
			pass

		self.indiLOG.log(20, "indigo variables initialized" )


		return 0
	
	
	
########################################
	def initFing(self, restartFing):
		try:
			if self.passwordOK != "2": return -1
			self.fingRestartCount +=1

			if self.fingRestartCount > 5:  # starts # 1
				self.indiLOG.log(30, "  (re)started FING 5 times, quiting ... reloading the plugin ")
				self.quitNOW = "FING problem"
				return -1
			
			## create directory if it does not exist
			try:
				subprocess.Popen("mkdir "+  self.indigoPreferencesPluginDir + "  > /dev/null 2>&1 &",shell=True)
			except:
				pass
	
			
			if os.path.exists(self.fingDataFileName):
				pass
			else:  ## if not create file
				subprocess.Popen("echo 0 > '"+ self.fingDataFileName+ "' &",shell=True )
				self.sleep(1)

			dataFileTimeOld = os.path.getmtime(self.fingDataFileName)  ## use for   if new filesize is longer  than old fs  fing is running


			if restartFing ==1:
				retCode = self.killFing("all")
			else:
				pids, parentPids = self.testFing()
				if len(pids) == 1 : return 1
				if len(pids) > 1 :
					retCode = self.killFing("onlyParents")
					return 1

 
			# start fing, send to background, dont wait, create 2 output files:  one table format file and one logfile
			if self.decideMyLog("StartFi"):	deblevelForStartFing = 20
			else:								deblevelForStartFing = 0
			
			params =  {"ppp":"&a3"+self.yourPassword[::-1]+"#5B", "theNetwork":self.theNetwork, "netwType":self.netwType,"logLevel": deblevelForStartFing, "fingEXEpath":self.fingEXEpath,"macUser":self.MACuserName, "pythonPath":self.pythonPath}
			f = open(self.indigoPreferencesPluginDir+"paramsForStart","w")
			f.write(json.dumps(params))
			f.close()
			cmd = "'{}' '{}startfing.py' '{}paramsForStart'  &".format(self.pythonPath, self.pathToPlugin, self.indigoPreferencesPluginDir)

			if self.decideMyLog("StartFi"): self.indiLOG.log(10, "FING cmd= {}".format(cmd) )
			os.system(cmd)
			self.sleep( 1 )
			self.killFing("onlyParents")

			self.indiLOG.log(20, "Waiting for first data from FING")

			found = False
			for ii in range(5):
				for kk in range(20):
					self.sleep( 1 )
				try:	gtime = os.path.getmtime(self.fingDataFileName)
				except: continue
				self.indiLOG.log(10, "Checking if FING created output, old timeStamp:{}; new timeStamp:{}".format(dataFileTimeOld, gtime) )
				if dataFileTimeOld != os.path.getmtime(self.fingDataFileName):
					found = True
					self.indiLOG.log(20, "Initializing ..  FING created new data   waiting ~ 1 minute for stable operation")
					break
			if not found: 
				self.indiLOG.log(20, "Initializing .. FING data file not created, return")
				return 0

		
			#test if it is actually running
			pids, parentPids = self.testFing()
			self.indiLOG.log(10, "FING Pids active after step3 = {}".format(pids))
			if len(pids) > 0:
				self.indiLOG.log(20, "..  (re)started FING, initialized")
				return 1

			self.indiLOG.log(30, "  (re)start FING not successful ")

			return 0 #  not successful
		except Exception:
			self.logger.error("", exc_info=True)
	
	
	
	
	
	
########################################
	def killFing(self,whomToKill):
		# all="all": kill fing and parents, if not just parents

		pids, parentPids = self.testFing()

		if self.decideMyLog("Logic"): self.indiLOG.log(10, "  killing FING Processes pids   " +whomToKill + " - " +"{}".format(pids))
		
		lenPid = len(pids)
		lenPidP = len(parentPids)

		pidsToKill =" "
		for kk in range (lenPidP):
			if parentPids[kk] != "1": pidsToKill += " "+parentPids[kk]
		
		if whomToKill ==  "all":
			for kk in range(lenPid):
				if pids[kk] != "1": pidsToKill += " "+pids[kk]


		if pidsToKill != " ":
			cmd = "echo '" + self.yourPassword + "' | sudo -S /bin/kill -9 " + pidsToKill +" > /dev/null 2>&1 &"
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "  FING kill cmd:" + cmd)
			ret, err = self.readPopen(cmd)
			#if self.decideMyLog("Logic"): self.indiLOG.log(10, "  FING kill ret= " +  "{}".format(ret))
			self.sleep(1)

		# check if successfull killed,  ps ... should return nothing
		pids, parentPids = self.testFing()
		if len(pids) >0:
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "  FING still running,  pids = " +  "{}".format(pids)+"--{}".format(parentPids))
			return 0
		return 1
		
		
########################################
	def killPing(self,whomToKill, ipnumber= "0.0.0.0"):
		if self.decideMyLog("Logic"): self.indiLOG.log(10, "killing ping jobs: {}".format(whomToKill))
		
		if whomToKill == "all":
			for theMAC in self.pingJobs:
				pid = self.pingJobs[theMAC]
				if int(pid) < 10 : continue
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "killing PID: {} - {}".format(theMAC, pid))
				ret, err = self.readPopen("/bin/kill {}".format(pid))
				self.pingJobs[theMAC] =-1

			ret, err = self.readPopen("ps -ef | grep 'do /sbin/ping' | grep -v grep | awk '{print$2}'")
			pids =ret.split()
				
			for pid  in pids:
				if int(pid) < 10: continue
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "killing PID: {}".format(pid))
				ret, err = self.readPopen("/bin/kill {}".format(pid))


			for i in range(1,2):
				try:
					os.remove("{}pings/*.ping".format(self.indigoPreferencesPluginDir))
				except:
					pass

		else:
			if whomToKill in self.pingJobs:
				pid = self.pingJobs[whomToKill]
				if int(pid) > 10:
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "killing : "+whomToKill +"-" +"{}".format(pid))
					ret, err = self.readPopen("/bin/kill {}".format(pid))
					self.pingJobs[whomToKill] =-1
			if ipnumber != "0.0.0.0":
				try:
					fname= ipnumber.split(".")[3]
					os.remove("{}pings/{}.ping".format(self.indigoPreferencesPluginDir, fname))
				except:
					pass

		return
		
########################################
	def killPGM(self,whomToKill):
		if self.decideMyLog("Logic"): self.indiLOG.log(10, "killing pgm: {}".format(whomToKill))

		ret, err = self.readPopen("ps -ef | grep '{}' | grep -v grep | awk '{{print$2}}'".format(whomToKill))
		pids =ret.split()
			
		for pid  in pids:
			if int(pid) < 10: continue
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "killing PID: {}".format(pid))
			ret, err = self.readPopen( "echo '{}' | sudo -S /bin/kill -9 {}".format(self.yourPassword, pid))
		return 	
		
########################################
	def testFing(self):
		if self.decideMyLog("Logic"): self.indiLOG.log(10, "testing if FING is running ")


		ret, err = self.readPopen("ps -ef | grep fing.bin | grep -v grep | grep -v fingscan| grep -v Indigo | awk '{print$2,$3}'")
		pids =ret.strip("\n")
		pids = pids.split("\n")
		fingPids=[]
		parentPids=[]
		if self.decideMyLog("Logic"): self.indiLOG.log(10, "  FING running pids2= ".format(pids))
		
		for kk in range(len(pids)):
			p = pids[kk].split(" ")
			if len(p)==0: continue
			fingPids.append(p[0])
			if len(p)!=2: continue
			if p[1] == "1": continue
			if p[1] == "0": continue
			if p[1] == " ": continue
			parentPids.append(p[1])
			# pids has the process ids #  of fing and parent shell as simple string have removed PID # 1 = the root
		return fingPids, parentPids
	
	
	
	
########################################
	def getfingLog(self):
		## get size of finglog file to check if there is new data
		try:
			if not os.path.isfile(self.fingLogFileName): return 0
			self.fingLogFileSizeNEW = int(os.path.getsize(self.fingLogFileName))
			if self.decideMyLog("Logic"): 
				if self.fingLogFileSizeold == self.fingLogFileSizeNEW and time.time() - self.timeOfStart < 50:
					self.indiLOG.log(10, "  FING LOG data ==> no change  file size: {}".format(self.fingLogFileSizeNEW))
			if self.fingLogFileSizeold != self.fingLogFileSizeNEW:
				self.fingLogFileSizeold = self.fingLogFileSizeNEW
				if self.decideMyLog("Logic"): 
					self.indiLOG.log(10, "  FING LOG data ==> changed    file size: {}".format(self.fingLogFileSizeNEW))
			
			## get last line of finglog file

				lines, err = self.readPopen(["tail", "-1", self.fingLogFileName])
				self.fingData = []
				for line in lines.split("\n"):
					if len(line) < 10: continue
					self.fingData.append(line.split(";"))
				if  self.decideMyLog("Logic"): self.indiLOG.log(10, "fing.log tail -1 line: {}".format(self.fingData) )
				if len(self.fingData[0]) < 7: return 0
				if self.fingData[0][5] in self.ignoredMAC: return 0
				self.indigoNeedsUpdate = True

				self.fingNumberOfdevices = 1
				self.fingDate            = self.column(self.fingData,0)
				self.fingStatus          = self.column(self.fingData,1)
				self.fingIPNumbers       = self.column(self.fingData,2)
				self.fingDeviceInfo      = self.column(self.fingData,4)
				self.fingMACNumbers      = self.column(self.fingData,5)
				self.fingVendor          = self.column(self.fingData,6)
				self.finglogerrorCount   = 0
				for kk in range(1):
					theMAC = self.fingMACNumbers[kk]
					if self.fingStatus[kk] == "up":
						if theMAC in self.inbetweenPing:	# if this is listed as down in inbetween pings, remove as we have new info.
							del self.inbetweenPing[theMAC]
						if  self.decideMyLog("Logic"): self.indiLOG.log(10, "fing.log status  --> UP for MAC#:{}".format(theMAC) )

					if self.fingStatus[kk] == "down":
						if  self.decideMyLog("Logic"): self.indiLOG.log(10, "fing.log status  --> down for MAC#:{}".format(theMAC) )
						if theMAC in self.allDeviceInfo and self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:  
							if self.sendWakewOnLanAndPing(theMAC,nBC= 2, waitForPing=500, countPings=2, waitBeforePing = 0.5, waitAfterPing = 0.1, calledFrom="getfingLog") ==0:
								self.fingStatus[kk] == "up"

					self.fingDate[kk] = self.fingDate[kk].replace("/", "-")
				return 1
			else:
				return 0
		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "{}".format(self.fingData))
			self.finglogerrorCount +=1
			if self.finglogerrorCount > 40 and self.totalLoopCounter > 100 :
				self.indiLOG.log(40, "fing.log file does not exist or is empty \n    trying to stop and restart fing  " )
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
				lines = f.read().strip("\n").split("\n")
				f.close()
				self.fingData = [ line.split(";") for line in lines ]
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
					theMAC = self.fingMACNumbers[kk]
					if theMAC in self.ignoredMAC: 
						removeMAC.append(kk)
						continue
					if theMAC in self.doubleIPnumbers:
						self.doubleIPnumbers[theMAC].append(self.fingIPNumbers[kk])
					else:
						self.doubleIPnumbers[theMAC]=[self.fingIPNumbers[kk]]
					if self.fingMACNumbers[kk] in self.inbetweenPing:	# if this is listed as down in inbetween pings, remove as we have new info.
						if self.fingStatus[kk] == "up":
							del self.inbetweenPing[self.fingMACNumbers[kk]]
					self.fingDate[kk] = self.fingDate[kk].replace("/", "-")

					if theMAC not in self.allDeviceInfo:
						self.allDeviceInfo[theMAC] = copy.copy(emptyAllDeviceInfo)
						self.allDeviceInfo[theMAC]["status"] = self.fingStatus[kk]
						self.allDeviceInfo[theMAC]["ipNumber"] = self.fingIPNumbers[kk]
						self.allDeviceInfo[theMAC]["hardwareVendor"] = self.fingDeviceInfo[kk]
							
					if self.fingStatus[kk] == "up" and self.allDeviceInfo[theMAC]["status"] != "up":
							if self.decideMyLog("Logic"): self.indiLOG.log(10, "fing.data status down --> up MAC#:{}".format(theMAC) )

					if self.fingStatus[kk] == "down" and len(self.fingDate[kk]) > 5:
						if theMAC in self.allDeviceInfo: 
							if self.allDeviceInfo[theMAC]["status"] == "up":
								if self.decideMyLog("Logic"): self.indiLOG.log(10, "fing.data status UP --> down for MAC#:{}".format(theMAC) )
							if "useWakeOnLanSecs" in self.allDeviceInfo[theMAC]:
								if self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:  
									if self.sendWakewOnLanAndPing(theMAC,nBC= 1, waitForPing=500, countPings=1, waitBeforePing = 0.2, waitAfterPing = 0.0, calledFrom="getfingData") ==0:
										self.fingStatus[kk] = "up"
										self.fingDate[kk] = nowdate.strftime("%Y-%m-%d %H:%M:%S")
							else:
								self.indiLOG.log(30, "error: useWakeOnLanSecs not in devI for MAC#:{} devI=\n{}".format(theMAC, self.allDeviceInfo[theMAC])) 
								
						deltaseconds = (  nowdate - datetime.datetime.strptime(self.fingDate[kk], "%Y-%m-%d %H:%M:%S")  ).total_seconds() 
						if deltaseconds > 70 : 
							removeMAC.append(kk)

				for kk in removeMAC[::-1]:
					del self.fingVendor[kk]
					del self.fingIPNumbers [kk]
					del self.fingStatus[kk]
					del self.fingDate[kk]
					del self.fingDeviceInfo[kk]
					del self.fingMACNumbers[kk]
				self.fingNumberOfdevices = len(self.fingVendor) 
				 
				return 1
		except Exception:
			self.logger.error("", exc_info=True)
			self.fingDataErrorCount +=1
			if self.fingDataErrorCount > 1 :
				self.indiLOG.log(30, "fing.data file does not exist \n    trying {}".format(5-self.fingDataErrorCount)+" more times")
				if self.fingDataErrorCount == 5:
					self.indiLOG.log(30, "   trying to stop and restart fing  " )
					self.initFing(1)  # restarting fing
					self.indiLOG.log(30, "   restarted fing  " )
					self.fingDataErrorCount =0
			else:
				return 0
		return 0
########################################
	def testfingError(self):
		fingOK1 = 0
		try:
			resp, err = self.readPopen('grep \'0/0 hosts up\' '+ self.fingErrorFileName)
			if len(resp) > 1  :  fingOK1 = 1
		except:
			pass
		fingOK2 = 0
		try:
			resp, err = self.readPopen('grep \'error\' ' + self.fingErrorFileName)
			if len(resp) > 1  :  fingOK2 = 1
		except:
			pass
		try:
			resp, err = self.readPopen("echo 0 > "+ self.fingErrorFileName)
		except:
			pass
		if fingOK1 >0 or fingOK1 > 0:
			self.fingDataErrorCount2 +=1
			self.indiLOG.log(40, " ERROR:  FING message -- network is not working  codes  0/0 hosts .. error codes:   " + "{}".format(fingOK1) + "{}".format(fingOK2) )
			if self.fingDataErrorCount2 > 1:
				self.indiLOG.log(40, "  relaunching plugin")
				self.quitNOW = "FING problem 2"
		else:
			self.fingDataErrorCount2 =0
		

		return fingOK1 +  fingOK2
	
########################################
	def checkIndigoVersion(self):

		try:  ## test if any data and if version 2, if yes, return
			theTest = indigo.variables["ipDevice01"]
			theTest = theTest.value
			if len (theTest) < 5:  # variable exists, but empty or too short  should be 8 or 9
				self.quitNOW = "Indigo variable error 1"
				self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice01 \n    please check if it has bad data, in doubt delete and let the program recreate  \n    stopping fingscan " )
				return 1
			theValue = theTest.split(";")
			if theValue[0].strip().count(":") == 5:
				test = self.getIndigoIpVariablesIntoData()
				return 0  ## version 2 nothing to do
		except Exception as exc:
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
					self.quitNOW = "Indigo variable error 2"
					self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice" + ii00 +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				theValue = theTest.split(";")
				macNO = theValue[1].strip()
				if macNO.count(":") != 5:
					self.quitNOW = "Indigo variable error 3"
					self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice" + ii00  +"\n  MAC number does not seem to be real MAC number" + theValue[0].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				ipNO =theValue[2].strip()
				if ipNO.count(".") != 3:
					self.quitNOW = "Indigo variable error 4"
					self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice" + ii00 +"\n  IP number does not seem to be real IP number" + theValue[1].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
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
			self.indigoNumberOfdevices	= 0
			self.indigoDevicesValues	= []
			self.indigoDevicesNumbers	= []
			self.indigoEmpty			= []
			self.indigoIndexEmpty		= 0
			self.indigoIpVariableData	= {}
			self.indigoNumberOfdevices	= 0

			for ii in range(1,indigoMaxDevices):
				ii00 = self.int2hexFor2Digit(ii)
				skip = 0
				try:
					theTest = indigo.variables["ipDevice"+ii00]
				except Exception as exc:
					self.indigoEmpty.append(ii00)
					self.indigoIndexEmpty += 1
					continue
				skip = 1
				theTest = theTest.value
				if len (theTest) < 5:  # that is minimum, should be 8 or 9
					skip = 1
					self.quitNOW = "Indigo variable error 6"
					self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice" + ii00 +";  deleting and letting the program recreate " )
					indigo.variable.delete("ipDevice"+ii00)
					continue
				theValue = theTest.split(";")

				while len(theValue) < 10:
					theValue.append("")

				skip = "no"
				self.indigoNumberOfdevices += 1
				self.indigoDevicesValues.append(theTest)
				self.indigoDevicesNumbers.append(ii00)
				theMAC =theValue[0].strip()
				if theValue[0].strip().count(":") != 5:
					skip = 1
					self.quitNOW = "Indigo variable error 7"
					self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice" + ii00 +"  MAC number does not seem to be real MAC number>>" + theValue[0].strip() +"<<  deleting and letting the program recreate " )
					indigo.variable.delete("ipDevice"+ii00)
					continue



				if theValue[1].strip().count(".") != 3:
					skip = 1
					self.quitNOW = "Indigo variable error 8"
					self.indiLOG.log(40, "getting data from indigo: bad variable ipDevice" + ii00 +"  IP number does not seem to be real IP number>>" + theValue[1].strip() +"<<\  deleting and letting the program recreate  " )
					indigo.variable.delete("ipDevice"+ii00)
					continue

				self.indigoIpVariableData[theMAC]=copy.deepcopy(emptyindigoIpVariableData)
				devV = self.indigoIpVariableData[theMAC]
				devV["ipNumber"]			= theValue[1].strip()
				devV["timeOfLastChange"]	= theValue[2].strip()
				devV["status"]				= theValue[3].strip()
				try:
					devV["noOfChanges"]	= int(theValue[4].strip())
				except:
					devV["noOfChanges"]	= 0
				devV["nickName"]			= theValue[5].strip()
				devV["hardwareVendor"]		= theValue[6].strip()
				devV["deviceInfo"]			= theValue[7].strip()
				try:
					devV["WiFi"]			= theValue[8].strip()
				except:
					devV["WiFi"]			= ""
				try:
					devV["usePing"]		= theValue[9].strip()
				except:
					devV["usePing"]		= "noPing-0"
				
				devV["ipDevice"]			= ii00
				devV["index"]				= self.indigoNumberOfdevices-1
				

			try:
				self.indigoStoredNoOfDevices = indigo.variables["ipDevsNoOfDevices"]
			except Exception as e:
				self.quitNOW = "Indigo variable error 9"  ## someting must be wrong, lets restart
				self.logger.error("getting data from indigo: bad variable ipDevsNoOfDevices \n   please check if it has bad data, in doubt delete and let the program recreate  stopping fingscan", exc_info=True)
		except Exception:
			self.logger.error("", exc_info=True)


		return
########################################
	def doInbetweenPing(self,force = False):
		try:
			sleepT = max(self.sleepTime/2., 1)
			pingWait = 900  #milli seconds
			maxOldTimeStamp = max(sleepT +pingWait/1000. +0.5,2)
			maxPingsBeforeReset= int(5.*60./(pingWait/1000.+sleepT)) # around 5 minutes equiv
	#		if self.decideMyLog("Ping"): self.indiLOG.log(10, "doInbetweenPing force= {}".format(force))
	#		if self.decideMyLog("Ping"): self.indiLOG.log(10, "ping parameters: %5.2f   %5.2f   %5.2f   %5.2f "%(sleepT,pingWait,maxOldTimeStamp,maxPingsBeforeReset))
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
					if devI["usePing"] in ["usePingifDown", "usePingifUPdown"]:
						retcode = 1
						if devI["useWakeOnLanSecs"] > 0:
							devI["useWakeOnLanLast"] = time.time()
							self.sendWakewOnLan(theMAC, calledFrom= "doInbetweenPing")
							self.sleep(0.5)
						retCode = self.checkPing(theMAC, waitForPing=pingWait, countPings=2, waitAfterPing = 0.1 )
						if self.decideMyLog("Ping"): self.indiLOG.log(10, "pinged "+ theMAC+"; retcode={}".format(retCode)+";  useWakeOnLan:{}".format(devI["useWakeOnLanSecs"]) )
						if retcode !=0: 
							self.inbetweenPing[theMAC] = "down"
						else:
							devI["status"] = "up"
							self.inbetweenPing[theMAC] = "up"
						continue

				if devI["status"] == "up" and devI["usePing"] in ["usePingifUP", "usePingifUPdown"]:
					ipN = devI["ipNumber"].split("-")[0]# just in case ...it is "-changed"
					nPing +=1
					if self.inbetweenPingType == "parallel":
						cmd = "for ((i=0;i<{};i++)); do /sbin/ping -c 2 -W {} -o {} &>/dev/null  && echo up > '{}pings/{}.ping' && sleep {}; done".format(maxPingsBeforeReset, pingWait, ipN, self.indigoPreferencesPluginDir, ipN.split(".")[3], sleepT)
						if theMAC in self.pingJobs:
							pingPid = self.pingJobs[theMAC]
							if pingPid >0:
								try:
									if time.time() - os.path.getmtime(self.indigoPreferencesPluginDir+"pings/"+ipN.split(".")[3]+".ping") < maxOldTimeStamp: # this will "except if it does not exist
										self.inbetweenPing[theMAC] = "up"
										self.excludeMacFromPing[theMAC] = -99999999 # it answered at least once, never never firewall again
										continue # all done still up
									resp, err = self.readPopen("ps -ef  | grep ' {} ' | grep {} | grep -v grep".format(pingPid, ipN))
									ok = resp.find(cmd[:50]) > -1
									if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping cheking if ping is running for {} grep  result:\n{}".format(ipN, resp))
									if ok:
										if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping file for {} older than  : {} secs".format(ipN, maxOldTimeStamp))
										self.inbetweenPing[theMAC] = "down"
										self.updateIndigoIpDeviceFromDeviceData(theMAC, ["status"],justStatus= "down")
										oneDown =  True
										self.killPing (theMAC,ipnumber =ipN)
										pingPid = -1
										continue
								except:
									resp, err = self.readPopen("ps -ef  | grep ' {} ' | grep {} | grep -v grep".format(pingPid, ipN) )
									ok = resp.find(cmd[:50]) > -1
									if ok: # still running?
											if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping file  not created , device is down "+ipN)
											self.killPing (theMAC)# yes, kill it
											if self.excludeMacFromPing[theMAC] <0: continue
											if self.checkIfFirewalled(devI["deviceName"],theMAC, ipN) > 0: continue
									else:
											if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping shell loop not running: {}".format(cmd[:50]))
										
						pid = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).pid
						self.pingJobs[theMAC] = pid
						if self.decideMyLog("Ping"): self.indiLOG.log(10, "launching ping cmd:"+cmd)
						if self.decideMyLog("Ping"): self.indiLOG.log(10, " ... {} pid= {} theMAC= {} timestamp={}".format(ipN, pid, theMAC, datetime.datetime.now().strftime("%M:%S")))
						continue
					
						
					if self.inbetweenPingType == "sequential":
					   #if self.decideMyLog("Ping"): self.indiLOG.log(10, "launching ping for : "+ipN +"  theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
						looptimes.append(time.time()-lptime)
						lptime=time.time()
						npTime=time.time()
						#   c 1: do 1 ping;  w: wait 800 msec; o: short output, q: quit if one response
						retCode = self.checkPing(theMAC, waitForPing=pingWait, countPings=2, waitAfterPing = 0.1)
						pingtimes.append(time.time()-npTime)
						if retCode > 0:  # ret code = 2 : no response ==> "down"
							#if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping response: {}".format(resp).strip() )
							if self.excludeMacFromPing[theMAC] >=0:
								msg=False
								if self.checkIfFirewalled(devI["deviceName"],theMAC, ipN) >0: continue
							if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping for  IP "+ipN +"  theMAC="  +theMAC +" timed out, status DOWN")
							self.inbetweenPing[theMAC] = "down"
							self.updateIndigoIpDeviceFromDeviceData(theMAC, ["status"], justStatus= "down")
							oneDown=True
						else:
							self.inbetweenPing[theMAC] = "up"
							self.excludeMacFromPing[theMAC] = -99999999 # it answered at least once, never test never firewall again
					#						if self.decideMyLog("Ping"): self.indiLOG.log(10, " ping ok : "+ipN +"  theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
					continue
						
						
	#		looptimes.append(time.time()-lptime)
	#		del looptimes[0]
			totalTime = time.time()-ticks
			if totalTime < 2  and msg: self.throttlePing = 0
			if totalTime > 4  and msg: self.throttlePing = 1
			if totalTime > 8  and msg: self.throttlePing = 2
			if totalTime > 12 and msg: self.throttlePing = 4
			if totalTime > 25 and msg: self.throttlePing = 8
	#		if self.decideMyLog("Ping"): self.indiLOG.log(10, " nPings      : {}".format(nPing) + "         seconds used: {}".format(totalTime) + " throttlePing: " + "{}".format(self.throttlePing))
	#		if self.decideMyLog("Ping"): self.indiLOG.log(10, " nPings      : {}".format(nPing) + "         seconds used: {}".format(totalTime) + " throttlePing: " + "{}".format(self.throttlePing)+" {}".format(max(pingtimes)))
	#		if self.decideMyLog("Ping"): self.indiLOG.log(10, " seconds loop: {}".format( [("%1.2f" %looptimes[k]) for k in range(len(looptimes)) ] )  )
	#		if self.decideMyLog("Ping"): self.indiLOG.log(10, " seconds ping: {}".format( [("%1.2f" %pingtimes[k]) for k in range(len(pingtimes))])  )
			if self.inbetweenPingType == "sequential" and len(pingtimes) >0: 
				if self.decideMyLog("Ping"): self.indiLOG.log(10, "time used for PINGing {}".format(nPing) + " times: %2.2f"%totalTime+" seconds needed;   max ping time: %2.2f"%max(pingtimes) )



		except Exception:
			self.logger.error("", exc_info=True)
		
		return oneDown


########################################
	def checkIfFirewalled(self, devName,theMAC, ipN):
		try:
			if theMAC not in self.excludeMacFromPing: self.excludeMacFromPing[theMAC] =0 # start the counter
			if self.decideMyLog("Ping"): self.indiLOG.log(10, "testing if  "+devName+"/"+theMAC +"/"+ipN+"  is firewalled, does not answer to PINGs (%1d"%(self.excludeMacFromPing[theMAC]+1)+"/3 tests)" )
			ret, err = self.readPopen("echo '"+self.yourPassword+"' | sudo -S '"+self.fingEXEpath+"' -s "+ipN)
			if ret.find("incorrect password attempt")>-1:
				self.indiLOG.log(40, "incorrect password  in config, please correct")
				return 3
			if self.decideMyLog("Ping"): self.indiLOG.log(10,"{}".format(ret).replace("--","").replace("  ","") )
			if ret.find("host unreachable") >-1:
				self.excludeMacFromPing[theMAC] +=1
				return 1
			if ret.find("no service found, firewalled")>-1 or(
			   ret.find("Non positive scan results")>-1 and ret.find("no service found")>-1) or(
			   ret.find("Detected firewall")>-1):
				self.excludeMacFromPing[theMAC] +=1
				if self.excludeMacFromPing[theMAC] > 2:
					if self.decideMyLog("Ping"): self.indiLOG.log(10, "excluding "+devName+"/"+theMAC +"/"+ipN+" from PING test as it is firewalled or does not answer on any port(%1d"%(self.excludeMacFromPing[theMAC])+"/3 tests)" )
					return 3
				return 1

		except Exception:
			self.logger.error("", exc_info=True)

		return 0



########################################
	def getIdandName(self,name):
		if name== "0": return "", "0", "0"
		if name== "1": return "", "1", "1"
		
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
				if self.decideMyLog("iFind"): self.indiLOG.log(10, "trigger actionFrom  :  {}".format(self.callingPluginName[ii])+ " {}".format(self.callingPluginCommand[ii]))
				plug = indigo.server.getPlugin(self.callingPluginName[ii])
				if not plug.isEnabled():
					if self.decideMyLog("iFind"): self.indiLOG.log(10, "trigger actionFrom Plugin  not enabled:  {}".format(plug)+ " {}".format(self.callingPluginCommand))
					continue
				try:
					idevId= self.callingPluginCommand[ii]
				except:
					if self.decideMyLog("iFind"): self.indiLOG.log(10, "triggerFromPlugin  no msg:  {}".format(plug)+ " {}".format(self.idevId))
					continue

				idevD,idevName,idevId = self.getIdandName(idevId)
				
				if idevName =="":
					if self.decideMyLog("iFind"): self.indiLOG.log(10, "params for iFind  idevName empty" )
					continue
				try:
					distance					= float(idevD.states["distanceHome"])			# distance from home
					distanceUnits				= idevD.states["distanceUnits"]					# convert to meters if needed, find ft or m and if display different from number
					deviceTimeChecked			= time.mktime(time.strptime(idevD.states["deviceTimeChecked"], "%a %b %d %H:%M:%S %Y")) # format:  Thu Mar  3 07:32:49 2016  deviceTimeChecked of "iphone " in seconds
					timeNextUpdate				= float(idevD.states["timeNextUpdate"])			#  time in secs of next check
					iFindMethod					= idevD.states["calculateMethod"]				#  using avriable input or iFind nternal method
				except:
					if self.decideMyLog("iFind"): self.indiLOG.log(10, "get params from iFind   not working:")
					continue
				if distanceUnits.find("kilometres")>-1:	distance *=  kmMeters
				elif distanceUnits.find("miles")>-1:	distance *= milesMeters

				found = False
				#if self.decideMyLog("iFind"): self.indiLOG.log(10, "testing: iDeviceName  " +"{}".format(idevName) +" {}".format(idevId) )
				for n in self.EVENTS:
					evnt= self.EVENTS[n]
					found =0
					for nDev in evnt["iDeviceName"]:
						if evnt["iDeviceName"][nDev]=="": continue
						if "{}".format(evnt["iDeviceName"][nDev])== "-1": continue
						found +=1
						#if self.decideMyLog("iFind"): self.indiLOG.log(10, "trying iDeviceName  " +"{}".format(evnt["iDeviceName"][nDev]) +";  nDev{}".format(nDev) +";  nEvent{}".format(n) )
					
						if  "{}".format(evnt["iDeviceName"][nDev]) == "{}".format(idevId) or "{}".format(evnt["iDeviceName"][nDev]) == "{}".format(idevName):
							found =10000
							break
					if  found > 0 and  found < 10000:
						#if self.decideMyLog("iFind"): self.indiLOG.log(10, "iDeviceName not found:  " +"{}".format(idevName) +" {}".format(idevId) )
						continue
					if  found  == 0: continue
					#if self.decideMyLog("iFind"): self.indiLOG.log(10, "iDeviceName  found:  " +"{}".format(idevName) +" {}".format(idevId) +";  nDev{}".format(nDev) +";  nEvent{}".format(n)+";  iDeviceName"+  "{}".format(evnt["iDeviceName"][nDev]))
					
					if deviceTimeChecked > float(evnt["iUpdateSecs"][nDev]) +1 :  # new info
						
						evnt["iSpeedLast"][nDev]		= evnt["iSpeed"][nDev]
						evnt["iDistanceLast"][nDev]	= evnt["iDistance"][nDev]
						evnt["iUpdateSecsLast"][nDev]	= evnt["iUpdateSecs"][nDev]
						evnt["iDistance"][nDev]		= distance
						evnt["iUpdateSecs"][nDev]		= deviceTimeChecked
						evnt["itimeNextUpdate"][nDev]	= timeNextUpdate
						dTime 							= evnt["iUpdateSecs"][nDev]  - evnt["iUpdateSecsLast"][nDev]
						dDist							= evnt["iDistance"][nDev]    - evnt["iDistanceLast"][nDev]  
						speed							= dDist  /   max(dTime,1.)
						evnt["iSpeed"][nDev]			= speed
						if self.decideMyLog("iFind"): self.indiLOG.log(10, "iFind old:  distance " +"%6.1f"%(evnt["iDistanceLast"][nDev])+ "; deviceTimeChecked " +"%6.1f"%(time.time()-evnt["iUpdateSecsLast"][nDev])+ ";  speed " +"%6.2f"%(evnt["iSpeedLast"][nDev])+";  ndev# {}".format(nDev))
						if self.decideMyLog("iFind"): self.indiLOG.log(10, "      new:  distance " +"%6.1f"%(evnt["iDistance"][nDev])    + "; deviceTimeChecked " +"%6.1f"%(time.time()-evnt["iUpdateSecs"][nDev])    + ";  speed " +"%6.2f"%(evnt["iSpeed"][nDev])    +";  dDist " +"%6.2f"%(dDist)+";  dTime " +"%6.0f"%(dTime))
					else:
						if self.decideMyLog("iFind"): self.indiLOG.log(10, "iFind trigger delivered no new data")
					evnt["iFindMethod"][nDev]			= iFindMethod
					
						
		except Exception:
			self.logger.error("", exc_info=True)

		self.triggerFromPlugin		= False
		self.callingPluginName=[]
		self.callingPluginCommand=[]
		return

########################################
	def checkTriggers(self):
		try:
	#		if self.decideMyLog("Events"): self.indiLOG.log(10, "<<<--- entering checkTriggers")
			for nEvent in self.EVENTS:
				timeNowNumberSecs = time.time()
				timeNowm2 = int(timeNowNumberSecs-2.) ## drop the 10th of seconds
				timeNowHMS = datetime.datetime.now().strftime("%H:%M:%S")
				ticks = time.time()
				evnt=self.EVENTS[nEvent]
				InfoTimeStampSecs =0
	#			if self.decideMyLog("Events"): self.indiLOG.log(10,
	#			" nevents "+nEvents+
	#			" EVENTS{}".format(self.EVENTS[nEvent])
	#			)
				if nEvent == "0": continue
				if evnt == "0": continue
				if evnt == "": continue
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

				evnt["nHome"]  = 0		
				evnt["nAway"]  = 0		

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
					#self.indiLOG.log(10, "nDev {}".format(nDev) +" AwayTime[nDev]{}".format(AwayTime[nDev]) )
					minAwayTime = min(minAwayTime,AwayTime[nDev])  #################### need to check
					maxAwayTime = max(maxAwayTime,AwayTime[nDev])
					HomeTime[nDev] = timeNowm2-float(evnt["secondsOfLastON"][nDev])
					minHomeTime = min(minHomeTime,HomeTime[nDev])
					maxHomeTime = max(maxHomeTime,HomeTime[nDev])

				for nDev in evnt["IPdeviceMACnumber"]:
					status = "0"
					if evnt["IPdeviceMACnumber"][nDev] == "0": continue
					if evnt["IPdeviceMACnumber"][nDev] == "": continue
					iDev = int(nDev)
					theMAC =evnt["IPdeviceMACnumber"][nDev]
					##self.indiLOG.log(10, " in trigger idev"+ nDev+"  "+ theMAC)
					if iDev< piBeaconStart:
						if len(theMAC) < 16:
							if self.decideMyLog("Events"): self.indiLOG.log(10, "theMAC=0")
							continue
						if not theMAC in self.allDeviceInfo:
							if self.decideMyLog("Ping"): self.indiLOG.log(10, "mac number "+theMAC+"\n   not present in data, deleting EVENT/device source for trigger" )
							evnt["IPdeviceMACnumber"][nDev] = "0"
							break
						devI= self.allDeviceInfo[theMAC]
						status		= devI["status"]
					elif iDev< piBeaconStart:
						status = "0"

					elif iDev< unifiStart:  ## check piBeacon devices
						try:
							status		= self.piBeaconDevices[theMAC]["currentStatus"]
						except:
							self.getpiBeaconAvailable()
							self.updatepiBeacons()
							if len(self.piBeaconDevices) ==0:
								status = "0"
							else:
								try:
									status = self.piBeaconDevices[theMAC]["currentStatus"]
								except:
									self.logger.error("error in checkTriggers, indigoID# "+theMAC+" not in piBeacondevices  :  " + "{}".format(self.piBeaconDevices)[0:100]+" ..  is  piBeacon plugin active? ", exc_info=True)
									status = "0"
									del self.piBeaconDevices[theMAC]
					elif iDev >= unifiStart:  ## check unifi devices
						try:
							status		= self.unifiDevices[theMAC]["currentStatus"]
						except:
							self.getUnifiAvailable()
							self.updateUnifi()
							if len(self.unifiDevices) ==0:
								status = "0"
							else:
								try:
									status = self.unifiDevices[theMAC]["currentStatus"]
								except Exception as e:
									self.logger.error("error in checkTriggers, indigoID# "+theMAC+" not in unifidevices  :  " + "{}".format(self.unifiDevices)[0:100]+" ..  is  unifi plugin active? ", exc_info=True)
									del self.unifiDevices[theMAC]
									status =  "0"



					## check iFind devcies
					metersH = -8888888888
					metersA = -1.
					if len(evnt["iDeviceName"][nDev]) > 1 and (
						evnt["iDeviceUseForAway"][nDev] == "1" or
						evnt["iDeviceUseForHome"][nDev] == "1"): 
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
									indigo.variable.create(varname, "99")
								except Exception as e:    
									self.logger.error("could not read or create variable  "+varname+" for iFind communication, ignoring iFind communication", exc_info=True)
									continue
							
							
							nextTimeToCheck= evnt["nextTimeToCheck"][nDev] # set to some default
							if status != "up":  # if not in IP range use iFind
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
									if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind after speed calc  nextTimeToCheck: {}".format(nextTimeToCheck)+" speed: {}".format(speed)+" iMaxSpeed: {}".format(evnt["iMaxSpeed"][nDev])  )
										 
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
								if evnt["iFindMethod"][nDev] != "Calculated":
									if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : switching method to OFF")
									if evnt["iFindMethod"][nDev] !="Calculated":
										if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : switching method to OFF (2)")
										plug.executeAction("refreshFrequencyOff", idevId)
										evnt["iFindMethod"][nDev] = "Calculated"
							
											
							elif distance > float(evnt["distanceHomeLimit"]): ## not FAR AWAY, but not home 
									if indigo.variables[varname].value != "{}".format(int(nextTimeToCheck)):
										indigo.variable.updateValue(varname,"{}".format(int(nextTimeToCheck)))
									if   nextTimeToCheck < timeNextUpdate -time.time() :
										if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : switching method to Variable (On)")
										plug.executeAction("refreshFrequencyOn", idevId)
										evnt["iFindMethod"][nDev] = "Variable"
									else:
										if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : no need to refresh")

							else:  # we are at home do things slowly ..
									if status != "up" :# if the other indicators believe it is away do an iFind update
										if time.time() - float(evnt["secondsOfLastOFF"][nDev]) > 600: #after 15 minutes switch back to calculated
											if evnt["iFindMethod"][nDev] == "Variable":
												evnt["iFindMethod"][nDev] = "Calculated"
												if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : switching method to OFF (1)")
												plug.executeAction("refreshFrequencyOff", idevId)
												if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : at home, do it slowly (1)")
										else:  # check ifind, then set nextTime to 60 secs, see how it works
											if evnt["iFindMethod"][nDev] != "Variable":  
												evnt["iFindMethod"][nDev] = "Variable"
												if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : at home, but do a refresh iFind as wifi just turned off  secondsOfLastOFF: " + "{}".format(evnt["secondsOfLastOFF"][nDev])+ ";  iUpdateSecs: {}".format(evnt["iUpdateSecs"][nDev]) )
												nextTimeToCheck =60 #set to 1 minutes
												evnt["nextTimeToCheck"][nDev]=  nextTimeToCheck
												if indigo.variables[varname].value != "{}".format(int(nextTimeToCheck)): indigo.variable.updateValue(varname,"{}".format(int(nextTimeToCheck)))
												plug.executeAction("refreshFrequencyOn", idevId)
									else:
											evnt["iMaxSpeed"][nDev]=1.003
											if evnt["iFindMethod"][nDev] != "Calculated":
												if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : switching method to OFF (2)")
												evnt["iFindMethod"][nDev] = "Calculated"
												plug.executeAction("refreshFrequencyOff", idevId)
											if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind time : at home, do it slowly (2)")


							if self.decideMyLog("iFind"): self.indiLOG.log(10,
									 "ifind time UpdSec: "		+ "{}".format(int( time.time() - float(pluginUpdateSecs) ))
									+";  lastUpdLast: "		+ "{}".format(int( time.time() - float(evnt["iUpdateSecs"][nDev]) ))
									+";  speed: "				+ "%7.3f"%speed
									+";  iMaxSpeed: "			+ "%7.3f"%evnt["iMaxSpeed"][nDev]
									+";  nextTimeToCheck: "	+ "{}".format(int(nextTimeToCheck))
									+";  timeNextUpdate: "		+ "{}".format(int(timeNextUpdate -time.time()))
									+";  secondsOfLastOFF: "	+ "{}".format(int(time.time()- float(evnt["secondsOfLastOFF"][nDev])))
									+";  newDistance: "		+ "{}".format(int(distance))
									+";  status: "				+ "{}".format(status	)
									+";  iFindMethod: "		+ "{}".format(evnt["iFindMethod"][nDev]	)
									)

						else:
							if self.decideMyLog("iFind"): self.indiLOG.log(10, "iFind is not enabled, please enable plugin or disable use of iFind in FINGSCAN")
							metersH=-7777777777
							metersA=-2.
					else:
						metersH=-6666666666
						metersA=-3.
					if evnt["iDeviceUseForAway"][nDev] == "1": self.metersAway[nDev]	= metersA
					else:										 self.metersAway[nDev]	= -4.
					if evnt["iDeviceUseForHome"][nDev] == "1": self.metersHome[nDev]	= metersH
					else:										 self.metersHome[nDev]	= -555555555.

					if float(self.metersHome[nDev]) >0. and float(self.metersHome[nDev]) <= float(evnt["distanceHomeLimit"]):
						HomeDist[nDev] = True
					#if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind  metersHome: {}".format(self.metersHome[nDev]) + ";  distanceHomeLimit: {}".format(evnt["distanceHomeLimit"])+ ";  HomeDist[nDev]: {}".format(HomeDist[nDev]))
					
					if (float(self.metersAway[nDev]) >0  and float(self.metersAway[nDev])  <= float(evnt["distanceAwayLimit"])):
						evnt["secondsOfLastOFF"][nDev] = timeNowm2
						evnt["timeOfLastOFF"][nDev]= timeNowHMS
						AwayDist[nDev] = False
					#if self.decideMyLog("iFind"): self.indiLOG.log(10, "ifind  metersAway: {}".format(self.metersAway[nDev]) + ";  distanceAwayLimit: {}".format(evnt["distanceAwayLimit"])+ ";  AwayDist[nDev]: {}".format(AwayDist[nDev]))

					if status == "up":
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



				#if self.decideMyLog("Events"): self.indiLOG.log(10, "minHomeTime {}".format(minHomeTime)+ " " + "{}".format(HomeTime))
				#if self.decideMyLog("Events"): self.indiLOG.log(10, "minAwayTime {}".format(minAwayTime)+ " " + "{}".format(AwayTime))
				#if self.decideMyLog("Events"): self.indiLOG.log(10, "Dist: AWAY-{}".format(AwayDist)+"-- HOME-{}".format(HomeDist))
				#if self.decideMyLog("Events"): self.indiLOG.log(10, "Stat: AWAY-{}".format(AwayStat)+"-- HOME-{}".format(HomeStat))
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

				out = "checkTrigger\n"
				if self.decideMyLog("Events"): out+="EVENT# {}".format(nEvent).ljust(2)+"  Dev#  HomeStat".ljust(15)                         +"HomeTime".ljust(12)           +"HomeDist".ljust(13)          +"AwayStat".ljust(12)         +"AwayTime".ljust(12)           +"AwayDist".ljust(11)           +" oneHome"            +" allHome"             +"  oneAway"           +" allAWay"+"\n"
				for nDev in evnt["IPdeviceMACnumber"]:
					if evnt["IPdeviceMACnumber"][nDev] == "0": continue
					if evnt["IPdeviceMACnumber"][nDev] ==  "": continue
					evnt["iDeviceAwayDistance"][nDev]= "%5.3f"%self.metersAway[nDev]
					evnt["iDeviceHomeDistance"][nDev]= "%5.3f"%self.metersHome[nDev]
					if AwayStat[nDev] and evnt["currentStatusAway"][nDev] == "0" and (minAwayTime < 30 and False):  ### need to fix 
						out+="          "+  "nDev{}".format(nDev)+" AwayStat[nDev]{}".format(AwayStat[nDev])+" evnt[currentStatusAway][nDev]" + "{}".format(evnt["currentStatusAway"][nDev])+" minAwayTime" + "{}".format(minAwayTime)+"\n"
						self.redoAWAY= 10  # increase frequency of up/down test to 1 per second for 10 seconds
	#### away status
					if evnt["currentStatusAway"][nDev] == "0":
						if (AwayStat[nDev] and AwayDist[nDev]) :
							if float(evnt["minimumTimeAway"]) >0.:
								evnt["currentStatusAway"][nDev]	= "startedTimer"
								allAway = False  # added , was missing 
							else:
								evnt["currentStatusAway"][nDev]	= "AWAY"
								oneAway = True
								self.redoAWAY= 0
							evnt["secondsOfLastOFF"][nDev]= timeNowm2
							evnt["timeOfLastOFF"][nDev]= timeNowHMS
						else:
							allAway = False
					elif evnt["currentStatusAway"][nDev] == "startedTimer":
							if (AwayStat[nDev] and AwayDist[nDev]):
								if AwayTime[nDev] >= float(evnt["minimumTimeAway"]):
									evnt["currentStatusAway"][nDev] = "AWAY"
								else:    
									allAway = False
							else:    
								evnt["currentStatusAway"][nDev] = "0"
								allAway = False
					 
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
					if evnt["currentStatusAway"][nDev] == "AWAY":
						evnt["nAway"] += 1


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
							allHome = False
					else:  # it is or was  home
						if (HomeStat[nDev] or HomeDist[nDev]): # still home: restart timer
							evnt["timeOfLastON"][nDev]= timeNowHMS
							evnt["secondsOfLastON"][nDev]= timeNowm2
							evnt["currentStatusHome"][nDev]	= "HOME"
							oneHome = True
							# this is wrong:
							#if minHomeTime >= float(evnt["minimumTimeHome"]):
							#    oneHomeTrigger =True
							#if maxHomeTime >= float(evnt["minimumTimeHome"]):
							#    allHomeTrigger =True
						else:
							evnt["currentStatusHome"][nDev]	= "0"
							allHome = False
					if evnt["currentStatusHome"][nDev]	== "HOME":
						evnt["nHome"] += 1
					if self.decideMyLog("Events"): out+="EVENT# {}".format(nEvent).ljust(2)+"  {}".format(nDev).rjust(3)+"   " +"{}".format(HomeStat[nDev]).ljust(12)+ "{}".format(HomeTime[nDev]).ljust(12) + "{}".format(HomeDist[nDev]).ljust(12)+ "{}".format(AwayStat[nDev]).ljust(12)+ "{}".format(AwayTime[nDev]).ljust(12)+ "{}".format(AwayDist[nDev]).ljust(12) + "{}".format(oneHome).ljust(8)+ "{}".format(allHome).ljust(8)+ "{}".format(oneAway).ljust(8)+ "{}".format(allAway).ljust(8) +"\n"


				if self.decideMyLog("Events"): out+="EVENT# {}".format(nEvent).ljust(2)+"  "+"oneHome:" + evnt["oneHome"]+"; allHome:" + evnt["allHome"]+"; oneAway:" + evnt["oneAway"]+"; allAway:" + evnt["allAway"] +"\n"
				if time.time() - self.timeOfStart > 100:
					if oneHome:
						if evnt["oneHome"] != "1" :
							if oneHomeTrigger:
								evnt["oneHome"] = "1"
								self.updatePrefs = True
								indigo.variable.updateValue("oneHome_"+nEvent, "1")
								if self.checkTriggerInitialized:
									try:indigo.variable.updateValue("FingEventDevChangedIndigoId","{}".format(self.allDeviceInfo[evnt["IPdeviceMACnumber"][oneHomeTrigger]]["deviceId"]))
									except: pass
									self.triggerEvent("EVENT_"+nEvent+"_oneHome")
					else:
						if evnt["oneHome"] != "0":
							evnt["oneHome"] = "0"
							indigo.variable.updateValue("oneHome_"+nEvent, "0")
							self.updatePrefs = True
					if allHome:
						if evnt["allHome"] != "1":
							if allHomeTrigger:
								evnt["allHome"] = "1"
								self.updatePrefs = True
								indigo.variable.updateValue("allHome_"+nEvent, "1")
								if self.checkTriggerInitialized:
									try: indigo.variable.updateValue("FingEventDevChangedIndigoId","{}".format(self.allDeviceInfo[evnt["IPdeviceMACnumber"][allHomeTrigger]]["deviceId"]))
									except: pass
									self.triggerEvent("EVENT_"+nEvent+"_allHome")
					else:
						if evnt["allHome"] != "0":
							evnt["allHome"] = "0"
							indigo.variable.updateValue("allHome_"+nEvent, "0")
							self.updatePrefs = True



					if allAway:
						if evnt["allAway"] != "1":
							if allAwayTrigger:
								self.updatePrefs = True
								evnt["allAway"] = "1"
								indigo.variable.updateValue("allAway_"+nEvent, "1")
								if self.checkTriggerInitialized:
									try: indigo.variable.updateValue("FingEventDevChangedIndigoId","{}".format(self.allDeviceInfo[evnt["IPdeviceMACnumber"][allAwayTrigger]]["deviceId"]))
									except: pass
									self.triggerEvent("EVENT_"+nEvent+"_allAway")
					else:
						if evnt["allAway"] != "0":
							evnt["allAway"] = "0"
							indigo.variable.updateValue("allAway_"+nEvent, "0")
							self.updatePrefs = True

					if oneAway:
						if evnt["oneAway"] != "1":
							if oneAwayTrigger:
								self.updatePrefs = True
								evnt["oneAway"] = "1"
								indigo.variable.updateValue("oneAway_"+nEvent, "1")
								if self.checkTriggerInitialized:
									try: indigo.variable.updateValue("FingEventDevChangedIndigoId","{}".format(self.allDeviceInfo[evnt["IPdeviceMACnumber"][allAwayTrigger]]["deviceId"]))
									except: pass
									self.triggerEvent("EVENT_"+nEvent+"_oneAway")
					else:
						if evnt["oneAway"] != "0":
							evnt["oneAway"] = "0"
							indigo.variable.updateValue("oneAway_"+nEvent, "0")
							self.updatePrefs = True

					if "{}".format(evnt["nAway"]) != indigo.variables["nAway_"+nEvent].value:
						indigo.variable.updateValue("nAway_"+nEvent, "{}".format(evnt["nAway"]))
					if "{}".format(evnt["nHome"]) != indigo.variables["nHome_"+nEvent].value:
						indigo.variable.updateValue("nHome_"+nEvent, "{}".format(evnt["nHome"]))



				if self.decideMyLog("Events"): self.printEvents(printEvents=nEvent)
	#		if self.decideMyLog("Events"): self.indiLOG.log(10, " leaving checkTriggers   ---->")

			self.checkTriggerInitialized =True
			
			

		except Exception:
			self.logger.error("", exc_info=True)
		return
	

########################################
	def sortIndigoIndex(self):
		try:
			sortFields =[]
			
			ll=0
			for theMAC in self.indigoIpVariableData:
				kk = self.indigoIpVariableData[theMAC]["index"]
				ipCompr = int(self.indigoIpVariableData[theMAC]["ipNumber"].strip().replace(".",""))  # "  192.168.1.5  " --> "  19216815  "
				sortFields.append([ipCompr,kk])  # [[192168110,1],[19216816,2], ....[....]]
				ll+=1
	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "sort: {}".format(ll) + " " + "{}".format(kk) +" " + "{}".format(ipCompr))
			sortedIP = sorted(sortFields, key=lambda tup: tup[0])  # sort ip number: tup([0]) as number,

	#		if self.decideMyLog("Logic"): self.indiLOG.log(10, "sort2.0 len: {}".format(len(self.indigoDevicesValues)) )
			for kk in range(ll):
				jj = sortedIP[kk][1]						# old index
	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "sort2: {}".format(kk) + " " + "{}".format(jj) )
				
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
		except Exception:
			self.logger.error("", exc_info=True)

		return 1





########################################
	def compareToFingIfExpired(self, calledFrom):
		try:
			dateTimeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			for theMAC in self.allDeviceInfo:
				if theMAC in self.ignoredMAC: continue
					
				update = False
				devI = self.allDeviceInfo[theMAC]
				if time.time() - self.startTime < 150:  devI["lastFingUp"] = time.time()

				try:  ## try to find this indigo mac number in  fingdata
					xxx = self.fingMACNumbers.index(theMAC)
				except:  ## this one is in indigo, but not in the fingdata file, set to exipred if not already done or ignore if better data from wifirouter
					if self.routerType != "0" and theMAC in self.wifiMacList and self.routerErrorCount==0:
						if devI["setWiFi"] != "Ethernet":
							if theMAC in self.WiFiChanged:
								if   devI[0] == "Yes":
									if devI["status"] != "up":
											devI["status"] = "up"
											update = True
								elif devI["status"] == "up":
									devI["status"] = "down"
									update = True
								elif devI["status"] == "down":
									devI["status"] =  "expired"
									update = True
				
					else:
							try:
								if (time.time() - devI["lastFingUp"] >  2*devI["expirationTime"] ): 
									if devI["status"] != "expired":
										update = True
										devI["status"] = "expired"
								elif (time.time() - devI["lastFingUp"] >  devI["expirationTime"] ): 
									if devI["status"] != "down":
										update = True
										devI["status"] = "down"
							except:
								pass
					if update:
						devI["timeOfLastChange"] = dateTimeNow
						self.updateIndigoIpDeviceFromDeviceData(theMAC,["status", "timeOfLastChange"])
						self.updateIndigoIpVariableFromDeviceData(theMAC)
				if self.decideMyLog("WiFi"): self.indiLOG.log(10, " fing end..theMAC/wifi/status/: "+theMAC+" -"  + devI["status"] )
				
				
			if self.routerType != "0":
				for theMAC in self.wifiMacList:
					if theMAC not in self.allDeviceInfo:
						if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
						self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
						devI= self.allDeviceInfo[theMAC]
						devI["ipNumber"]			= "256.256.256.256"
						devI["timeOfLastChange"]	= "{}".format(dateTimeNow)
						devI["status"]				= "up"
						devI["nickName"]			= "unidentifiedWiFiDevice"
						devI["noOfChanges"]		= 1
						devI["deviceInfo"]			= "unidentified"
						if devI["setWiFi"] != "Ethernet":
							devI["WiFi"]			= self.wifiMacList[theMAC][9]
						devI["usePing"]			= "usePingUP"
						devI["useWakeOnLanSecs "]	= 0
						devI["suppressChangeMSG"]	= "show"
						devI["hardwareVendor"]      = self.getVendortName(theMAC)

						newIPDevNumber = "{}".format(self.indigoEmpty[0])
						if self.decideMyLog("Logic"): self.indiLOG.log(10, "new device added ipDevice" +  newIPDevNumber)
						
						self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"])
						self.updateIndigoIpVariableFromDeviceData(theMAC)


						## count down empty space
						self.indigoIndexEmpty -= 1  # one less empty slot
						if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list

						## start any triggers if setup
						try:
							indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI["deviceName"])
						except:
							indigo.variable.create("ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI["deviceName"],self.indigoVariablesFolderID)
						self.triggerEvent("NewDeviceOnNetwork")

						try:
							if self.indigoStoredNoOfDevices != "{}".format(self.indigoNumberOfdevices):
								indigo.variable.updateValue("ipDevsNoOfDevices", "{}".format(self.indigoNumberOfdevices))
						except:
							indigo.variable.create("ipDevsNoOfDevices", "{}".format(indigoNumberOfdevices))

		except Exception:
			self.logger.error("", exc_info=True)

		return 0
	
	
	
########################################
	def compareToIndigoDeviceData(self, lastUpdateSource="0"):
		try:
			indigoIndexFound =[]
			anyUpdate = 0
			dateTimeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "compareToIndigoDeviceData:  lastUpdateSource:{}".format(lastUpdateSource))
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
					theAction = "exist"
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " theMAC action: "+theMAC+"/"+theAction )
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10,"{}".format(self.allDeviceInfo[theMAC]))
				else:
					theAction = "new"
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " theMAC action: "+theMAC+"/"+theAction )
				
				updateStates = []

				
				if theAction == "exist" :
					if "setWiFi" not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC]["setWiFi"] = copy.deepcopy(emptyAllDeviceInfo["setWiFi"])
					devI= self.allDeviceInfo[theMAC]
					
					useFing = True
					if self.allDeviceInfo[theMAC]["setWiFi"] == "Wifi":
						useFing = False
						theStatus = "down"
					else:
						theStatus = self.fingStatus[kk]
						if self.inbetweenPingType!= "0" and theMAC in self.inbetweenPing:
							if  self.inbetweenPing[theMAC] == "down": theStatus = "down"

					#if theMAC =="1C:36:BB:97:C0:85": 
					#    indigo.server.log("exists "+ theStatus+"  {}".format(devI["lastFingUp"]))

					if theStatus != "up":
						if theMAC in self.allDeviceInfo and "useWakeOnLanSecs" in self.allDeviceInfo[theMAC] and  self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:
							self.sendWakewOnLanAndPing(theMAC, nBC= 1,waitForPing=10, countPings=1, waitBeforePing = 0., waitAfterPing = 0.0, calledFrom="compareToIndigoDeviceData")

					if time.time() - self.startTime < 150:  devI["lastFingUp"] = time.time()
					if theStatus == "up":
						devI["lastFingUp"] = time.time()
					else:
						if devI["expirationTime"] != 0 and (time.time() - devI["lastFingUp"] < devI["expirationTime"]): 
							theStatus = "up"

					if self.routerType !="0" and self.routerErrorCount ==0:					# check wifi router info if available
						if devI["setWiFi"] != "Ethernet":									# ignore if set to ethernet
							if theMAC in self.wifiMacList:
								associated =self.wifiMacList[theMAC][0]
								if self.decideMyLog("WiFi"): self.indiLOG.log(10, "before theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI["ipNumber"]+" LastUpdateby:"+lastUpdateSource)
								if associated == "Yes":
									if theStatus != "up":
										self.fingDate[kk] = "{}".format(dateTimeNow)
										doIndigoUpdate = 9
									if theStatus != "changed": theStatus = "up"
								else:
									if theStatus == "up" and lastUpdateSource == "WiFi":
										self.fingDate[kk] = "{}".format(dateTimeNow)
										theStatus = "down"
										doIndigoUpdate = 9
		#								if self.decideMyLog("WiFi"): self.indiLOG.log(10, "wifi theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI["ipNumber"]+" LastUpdateby:"+lastUpdateSource)
	
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
								if self.decideMyLog("WiFi"): self.indiLOG.log(10, "after WiFiF checks theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI["ipNumber"]+" LastUpdateby:"+lastUpdateSource)


					## found device, check if anything has changed: ip & status, if changed increment # of changes
					if devI["status"] != theStatus:
						updateStates.append("status")
						updateStates.append("noOfChanges")
						doIndigoUpdate = 2
						devI["noOfChanges"] += 1
						if theStatus == "up":
							if devI["ipNumber"].split("-")[0] != self.fingIPNumbers[kk]:  # split("-") to remove "-changed" string
								devI["ipNumber"] = self.fingIPNumbers[kk]
								updateStates.append("ipNumber")
								doIndigoUpdate = 3
						if theStatus == "down":
							if devI["ipNumber"].find("changed")>-1 or devI["ipNumber"].find("double")>-1:
								devI["ipNumber"] = self.fingIPNumbers[kk]
								updateStates.append("ipNumber")
							self.fingDate[kk] = "{}".format(dateTimeNow)
							doIndigoUpdate = 5
						if theStatus == "changed":
							doIndigoUpdate = 6
							updateStates.append("ipNumber")
							theStatus = "up"
					#no status change, check if IP number changed
					else :
						if theStatus == "up":
							if devI["ipNumber"].find("changed") > -1 or devI["ipNumber"].find("double")>-1:
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
						if doIndigoUpdate == 6:
							if theMAC in self.doubleIPnumbers:
								if len(self.doubleIPnumbers[theMAC]) 	==1: devI["ipNumber"]=self.fingIPNumbers[kk]+ "-changed"
								elif len(self.doubleIPnumbers[theMAC]) 	>1:	 devI["ipNumber"]=self.fingIPNumbers[kk]+ "-double"
						dd = self.fingDate[kk]
						if len(dd) < 5 : dd = "{}".format(dateTimeNow)
						devI["timeOfLastChange"]	= dd
						self.updateDeviceWiFiSignal(theMAC)
						#updateStates.append("deviceInfo")
						if  self.decideMyLog("Logic"): self.indiLOG.log(10, "compareToIndigoDeviceData update  MAC#:{}, changes:{}".format(theMAC, updateStates) )
						self.updateIndigoIpDeviceFromDeviceData(theMAC, updateStates)
						self.updateIndigoIpVariableFromDeviceData(theMAC)

						if doIndigoUpdate == 3 or doIndigoUpdate == 6 or doIndigoUpdate == 7 :
							try:
								indigo.variable.updateValue("ipDevsNewIPNumber", "ipDevice"+self.indigoIpVariableData[theMAC]["ipDevice"]+";"+devI["deviceName"])
							except:
								indigo.variable.create("ipDevsNewIPNumber", "ipDevice"+self.indigoIpVariableData[theMAC]["ipDevice"]+";"+devI["deviceName"],self.indigoVariablesFolderID)
							if theMAC in self.doubleIPnumbers:
								if (len(self.doubleIPnumbers[theMAC])==1 or  (len(self.doubleIPnumbers[theMAC])>1) and  devI["suppressChangeMSG"]=="show"):
									self.triggerEvent("IPNumberChanged")


				if theAction == "new" :################################# new device, add device to indigo
					if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
					self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
					devI= self.allDeviceInfo[theMAC]
					devI["ipNumber"]			=self.fingIPNumbers[kk]
					dd = self.fingDate[kk]
					if len(dd) < 5 : dd = "{}".format(dateTimeNow)
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
					
					devI["timeOfLastChange"]	= dd
					devI["status"]				= "up"
					devI["nickName"]			= "new-{}".format(sqNumber)+"-"+theMAC
					devI["noOfChanges"]			=1
					if len(self.fingVendor[kk]) < 4:
						devI["hardwareVendor"]      = self.getVendortName(theMAC)
					else:
						devI["hardwareVendor"]		=self.fingVendor[kk]

					devI["deviceInfo"]			= self.fingDeviceInfo[kk]
					devI["WiFi"]				= ""
					devI["usePing"]			= "usePingUP"
					devI["useWakeOnLanSecs"]	= 0
					devI["suppressChangeMSG"]	= "show"
					#if theMAC =="1C:36:BB:97:C0:85": 
					#    indigo.server.log("new "+ theStatus+"  {}".format(devI["lastFingUp"]))
					devI["lastFingUp"]	        = time.time()

					newIPDevNumber = "{}".format(self.indigoEmpty[0])
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "new device added ipDevice" +  newIPDevNumber)
					
					self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"])
					self.updateIndigoIpVariableFromDeviceData(theMAC)


					## count down empty space
					self.indigoIndexEmpty -= 1  # one less empty slot
					if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list

					anyUpdate +=1
					## start any triggers if setup
					try:
						indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI["deviceName"])
					except:
						indigo.variable.create("ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI["deviceName"],self.indigoVariablesFolderID)
					self.triggerEvent("NewDeviceOnNetwork")



			if self.routerType != "0" and lastUpdateSource == "WiFi":
				for theMAC in self.wifiMacList:
					if theMAC in self.allDeviceInfo: continue
					if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
					self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
					devI= self.allDeviceInfo[theMAC]
					devI["ipNumber"]			= "254.254.254.254"
					devI["timeOfLastChange"]	= "{}".format(dateTimeNow)
					devI["status"]				= "up"
					devI["nickName"]			= "unidentified_WiFi_Device"
					devI["noOfChanges"]		= 1
					devI["hardwareVendor"]     = self.getVendortName(theMAC)
					devI["deviceInfo"]			= "unidentified"
					devI["WiFi"]				= self.wifiMacList[theMAC][9]
					devI["usePing"]			= ""
					devI["useWakeOnLanSecs "]	= 0
					devI["suppressChangeMSG"]	= "show"
					try:
						newIPDevNumber = "{}".format(self.indigoEmpty[0])
					except:
						newIPDevNumber = "1"
						self.indiLOG.log(20, "new device added indigoEmpty not initialized" +  "{}".format(self.indigoEmpty))
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "new device added ipDevice#" +  newIPDevNumber)
					
					self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"])
					self.updateIndigoIpVariableFromDeviceData(theMAC)
					## count down empty space
					self.indigoIndexEmpty -= 1  # one less empty slot
					if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list

					try:
						indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI["deviceName"])
					except:
						indigo.variable.create("ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI["deviceName"],self.indigoVariablesFolderID)
					self.triggerEvent("NewDeviceOnNetwork")

			try:
				if self.indigoStoredNoOfDevices != "{}".format(self.indigoNumberOfdevices):
					indigo.variable.updateValue("ipDevsNoOfDevices", "{}".format(self.indigoNumberOfdevices))
			except:
				indigo.variable.create("ipDevsNoOfDevices", "{}".format(indigoNumberOfdevices))

		except Exception:
			self.logger.error("", exc_info=True)


		return 0



########################################
	def getVendortName(self, MAC):
		if self.enableMACtoVENDORlookup == "0" : return ""
		if not self.waitForMAC2vendor:
			self.waitForMAC2vendor = self.M2V.makeFinalTable(quiet=False)
			return  self.M2V.getVendorOfMAC(MAC)



	###########################	   cProfile stuff   ############################ START
	####-----------------  ---------
	def getcProfileVariable(self):

		try:
			if self.timeTrVarName in indigo.variables:
				xx = (indigo.variables[self.timeTrVarName].value).strip().lower().split("-")
				if len(xx) ==1: 
					cmd = xx[0]
					pri = ""
				elif len(xx) == 2:
					cmd = xx[0]
					pri = xx[1]
				else:
					cmd = "off"
					pri  = ""
				self.timeTrackWaitTime = 20
				return cmd, pri
		except	Exception as e:
			pass

		self.timeTrackWaitTime = 60
		return "off",""

	####-----------------            ---------
	def printcProfileStats(self,pri=""):
		try:
			if pri !="": pick = pri
			else:		 pick = 'cumtime'
			outFile		= self.indigoPreferencesPluginDir+"timeStats"
			indigo.server.log(" print time track stats to: "+outFile+".dump / txt  with option: "+pick)
			self.pr.dump_stats(outFile+".dump")
			sys.stdout 	= open(outFile+".txt", "w")
			stats 		= pstats.Stats(outFile+".dump")
			stats.strip_dirs()
			stats.sort_stats(pick)
			stats.print_stats()
			sys.stdout = sys.__stdout__
		except: pass
		"""
		'calls'			call count
		'cumtime'		cumulative time
		'file'			file name
		'filename'		file name
		'module'		file name
		'pcalls'		primitive call count
		'line'			line number
		'name'			function name
		'nfl'			name/file/line
		'stdname'		standard name
		'time'			internal time
		"""

	####-----------------            ---------
	def checkcProfile(self):
		try: 
			if time.time() - self.lastTimegetcProfileVariable < self.timeTrackWaitTime: 
				return 
		except: 
			self.cProfileVariableLoaded = 0
			self.do_cProfile  			= "x"
			self.timeTrVarName 			= "enableTimeTracking_"+self.pluginShortName
			indigo.server.log("testing if variable "+self.timeTrVarName+" is == on/off/print-option to enable/end/print time tracking of all functions and methods (option:'',calls,cumtime,pcalls,time)")

		self.lastTimegetcProfileVariable = time.time()

		cmd, pri = self.getcProfileVariable()
		if self.do_cProfile != cmd:
			if cmd == "on": 
				if  self.cProfileVariableLoaded ==0:
					indigo.server.log("======>>>>   loading cProfile & pstats libs for time tracking;  starting w cProfile ")
					self.pr = cProfile.Profile()
					self.pr.enable()
					self.cProfileVariableLoaded = 2
				elif  self.cProfileVariableLoaded >1:
					self.quitNOW = " restart due to change  ON  requested for print cProfile timers"
			elif cmd == "off" and self.cProfileVariableLoaded >0:
					self.pr.disable()
					self.quitNOW = " restart due to  OFF  request for print cProfile timers "
		if cmd == "print"  and self.cProfileVariableLoaded >0:
				self.pr.disable()
				self.printcProfileStats(pri=pri)
				self.pr.enable()
				indigo.variable.updateValue(self.timeTrVarName, "done")

		self.do_cProfile = cmd
		return 

	####-----------------            ---------
	def checkcProfileEND(self):
		if self.do_cProfile in["on", "print"] and self.cProfileVariableLoaded >0:
			self.printcProfileStats(pri="")
		return
	###########################	   cProfile stuff   ############################ END

	####-----------	------	 ---------
	def setSqlLoggerIgnoreStatesAndVariables(self):
		try:
			if self.indigoVersion <  7.4:                             return 
			if self.indigoVersion == 7.4 and self.indigoRelease == 0: return 
			#tt = ["beacon",              "rPI","rPI-Sensor","BLEconnect","sensor"]

			outOffD = ""
			outOffV = ""

			for dev in indigo.devices.iter(self.pluginId):
					sp = dev.sharedProps
					if "sqlLoggerIgnoreStates" not in sp:
						sp["sqlLoggerIgnoreStates"] = "lastfingup"
						dev.replaceSharedPropsOnServer(sp)
						outOffD += dev.name+";"
					elif sp["sqlLoggerIgnoreStates"].find("lastfingup") == -1:
						sp["sqlLoggerIgnoreStates"] += ",lastfingup"
						dev.replaceSharedPropsOnServer(sp)
						outOffD += dev.name+";"

			varExcludeSQLList = ["ipDevsLastDevChangedIndigoName", "ipDevsLastUpdate", "ipDevsNewDeviceNo",  "ipDevsNewIPNumber", "ipDevsOldNewIPNumber"]
			if True:
				for var in indigo.variables.iter():
					if var.name.find("ipDevice") >-1:
						varExcludeSQLList.append(var.name)

			for v in varExcludeSQLList:
					var = indigo.variables[v]
					sp = var.sharedProps
					#self.indiLOG.log(30, "setting /testing off: Var: {} sharedProps:{}".format(var.name.encode("utf8"), sp) )
					if "sqlLoggerIgnoreChanges" in sp and sp["sqlLoggerIgnoreChanges"] == "true": 
						continue
					#self.indiLOG.log(30, "====set to off ")
					outOffV += var.name+"; "
					sp["sqlLoggerIgnoreChanges"] = "true"
					var.replaceSharedPropsOnServer(sp)
					if False: # check if it was written
						var = indigo.variables[v]
						sp = var.sharedProps
						self.indiLOG.log(20, "switching off SQL logging for variable :{}: sp:{}".format(var.name.encode("utf8"), sp) )
					

			if len(outOffV) > 0: 
				self.indiLOG.log(20, " \n")
				self.indiLOG.log(20, "switching off SQL logging for variables\n :{}".format(outOffV.encode("utf8")) )
				self.indiLOG.log(20, "switching off SQL logging for variables END\n")
			if len(outOffD) > 0: 
				self.indiLOG.log(20, " \n")
				self.indiLOG.log(20, "switching off SQL logging for devices/state[lastfingup]\n :{}".format(outOffD.encode("utf8")) )
				self.indiLOG.log(20, "switching off SQL logging for devices END\n")
		except Exception:
			self.logger.error("", exc_info=True)

		return 

####-----------------   main loop          ---------
	def runConcurrentThread(self):

		self.initConfig()

		self.setSqlLoggerIgnoreStatesAndVariables()

		indigo.server.savePluginPrefs() 
		self.dorunConcurrentThread()
		self.checkcProfileEND()
		indigo.server.savePluginPrefs() 

		self.sleep(1)
		if self.quitNOW !="":
			indigo.server.log( "runConcurrentThread stopping plugin due to:  ::::: " + self.quitNOW + " :::::")
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)


		indigo.server.log( "killing 2")
		os.system("/bin/kill -9 {}".format(self.myPID) )

		return




####-----------------   main loop          ---------
	def dorunConcurrentThread(self): 

		self.indigoCommand = "none"
		self.pluginState   = "run"
		## loop:  get fing data and enter fill indigo variables
		fingNotActiveCounter = 0
		self.totalLoopCounter = 0
		self.routerErrorCount =0
#		observer = Observer()
#		stream = Stream(self.checkLog, self.indigoPreferencesPluginDir, file_events=True)
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
		rebootMinute = 19 # 19 minutes after midnight, dont do it too close to 00:00 because of other processes might be active


		self.timeOfStart = time.time()
		try:
			while self.quitNOW == "no":

				if self.savePrefs > 0: 
					self.savePrefs = 0
					indigo.server.savePluginPrefs() 

				if self.redoAWAY >0:
					self.sleep(1)
					self.redoAWAY -=1
					if self.decideMyLog("Ping"): self.indiLOG.log(10, "redo tests, check if device is back UP: {}".format(self.redoAWAY))
				else:
					xsleep=max(0.5,self.newSleepTime/10)  ## this is to enable a fast reaction to asynchronous events 
					nsleep = int(self.newSleepTime /xsleep)
					tt=time.time()
					for i in range(nsleep):
						if self.newSleepTime == 0: break
						if time.time()-tt > self.newSleepTime: break
						self.sleep( xsleep )
					self.newSleepTime = self.sleepTime
				#self.indiLOG.log(10, "after sleeploop self.redoAWAY {}".format(self.redoAWAY) +"  nsleep{}".format(nsleep)+"  self.newSleepTime{}".format(self.newSleepTime))    
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
					self.checkcProfile()
					lastmin =checkTime[1]
					self.updateDeviceWiFiSignal()
					self.checkIfDevicesChanged() # check for changed device parameters once a minute .
					self.checkDEVICES() # complete sync every minutes
					self.setupEventVariables()
				if lastmin5 !=checkTime[1] and checkTime[1]%5 ==0 and checkTime[1] >0 and checkTime[2]>20 :
					lastmin5 =checkTime[1]
					self.updateAllIndigoIpDeviceFromDeviceData(["deviceInfo"])
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
							if dev.deviceTypeId != "iAppleDeviceAuto": continue
							self.IDretList.append((dev.id,dev.name))
							self.iDevicesEnabled = True
					if self.iDevicesEnabled:
						self.pluginPrefs["iDevicesEnabled"] = True
					else:
						self.pluginPrefs["iDevicesEnabled"] = False



			
				if lastmin53 !=checkTime[1] and checkTime[1]%53 ==0 and checkTime[1] >0 and checkTime[2]>35 :
					lastmin53 =checkTime[1]
					self.doInbetweenPing(force=True)
					self.totalLoopCounter= 500
					
				if checkTime[0] == 0  and rebootMinute == checkTime[1] and self.totalLoopCounter > 200:
					self.refreshVariables()
					self.quitNOW = "reboot after midnight"
										


				self.totalLoopCounter +=1
				if self.quitNOW !="no": break
				if self.updatePrefs:
					self.updatePrefs = False
					self.pluginPrefs["EVENTS"]	=	json.dumps(self.EVENTS)
					indigo.server.savePluginPrefs() 

				
				if time.time()-lastFingActivity > 280:
					self.indiLOG.log(40, "seems that FING is not active - no change in data, restarting fing, seconds since last change: {}".format(time.time() - lastFingActivity))
					retCode = self.initFing(1)
					if retCode ==1:
						self.indiLOG.log(20, "fing restarted successfully")
						fingNotActiveCounter =0
						self.sleep(5) ## give it some time
					else:
						if self.decideMyLog("Logic"): self.indiLOG.log(40, "fing not active, tried to restart fing, did not work, stopping fingscan, may be wrong password \n   in plugins/fingscan/configure:  set password" )
						self.quitNOW = "yes"
						break

				self.indigoNeedsUpdate=True
				if self.inbetweenPingType != "0":
					self.throttlePing -=1
					if self.throttlePing <0 :
						if self.doInbetweenPing():
							if self.indigoNeedsUpdate:
								self.getIndigoIpDevicesIntoData()
								self.indigoNeedsUpdate=False
							self.compareToIndigoDeviceData(lastUpdateSource= "ping")
							self.checkTriggers()


				if time.time() - lastdoWOL > repeatdoWOL:
					lastdoWOL = time.time()
					for theMAC in self.allDeviceInfo:
						devI = self.allDeviceInfo[theMAC]
						if "useWakeOnLanSecs" in devI and devI["useWakeOnLanSecs"] >0:
							if time.time() - devI["useWakeOnLanLast"] > devI["useWakeOnLanSecs"]:
								devI["useWakeOnLanLast"] = time.time()
								self.sendWakewOnLanAndPing(theMAC, nBC= 1, waitForPing=10, countPings=1, waitBeforePing = 0.01, waitAfterPing = 0.0, calledFrom="loop")


				if self.routerType != "0":
					self.WiFiChanged = {}
					errorMsg = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, rType=self.routerType)
					if errorMsg != "ok":
						self.routerErrorCount+=1
						if self.routerErrorCount%100 < 3 and self.badWiFiTrigger["trigger"]<1:
							if self.decideMyLog("Ping"): self.indiLOG.log(10, "WiFi Router does not return valid MAC numbers: "+errorMsg[:200])
							if self.routerErrorCount > 3600:  # about 1 hour
								self.indiLOG.log(30, "WiFi Router: turning off WiFi Router query, you need to re-enable in configuration after router is back online")
								self.routerType = "0"

					else:
						if self.routerErrorCount >0:
							if self.decideMyLog("WiFi"): self.indiLOG.log(10, "WiFi Router back up again")
						self.routerErrorCount = 0
						if 	self.checkIfBadWiFi():
							self.badWiFiTrigger["trigger"]=10
							if self.decideMyLog("WiFi"): self.indiLOG.log(10, "WiFi signal is weak ")#, triggering external python command "+self.indigoPreferencesPluginDir+"pings/doThisWhenWiFiIsBad.py")
							self.printWiFi()
							self.triggerEvent("badWiFi")
							self.resetbadWifiTrigger()
							
						if len(self.WiFiChanged)>0 or self.redoAWAY >0:
							if self.indigoNeedsUpdate:
								self.getIndigoIpDevicesIntoData()
								self.indigoNeedsUpdate=False
							self.compareToIndigoDeviceData(lastUpdateSource= "WiFi")
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
				
				retCode = self.getfingLog() ## test log file if new data
				if retCode == 1:
					self.redoAWAY =0
					lastFingActivity =time.time()
					if self.quitNOW != "no": break
					if self.indigoNeedsUpdate:
						self.getIndigoIpDevicesIntoData(lastUpdateSource= "fingLog")
						self.indigoNeedsUpdate = False
					if self.quitNOW != "no": break
					self.compareToIndigoDeviceData(lastUpdateSource= "fingLog")
					if self.quitNOW != "no": break
#						retCode = self.getIndigoIpVariablesIntoData()
					self.checkTriggers()
					try:
						if self.debugLevel != []: indigo.variable.updateValue("ipDevsLastUpdate", time.strftime("%H:%M:%S", time.localtime()) )
					except:
						self.quitNOW = "Indigo variable error 9"#  someting must be wrong, restart
						self.indiLOG.log(30, "can not update variable ipDevsLastUpdate  \n  restarting fingscan" )
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
						except Exception as exc:
							self.quitNOW = " ipDevsLastUpdate can not be updated"#  something must be wrong, restart
							self.indiLOG.log(40, "can not update variable ipDevsLastUpdate  \n  restarting fingscan\n exception code: {}".format(exc) )
							break
						if self.indigoNeedsUpdate:
							self.getIndigoIpDevicesIntoData()
							self.indigoNeedsUpdate = False
						if self.quitNOW != "no": break
						retCode = self.compareToIndigoDeviceData(lastUpdateSource= "fingData")
						if self.quitNOW != "no": break
						retCode = self.compareToFingIfExpired(2)
						if self.quitNOW != "no": break
						if not self.indigoInitialized:
							self.indiLOG.log(20, "FINGSCAN initialized")
						self.indigoInitialized = True
#						retCode = self.getIndigoIpVariablesIntoData()
						self.checkTriggers()


			self.pluginState  = "end"
			self.pluginPrefs["EVENTS"]	=	json.dumps(self.EVENTS)
			indigo.server.savePluginPrefs() 

			self.killFing("all")
			self.killPGM("/startfing.py")
		
			try:
				quitNowX = self.quitNOW
			except:
				quitNowX = "please setup config , waiting"
				self.indiLOG.log(40, "-->  setup config, save, then a manual reload of plugin")

			self.indiLOG.log(20, "--> while loop break  stopping ...  quitNOW was: {}".format(quitNowX) )
			if quitNowX.find("wait") >-1: 
				self.indiLOG.log(40, "--> you have 2 minutes to fix config, before restart")
				for ii in range(20): 
					if self.passwordOK != "0": 
						self.indiLOG.log(40, "--> do a manual reload of plugin")
						break
					time.sleep(10)

			self.quitNOW = "no"
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
			indigo.server.savePluginPrefs() 
			try:
				quitNowX = self.quitNOW
			except Exception as e:
				quitNowX = "please setup config"
				self.logger.error("-->  exception StopThread triggered ... stopped,  quitNOW was: {}".format(quitNowX), exc_info=True)
			self.quitNOW = "no"
			############ if there are PING jobs left  kill them
		return








	############# main program  -- end ###########
	def	updateDeviceWiFiSignal(self,theMACin= "all"):
		try:
			if theMACin == "all":
				for theMAC in self.wifiMacList:
					if theMAC in self.ignoredMAC: continue
					if theMAC in self.allDeviceInfo:
						self.allDeviceInfo[theMAC]["WiFi"] =  self.wifiMacList[theMAC][9]
						if self.wifiMacList[theMAC][0] == "Yes" and self.wifiMacList[theMAC][1] == "Yes" :
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
							if self.wifiMacList[theMAC][0] == "Yes" and self.wifiMacList[theMAC][1] == "Yes" :
								self.allDeviceInfo[theMAC]["WiFiSignal"] =  (("Sig[dBm]:%4.0f"%self.wifiMacList[theMAC][2]  ).strip()
															+ ","+("ave:%4.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))).strip()
															#+","+("cnt:%8.0f"%self.wifiMacList[theMAC][11]).strip()
															)
						if self.wifiMacList[theMAC][11] > 9999999: self.resetbadWifiTrigger() # reset counter if tooo big
		except Exception:
			self.logger.error("", exc_info=True)

		return


	
##############################################
	def getWifiDevices(self, uid, pwd, ipN, rType="ASUS" ):
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
			response, err = self.readPopen("/usr/bin/curl  --max-time 3 -u "+uid+":"+pwd+" 'http://"+ipN+"/Main_WStatus_Content.asp'")
			if len(response) < 2 :
				self.wifiErrCounter+=1
				if self.wifiErrCounter > 2:
					self.indiLOG.log(20, " wifi data received not complete(len=0): {}".format(response))
				return "error bad return from  curl {}".format(response)
			self.wifiErrCounter =0
			if rType== "MERLIN378_54":
				response2 = response.split("wificlients") # this where the information starts:
				if len(response2) <2:
						self.indiLOG.log(20, " wifi data received not complete(wificlients): {}".format(response2))
						return "error bad return from  curl {}".format(response2)
				noiseSplit =response.upper().split("\nDATAARRAY")
				if len(noiseSplit) <2:
						self.indiLOG.log(20, " wifi data received not complete(no nDATAARRAY) {}".format(response2))
						return "error bad return from  curl {}".format(response2)
					
			else:
				response2 = response.split("\n----------------------------------------\n") # this where the information starts:
				if len(response2) < 3: 				return "error bad return from  curl {}".format(response2) # no valid data return, or bad password...
				noiseSplit =response.upper().split("NOISE:")
				if len(noiseSplit) < 2: 			return "error bad return from  curl {}".format(response2) # no valid data return, or bad password...

			fo2 =["", "2GHz", "5GHz"]
			for i in range(1,3):
				fiveORtwo =fo2[i]
				if rType== "MERLIN378_54":
					nsplit=  noiseSplit[i].split(";")[0].split("= ")
					if len(nsplit) < 2:
						if self.decideMyLog("WiFi"): self.indiLOG.log(10, " wifi data received not complete (nsplit <2): {}".format(noiseSplit))
						continue
					self.wifiMacAv["noiseLevel"][fiveORtwo] = json.loads(nsplit[1])[3]
	#				if self.decideMyLog("WiFi"): self.indiLOG.log(10, " wifi noiseLevel {}".format(fiveORtwo)+" {}".format(noiseSplit[i]))
				else:
					if len(noiseSplit) > 2:
						self.wifiMacAv["noiseLevel"][fiveORtwo] = noiseSplit[i].strip(" ").split(" ")[0]
				errorMSG= " "
				if rType== "ASUS":			errorMSG =self.parseWIFILogA(response2[i].split("\n\n")[0].split("\n"),fiveORtwo)
				elif rType== "MERLIN":		errorMSG =self.parseWIFILogM(response2[i].split("\n\n")[0].split("\n"),fiveORtwo)
				elif rType== "MERLIN378_54":	errorMSG =self.parseWIFILogM378(response2[i],fiveORtwo)
				else: return "bad wifi defnition"
				if errorMSG != "ok": 			return errorMSG
				if self.wifiMacAv["numberOfCycles"][fiveORtwo] >3 and self.wifiMacAv["curDev"][fiveORtwo]>0. :
					if    abs(self.wifiMacAv["curAvSignal"][fiveORtwo] - self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]) > 5.:
						self.signalDelta["5"][fiveORtwo] +=1
					elif  abs(self.wifiMacAv["curAvSignal"][fiveORtwo] - self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]) > 2.:
						self.signalDelta["2"][fiveORtwo] +=1
					elif  abs(self.wifiMacAv["curAvSignal"][fiveORtwo] - self.wifiMacAv["sumSignal"][fiveORtwo]/self.wifiMacAv["numberOfDevices"][fiveORtwo]) > 1:
						self.signalDelta["1"][fiveORtwo] +=1
					if    self.totalLoopCounter >99999:
						if self.decideMyLog("WiFi"): self.indiLOG.log(10, " wifi signals "+fiveORtwo+": sumSig:%8.0f sumNdev:%8.0f sumNMeas:%8.0f longAv%6.2f longnDevAv%6.2f thisAV:%6.2f thisnMeas:%3.1f del5:%5.0f del2:%5.0f del1:%5.0f"%
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
					self.WiFiChanged[theMAC]=self.oldwifiMacList[theMAC][0]
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
	
				
					
			#if self.decideMyLog("WiFi"): self.indiLOG.log(10, " wifi curl time elapsed: %9.3f " %(time.time()-ticks))
		except Exception as e:
			self.indiLOG.log(40, "error in  Line '%s' ;  error='%s'" % (sys.exc_info()[2].tb_lineno, e)+" wifi router reponse:{}".format(resp))
			return "error {}".format(resp)

		return "ok"  # [MACno][MACno,Associated,Authorized,RSSI,PSM,SGI,STBC,Tx rate,Rx rate,Connect Time]], "ok"


##############################################
	def resetbadWifiTrigger(self):
		try:
			for theMAC in self.wifiMacList:
				self.wifiMacList[theMAC][10] =0
				self.wifiMacList[theMAC][11] =0
			self.badWiFiTrigger["numberOfSecondsBad"] =0
			self.wifiMacAv=copy.deepcopy(emptyWifiMacAv)
		except Exception:
			self.logger.error("", exc_info=True)
		return

##############################################
	def checkIfBadWiFi(self):
		try:
			if self.badWiFiTrigger["minNumberOfSecondsBad"] >998: return False
	#		if self.badWiFiTrigger["minNumberOfDevicesBad"] >998: return False
	#		if self.badWiFiTrigger["minSignalDrop"] >998: return False
			candidates =0
			for theMAC in self.wifiMacList:
				if self.wifiMacList[theMAC][0]!= "Yes": continue
				if self.wifiMacList[theMAC][1]!= "Yes": continue
				if self.wifiMacList[theMAC][9]!= "2GHz": continue
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
					if self.decideMyLog("WiFi"): self.indiLOG.log(10, " bad wifi signal for %3.0f seconds"%(nSecBad) )
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
		except Exception:
			self.logger.error("", exc_info=True)
		return False


##############################################
	def parseWIFILogM378(self,wifiLog,fiveORtwo):
	# wdataarray24 = ["2","0","0","-92","8","D8:50:E6:CF:B4:E0","AP"];
	#wificlients24 = [["54:9F:13:3F:95:25", "192.168.1.192","iPhone-20","-62", "13", "72","  0:24:56"," S AU"],["FC:E9:98:49:BB:B9", "192.168.1.155", "Kristins-iPhone","-65", "24", "72","  0:37:11","PS AU"],["6C:AD:F8:26:69:9E", "192.168.1.242","Chromecast","-50","72", "72","  0:38:00"," STAU"],["F0:7D:68:08:5F:D0", "192.168.1.74","<not found>","-68","52", "58","  0:38:02"," STAU"],["28:10:7B:0C:CB:4B", "192.168.1.77","<not found>","-72","52", "72","  0:38:03"," STAU"],["F0:7D:68:06:F6:87", "192.168.1.71","<not found>","-51","72", "72","  0:38:03"," STAU"],"-1"];
	#dataarray5 = ["5","0","0","-92", "149/80","D8:50:E6:CF:B4:E4","AP"];
	#wificlients5 = [["F0:F6:1C:D5:51:16", "192.168.1.215","<not found>","-69", "24", "243","  0:36:53","PSTAU"],"-1"];

		try:
			if self.decideMyLog("WiFi"): self.indiLOG.log(10, "wifiLog:{}".format(wifiLog))
			wl= wifiLog.split(";")[0].split("= ")
			if len(wl) < 2:
				self.indiLOG.log(20, "parseWIFILogM378 wifilog data not complete (wl=0): {}".format(wifiLog))
				return "error"
			try:
				wlist= json.loads(wl[1])
			except:
				self.indiLOG.log(20, "parseWIFILogM378: wifilog data not complete( Wl json): {}".format(wifiLog))
				return "error"


			# now parse
			nDevices = len(wlist)-1
			if nDevices <1: return "ok"
			sumSignal =0.
			nDevConnected=0
			for thisDevice1 in wlist:
				if self.decideMyLog("WiFi"): self.indiLOG.log(10, "thisDevice1:{}".format(thisDevice1))
				thisDevice=[]

				if thisDevice1 =="-1": continue
				
				theMAC =thisDevice1[0]

				if self.decideMyLog("WiFi"): self.indiLOG.log(10, "thisDevice1>>"+ theMAC+"<<  {}".format(thisDevice1))
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

		except Exception:
			self.logger.error("", exc_info=True)
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
			pointerText = ["MAC   ", "IP Address   ", "Name   ", "  RSSI", "   Rx", "/", "Tx Rate   ", "Connected ", "Flags"]
			thepointers=[]
	#		if self.decideMyLog("WiFi"): self.indiLOG.log(10, "line:"+ wifiLog[0])
			for pT in range(len(pointerText)):
				p= wifiLog[0].find(pointerText[pT])
				if p ==-1: return "error parsing return string "+pointerText[pT]
				thepointers.append(p)
			thepointers.append(len(wifiLog[0]))
	#		if self.decideMyLog("WiFi"): self.indiLOG.log(10, "line:{}".format(thepointers))

			# records should be ok..
			
			
			# now parse
			nDevices = len(wifiLog)
			if nDevices <1: return "ok"
			sumSignal =0.
			nDevConnected=0
			for line in range(1,nDevices):
	#			if self.decideMyLog("WiFi"): self.indiLOG.log(10, "line:"+ wifiLog[line])
				if len(wifiLog[line])< 20: continue

				thisDevice1=[]
				for p in range(1,len(pointerText)):
					thisDevice1.append( wifiLog[line][thepointers[p]: min(thepointers[p+1],len(wifiLog[line]))].strip() )
				
				theMAC = wifiLog[line][:17].strip(" ")

				if self.decideMyLog("WiFi"): self.indiLOG.log(10, "thisDevice1>>"+ theMAC+"<<  {}".format(thisDevice1))
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

		except Exception:
			self.logger.error("", exc_info=True)
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
			pointerText = ["MAC", "Associated", "Authorized", "   RSSI", "PSM", "SGI", "STBC", "Tx rate", "Rx rate", "Connect Time"]
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
				
		except Exception:
			self.logger.error("", exc_info=True)

		return  "ok"


##############################################
	def checkWIFIinfo(self):
		try:
			for mac in self.wifiMacList:
				self.wifiMacList[mac]=copy.deepcopy(emptyWiFiMacList)
			if self.routerType !="0":
				errorMSG = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, rType=self.routerType)
				if errorMSG !="ok":
					if self.decideMyLog("WiFi"): self.indiLOG.log(10, "Router wifi not reachable, userid password or ipnumber wrong?\n{}".format(errorMSG))
					return
				else:
					if self.decideMyLog("WiFi"): self.indiLOG.log(10, "Router wifi data ok")
			else:
				self.routerUID	= ""
				self.routerPWD	= ""
				self.routerIPn	= ""


		except Exception:
			self.logger.error("", exc_info=True)
		return



##############################################
	def checkDEVICES(self):
	#		if self.decideMyLog("Logic"): self.indiLOG.log(10, "checking devices")
	#					emptyAllDeviceInfo={"00:00:00:00:00:00":{"ipNumber":"0.0.0.0","timeOfLastChange":"timeOfLastChange","status":"down","nickName":"iphonexyz":"noOfChanges":"0", "hardwareVendor":"", "deviceInfo":"","WiFi":"","deviceId":0,"deviceName":"","devExists":0}}
		try:
			for theMAC in self.allDeviceInfo:
				self.allDeviceInfo[theMAC]["devExists"]=0

			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				devID="{}".format(dev.id)
				theStates = dev.states.keys()
	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "device testing: "+dev.name)
	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "device states: MAC-{}".format(theStates))
				
				if "MACNumber" in theStates:
					anyUpdate = False
					theMAC = dev.states["MACNumber"]
					if theMAC =="": continue
					if not theMAC in self.allDeviceInfo: continue
					if theMAC in self.ignoredMAC: continue
					devI=self.allDeviceInfo[theMAC]
					devI["deviceId"]	=dev.id
					if dev.name != devI["deviceName"]:
						devI["nickName"] = dev.name
						devI["deviceName"]	=dev.name
						
					if theMAC in self.wifiMacList:
						self.updateDeviceWiFiSignal(theMAC)
						dev.description = theMAC+"-"+devI["WiFi"]+"-"+devI["WiFiSignal"]
						dev.replaceOnServer()
						self.addToStatesUpdateList("{}".format(dev.id),"WiFi",				devI["WiFi"])
						try:
							string ="%5.1f"%self.wifiMacList[theMAC][2]
						except:
							string ="{}".format(self.wifiMacList[theMAC][2])
						
						self.addToStatesUpdateList("{}".format(dev.id),"WiFiSignal",string)
					
					if dev.states["ipNumber"] != devI["ipNumber"]:
						self.addToStatesUpdateList("{}".format(dev.id),"ipNumber",			devI["ipNumber"])
						anyUpdate=True
					if dev.states["status"] != devI["status"]:
						self.addToStatesUpdateList("{}".format(dev.id),"status",			devI["status"])
						if self.decideMyLog("Logic"): self.indiLOG.log(10, "checkDEVICES  dev:{}   new status{}".format(dev.name, devI["status"]))
						anyUpdate=True
					if dev.states["nickName"] != devI["nickName"]:
						self.addToStatesUpdateList("{}".format(dev.id),"nickName",			devI["nickName"])
						anyUpdate=True
					if "{}".format(dev.states["noOfChanges"]) != "{}".format(devI["noOfChanges"]):
						self.addToStatesUpdateList("{}".format(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
						anyUpdate=True
					if dev.states["hardwareVendor"] !=devI["hardwareVendor"]:
						self.addToStatesUpdateList("{}".format(dev.id),"hardwareVendor",	devI["hardwareVendor"])
						anyUpdate=True
					if dev.states["deviceInfo"] !=devI["deviceInfo"]:
						self.addToStatesUpdateList("{}".format(dev.id),"deviceInfo",		devI["deviceInfo"])
						anyUpdate=True
					if dev.states["WiFi"] !=devI["WiFi"]:
						self.addToStatesUpdateList("{}".format(dev.id),"WiFi",				devI["WiFi"])
						anyUpdate=True
					if "created" in dev.states and len(dev.states["created"]) < 10:
						self.addToStatesUpdateList("{}".format(dev.id),"created",		datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
						anyUpdate=True
					usePing = devI["usePing"]
					if  "{}".format(devI["useWakeOnLanSecs"]) !="0":
						usePing +="-WOL:{}".format(devI["useWakeOnLanSecs"])
					if "usePing-WOL" in dev.states:
						if dev.states["usePing-WOL"] !=usePing:
							anyUpdate=True
							#dev.updateStateOnServer("usePing",			devI["usePing"])
							self.addToStatesUpdateList("{}".format(dev.id),"usePing-WOL",			usePing)
					if "suppressChangeMSG" in dev.states:
						if dev.states["suppressChangeMSG"] != devI["suppressChangeMSG"]:
							anyUpdate=True
							#dev.updateStateOnServer("suppressChangeMSG",devI["suppressChangeMSG"])
							self.addToStatesUpdateList("{}".format(dev.id),"suppressChangeMSG",devI["suppressChangeMSG"])
							
					if "lastFingUp" in dev.states:
						if "lastFingUp" not in devI:
							devI["lastFingUp"] = 0
						if dev.states["lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])):
							anyUpdate=True
							self.addToStatesUpdateList("{}".format(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])))

					if anyUpdate:
						self.addToStatesUpdateList("{}".format(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])

					pad = self.padStatusForDevListing(devI["status"])

					if dev.states["statusDisplay"] != (devI["status"]).ljust(pad)+devI["timeOfLastChange"]:
						self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
					self.executeUpdateStatesList()

					try:
						props = dev.pluginProps
						if props["address"] != self.formatiPforAddress(devI["ipNumber"]):
							if props["address"].split("-")[0] != self.formatiPforAddress(devI["ipNumber"]).split("-")[0] :
								if "suppressChangeMSG" in dev.states:
									if dev.states["suppressChangeMSG"] =="show":
										if theMAC in self.doubleIPnumbers:
											if len(self.doubleIPnumbers[theMAC]) ==1:
												self.indiLOG.log(10, "IPNumber changed,  old: {}".format(props["address"])+ "; new: {}".format(self.formatiPforAddress(devI["ipNumber"]))+ " for device MAC#: "+theMAC +" to switch off changed message: edit this device and select no msg")
											else:
												self.indiLOG.log(10, "Multiple IPNumbers for device MAC#: "+theMAC+" -- {}".format(self.doubleIPnumbers[theMAC])+" to switch off changed message: edit this device and select no msg")
										else:
												self.indiLOG.log(10, "IPNumber changed,  old: {}".format(props["address"])+ "; new: {}".format(self.formatiPforAddress(devI["ipNumber"]))+ " for device MAC#: "+theMAC+" to switch off changed message: edit this device and select no msg")
								indigo.variable.updateValue( "ipDevsOldNewIPNumber", dev.name.strip(" ")+"/"+theMAC.strip(" ")+"/"+props["address"].strip(" ")+"/"+self.formatiPforAddress(devI["ipNumber"]).strip(" ") )

							props["address"]=self.formatiPforAddress(devI["ipNumber"])
							dev.replacePluginPropsOnServer(props)
					except:
						if self.decideMyLog("Ping"): self.indiLOG.log(10, "props check did not work")
					devI["devExists"]	=1

			for theMAC in self.allDeviceInfo:
				if theMAC == "": continue
				devI = self.allDeviceInfo[theMAC]
				if devI["devExists"] == 0 and self.acceptNewDevices and theMAC not in self.ignoredMAC:

	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " creating device {}".format(devI))
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
						self.addToStatesUpdateList("{}".format(dev.id),"MACNumber",		theMAC)
						self.addToStatesUpdateList("{}".format(dev.id),"ipNumber",			devI["ipNumber"])
						self.addToStatesUpdateList("{}".format(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
						self.addToStatesUpdateList("{}".format(dev.id),"status",			devI["status"])
						self.addToStatesUpdateList("{}".format(dev.id),"nickName",			devI["nickName"])
						self.addToStatesUpdateList("{}".format(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
						self.addToStatesUpdateList("{}".format(dev.id),"hardwareVendor",	devI["hardwareVendor"])
						self.addToStatesUpdateList("{}".format(dev.id),"deviceInfo",		devI["deviceInfo"])
						self.addToStatesUpdateList("{}".format(dev.id),"suppressChangeMSG", devI["suppressChangeMSG"])
						self.addToStatesUpdateList("{}".format(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						self.addToStatesUpdateList("{}".format(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						if theMAC in self.wifiMacList:
							self.addToStatesUpdateList("{}".format(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])

						self.updateDeviceWiFiSignal(theMAC)
						usePing = devI["usePing"]
						if  "{}".format(devI["useWakeOnLanSecs"]) !="0":
							usePing +="-WOL:{}".format(devI["useWakeOnLanSecs"])
						if "usePing-WOL" in dev.states: self.addToStatesUpdateList("{}".format(dev.id),"usePing-WOL",			usePing)
						self.addToStatesUpdateList("{}".format(dev.id),"WiFi",				devI["WiFi"])
						pad = self.padStatusForDevListing(devI["status"])
						self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",	devI["status"].ljust(pad)+devI["timeOfLastChange"])
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
		except Exception:
			self.logger.error("", exc_info=True)
			
		return

##############################################
	def checkIfDevicesChanged(self):
		try:
	#		if self.decideMyLog("Logic"): self.indiLOG.log(10, " check if devices changed..")
			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				#if  dev.pluginId.find("com.karlwachs.fingscan") == -1 :continue
				devID="{}".format(dev.id)
				theStates = dev.states.keys()
				update = 0
				if "MACNumber" in theStates:
					theMAC = dev.states["MACNumber"]
					if theMAC =="": continue
					if not theMAC in self.allDeviceInfo: continue
					devI=self.allDeviceInfo[theMAC]
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " checking MAC/values: "+theMAC+":{}".format(devI))
					devI["deviceId"]	=dev.id
					if dev.name != devI["deviceName"]:
						update = 1
						devI["nickName"] 	= dev.name
						devI["deviceName"]	= dev.name
						#dev.updateStateOnServer("nickName",	devI["nickName"])
						self.addToStatesUpdateList("{}".format(dev.id),"nickName",	devI["nickName"])
					if dev.states["hardwareVendor"] != devI["hardwareVendor"]:
						devI["hardwareVendor"]		=dev.states["hardwareVendor"]
						update = 2
					if dev.states["deviceInfo"] != devI["deviceInfo"]:
						devI["deviceInfo"]		= dev.states["deviceInfo"]
					if dev.states["WiFi"] != devI["WiFi"]:
						test 					=dev.states["WiFi"]
						if test ==0:devI["WiFi"]=""
						else:		devI["WiFi"]=dev.states["WiFi"]
						update = 3
				if update>0:
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " updating MAC: "+theMAC)
					self.updateIndigoIpVariableFromDeviceData(theMAC)
		except Exception:
			self.logger.error("", exc_info=True)
		return

##############################################
	def updateAllIndigoIpDeviceFromDeviceData(self,statesToUdate=["all"]):
		devcopy = copy.deepcopy(self.allDeviceInfo)
		for theMAC in devcopy:
			if theMAC in self.ignoredMAC: continue
			self.updateIndigoIpDeviceFromDeviceData(theMAC,statesToUdate)
##############################################
	def updateIndigoIpDeviceFromDeviceData(self,theMAC, statesToUpdate, justStatus=""):
		if theMAC in self.ignoredMAC: return
		try:
			try:
				devI = self.allDeviceInfo[theMAC]
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "updating dev and states: {}/{}, newStatus:{}".format(theMAC, statesToUpdate, devI["status"]))
			except:
				self.indiLOG.log(40, "deleteIndigoIpDevicesData: MAC Number: {} information does not exist in allDeviceInfo".format(theMAC))
				return
			try:
				devId =devI["deviceId"]
				dev = indigo.devices[devId]
				if justStatus != "": # update only status for quick turn around
					#dev.updateStateOnServer("status",justStatus)
					self.addToStatesUpdateList("{}".format(dev.id), "status", justStatus)
					pad = self.padStatusForDevListing(justStatus)
					#dev.updateStateOnServer("statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", localtime()))
					self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
					if "lastFingUp" in dev.states:
						if dev.states["lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])):
							self.addToStatesUpdateList("{}".format(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])))
					self.executeUpdateStatesList()
					self.allDeviceInfo[theMAC]["status"] =justStatus
					return
			except:
	# create new device
				name = "MAC-"+theMAC,
				if "nickName" in devI:
					if devI["nickName"] != "": 	name = devI["nickName"]
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
						self.addToStatesUpdateList("{}".format(dev.id),"MACNumber",			theMAC)
						self.addToStatesUpdateList("{}".format(dev.id),"ipNumber",			devI["ipNumber"])
						self.addToStatesUpdateList("{}".format(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
						self.addToStatesUpdateList("{}".format(dev.id),"status",			devI["status"])
						self.addToStatesUpdateList("{}".format(dev.id),"nickName",			devI["nickName"])
						self.addToStatesUpdateList("{}".format(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
						self.addToStatesUpdateList("{}".format(dev.id),"hardwareVendor",	devI["hardwareVendor"])
						self.addToStatesUpdateList("{}".format(dev.id),"deviceInfo",		devI["deviceInfo"])
						self.addToStatesUpdateList("{}".format(dev.id),"WiFi",				devI["WiFi"])
						self.addToStatesUpdateList("{}".format(dev.id),"usePing-WOL",		devI["usePing"]+"-{}".format(devI["useWakeOnLanSecs"]))
						self.addToStatesUpdateList("{}".format(dev.id),"suppressChangeMSG", devI["suppressChangeMSG"])
						self.addToStatesUpdateList("{}".format(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						self.addToStatesUpdateList("{}".format(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						if theMAC in self.wifiMacList:
							self.addToStatesUpdateList("{}".format(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])
				
						pad = self.padStatusForDevListing(devI["status"])
						self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
						devI["deviceId"]	=dev.id
						devI["deviceName"]	=dev.name
						devI["devExists"]	=1
						self.executeUpdateStatesList()

				return
			
			if len(statesToUpdate) > 0:
				anyUpdate = False
	# update old device
				if "ipNumber" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states["ipNumber"] != devI["ipNumber"]:
						self.addToStatesUpdateList("{}".format(dev.id),"ipNumber",			devI["ipNumber"])
						anyUpdate=True
				if "status" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states["status"] != devI["status"]:
						self.addToStatesUpdateList("{}".format(dev.id),"status",			devI["status"])
						anyUpdate=True

				if "nickName" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states["nickName"] != devI["nickName"]:
						self.addToStatesUpdateList("{}".format(dev.id),"nickName",			devI["nickName"])
						anyUpdate=True
				if "noOfChanges" in statesToUpdate or statesToUpdate[0]=="all":
					if "{}".format(dev.states["noOfChanges"]) != "{}".format(devI["noOfChanges"]):
						self.addToStatesUpdateList("{}".format(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
						anyUpdate=True
				if "hardwareVendor" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states["hardwareVendor"] != devI["hardwareVendor"]:
						self.addToStatesUpdateList("{}".format(dev.id),"hardwareVendor",	devI["hardwareVendor"])
						anyUpdate=True
				if "deviceInfo" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states["deviceInfo"] != devI["deviceInfo"]:
						self.addToStatesUpdateList("{}".format(dev.id),"deviceInfo",		devI["deviceInfo"])
						anyUpdate=True
				if "WiFi" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states["WiFi"] != devI["WiFi"]:
						self.addToStatesUpdateList("{}".format(dev.id),"WiFi",				devI["WiFi"])
						if theMAC in self.wifiMacList:
							self.addToStatesUpdateList("{}".format(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])
						anyUpdate=True

				usePing = devI["usePing"]
				if  "{}".format(devI["useWakeOnLanSecs"]) !="0":
					usePing +="-WOL:{}".format(devI["useWakeOnLanSecs"])
				if "usePing-WOL" in statesToUpdate or statesToUpdate[0]=="all":
					if "usePing-WOL" in dev.states:
						if dev.states["usePing-WOL"] != usePing:
							anyUpdate=True
							self.addToStatesUpdateList("{}".format(dev.id),"usePing-WOL",			usePing)
				if "suppressChangeMSG" in statesToUpdate or statesToUpdate[0]=="all":
					if "suppressChangeMSG" in dev.states:
						if dev.states["suppressChangeMSG"] !=devI["suppressChangeMSG"]:
							anyUpdate=True
							self.addToStatesUpdateList("{}".format(dev.id),"suppressChangeMSG",			devI["suppressChangeMSG"])

				if anyUpdate:
					self.addToStatesUpdateList("{}".format(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])

				if statesToUpdate[0]=="all" or "status" in statesToUpdate or "ipNumber" in statesToUpdate or "WiFi" in statesToUpdate:
					pad = self.padStatusForDevListing(devI["status"])
					if (devI["status"]).ljust(pad)+devI["timeOfLastChange"] !=dev.states["statusDisplay"]:
						self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",	(devI["status"]).ljust(pad)+devI["timeOfLastChange"])
					props = dev.pluginProps
					try:
						if props["address"] != self.formatiPforAddress(devI["ipNumber"]):
							if "suppressChangeMSG" in dev.states:
								if dev.states["suppressChangeMSG"] =="show":
									self.indiLOG.log(10, "MAC#:"+theMAC  +" -- old IP: {}".format(props["address"])+ ";  new IP number: {}".format(self.formatiPforAddress(devI["ipNumber"]))+" to switch off changed message: edit this device and select no msg")
							indigo.variable.updateValue( "ipDevsOldNewIPNumber", dev.name.strip(" ")+"/"+theMAC.strip(" ")+"/"+props["address"].strip(" ")+"/"+self.formatiPforAddress(devI["ipNumber"]).strip(" ") )
							props["address"]=self.formatiPforAddress(devI["ipNumber"])
							dev.replacePluginPropsOnServer(props)
					except:
						if self.decideMyLog("Ping"): self.indiLOG.log(10, "props check did not work")

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


		except Exception:
			self.logger.error("", exc_info=True)
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

	#		if self.decideMyLog("Logic"): self.indiLOG.log(10, " list of devices to be deleted: %s"%theList)

			for theMAC in theList:
				try:
					devI=self.allDeviceInfo[theMAC]
					devID =devI["deviceId"]
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, "deleting device information for theMAC/deviceName "+ theMAC+"/{}".format(self.allDeviceInfo[theMAC]["deviceName"]))
					indigo.device.delete(devID)
				except:
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "deleteIndigoIpDevicesData: theMAC/deviceID/deviceName"+ theMAC+"/{}".format(devID)+"/{}".format(self.allDeviceInfo[theMAC]["deviceName"])+" device does not exist")
				
				try:
					devV=self.indigoIpVariableData[theMAC]
					indigo.variable.delete("ipDevice"+devV["ipDevice"])
				except:
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "deleteIndigoIpDevicesData: theMAC "+ theMAC+ " information does not exist in indigoIpVariableData")


				try:
					theName= devI["deviceName"]
					del self.allDeviceInfo[theMAC]
				except:
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "deleteIndigoIpDevicesData: name/MAC "+ theName+"/"+theMAC+" information does not exist in allDeviceInfo")

	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "deleted device MAC: "+theMAC)

			self.getIndigoIpVariablesIntoData()
		except Exception:
			self.logger.error("", exc_info=True)
		return

##############################################
	def getIndigoIpDevicesIntoData(self, lastUpdateSource= ""):  # do this once in the beginning..
	
		try:
			theMAC = ""
			if self.decideMyLog("Logic"): self.indiLOG.log(10, "getIndigoIpDevicesIntoData:  lastUpdateSource:{}".format(lastUpdateSource) )
			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				if not dev.enabled: continue
				theStates = dev.states.keys()
				if "MACNumber" in theStates:
					theMAC = dev.states["MACNumber"]
					if theMAC =="": continue
					update = 0
					if not theMAC in self.allDeviceInfo:
						self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
						update = 5
					devI=self.allDeviceInfo[theMAC]
					props = dev.pluginProps
					if dev.name != devI["deviceName"]:
						update = 1
						devI["nickName"] 	= dev.name
						devI["deviceName"]	= dev.name
						#dev.updateStateOnServer("nickName",	devI["nickName"])
						self.addToStatesUpdateList("{}".format(dev.id),"nickName",	devI["nickName"])
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
					devI["noOfChanges"]		= int(dev.states["noOfChanges"])
					devI["hardwareVendor"]		= dev.states["hardwareVendor"]
					devI["deviceInfo"]			= dev.states["deviceInfo"]
					try:    devI["lastFingUp"]	= devI["lastFingUp"]	= time.mktime( datetime.datetime.strptime(dev.states["lastFingUp"],"%Y-%m-%d %H:%M:%S").timetuple()  )
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
						devI["expirationTime"]  = 90


					if "suppressChangeMSG" in dev.states:
						devI["suppressChangeMSG"]			= dev.states["suppressChangeMSG"]
					else:
						devI["suppressChangeMSG"]			= "show"
				if update > 0:
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " updating MAC: "+theMAC)
					self.updateIndigoIpVariableFromDeviceData(theMAC)
			self.executeUpdateStatesList()    

		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "MAC#                           "+ theMAC)
			try:
				self.indiLOG.log(40, " indigoIpVariableData:     {}".format(self.indigoIpVariableData[theMAC]))
			except:
				self.indiLOG.log(40, " indigoIpVariableData: all {}".format(self.indigoIpVariableData))
			try:
				self.indiLOG.log(40, " allDeviceInfo:            {}".format(self.allDeviceInfo[theMAC]))
			except:
				self.indiLOG.log(40, " allDeviceInfo:  all       {}".format(self.allDeviceInfo))
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
					devV["ipDevice"] = "{}".format(self.indigoEmpty[0])
				except:
					self.indiLOG.log(40,  "updateIndigoIpVariableFromDeviceData indigoEmpty not initialized" +"{}".format(self.indigoEmpty))
					self.indiLOG.log(40,  "updateIndigoIpVariableFromDeviceData theMAC# " +"{}".format(theMAC))
					self.indiLOG.log(40,  "updateIndigoIpVariableFromDeviceData indigoIpVariableData" +"{}".format(self.indigoIpVariableData[theMAC]))
					devV["ipDevice"] = "1"
				self.indigoNumberOfdevices +=1
				devV["index"] = self.indigoNumberOfdevices-1
				self.indigoIndexEmpty -= 1  # one less empty slot
				if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list


			devI=self.allDeviceInfo[theMAC]
			updstr  =self.padMAC(theMAC)
			updstr += ";"+self.padIP(devI["ipNumber"])
			updstr += ";"+self.padDateTime(devI["timeOfLastChange"])
			updstr += ";"+devI["status"]
			updstr += ";"+self.padStatus(devI["status"])+self.padNoOfCh(devI["noOfChanges"])
			updstr += ";"+self.padNickName(devI["nickName"])
			updstr += ";"+self.padVendor(devI["hardwareVendor"])
			updstr += ";"+self.padDeviceInfo(devI["deviceInfo"])
			updstr += ";"+devI["WiFi"].rjust(5)
			updstr += ";"+devI["WiFiSignal"].rjust(10)
			updstr += ";"+(devI["usePing"]+"-{}".format(devI["useWakeOnLanSecs"])).rjust(13)+";"
			theValue = updstr.split(";")

			devV["ipNumber"]			= theValue[1].strip()
			devV["timeOfLastChange"]	= theValue[2].strip()
			devV["status"]				= theValue[3].strip()
			try:
				devV["noOfChanges"]	= int(theValue[4].strip())
			except:
				devV["noOfChanges"]	= 0
			devV["nickName"]			= theValue[5].strip()
			devV["hardwareVendor"]		= theValue[6].strip()
			devV["deviceInfo"]			= theValue[7].strip()
			devV["WiFi"]				= theValue[8].strip()
			devV["usePing"]			= theValue[9].strip()


			diff = False
			try:
				curr = indigo.variables["ipDevice"+devV["ipDevice"]].value.split(";")
			except:
				self.indiLOG.log(30, " updating ipDevice "+devV["ipDevice"]+" does not exist , (re)creating")
				
				curr =[]
			
			old = updstr.split(";")
			if len(old) ==len(curr):
				for i in range(len(curr)):
					if i==2: continue# skip the date field.
					if curr[i] != old[i]:
						diff= True
						break
			else:
				diff=True
			if diff:
				try:
					indigo.variable.updateValue("ipDevice"+devV["ipDevice"], updstr)
				except:
					indigo.variable.create("ipDevice"+devV["ipDevice"], updstr,self.indigoVariablesFolderID)

		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "MAC#                           "+ theMAC)
			try:
				self.indiLOG.log(40, " indigoIpVariableData:     {}".format(self.indigoIpVariableData[theMAC]))
			except:
				self.indiLOG.log(40, " indigoIpVariableData: all {}".format(self.indigoIpVariableData))
			try:
				self.indiLOG.log(40, " allDeviceInfo:            {}".format(self.allDeviceInfo[theMAC]))
			except:
				self.indiLOG.log(40, " allDeviceInfo:  all       {}".format(self.allDeviceInfo))

		return 0


########################################
	def updateallDeviceInfofromVariable(self):


		try:
			for theMAC in self.indigoIpVariableData:
				devV = self.indigoIpVariableData[theMAC]
				if not theMAC in self.allDeviceInfo:
					self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
				for xx in emptyAllDeviceInfo:
					if xx not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC] = copy.copy(emptyAllDeviceInfo[xx])
				devI = self.allDeviceInfo[theMAC]
				devI["ipNumber"]			= devV["ipNumber"].strip()
				devI["timeOfLastChange"]	= devV["timeOfLastChange"].strip()
				devI["status"]				= devV["status"].strip()
				try:
					devI["noOfChanges"]	= int(devV["noOfChanges"])
				except:
					devI["noOfChanges"]	= 0
				devI["nickName"]			= devV["nickName"].strip()
				devI["hardwareVendor"]		= devV["hardwareVendor"].strip()
				devI["deviceInfo"]			= devV["deviceInfo"].strip()
				if "WiFi" not in devV:
					devI["WiFi"]			= ""
				else:
					devI["WiFi"]			= devV["WiFi"].strip()
					
				devI["usePing"]			= "usePing"
				devI["usePing"]		    = ""
				devI["useWakeOnLanSecs"]	= 0
				if "usePing"  in devV:
					usePing = (devV["usePing"].strip()).split("-")
					devI["usePing"]			 = usePing[0]
					if len(usePing) == 2:
						devI["useWakeOnLanSecs"] = int(usePing[1])
						
				if "deviceId" not in devI: 		devI["deviceId"]=""
				if "deviceName" not in devI:	devI["deviceName"]=""

		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "MAC# "+ theMAC+" indigoIpVariableData: {}".format(self.indigoIpVariableData[theMAC]))
			self.indiLOG.log(40, "MAC# "+ theMAC+" allDeviceInfo:        {}".format(self.allDeviceInfo[theMAC]))

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
		if ddd == None:
			return " ".ljust(25)
		ddd= ddd.replace("\n","")
		theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
		blanks = " "
		for kk in range(1,theNumberOfBlanks):
			blanks += " "
		return "  "+ddd+blanks
	
########################################
	def padDeviceInfo(self,ddd):
		if ddd == None:
			return " ".ljust(25)
		ddd= ddd.replace("\n","")
		theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
		blanks = " "
		for kk in range(1,theNumberOfBlanks):
			blanks += " "
		return "  "+ddd+blanks
	
########################################
	def padIP(self,xxx):
		if xxx == None:
			return " ".ljust(25)
		ddd = len(xxx)
		pad = "   "
		if ddd == 11:	pad = "       "
		if ddd == 12:	pad = "     "
		return "   "+xxx+pad
	
########################################
	def padNickName(self,ddd):
		if ddd == None:
			return " ".ljust(32)
		theNumberOfBlanks =min(32,max(0,(17-len(ddd))*2))
		blanks = "   "
		for kk in range(1,theNumberOfBlanks):
			blanks += " "
		return "   "+ddd+blanks
	
########################################
	def padNoOfCh(self,xxx):
		if xxx == None:
			return " ".ljust(25)
		xxx=int(xxx)
		if xxx < 10:	return "    {}".format(xxx)+"               "
		if xxx < 100:	return "    {}".format(xxx)+"             "
		if xxx < 1000:	return "    {}".format(xxx)+"           "
		if xxx < 10000:	return "    {}".format(xxx)+"         "
		return "    {}".format(xxx)+"       "
	
	
########################################
	def padStatus(self,xxx):
		if xxx == "up":		return "       "
		if xxx == "down":	 	return "   "
		if xxx == "expired":	return ""
		if xxx == "changed":	return ""
		if xxx == "double":	return " "
		return " "
	
########################################
	def padMAC(self,xxx):
		yyy ="{}".format(xxx)
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
		theNumberOfBlanks = min(10,max(0,theNumberOfBlanks))
		
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
			ips[3] += "-changed"
		elif "double" in ipN:
			ips[3] += "-double"
		else:
			ips[3] += "        "
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


####----------------- get path to indigo programs ---------

	def addToStatesUpdateList(self,devId,key,value):
		try:

			if devId in self.updateStatesList: 
				if key in self.updateStatesList[devId]:
					if value != self.updateStatesList[devId][key]:
						self.updateStatesList[devId][key]=value
					return
			else:  self.updateStatesList[devId]={}      
			self.updateStatesList[devId][key] = value

		except Exception as e:
			sself.logger.error("", exc_info=True)
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
								actualChanged.append({"key":key, "value":value})
								if key == "status": indigo.variable.updateValue("ipDevsLastDevChangedIndigoName",dev.name)
						else:            
							if value != newStates[key]:
								newStates[key] = value
						if key == "status":
							if value in ["up", "ON"] :
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							elif value in ["down", "off"]:
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
							elif value in ["expired", "REC"] :
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
							msg = {"action":"event", "id":"{}".format(dev.id), "name":dev.name, "state":"status", "valueForON":"up", "newValue":value.lower()}
							if self.decideMyLog("BC"): self.indiLOG.log(10, "executeUpdateStatesDict  msg added :" + "{}".format(msg))
							self.sendBroadCastEventsList.append(msg)
							

					if  newStates == "":
						self.updateStatesList[devId]={}           
						if actualChanged !=[]:
							#indigo.server.log("%14.3f"%time.time()+"  "+dev.name.ljust(25)  + "{}".format(actualChanged)) 
							dev.updateStatesOnServer(actualChanged)
							
			if len(self.sendBroadCastEventsList) >0: self.sendBroadCastNOW()
			if  newStates != "":  
				return newStates              
		except Exception:
			self.logger.error("", exc_info=True)


	####----------------- if FINGSCAN is enabled send update signal  ---------
	def sendBroadCastNOW(self):
		try:
			if self.decideMyLog("BC"): self.indiLOG.log(10, "sendBroadCastNOW enter" )
			x = ""
			if  self.enableBroadCastEvents == "0":
				self.sendBroadCastEventsList = []
				return x
			if self.sendBroadCastEventsList == []:  
				return x
				
			msg = copy.copy(self.sendBroadCastEventsList)
			self.sendBroadCastEventsList = []
			if len(msg) >0:
				msg ={"pluginId":self.pluginId, "data":msg}
				try:
					if self.decideMyLog("BC"): self.indiLOG.log(10, "updating BC with " + "{}".format(msg) )
					indigo.server.broadcastToSubscribers("deviceStatusChanged", json.dumps(msg))
				except Exception as e:
					self.logger.error("", exc_info=True)

		except Exception as e:
				self.logger.error("", exc_info=True)
		return x

####-------------------------------------------------------------------------####
	def isValidIP(self, ip0):
		ipx = ip0.split(".")
		if len(ipx) != 4:									return False	# not complete
		else:
			for ip in ipx:
				try:
					if  int(ip) < 0  or  int(ip) > 255: 	return False	# out of range
				except:										return False	# not integer
		if True:											return True		# test passed 

	####-----------------	 ---------
	def completePath(self,inPath):
		if len(inPath) == 0: return ""
		if inPath == " ":	 return ""
		if inPath[-1] != "/": inPath += "/"
		return inPath


####-----------------	 ---------
	def decideMyLog(self, msgLevel):
		try:
			if msgLevel	 == "all" or "all" in self.debugLevel:	 return True
			if msgLevel	 == ""	 and "all" not in self.debugLevel:	 return False
			if msgLevel in self.debugLevel:							 return True
			return False
		except Exception as e:
				self.logger.error("", exc_info=True)
		return False


####-----------------	 ---------
	def IPCalculator(self, ip_address, cdir):
		try:
			binary_IP = list(map(lambda x: bin(x)[2:].zfill(8), map(int, ip_address.split('.'))))

			mask = [0, 0, 0, 0]
			for i in range(int(cdir)):
				#print( i//8, i%8)
				mask[i // 8] += 1 << (7 - i % 8)
			binary_Mask   = list(map(lambda x: bin(x)[2:].zfill(8), mask))

			tt = list()
			for i in mask:
				tt.append(255 - i)
			negation_Mask = list(map(lambda x: bin(x)[2:].zfill(8),tt))

			network = list()
			for x, y in zip(binary_IP, binary_Mask):
				network.append(int(x, 2) & int(y, 2))

			broadcast = list()
			for x, y in zip(binary_IP, negation_Mask):
				broadcast.append(int(x, 2) | int(y, 2))

			min_range = network
			min_range[-1] += 1
			max_range = copy.copy(broadcast) # copy.copy is needed, otherwise boradcast itself is changed
			max_range[-1] -= 1

			netinfo= {"netMask":"{}".format(".".join(map(str, mask))),
					"netWorkId":"{}".format(".".join(map(str, network))),
					"broadcast":"{}".format(".".join(map(str, broadcast))),
					"hostRange":"{}".format("{} - {}".format(".".join(map(str, min_range)), ".".join(map(str, max_range)))),
					"maxHosts":(2 ** sum(map(lambda x: sum(c == '1' for c in x), negation_Mask))) - 2}	   

			return netinfo
		except Exception:
			self.logger.error("", exc_info=True)


####-------------------------------------------------------------------------####
	def readPopen(self, cmd, pid = False):
		try:
			if type(cmd) == type([]):
				ret, err = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			else:
				ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			return ret.decode('utf_8'), err.decode('utf_8')
		except Exception:
			self.logger.error("", exc_info=True)



##################################################################################################################
####-----------------  valiable formatter for differnt log levels ---------
# call with: 
# formatter = LevelFormatter(fmt='<default log format>', level_fmts={logging.INFO: '<format string for info>'})
# handler.setFormatter(formatter)
class LevelFormatter(logging.Formatter):
	def __init__(self, fmt=None, datefmt=None, level_fmts={}, level_date={}):
		self._level_formatters = {}
		self._level_date_format = {}
		for level, formt in level_fmts.items():
			# Could optionally support level names too
			self._level_formatters[level] = logging.Formatter(fmt=formt, datefmt=level_date[level])
		# self._fmt will be the default format
		super(LevelFormatter, self).__init__(fmt=formt, datefmt=datefmt)

	def format(self, record):
		if record.levelno in self._level_formatters:
			return self._level_formatters[record.levelno].format(record)

		return super(LevelFormatter, self).format(record)


