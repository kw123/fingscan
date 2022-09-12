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

nOfDevicesInEvent   = 12
nEvents		        = 20


emptyAllDeviceInfo = {
	"ipNumber": "0.0.0.0",
	"timeOfLastChange": "0",
	"status": "down",
	"noOfChanges": 0,
	"hardwareVendor": "",
	"deviceInfo": "",
	"usePing": "doNotUsePing",
	"useWakeOnLanSecs": 0,
	"useWakeOnLanLast": 0,
	"suppressChangeMSG": "show",
	"deviceId": 0,
	"deviceName": "",
	"fingLastUp": 0,
	"expirationTime": 0,
	"variableName": ""
	}
emptyindigoIpVariableData = {
	"ipNumber": "0.0.0.0",
	"timeOfLastChange": "0",
	"status": "down",
	"noOfChanges": 0,
	"hardwareVendor": "",
	"deviceInfo": "",
	"ipDevice": "00",
	"index": 0,
	"usePing": ""
	}
emptyEVENT = {#        
	"IPdeviceMACnumber"    :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"timeOfLastON"         :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"timeOfLastOFF"        :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"secondsOfLastON"      :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"secondsOfLastOFF"     :{"{}".format(i):0   for i in range(1,nOfDevicesInEvent)},
	"currentStatusHome"    :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"currentStatusAway"    :{"{}".format(i):"0" for i in range(1,nOfDevicesInEvent)},
	"nextTimeToCheck"	   :{"{}".format(i):1.0 for i in range(1,nOfDevicesInEvent)},
	"oneAway": "0",
	"allAway": "0",
	"nAway": 0,
	"allHome": "0",
	"oneHome": "0",
	"nHome": 0,
	"secsOfLastAllHomeTrigger": 0,
	"timeofLastAllAwayTrigger": 0,
	"secsOfLastOneHomeTrigger": 0,
	"timeofLastOneAwayTrigger": 0,
	"minimumTimeAway": 300,
	"minimumTimeHome": 0,
	"enableDisable": "0",
	"dataFormat": "3.0"
	}
indigoMaxDevices = 1024

_debAreas = ["Logic", "Ping", "Events", "BC", "Special", "all"]


kDefaultPluginPrefs = {
				"network":					"192.168.1.0",
				"netwType":					"24",
				"indigoDevicesFolderName":	"ipDevices",
				"indigoVariablesFolderName":"ipDevices",
				"acceptNewDevices":			"1",
				"enableBroadCastEvents":	"0",
				"password":					"your MAC password here",
				"inbetweenPingType":		"1",
				"sleepTime":				"2",
				"debugLogic":				False,
				"debugPing":				False,
				"debugEvents":				False,
				"debugBC":					False,
				"debugStartFi":				False,
				"debugSpecial":				False,
				"debugall":					False,
				"enableMACtoVENDORlookup":	"30",
				"do_cProfile":				"on/off/print",
				"enableReLoadPluginHourHour":		"1"
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
				self.pythonPath = "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
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
			if False and os.path.exists(self.indigoPluginDirOld+"fing.data"):
				indigo.server.log(" moving "+ "cp -R " + self.indigoPluginDirOld+"* '" + self.indigoPreferencesPluginDir+"'" )
				os.system("cp -R " + self.indigoPluginDirOld+"* '" + self.indigoPreferencesPluginDir+"'" )

			self.checkOpsysVersion()

			self.indigoCommand				= "none"
			self.savePrefs 					= 0
			self.updateStatesList			= {}
			self.updatePrefs				= False
			self.fingDataModTimeOLD			= 0
			self.fingDataModTimeNEW			= 0
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
			self.allDeviceInfo				= {}
			self.triggerList				= []
			self.EVENTS						= {}
			self.indigoVariablesFolderID	= 0
			self.passwordOK					= "no"
			self.yourPassword				= ""
			self.quitNOW					= "no"

			self.executionMode				= "noInterruption"  ## interrupted by plugin/fingscan/configuration
			self.theNetwork					= "0.0.0.0"

			self.initConfig0()

		except Exception:
			self.logger.error("", exc_info=True)

		self.startTime = time.time()


####----------------- @ startup set global parameters, ---------
	def initConfig0(self):

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
			
			self.inbetweenPingType 		= self.pluginPrefs.get("inbetweenPingType", "0")
			self.sleepTime 				= int(self.pluginPrefs.get("sleepTime", 1))
			self.newSleepTime 			= self.sleepTime
			self.enableReLoadPluginHour	= self.pluginPrefs.get("enableLoadPlugin", "1")

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

############ kill old pending PING jobs
			self.killPing("all")

		except Exception as e:
				self.logger.error("", exc_info=True)
				self.quitNOW = "restart required; {}".format(e) 
				self.sleep(20)
		return


####----------------- @ startup set global parameters, ---------
	def initConfig(self):

		try:

########## get password
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

############ en/ disable mac to vendor lookup
		
			self.enableMACtoVENDORlookup    = self.pluginPrefs.get("enableMACtoVENDORlookup", "21")
			try: int(self.enableMACtoVENDORlookup)
			except: self.enableMACtoVENDORlookup = "0"
			self.waitForMAC2vendor = False
			if self.enableMACtoVENDORlookup != "0":
				self.M2V = MAC2Vendor.MAP2Vendor(pathToMACFiles=self.indigoPreferencesPluginDir+"mac2Vendor/", refreshFromIeeAfterDays = self.enableMACtoVENDORlookup, myLogger = self.indiLOG.log)
				self.waitForMAC2vendor = not self.M2V.makeFinalTable(quiet=True)


############ setup mac / devname /number selection list
			self.IPretList=[]
			for theMAC in self.allDeviceInfo:
				theString = self.allDeviceInfo[theMAC]["deviceName"] +"-" +self.allDeviceInfo[theMAC]["ipNumber"] + "-"+theMAC
				self.IPretList.append(( theMAC,theString ))
			self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
			self.IPretList.append((1, "Not used"))


############ check if version 1 if yes, upgrade to version 2
			retCode = self.checkIndigoVersion()


############ create indigo Event variables  and initialize ..
				
			self.cleanUpEvents()
			self.setupEventVariables()
	 

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
			

############ try to find hw vendor 
			self.indiLOG.log(20, "getting vendor info.. ")
			self.updateVendors()

		except Exception as e:
				self.logger.error("", exc_info=True)
				self.quitNOW = "restart required; {}".format(e) 
				self.sleep(20)


		return



########################################
	def updateVendors(self):
		try:
			if not self.waitForMAC2vendor:  self.waitForMAC2vendor = not self.M2V.makeFinalTable(quiet=True)
			if self.waitForMAC2vendor:  return 

			for theMAC in self.allDeviceInfo:
				for item in emptyAllDeviceInfo:
					if item not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC][item] = copy.copy(emptyAllDeviceInfo[item])
				if self.allDeviceInfo[theMAC]["timeOfLastChange"].find("0"): self.allDeviceInfo[theMAC]["timeOfLastChange"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

				update = 0
				if self.allDeviceInfo[theMAC]["hardwareVendor"].find("\n") >-1: 
					update = 1
					self.allDeviceInfo[theMAC]["hardwareVendor"] = self.allDeviceInfo[theMAC]["hardwareVendor"].strip("\n").strip()
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "{:}  devID:{:>15d} existingVendor >>{:}<<".format(theMAC, self.allDeviceInfo[theMAC]["deviceId"], self.allDeviceInfo[theMAC]["hardwareVendor"]) )
				if self.allDeviceInfo[theMAC]["deviceId"] != 0:             
					if len(self.allDeviceInfo[theMAC]["hardwareVendor"]) < 3 or  (self.allDeviceInfo[theMAC]["hardwareVendor"].find("<html>")) > -1 :
						vend = self.getVendorName(theMAC)
						if vend is None: vend = ""
						if self.decideMyLog("Logic"): self.indiLOG.log(10, "{}  Vendor info  >>{}<<".format(theMAC, vend ) )
						if vend != ""  or self.allDeviceInfo[theMAC]["hardwareVendor"].find("<html>") > -1: 
							update = 2

				if update > 0:
					if update == 1: 
						vend = self.allDeviceInfo[theMAC]["hardwareVendor"].strip("\n")
						if vend is None: vend = ""
					try: 
						self.indiLOG.log(10, " updating :{}  {}  to >>{}<<".format(theMAC, self.allDeviceInfo[theMAC]["deviceId"], vend))
						self.allDeviceInfo[theMAC]["hardwareVendor"]  = vend
						dev = indigo.devices[self.allDeviceInfo[theMAC]["deviceId"]]
						dev.updateStateOnServer("hardwareVendor",vend)
					except Exception as e:
						self.logger.error("", exc_info=True)
						
		except Exception as e:
				self.logger.error("", exc_info=True)
				self.quitNOW = "restart required; {}".format(e) 
				self.sleep(20)

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

				self.fingVersion = self.checkVersion()
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

		try:
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
			return fingVersion
		except Exception:
			self.logger.error("", exc_info=True)
		return  -1.0			


########################################
	def checkOpsysVersion(self):
		import platform
		self.opsys = 10.0
		try:
			opsys		= platform.mac_ver()[0].split(".")
			self.opsys		= float(opsys[0]+"."+opsys[1])
		except Exception:
			self.logger.error("", exc_info=True)
		return self.opsys			


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
	def setupEventVariables(self):
		try:
			try:
				indigo.variables.folder.create("FINGscanEvents")
				self.indiLOG.log(20, "FINGscanFolder folder created")
			except:
				pass
			self.FINGscanFolderID = indigo.variables.folders["FINGscanEvents"].id
			for nEvent in self.EVENTS:
				if self.EVENTS[nEvent]["enableDisable"] == "1":
					try: 	indigo.variable.create("allHome_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.create("oneHome_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.create("nHome_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.create("allAway_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.create("oneAway_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.create("nAway_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
				else:
					try: 	indigo.variable.delete("allHome_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.delete("oneHome_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.creadeletete("nHome_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.delete("allAway_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.delete("oneAway_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
					try: 	indigo.variable.delete("nAway_{}".format(nEvent), "",folder=self.FINGscanFolderID)
					except:	pass
	

			
			try:
				indigo.variable.create("FingEventDevChangedIndigoId",folder=self.FINGscanFolderID)
			except: pass

			for nEvent in self.EVENTS:
				if self.EVENTS[nEvent]["enableDisable"] == "1":
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
	def printConfig(self):
		try:
			self.indiLOG.log(10, "settings:  inbetweenPingType            {}".format(self.inbetweenPingType))
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
		self.killFing("all")
		self.killPing("all")


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
			imac = valuesDict["IPdeviceMACnumber"+nDev]
		
		except Exception:
			self.logger.error("", exc_info=True)
		return valuesDict


########################################
	def CALLBACKevent(self, valuesDict,typeId=""):

		try:
			
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
				imac= valuesDict["IPdeviceMACnumber"+nDev]

		
			valuesDict["minimumTimeHome"]				    	=	"{}".format(int(float(self.EVENTS[self.currentEventN]["minimumTimeHome"])))
			valuesDict["minimumTimeAway"]				    	=	"{}".format(int(float(self.EVENTS[self.currentEventN]["minimumTimeAway"])))
			valuesDict["enableDisable"]					    	=	self.EVENTS[self.currentEventN]["enableDisable"]
		
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
		return

##

########################################
	def buttonConfirmAddIgnoredMACsCALLBACK(self, valuesDict, typeId=""):
		theMAC = valuesDict["selectedMACIgnore"]
		if theMAC not in self.ignoredMAC:
			info = theMAC
			if theMAC in self.allDeviceInfo:
				info = theMAC+"-"+self.allDeviceInfo[theMAC]["deviceName"]+"-"+self.allDeviceInfo[theMAC]["ipNumber"]
			self.ignoredMAC[theMAC] = info
			self.saveIgnoredMAC()
		return valuesDict
########################################
	def buttonConfirmRemoveIgnoredMACsCALLBACK(self, valuesDict,typeId=""):
		theMAC = valuesDict["selectedMACRemove"]
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
	def buttonConfirmDevicesCALLBACK(self, valuesDict,typeId=""):
		errorDict=indigo.Dict()

		try:
			self.currentEventN = "{}".format(valuesDict["selectEvent"])
			if self.currentEventN == "0" or  self.currentEventN =="":
	#			errorDict = valuesDict
				return valuesDict

			if not self.currentEventN in self.EVENTS:
				self.EVENTS[self.currentEventN]= copy.deepcopy(emptyEVENT)

			if valuesDict["DeleteEvent"]:
				for nDev in self.EVENTS[self.currentEventN]["IPdeviceMACnumber"]:
					iDev= int(nDev)
					valuesDict["IPdeviceMACnumber"+nDev]	= "0"
				valuesDict["DeleteEvent"] 		= False
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


			for lDev in range(1,nOfDevicesInEvent+1):
				nDev= "{}".format(lDev)
				if "IPdeviceMACnumber"+nDev not in valuesDict: continue
				selectedMAC = valuesDict["IPdeviceMACnumber"+nDev]
				if selectedMAC == "1" or selectedMAC == "":
					self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev]	= "0"
					self.EVENTS[self.currentEventN]["currentStatusAway"][nDev]	= "0"
					self.EVENTS[self.currentEventN]["currentStatusHome"][nDev]	= "0"
					continue
				else:
					self.EVENTS[self.currentEventN]["secondsOfLastON"][nDev]	= int(time.time()+20.)
					self.EVENTS[self.currentEventN]["secondsOfLastOFF"][nDev]	= int(time.time()+20.)

					self.EVENTS[self.currentEventN]["IPdeviceMACnumber"][nDev] = selectedMAC


			valuesDict["EVENTS"] = json.dumps(self.EVENTS)

			#indigo.server.log("{}".format(self.EVENTS[self.currentEventN]))
			self.setupEventVariables()

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

			self.enableReLoadPluginHour = valuesDict["enableReLoadPluginHour"]


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
				self.inbetweenPing = {}
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


			if self.enableMACtoVENDORlookup != valuesDict["enableMACtoVENDORlookup"] and self.enableMACtoVENDORlookup == "0":
				rebootRequired                         = True
			self.enableMACtoVENDORlookup               = valuesDict["enableMACtoVENDORlookup"]

			self.acceptNewDevices = valuesDict["acceptNewDevices"] == "1"

	# clean up empty events
			self.cleanUpEvents()
	# save to indigo
			valuesDict["EVENTS"]	=	json.dumps(self.EVENTS)
			self.printConfig()

		except Exception:
			self.logger.error("", exc_info=True)
		return True, valuesDict



########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, devId):
		for theMAC in self.allDeviceInfo:
			if int(self.allDeviceInfo[theMAC]["deviceId"]) == devId:
				if valuesDict["setHardwareVendor"] !="":
					self.allDeviceInfo[theMAC]["hardwareVendor"]	= valuesDict["setHardwareVendor"]
				if valuesDict["setDeviceInfo"] !="":
					self.allDeviceInfo[theMAC]["deviceInfo"]		= valuesDict["setDeviceInfo"]
				self.allDeviceInfo[theMAC]["useWakeOnLanSecs"]	= int(valuesDict["setuseWakeOnLan"])
				if "useWakeOnLanLast" not in self.allDeviceInfo[theMAC]:
					self.allDeviceInfo[theMAC]["useWakeOnLanLast"]		= 0
				self.allDeviceInfo[theMAC]["usePing"]			= valuesDict["setUsePing"]
				self.allDeviceInfo[theMAC]["exprirationTime"]	= float(valuesDict["setExpirationTime"])
				self.allDeviceInfo[theMAC]["suppressChangeMSG"]	= valuesDict["setSuppressChangeMSG"]
				self.updateIndigoIpDeviceFromDeviceData(theMAC,["hardwareVendor", "deviceInfo", "usePing", "suppressChangeMSG"], calledFrom="validateDeviceConfigUi")
				self.updateIndigoIpVariableFromDeviceData(theMAC)
		return (True, valuesDict)



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
				
			self.deleteIndigoIpDevicesData("all")
			indigo.variable.updateValue("ipDevsNewDeviceNo","")
			indigo.variable.updateValue("ipDevsNoOfDevices","0")

		except Exception:
			self.logger.error("", exc_info=True)
		return

########################################
	def printEvents(self, printEvents="all"):
		try:
			if len(self.EVENTS) == 0:
				self.indiLOG.log(20, "printEvents: no EVENT defined \n")
				return


			out ="\nEVENT defs:::::::::::::::::: Start :::::::::::::::: -- {}\n".format(printEvents)
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
				listOfDevs = []
				evnt = self.EVENTS[nEvent]
				prntDist = False
				for nDev in evnt["IPdeviceMACnumber"]:
					try:
						if evnt["IPdeviceMACnumber"][nDev] == "": continue
						if evnt["IPdeviceMACnumber"][nDev] == "0": continue
						listOfDevs.append(int(nDev))
					except:
						continue

				if len(listOfDevs) == 0: continue
				out+= "EVENT:------------- #{:2},  is enabled:{} -----------------------------------------------------------------------------------------\n".format(nEvent, "T" if evnt["enableDisable"] == "1"  else"F")
				for iDev in range(1, nOfDevicesInEvent+1):
					if iDev not in listOfDevs: continue
					nDev = "{}".format(iDev)
					#sout+= "{}".format(evnt["IPdeviceMACnumber"]))
					try:
						theMAC = evnt["IPdeviceMACnumber"][nDev]
					except:
						continue
					
					try:
						devI = self.allDeviceInfo[theMAC]
					except: 
						out = "{}  is not defined, please remove from event# {}".format(theMAC, nEvent)
						continue
					out+= "dev#: {}".format(nDev).rjust(2)+" -- devNam:"+devI["deviceName"].ljust(25)[:25] +" -- MAC#:"+theMAC+" -- ip#:"+devI["ipNumber"].ljust(15)+" -- status:"+devI["status"].ljust(8)+"\n"
					


				out+= self.printEventLine("currentStatusHome"	 		, "currentStatusHome"		,nEvent,listOfDevs)
				out+= self.printEventLine("currentStatusAway"	 		, "currentStatusAway"		,nEvent,listOfDevs)
				out+= self.printEventLine("secondsOfLastON"				, "seconds WhenLast UP"		,nEvent,listOfDevs)
				out+= self.printEventLine("secondsOfLastOFF"			, "seconds WhenLast DOWN"	,nEvent,listOfDevs)
				out+= self.printEventLine("timeOfLastOFF"				, "time WhenLast DOWN"		,nEvent,listOfDevs)
				out+= self.printEventLine("timeOfLastON"				, "time WhenLast UP"		,nEvent,listOfDevs)
				out+=   	"Time right now:          :    {}\n".format(timeNowHMS)
				out+=   	"ALL Devices         Home :{}  -- reacts after minTimeNotHome\n".format(evnt["allHome"])
				out+=   	"AtLeast ONE Device  Home :{}  -- reacts after minTimeNotHome\n".format(evnt["oneHome"])
				out+=   	"n Devices           Home :{}  -- reacts after minTimeNotHome\n".format(evnt["nHome"])
				out+=   	"ALL Devices         Away :{}  -- reacts minTimeAway before trigger\n".format(evnt["allAway"])
				out+=   	"AtLeast ONE Device  Away :{}  -- reacts minTimeAway before trigger\n".format(evnt["oneAway"])
				out+=   	"n Devices           Away :{}  -- reacts minTimeAway before trigger\n".format(evnt["nAway"]) 
				out+=		"minTimeAway              :{:4.0f}[secs] before Away trigger\n".format(evnt["minimumTimeAway"])
				out+= 		"minTimeNotHome           :{:4.0f}[secs] before re-trigger Home\n".format(evnt["minimumTimeHome"])
			out+=			"EVENT defs:::::::::::::::::: END ::::::::::::::::::"
			self.indiLOG.log(20, out+"\n")
		except Exception:
			self.logger.error("", exc_info=True)
		return
########################################
	def printEventLine(self, name, nameText, nEvent, listOfDevs):
		out=""
		try:
			list = "" 
			for iDev in range(1, nOfDevicesInEvent+1):
				if iDev not in listOfDevs: continue
				nDev = "{}".format(iDev)
				if name == "secondsOfLastON" or  name == "secondsOfLastOFF" :
					list += "#"+nDev.rjust(2)+":"+"{}".format( int(time.time()) - int(self.EVENTS[nEvent][name][nDev]) ).rjust(12)+"  "
				elif name == "iDeviceName" :
					idevD,idevName,idevId = self.getIdandName("{}".format(self.EVENTS[nEvent][name][nDev]))
					list += "#"+nDev.rjust(2)+":"+idevName.rjust(12)+"  "
				else:
					list += "#"+nDev.rjust(2)+":"+"{}".format(self.EVENTS[nEvent][name][nDev]).rjust(12)+"  "
			out = (nameText+":").ljust(22) + list.strip("  ")
		except Exception as e:
			self.logger.error("{}".format(self.EVENTS[nEvent]), exc_info=True)
		return out+"\n"


##### execute triggers:

######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

	def triggerStartProcessing(self, trigger):
		self.triggerList.append(trigger.id)

	def triggerStopProcessing(self, trigger):
		if trigger.id in self.triggerList:
			self.triggerList.remove(trigger.id)

	#def triggerUpdated(self, origDev, newDev):
	#	self.logger.log(4, "<<-- entering triggerUpdated: %s" % origDev.name)
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

	def triggerEvent(self, eventId):
		try:
			if self.decideMyLog("Events"): self.indiLOG.log(10, "triggerEvent:{};".format(eventId))
			for trigId in self.triggerList:
				trigger = indigo.triggers[trigId]
				if self.decideMyLog("Events"): self.indiLOG.log(10, "testing trigger id:{}; eventId:{};  typeId:{}, fire:{}".format(trigId, eventId, trigger.pluginTypeId, trigger.pluginTypeId == eventId))
				if trigger.pluginTypeId == eventId:
					if self.decideMyLog("Events"): self.indiLOG.log(10, "firing trigger id:{}".format(trigId))
					indigo.trigger.execute(trigger)
					break
		except Exception:
			self.logger.error("", exc_info=True)
		return



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
			
		return True
########################################
	def pickDeviceFilter(self,filter=None,valuesDict=None,typeId=0):
		retList =[]
		for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				retList.append((dev.id,dev.name))
		retList.append((0, "all devices"))
		return retList
########################################
	def triggerEventCALLBACK(self, valuesDict, typeId):
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
	def inpPrintEVENTS(self, dummy1="", dummy2=""):
		self.indigoCommand = "PrintEVENTS"
		self.indiLOG.log(20, "command: Print EVENTS and configuration")
		return
########################################
	def inpResetEVENTS(self, dummy1="", dummy2=""):
		self.indigoCommand = "ResetEVENTS"
		self.indiLOG.log(20, "command: ResetEVENTS")
		return
########################################
	def inpResetDEVICES(self, dummy1="", dummy2=""):
		self.indigoCommand = "ResetDEVICES"
		self.indiLOG.log(20, "command: ResetDEVICES")
		return
########################################  not used anymore
	def inpEVENTAway1(self, dummy1="", dummy2=""):
		self.indigoCommand = "EVENT_Away_1"
		self.indiLOG.log(20, "command: EVENT_Away_1")
		return
########################################  not used anymore
	def inpEVENTHome1(self):
		self.indigoCommand = "EVENT_Home_1"
		self.indiLOG.log(20, "command: EVENT_Home_1")
		return
########################################
	def inpSaveData(self, dummy1="", dummy2=""):
		self.indigoCommand = "save"
		self.indiLOG.log(20, "command: save")
		retCode = self.writeToFile()
		self.indigoCommand = "none"
		self.indiLOG.log(20, "save done")
		return
########################################
	def inpLoadDevices(self, dummy1="", dummy2=""):
		self.indigoCommand = "loadDevices"
		self.indiLOG.log(20, "command: loadDevices")
		return
########################################
	def inpinpreloadVendorInfo(self, dummy1="", dummy2=""):
		self.indigoCommand = "reloadVendorInfo"
		self.indiLOG.log(20, "command: reloadVendorInfo")
		return
########################################
	def inpSortData(self, dummy1="", dummy2=""):
		self.indigoCommand = "sort"
		self.indiLOG.log(20, "command: sort")
		return
########################################
	def inpDetails(self, dummy1="", dummy2=""):
		self.indigoCommand = "details"
		self.indiLOG.log(20, "command: log IP-Services of your network")
		return
########################################
	def inpSoftrestart(self, dummy1="", dummy2=""):
		self.quitNOW = "softrestart"
		self.indiLOG.log(20, "command: softrestart")
		return
########################################


########################################
	def doLoadDevices(self):
		try:
			self.deleteIndigoIpDevicesData("all")
			self.sleep(1)
			self.readFromFile()
			self.sleep(1)
			self.getIndigoIpVariablesIntoData()
			self.sleep(1)
			self.updateallDeviceInfofromVariable()
			self.sleep(1)
			self.updateAllIndigoIpDeviceFromDeviceData(calledFrom="doLoadDevices")
			self.sleep(1)
			self.indiLOG.log(20, "       restore done")
		except Exception:
			self.logger.error("", exc_info=True)
		return


########################################
	def doSortData(self):
		self.indiLOG.log(20, "sorting ipDevices with IP Numbers")
		self.getIndigoIpVariablesIntoData()
		self.sortIndigoIndex()
		self.getIndigoIpVariablesIntoData()
		self.indiLOG.log(20, " sorting  done")
		return

########################################
	def doDetails(self):

		self.indiLOG.log(20, "starting log IP-Services of your network, might take several minutes, it will test each port on each ip-device, output to plugin.log and:{}".format(self.fingServicesOutputFileName))
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
		
		self.getIndigoIpVariablesIntoData()  ## refresh indigo data

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
				n2=devV["hardwareVendor"].strip()
				n3=devV["deviceInfo"].strip()
				if n3== "-":n3=""
				nickname= (n2+" "+n3).strip()
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
				n2=devI["hardwareVendor"].strip()
				n3=devI["deviceInfo"].strip()
				n4= "status: "+devI["status"].strip()
				if n3 == "-":n3=""
				nickname= (n2+" "+n3)
				out+= "IP-Device Number, Name, Vendor,..."+ devI["ipNumber"].ljust(17)+theMAC.ljust(19)+n4.ljust(17)+nickname+"\n"
		out+= "IP-Device Number, Name, Vendor,..."+"------------------------------------------------------------------------ "
		self.indiLOG.log(20,out+"         log IP-Services of your network, .......  done")
		fout=open(self.fingServicesOutputFileName,"w")
		fout.write(out)
		fout.close()
		return
	
	
########################################
	def writeToFile(self):
		
		self.indiLOG.log(20, "saving indigo data to file")
		f = open ( self.fingSaveFileName , "w")
		nwrite= min( len(self.indigoDevicesNumbers),self.indigoNumberOfdevices )
		for kk in range(nwrite):
				writestring = "{}".format(self.indigoDevicesNumbers[kk] )+";"+self.indigoDevicesValues[kk]+"\n"
				f.write(writestring)# .encode("utf8"))
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
			test = indigo.variables["ipDevice00"].value
			nitems = test.split(";")
			if len(nitems) != 9:
				self.indiLOG.log(30, "indigo variables:  resetting, due to new version" )
				for var in indigo.variables:
					if var.name.find("ipDevice") == -1: continue
					if var.name.find("00") >1: continue
					indigo.variable.delete(var.id)
		except Exception:
			pass

				
		try:
			test = indigo.variable.create("ipDevice00", "MAC-Number                ;     IP-Number       ;   Time-Of-Last-Change   ;Status;     N.of-Ch.    ;Name                     ;   Hardware-Vendor        ;   DeviceInfo               ;   usePing",self.indigoVariablesFolderID)
		except:
			test = indigo.variable.updateValue("ipDevice00", "MAC-Number                ;     IP-Number       ;   Time-Of-Last-Change   ;Status;     N.of-Ch.    ;Name                     ;   Hardware-Vendor        ;   DeviceInfo              ;   usePing")
		try:
			test = indigo.variable.create("ipDevsLastUpdate", "1",self.indigoVariablesFolderID)
		except:
			pass
		try:
			test = indigo.variable.create("ipDevsNewIPNumber", "1",self.indigoVariablesFolderID)
		except:
			pass
		try:
			test = indigo.variable.create("ipDevsNoOfDevices", "0",self.indigoVariablesFolderID)
		except:
			pass
		try:
			test = indigo.variable.create("ipDevsNewDeviceNo", "",self.indigoVariablesFolderID)
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsCommand", "-- not used anymore can be deleted --")
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsPid", "-- not used anymore can be deleted --")
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsFormat", "-- not used anymore can be deleted --")
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsDoNotAsk", "-- not used anymore can be deleted --")
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsPasswordMode", "-- not used anymore can be deleted --")
		except:
			pass
		try:
			test = indigo.variable.updateValue("ipDevsDebug", "-- not used anymore can be deleted --")
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


			if restartFing == 1:
				self.killFing("all")
			else:
				pids, parentPids = self.testFing()
				if len(pids) == 1 : return 1
				if len(pids) > 1 :
					self.killFing("onlyParents")
					return 1

 
			# start fing, send to background, dont wait, create 2 output files:  one table format file and one logfile
			if self.decideMyLog("StartFi"):	deblevelForStartFing = 20
			else:							deblevelForStartFing = 0
			
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
				lines = lines.strip("\n").split("\n")

				fingData = []
				for line in lines:
					ll = line.split(";")
					if len(ll) < 7: continue
					fingData.append(ll)
				if len(fingData) == 0: return 

				if fingData[0][5] in self.ignoredMAC: return 0

				self.indigoNeedsUpdate = True
				self.fingNumberOfdevices = 1
				self.fingDate            = self.column(fingData,0)
				self.fingStatus          = self.column(fingData,1)
				self.fingIPNumbers       = self.column(fingData,2)
				self.fingDeviceInfo      = self.column(fingData,4)
				self.fingMACNumbers      = self.column(fingData,5)
				self.fingVendor          = self.column(fingData,6)

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
							if self.sendWakewOnLanAndPing(theMAC,nBC= 2, waitForPing=500, countPings=2, waitBeforePing = 0.5, waitAfterPing = 0.1, calledFrom="getfingLog") == 0:
								self.fingStatus[kk] = "up"

					self.fingDate[kk] = self.fingDate[kk].replace("/", "-")
				return 1
			else:
				return 0
		except Exception:
			self.logger.error("", exc_info=True)
			self.indiLOG.log(40, "{}".format(fingData))
			self.finglogerrorCount +=1
			if self.finglogerrorCount > 40 and self.totalLoopCounter > 100 :
				self.indiLOG.log(40, "fing.log file does not exist or is empty \n    trying to stop and restart fing  " )
				self.initFing(1)  # restarting fing
				self.finglogerrorCount =0
			return -1
		return 1
	
	
########################################
	def getfingData(self):
		## get time stamp of last mode of fingData file in secs since 197x.., if new data read
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
				fingData = []
				for line in lines:
					ll = line.split(";")
					if len(ll) < 7: continue
					fingData.append(ll)
				
				self.fingDataModTimeOLD     = self.fingDataModTimeNEW
				if len(fingData) > 0:
					self.fingIPNumbers          = self.column(fingData,0)
					self.fingStatus             = self.column(fingData,2)
					self.fingDate               = self.column(fingData,3)
					self.fingDeviceInfo         = self.column(fingData,4)
					self.fingMACNumbers         = self.column(fingData,5)
					self.fingVendor             = self.column(fingData,6)
					fingDataErrorCount     = 0
					self.doubleIPnumbers        = {}
				else:
					self.fingIPNumbers          = []
					self.fingStatus             = []
					self.fingDate               = []
					self.fingDeviceInfo         = []
					self.fingMACNumbers         = []
					self.fingVendor             = []
					self.fingDataErrorCount     = 0
					self.doubleIPnumbers        = {}
				self.fingNumberOfdevices    = len(fingData)
				#self.indiLOG.log(20, "getfingData fingData {}".format(fingData))

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
						self.allDeviceInfo[theMAC]["hardwareVendor"] = self.fingVendor[kk]
						self.allDeviceInfo[theMAC]["deviceInfo"] = self.fingDeviceInfo[kk]

						self.allDeviceInfo[theMAC]["timeOfLastChange"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
							
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
			if len(theTest) < 5:  # variable exists, but empty 
				return 0
			theValue = theTest.split(";")
			if self.isValidMAC(theValue[0].strip()):
				self.getIndigoIpVariablesIntoData()
				return 0  ## version 2 nothing to do
		except Exception as e:
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
					self.indiLOG.log(30, "getting data from indigo: bad variable ipDevice" + ii00 +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				theValue = theTest.split(";")
				macNO = theValue[1].strip()
				if not self.isValidMAC(macNO):
					self.quitNOW = "Indigo variable error 3"
					self.indiLOG.log(30, "getting data from indigo: bad variable ipDevice" + ii00  +"\n  does not have a valid MAC number:" + theValue[0].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				ipNO =theValue[2].strip()
				if not self.isValidIP(ipNO):
					self.quitNOW = "Indigo variable error 4"
					self.indiLOG.log(30, "getting data from indigo: bad variable ipDevice" + ii00 +"\n  does not have a valid  IP number:" + theValue[1].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				nick  = self.padName("")
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
		self.getIndigoIpVariablesIntoData()
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
					if self.indigoCommand == "none":
						skip = 1
						self.quitNOW = "Indigo variable error 6"
						self.indiLOG.log(30, "getting data from indigo: bad variable ipDevice{};  deleting and letting the program recreate ".format(ii00) )
						indigo.variable.delete("ipDevice"+ii00)
					continue
				theValue = theTest.split(";")
				if len(theValue) == 10:
					theValue[8] = copy.copy(theValue[9])
					del theValue[9]

				while len(theValue) < 9:
					theValue.append("")

				skip = "no"
				self.indigoNumberOfdevices += 1
				self.indigoDevicesValues.append(theTest)
				self.indigoDevicesNumbers.append(ii00)
				theMAC =theValue[0].strip()
				if not self.isValidMAC(theValue[0].strip()):
					if self.indigoCommand == "none":
						skip = 1
						self.quitNOW = "Indigo variable error 7"
						self.indiLOG.log(30, "getting data from indigo: bad variable ipDevice{} does not have a valid MAC number>>{}<<  deleting and letting the program recreate it ".format(ii00, theValue[0].strip()) )
						indigo.variable.delete("ipDevice"+ii00)
					continue



				if not self.isValidIP(theValue[1].strip()):
					if self.indigoCommand == "none":
						skip = 1
						self.quitNOW = "Indigo variable error 8"
						self.indiLOG.log(30, "getting data from indigo: bad variable ipDevice{} does not have a valid  IP number>>{}<<\  deleting and letting the program recreate  it ".format(ii00, theValue[1].strip()) )
						indigo.variable.delete("ipDevice"+ii00)
					continue

				self.indigoIpVariableData[theMAC] = copy.deepcopy(emptyindigoIpVariableData)
				devV = self.indigoIpVariableData[theMAC]
				devV["ipNumber"]			= theValue[1].strip()
				devV["timeOfLastChange"]	= theValue[2].strip()
				devV["status"]				= theValue[3].strip()
				try:
					devV["noOfChanges"]	= int(theValue[4].strip())
				except:
					devV["noOfChanges"]	= 0
				devV["deviceName"]			= theValue[5].strip()
				devV["hardwareVendor"]		= theValue[6].strip()
				devV["deviceInfo"]			= theValue[7].strip()

				try:
					devV["usePing"]			= theValue[8].strip()
				except:
					devV["usePing"]			= "noPing-0"
				
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
										self.updateIndigoIpDeviceFromDeviceData(theMAC, ["status"],justStatus= "down", calledFrom="doInbetweenPing1")
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
							self.updateIndigoIpDeviceFromDeviceData(theMAC, ["status"], justStatus= "down", calledFrom="doInbetweenPing2")
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
		return

########################################
	def checkTriggers(self):
		try:
	#		if self.decideMyLog("Events"): self.indiLOG.log(10, "<<<--- entering checkTriggers")
			for nEvent in self.EVENTS:
				timeNowNumberSecs = time.time()
				timeNowm2 = int(timeNowNumberSecs-.2) ## drop the 10th of seconds
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
				minHomeTime = 999999
				minAwayTime = 999999
				maxHomeTime = 0
				maxAwayTime = 0

				evnt["nHome"]  = 0		
				evnt["nAway"]  = 0		

				if True:
					for nDev in evnt["IPdeviceMACnumber"]:
						if evnt["IPdeviceMACnumber"][nDev] == "0": continue
						if evnt["IPdeviceMACnumber"][nDev] == "": continue
						AwayTime[nDev]			=  999999999123
						HomeTime[nDev]			=  999999999123
						AwayStat[nDev]			=  False
						HomeStat[nDev]			=  False


				for nDev in evnt["IPdeviceMACnumber"]:
					AwayTime[nDev] 	= timeNowm2-float(evnt["secondsOfLastOFF"][nDev])
					minAwayTime 	= min(minAwayTime,AwayTime[nDev])  #################### need to check
					maxAwayTime 	= max(maxAwayTime,AwayTime[nDev])

					HomeTime[nDev] 	= timeNowm2-float(evnt["secondsOfLastON"][nDev])
					minHomeTime 	= min(minHomeTime,HomeTime[nDev])
					maxHomeTime 	= max(maxHomeTime,HomeTime[nDev])

				for nDev in evnt["IPdeviceMACnumber"]:
					status = "0"
					if evnt["IPdeviceMACnumber"][nDev] == "0": continue
					if evnt["IPdeviceMACnumber"][nDev] == "": continue
					iDev = int(nDev)
					theMAC = evnt["IPdeviceMACnumber"][nDev]
					##self.indiLOG.log(10, " in trigger idev"+ nDev+"  "+ theMAC)
					if len(theMAC) < 16:
						if self.decideMyLog("Events"): self.indiLOG.log(10, "theMAC=0")
						continue
					if not theMAC in self.allDeviceInfo:
						if self.decideMyLog("Ping"): self.indiLOG.log(10, "mac number {}\n   not present in data, deleting EVENT/device source for trigger".format(theMAC) )
						evnt["IPdeviceMACnumber"][nDev] = "0"
						break
					devI = self.allDeviceInfo[theMAC]
					status		= devI["status"]

					if status == "up":	HomeStat[nDev] = True
					else:				AwayStat[nDev] = True

					AwayTime[nDev] 	= timeNowm2-float(evnt["secondsOfLastOFF"][nDev])
					minAwayTime 	= min(minAwayTime,AwayTime[nDev])
					maxAwayTime 	= max(maxAwayTime,AwayTime[nDev])

					HomeTime[nDev] 	= timeNowm2-float(evnt["secondsOfLastON"][nDev])
					minHomeTime 	= min(minHomeTime,HomeTime[nDev])
					maxHomeTime 	= max(maxHomeTime,HomeTime[nDev])


	## all info set, now set final outcome
				oneAway				= 0
				allAway				= 0
				allHome				= 0
				oneHome				= 0
				oneHomeTrigger		= 0
				oneAwayTrigger		= 0
				allHomeTrigger		= 0
				allAwayTrigger		= 0

				out = "checkTrigger\n"
				if self.decideMyLog("Events"): out+="EVENT# {}".format(nEvent).ljust(2)+"  Dev# HomeStat ".ljust(16)                         +"HomeTime".ljust(12)          +"AwayStat".ljust(12)         +"AwayTime".ljust(12)            +" oneHome"            +" allHome"             +"  oneAway"           +" allAWay"+"  Hometime"+"\n"
				for nDev in evnt["IPdeviceMACnumber"]:
					if evnt["IPdeviceMACnumber"][nDev] == "0": continue
					if evnt["IPdeviceMACnumber"][nDev] ==  "": continue
					if AwayStat[nDev] and evnt["currentStatusAway"][nDev] == "0" and (minAwayTime < 30 and False):  ### need to fix 
						if self.decideMyLog("Events"): out += "          "+  "nDev{}".format(nDev)+" AwayStat[nDev]{}".format(AwayStat[nDev])+" evnt[currentStatusAway][nDev]" + "{}".format(evnt["currentStatusAway"][nDev])+" minAwayTime" + "{}".format(minAwayTime)+"\n"
						self.redoAWAY= 10  # increase frequency of up/down test to 1 per second for 10 seconds
	#### away status
					if evnt["currentStatusAway"][nDev] == "0":
						if AwayStat[nDev]:
							if float(evnt["minimumTimeAway"]) > 0.:
								evnt["currentStatusAway"][nDev]	= "startedTimer"
								allAway = -1 
							else:
								evnt["currentStatusAway"][nDev]	= "AWAY"
								oneAway = 1
								if allAway == 0: allAway = 1
								self.redoAWAY = 0
							evnt["secondsOfLastOFF"][nDev]= timeNowm2
							evnt["timeOfLastOFF"][nDev]= timeNowHMS
						else:
							allAway = -1

					elif evnt["currentStatusAway"][nDev] == "startedTimer":
							if AwayStat[nDev]:
								if AwayTime[nDev] >= float(evnt["minimumTimeAway"]):
									evnt["currentStatusAway"][nDev] = "AWAY"
									if allAway == 0: allAway = 1
								else:    
									allAway = -1
							else:    
								evnt["currentStatusAway"][nDev] = "0"
								allAway = -1
					 
					if evnt["currentStatusAway"][nDev] == "AWAY":
						if AwayStat[nDev]:
							oneAway = 1
							if AwayTime[nDev] >= float(evnt["minimumTimeAway"]):
								oneAwayTrigger = True
							if minAwayTime >= float(evnt["minimumTimeAway"]):
								allAwayTrigger = True
						else:
							allAway = -1
							evnt["currentStatusAway"][nDev]	= "0"
							evnt["secondsOfLastOFF"][nDev]= timeNowm2
					if evnt["currentStatusAway"][nDev] == "AWAY":
						evnt["nAway"] += 1

	#### home status
					if evnt["currentStatusHome"][nDev] == "0": # was not home
						if HomeStat[nDev]:
							evnt["currentStatusHome"][nDev]	= "HOME"
							evnt["secondsOfLastON"][nDev]= timeNowm2
							evnt["timeOfLastON"][nDev]= timeNowHMS
							oneHome = 1
							oneHomeTrigger = 1
							allHomeTrigger = 1
							if allHome == 0: allHome = 1
						else:
							allHome = -1
					else:  # it is or was  home
						if HomeStat[nDev]: # still home: restart timer
							evnt["timeOfLastON"][nDev]= timeNowHMS
							evnt["secondsOfLastON"][nDev]= timeNowm2
							evnt["currentStatusHome"][nDev]	= "HOME"
							if allHome == 0: allHome = 1
							oneHome = 1
						else:
							evnt["currentStatusHome"][nDev]	= "0"
							allHome = -1
					if evnt["currentStatusHome"][nDev]	== "HOME":
						evnt["nHome"] += 1
					#if self.decideMyLog("Events"): out+="EVENT# {}".format(nEvent).ljust(2)+"  {}".format(nDev).rjust(3)+"   " +"{}".format(HomeStat[nDev]).ljust(12)+ "{}".format(HomeTime[nDev]).ljust(12)+ "{}".format(AwayStat[nDev]).ljust(12)+ "{}".format(AwayTime[nDev]).ljust(12)+ "{}".format(oneHome).ljust(8)+ "{}".format(allHome).ljust(8)+ "{}".format(oneAway).ljust(8)+ "{}".format(allAway).ljust(8)+"{}".format(HomeTime[nDev]) +"\n"

				#if self.decideMyLog("Events"): out += "EVENT# {}".format(nEvent).ljust(2)+"  "+"oneHome:" + evnt["oneHome"]+"; allHome:" + evnt["allHome"]+"; oneAway:" + evnt["oneAway"]+"; allAway:" + evnt["allAway"]+" minHomeTime:{}, minimumTimeHome:{} \n".format(minHomeTime, evnt["minimumTimeHome"])
				if time.time() - self.timeOfStart > 100:
					if oneHome > 0:
						if evnt["oneHome"] != "1" :
							evnt["oneHome"] = "1"
							if oneHomeTrigger:
								if timeNowm2 - evnt["secsOfLastOneHomeTrigger"]  >= float(evnt["minimumTimeHome"]):
									evnt["secsOfLastOneHomeTrigger"] = timeNowm2
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
					if allHome > 0:
						if evnt["allHome"] != "1":
							if allHomeTrigger:
								evnt["allHome"] = "1"
								if timeNowm2 - evnt["secsOfLastAllHomeTrigger"]  >= float(evnt["minimumTimeHome"]):
									evnt["secsOfLastAllHomeTrigger"] = timeNowm2
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



					if allAway >0:
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

					if oneAway > 0:
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



				#if self.decideMyLog("Events"): self.indiLOG.log(10, out)
				if self.decideMyLog("Events"): self.printEvents(printEvents=nEvent)

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
				except:  
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
						self.updateIndigoIpDeviceFromDeviceData(theMAC,["status", "timeOfLastChange"], calledFrom="compareToFingIfExpired")
						self.updateIndigoIpVariableFromDeviceData(theMAC)
				
				
		except Exception:
			self.logger.error("", exc_info=True)

		return 0
	
	
	
########################################
	def compareToIndigoDeviceData(self, lastUpdateSource="0"):
		try:
			indigoIndexFound =[]
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
				else:
					theAction = "new"
				
				updateStates = []

				
				if theAction == "exist" :
					devI= self.allDeviceInfo[theMAC]
					
					useFing = True
					theStatus = self.fingStatus[kk]
					if self.inbetweenPingType!= "0" and theMAC in self.inbetweenPing:
						if  self.inbetweenPing[theMAC] == "down": theStatus = "down"

					#if theMAC =="1C:36:BB:97:C0:85": 
					#    indigo.server.log("exists "+ theStatus+"  {}".format(devI["lastFingUp"]))

					if theStatus != "up":
						if theMAC in self.allDeviceInfo and "useWakeOnLanSecs" in self.allDeviceInfo[theMAC] and  self.allDeviceInfo[theMAC]["useWakeOnLanSecs"] > 0:
							self.sendWakewOnLanAndPing(theMAC, nBC= 1,waitForPing=10, countPings=1, waitBeforePing = 0., waitAfterPing = 0.0, calledFrom="compareToIndigoDeviceData1")

					if time.time() - self.startTime < 150:  devI["lastFingUp"] = time.time()
					if theStatus == "up":
						devI["lastFingUp"] = time.time()
					else:
						if devI["expirationTime"] != 0 and (time.time() - devI["lastFingUp"] < devI["expirationTime"]): 
							theStatus = "up"

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
						if  self.decideMyLog("Logic"): self.indiLOG.log(10, "compareToIndigoDeviceData update  MAC#:{}, changes:{}".format(theMAC, updateStates) )
						self.updateIndigoIpDeviceFromDeviceData(theMAC, updateStates, calledFrom="compareToIndigoDeviceData2")
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
					self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
					self.allDeviceInfo[theMAC]["timeOfLastChange"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
						
					devI = self.allDeviceInfo[theMAC]
					devI["ipNumber"] = self.fingIPNumbers[kk]
					dd = self.fingDate[kk]
					if len(dd) < 5 : dd = "{}".format(dateTimeNow)
					
					devI["timeOfLastChange"]	= dd
					devI["status"]				= "up"
					devI["noOfChanges"]			= 1
					if len(self.fingVendor[kk]) > 3:
						devI["hardwareVendor"]	= self.fingVendor[kk]
					else:
						devI["hardwareVendor"]	= self.getVendorName(theMAC)

					devI["deviceInfo"]			= self.fingDeviceInfo[kk]
					devI["usePing"]				= "usePingUP"
					devI["useWakeOnLanSecs"]	= 0
					devI["suppressChangeMSG"]	= "show"
					#if theMAC =="1C:36:BB:97:C0:85": 
					#    indigo.server.log("new "+ theStatus+"  {}".format(devI["lastFingUp"]))
					devI["lastFingUp"]	        = time.time()

					self.updateIndigoIpDeviceFromDeviceData(theMAC,["all"], calledFrom="compareToIndigoDeviceData2")

					self.updateIndigoIpVariableFromDeviceData(theMAC)


			try:
				if self.indigoStoredNoOfDevices != "{}".format(self.indigoNumberOfdevices):
					indigo.variable.updateValue("ipDevsNoOfDevices", "{}".format(self.indigoNumberOfdevices))
			except:
				indigo.variable.create("ipDevsNoOfDevices", "{}".format(indigoNumberOfdevices))

		except Exception:
			self.logger.error("", exc_info=True)


		return 0



########################################
	def getVendorName(self, MAC):
		#self.indiLOG.log(10, "getVendorName  check :{} - {}".format(self.enableMACtoVENDORlookup, self.waitForMAC2vendor))
		if self.enableMACtoVENDORlookup == "0" : return ""
		if self.waitForMAC2vendor:
			self.waitForMAC2vendor = not self.M2V.makeFinalTable(quiet=False)

		if not self.waitForMAC2vendor:
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
						self.indiLOG.log(10, "switching off SQL logging for variable :{}: sp:{}".format(var.name.encode("utf8"), sp) )
					

			if len(outOffV) > 0: 
				self.indiLOG.log(10, " \n")
				self.indiLOG.log(10, "switching off SQL logging for variables\n :{}".format(outOffV.encode("utf8")) )
				self.indiLOG.log(10, "switching off SQL logging for variables END\n")
			if len(outOffD) > 0: 
				self.indiLOG.log(10, " \n")
				self.indiLOG.log(10, "switching off SQL logging for devices/state[lastfingup]\n :{}".format(outOffD.encode("utf8")) )
				self.indiLOG.log(10, "switching off SQL logging for devices END\n")
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

				if self.indigoCommand != "none" and self.indigoCommand != "":
					if self.indigoCommand == "loadDevices": self.doLoadDevices()
					if self.indigoCommand == "sort": self.doSortData()
					if self.indigoCommand == "reloadVendorInfo": self.updateVendors()
					if self.indigoCommand == "details": self.doDetails()
					if self.indigoCommand == "ResetEVENTS": 
						self.resetEvents()
					if self.indigoCommand == "ResetDEVICES":
						self.resetDevices()
						break
					if self.indigoCommand == "PrintEVENTS":   self.printEvents()
				self.indigoCommand = "none"

				checkTime=datetime.datetime.now().strftime("%H:%M:%S").split(":")
				checkTime[0]=int(checkTime[0]) #H
				checkTime[1]=int(checkTime[1]) #M
				checkTime[2]=int(checkTime[2]) #S

				# every minute
				if lastmin !=checkTime[1] and checkTime[2]>10 :
					self.checkcProfile()
					lastmin =checkTime[1]
					self.checkIfDevicesChanged() # check for changed device parameters once a minute .
					self.checkDEVICES() # complete sync every minutes
					self.setupEventVariables()

				# every 5 minutes
				if lastmin5 !=checkTime[1] and checkTime[1]%5 ==0 and checkTime[1] >0 and checkTime[2]>20 :
					lastmin5 =checkTime[1]
					self.updateAllIndigoIpVariableFromDeviceData() # copy any new / changed devices to variables
					self.setupEventVariables()
					
				# at 29 minutes
				if lastmin29 !=checkTime[1] and checkTime[1]%29 ==0 and checkTime[1] >0 and checkTime[2]>25 :
					lastmin29 =checkTime[1]
					self.cleanUpEvents()
					self.IDretList=[]
					self.updateVendors()

			
				# at 53 minutes
				if lastmin53 !=checkTime[1] and checkTime[1]%53 ==0 and checkTime[1] >0 and checkTime[2]>35 :
					lastmin53 =checkTime[1]
					self.doInbetweenPing(force=True)
					self.totalLoopCounter= 500
					
				# check for reload of plugin at 0,1,2 am 
				if self.enableReLoadPluginHour in ["0","1","2"]:
					if checkTime[0] == int(self.enableReLoadPluginHour)  and rebootMinute == checkTime[1] and self.totalLoopCounter > 200:
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
			indigo.server.savePluginPrefs() 
			try:
				quitNowX = self.quitNOW
			except Exception as e:
				quitNowX = "please setup config"
				self.logger.error("-->  exception StopThread triggered ... stopped,  quitNOW was: {}".format(quitNowX), exc_info=True)
			self.quitNOW = "no"
			############ if there are PING jobs left  kill them
		return

##############################################
	def checkDEVICES(self):
	#		if self.decideMyLog("Logic"): self.indiLOG.log(10, "checking devices")
		try:
			for theMAC in self.allDeviceInfo:
				self.allDeviceInfo[theMAC]["devExists"] = 0

			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				devID = "{}".format(dev.id)
				theStates = dev.states.keys()
	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "device testing: "+dev.name)
	#			if self.decideMyLog("Logic"): self.indiLOG.log(10, "device states: MAC-{}".format(theStates))
				
				if "MACNumber" in theStates:
					anyUpdate = False
					theMAC = dev.states["MACNumber"]
					if theMAC == "": continue
					if theMAC not in self.allDeviceInfo: continue
					if theMAC in self.ignoredMAC: continue
					devI=self.allDeviceInfo[theMAC]
					devI["deviceId"]	=dev.id
					if dev.name != devI["deviceName"]:
						devI["deviceName"]	=dev.name
						
					if dev.states["ipNumber"] != devI["ipNumber"]:
						self.addToStatesUpdateList("{}".format(dev.id),"ipNumber",			devI["ipNumber"])
						anyUpdate=True
					if dev.states["status"] != devI["status"]:
						self.addToStatesUpdateList("{}".format(dev.id),"status",			devI["status"])
						if self.decideMyLog("Logic"): self.indiLOG.log(10, "checkDEVICES  dev:{}   new status{}".format(dev.name, devI["status"]))
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

					if devI["timeOfLastChange"] == "0": devI["timeOfLastChange"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


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
												self.indiLOG.log(10, "IPNumber changed,  old: {}; new: {} for device MAC#: {} to switch off changed message: edit this device and select no msg".format(props["address"], self.formatiPforAddress(devI["ipNumber"]), theMAC) )
											else:
												self.indiLOG.log(10, "Multiple IPNumbers for device MAC#: "+theMAC+" -- {}  to switch off changed message: edit this device and select no msg".format(self.doubleIPnumbers[theMAC]))
										else:
												self.indiLOG.log(10, "IPNumber changed,  old: {}; new: {} for device MAC#: {} to switch off changed message: edit this device and select no msg".format(props["address"], self.formatiPforAddress(devI["ipNumber"]), theMAC))
								indigo.variable.updateValue( "ipDevsOldNewIPNumber", dev.name.strip(" ")+"/"+theMAC.strip(" ")+"/"+props["address"].strip(" ")+"/"+self.formatiPforAddress(devI["ipNumber"]).strip(" ") )

							props["address"]=self.formatiPforAddress(devI["ipNumber"])
							dev.replacePluginPropsOnServer(props)
					except:
						if self.decideMyLog("Ping"): self.indiLOG.log(10, "props check did not work")
					devI["devExists"] = 1

			for theMAC in self.allDeviceInfo:
				if theMAC == "": continue
				devI = self.allDeviceInfo[theMAC]
				if devI["devExists"] == 0 and self.acceptNewDevices and theMAC not in self.ignoredMAC:
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " creating device {}".format(devI))
					theName = "FING_"+theMAC
					self.createDev(theName, theMAC)
					self.updateIndigoIpVariableFromDeviceData(theMAC)


			# resync indigoIpVariableData with actual variables 
			for theMAC in self.indigoIpVariableData:
				try:
					devV = self.indigoIpVariableData[theMAC]
					test = indigo.variables["ipDevice{}".format(devV["ipDevice"])]
				except:
					self.updateIndigoIpVariableFromDeviceData(theMAC)

			#self.indiLOG.log(20, "checkDEVICES testing variables ")
			nn = 0
			for ii in range(1,indigoMaxDevices):
				ii00 = self.int2hexFor2Digit(ii)
				skip = 0
				try:
					theTest = indigo.variables["ipDevice"+ii00].value
					theMAC = theTest.split(";")[0].strip()
					#self.indiLOG.log(20, "testing variable  ipDevice{}, mac:{} if in indigoIpVariableData".format(ii00, theMAC))
					if theMAC not in self.indigoIpVariableData:
						self.indiLOG.log(20, "removing variable  ipDevice{}, mac:{} does not exist as device".format(ii00, theMAC))
						indigo.variable.delete("ipDevice"+ii00)
					else:
						nn+=1
				except Exception:
					self.indigoEmpty.append(ii00)
					self.indigoIndexEmpty += 1
					continue
			try:
				indigo.variable.updateValue("ipDevsNoOfDevices"," {}".format(nn))
			except:
				indigo.variable.create("ipDevsNoOfDevices"," {}".format(nn), self.indigoVariablesFolderID)
			


						
			self.executeUpdateStatesList()        
		except Exception:
			self.logger.error("", exc_info=True)
			
		return

	def createDev(self, theName, theMAC):
		try:
			devI = self.allDeviceInfo[theMAC]
			vInfo = self.getVendorName(theMAC)
			if len(vInfo)> 3: 
				devI["hardwareVendor"] = vInfo
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
			self.addToStatesUpdateList("{}".format(dev.id),"MACNumber",			theMAC)
			self.addToStatesUpdateList("{}".format(dev.id),"ipNumber",			devI["ipNumber"])
			self.addToStatesUpdateList("{}".format(dev.id),"timeOfLastChange",	devI["timeOfLastChange"])
			self.addToStatesUpdateList("{}".format(dev.id),"status",			devI["status"])
			self.addToStatesUpdateList("{}".format(dev.id),"noOfChanges",		int(devI["noOfChanges"]) )
			self.addToStatesUpdateList("{}".format(dev.id),"hardwareVendor",	devI["hardwareVendor"])
			self.addToStatesUpdateList("{}".format(dev.id),"deviceInfo",		devI["deviceInfo"])
			self.addToStatesUpdateList("{}".format(dev.id),"suppressChangeMSG", devI["suppressChangeMSG"])
			self.addToStatesUpdateList("{}".format(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
			self.addToStatesUpdateList("{}".format(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )

			usePing = devI["usePing"]
			if  "{}".format(devI["useWakeOnLanSecs"]) !="0":
				usePing +="-WOL:{}".format(devI["useWakeOnLanSecs"])
			if "usePing-WOL" in dev.states: self.addToStatesUpdateList("{}".format(dev.id),"usePing-WOL", usePing)
			pad = self.padStatusForDevListing(devI["status"])
			self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",	devI["status"].ljust(pad)+devI["timeOfLastChange"])
			devI["deviceId"]	= dev.id
			devI["deviceName"]	= dev.name
			devI["devExists"]	= 1
			self.executeUpdateStatesList()
			self.updateIndigoIpVariableFromDeviceData(theMAC)

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
					devI["deviceId"]	= dev.id
					if dev.name != devI["deviceName"]:
						update = 1
						devI["deviceName"]	= dev.name
					if dev.states["hardwareVendor"] != devI["hardwareVendor"]:
						devI["hardwareVendor"]		= dev.states["hardwareVendor"]
						update = 2
					if dev.states["deviceInfo"] != devI["deviceInfo"]:
						devI["deviceInfo"]		= dev.states["deviceInfo"]
				if update>0:
	#				if self.decideMyLog("Logic"): self.indiLOG.log(10, " updating MAC: "+theMAC)
					self.updateIndigoIpVariableFromDeviceData(theMAC)
		except Exception:
			self.logger.error("", exc_info=True)
		return

##############################################
	def updateAllIndigoIpDeviceFromDeviceData(self, statesToUdate=["all"], calledFrom="updateAllIndigoIpDeviceFromDeviceData"):
		devcopy = copy.deepcopy(self.allDeviceInfo)
		for theMAC in devcopy:
			self.updateIndigoIpDeviceFromDeviceData(theMAC,statesToUdate, calledFrom=calledFrom)
		return 
##############################################
	def updateIndigoIpDeviceFromDeviceData(self, theMAC, statesToUpdate, justStatus="", calledFrom=""):
		if not self.isValidMAC(theMAC): 
			self.indiLOG.log(30, "updateIndigoIpDeviceFromDeviceData: MAC Number>>{}<< not valid, calledFrom:{}".format(theMAC, calledFrom))
			return
		if theMAC in self.ignoredMAC: return

		try:
			try:
				devI = self.allDeviceInfo[theMAC]
				if self.decideMyLog("Logic"): self.indiLOG.log(10, "updating dev and states: {}/{}, newStatus:{}".format(theMAC, statesToUpdate, devI["status"]))
			except:
				self.indiLOG.log(40, "updateIndigoIpDeviceFromDeviceData: MAC Number: {} information does not exist in allDeviceInfo".format(theMAC))
				return

			dev = ""
			devId = devI["deviceId"]
			try:
				dev = indigo.devices[devId]
			except:
				dev = ""
				self.indiLOG.log(20, "updateIndigoIpDeviceFromDeviceData: devId {}  does not exist in indigo devices, recreate for mac#:{}, calledFrom:{}".format(devId, theMAC, calledFrom))
			if justStatus != "": # update only status for quick turn around
				if dev != "":
					#dev.updateStateOnServer("status",justStatus)
					self.addToStatesUpdateList("{}".format(dev.id), "status", justStatus)
					pad = self.padStatusForDevListing(justStatus)
					#dev.updateStateOnServer("statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", localtime()))
					self.addToStatesUpdateList("{}".format(dev.id),"statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
					if "lastFingUp" in dev.states:
						if dev.states["lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])):
							self.addToStatesUpdateList("{}".format(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI["lastFingUp"])))
					self.executeUpdateStatesList()
					self.allDeviceInfo[theMAC]["status"] = justStatus
				return

			if dev == "":
				# create new device
				theName = "MAC-{}".format(theMAC)
				if self.acceptNewDevices:
					self.createDev(theName, theMAC)
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

				if statesToUpdate[0]=="all" or "status" in statesToUpdate or "ipNumber" in statesToUpdate:
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

				devI["deviceId"]	= dev.id
				devI["deviceName"]	= dev.name
				devI["devExists"]	= 1

				self.executeUpdateStatesList()

		except Exception:
			self.logger.error("calledfrom:{}".format(calledFrom), exc_info=True)
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


			for theMAC in theList:
				try:
					devI = self.allDeviceInfo[theMAC]
					devID = devI["deviceId"]
					indigo.device.delete(devID)
				except:
					pass
				
				try:
					devV = self.indigoIpVariableData[theMAC]
					indigo.variable.delete("ipDevice"+devV["ipDevice"])
				except:
					pass
				try:
					theName = devI["deviceName"]
					del self.allDeviceInfo[theMAC]
				except:
					if self.decideMyLog("Logic"): self.indiLOG.log(10, "deleteIndigoIpDevicesData: name/MAC "+ theName+"/"+theMAC+" information does not exist in allDeviceInfo")

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
						self.allDeviceInfo[theMAC]["timeOfLastChange"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
						update = 5
					devI=self.allDeviceInfo[theMAC]
					props = dev.pluginProps
					if dev.name != devI["deviceName"]:
						update = 1
						devI["deviceName"]		= dev.name
					if dev.states["hardwareVendor"] != devI["hardwareVendor"]:
						devI["hardwareVendor"]		= dev.states["hardwareVendor"]
						update = 2
					if dev.states["deviceInfo"] != devI["deviceInfo"]:
						devI["deviceInfo"]		= dev.states["deviceInfo"]
						update = 3
					devI["ipNumber"]			= dev.states["ipNumber"]
					devI["timeOfLastChange"]	= dev.states["timeOfLastChange"]
					devI["status"]				= dev.states["status"]
					devI["noOfChanges"]			= int(dev.states["noOfChanges"])
					devI["hardwareVendor"]		= dev.states["hardwareVendor"]
					devI["deviceInfo"]			= dev.states["deviceInfo"]
					try:    devI["lastFingUp"]	= devI["lastFingUp"]	= time.mktime( datetime.datetime.strptime(dev.states["lastFingUp"],"%Y-%m-%d %H:%M:%S").timetuple()  )
					except: devI["lastFingUp"]	= time.time()
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
	def updateIndigoIpVariableFromDeviceData(self, theMAC):
		try:
			if theMAC in self.ignoredMAC: return 
			if theMAC not in self.allDeviceInfo: return 
			if theMAC in self.indigoIpVariableData:
				devV = self.indigoIpVariableData[theMAC]
			else:
				self.indigoIpVariableData[theMAC] = copy.deepcopy(emptyindigoIpVariableData)
				devV = self.indigoIpVariableData[theMAC]
				#self.indiLOG.log(30, "updateIndigoIpVariableFromDeviceData devV[theMAC]:{},  does not exist, indigoEmpty0:{}".format(theMAC, self.indigoEmpty[0]))
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


			devI = self.allDeviceInfo[theMAC]
			updstr  =self.padMAC(theMAC)
			updstr += ";"+self.padIP(devI["ipNumber"])
			updstr += ";"+self.padDateTime(devI["timeOfLastChange"])
			updstr += ";"+devI["status"]
			updstr += ";"+self.padStatus(devI["status"])+self.padNoOfCh(devI["noOfChanges"])
			updstr += ";"+self.padName(devI["deviceName"])
			updstr += ";"+self.padVendor(devI["hardwareVendor"])
			updstr += ";"+self.padDeviceInfo(devI["deviceInfo"])
			updstr += ";"+(devI["usePing"]+"-{}".format(devI["useWakeOnLanSecs"])).rjust(13)
			theValue = updstr.split(";")

			devV["ipNumber"]			= theValue[1].strip()
			devV["timeOfLastChange"]	= theValue[2].strip()
			devV["status"]				= theValue[3].strip()
			try:
				devV["noOfChanges"]	= int(theValue[4].strip())
			except:
				devV["noOfChanges"]	= 0
			devV["name"]				= theValue[5].strip()
			devV["hardwareVendor"]		= theValue[6].strip()
			devV["deviceInfo"]			= theValue[7].strip()
			devV["usePing"]				= theValue[8].strip()


			try:
				curr = indigo.variables["ipDevice"+devV["ipDevice"]]
			except:
				#self.indiLOG.log(30, "updateIndigoIpVariableFromDeviceData updating ipDevice:{},  does not exist, (re)creating variable".format(devV["ipDevice"]))
				curr = ""
			
			if updstr != curr:
				try:
					indigo.variable.updateValue("ipDevice"+devV["ipDevice"], updstr)
				except:
					self.indiLOG.log(30, "new dev#:  newIPDevNumber:{}<<    devV[ipDevice]:{}<<".format(self.indigoEmpty[0], devV["ipDevice"]))
					indigo.variable.create("ipDevice"+devV["ipDevice"], updstr, self.indigoVariablesFolderID)
					try:
						indigo.variable.updateValue("ipDevsNewDeviceNo", "ipDevice{};{}".format(devV["ipDevice"], devI["deviceName"]))
					except:
						indigo.variable.create("ipDevsNewDeviceNo", "ipDevice{};{}".format(devV["ipDevice"], devI["deviceName"]), self.indigoVariablesFolderID)
					self.triggerEvent("NewDeviceOnNetwork")

					nn = 0
					for ii in range(1,indigoMaxDevices):
						ii00 = self.int2hexFor2Digit(ii)
						skip = 0
						try:
							theTest = indigo.variables["ipDevice"+ii00]
							nn+=1
						except Exception as exc:
							self.indigoEmpty.append(ii00)
							self.indigoIndexEmpty += 1
							continue
					try:
						indigo.variable.updateValue("ipDevsNoOfDevices"," {}".format(nn))
					except:
						indigo.variable.create("ipDevsNoOfDevices"," {}".format(nn), self.indigoVariablesFolderID)




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
					self.allDeviceInfo[theMAC]["timeOfLastChange"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				for xx in emptyAllDeviceInfo:
					if xx not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC] = copy.copy(emptyAllDeviceInfo[xx])
				devI = self.allDeviceInfo[theMAC]
				devI["ipNumber"]			= devV["ipNumber"].strip()
				devI["timeOfLastChange"]	= devV["timeOfLastChange"].strip()
				devI["status"]				= devV["status"].strip()
				try:
					devI["noOfChanges"]		= int(devV["noOfChanges"])
				except:
					devI["noOfChanges"]		= 0
				devI["hardwareVendor"]		= devV["hardwareVendor"].strip()
				devI["deviceInfo"]			= devV["deviceInfo"].strip()
				
				devI["usePing"]				= "usePing"
				devI["usePing"]		    	= ""
				devI["useWakeOnLanSecs"]	= 0
				if "usePing"  in devV:
					usePing = (devV["usePing"].strip()).split("-")
					devI["usePing"]			 = usePing[0]
					if len(usePing) == 2:
						devI["useWakeOnLanSecs"] = int(usePing[1])
						
				if "deviceId" not in devI: 		devI["deviceId"] = ""
				if "deviceName" not in devI:	devI["deviceName"] = ""

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
		if ddd is None:
			return " ".ljust(25)
		ddd= ddd.replace("\n","")
		theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
		blanks = " "
		for kk in range(1,theNumberOfBlanks):
			blanks += " "
		return "  "+ddd+blanks
	
########################################
	def padDeviceInfo(self,ddd):
		if ddd is None:
			return " ".ljust(25)
		ddd= ddd.replace("\n","")
		theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
		blanks = " "
		for kk in range(1,theNumberOfBlanks):
			blanks += " "
		return "  "+ddd+blanks
	
########################################
	def padIP(self,xxx):
		if xxx is None:
			return " ".ljust(25)
		ddd = len(xxx)
		pad = "   "
		if ddd == 11:	pad = "       "
		if ddd == 12:	pad = "     "
		return "   "+xxx+pad
	
########################################
	def padName(self, ddd):
		if ddd is None:
			return " ".ljust(32)
		theNumberOfBlanks =min(32,max(0,(17-len(ddd))*2))
		blanks = "   "
		for kk in range(1,theNumberOfBlanks):
			blanks += " "
		return "   "+ddd+blanks
	
########################################
	def padNoOfCh(self, xxx):
		if xxx is None:
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


####-------------------------------------------------------------------------####
	def isValidIP(self, ip0):
		ipx = ip0.split(".")
		if len(ipx) != 4:									return False	# not complete
		else:
			for ip in ipx:
				try:
					if int(ip) < 0 or  int(ip) > 255: 		return False	# out of range
				except:										return False	# not integer
		if True:											return True		# test passed 


####-------------------------------------------------------------------------####
	def isValidMAC(self, mac0):
		macx = mac0.split(":")
		if len(macx) != 6:									return False	# len(mac.split("D0:D2:B0:88:7B:76")):

		for xx in macx:
			if len(xx) !=2:									return False	# not 2 digits
			try: 	int(xx,16)
			except: 										return False	# is not a hex number

		if True:											return True		# test passed


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


