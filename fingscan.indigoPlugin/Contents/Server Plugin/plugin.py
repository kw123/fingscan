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

try:
	import json
except:
	import simplejson as json


import copy
import math
import shutil
import MACMAP.MAC2Vendor as M2Vclass
import cProfile
import pstats
import logging

try:
	unicode("x")
except:
	unicode = str


nOfDevicesInEvent   = 35
nOfIDevicesInEvent  = 5
piBeaconStart       = 22
unifiStart          = 30
milesMeters         = 1609.34
kmMeters	        = 1000.
nEvents		        = 12

iFindPluginMinText = u"com.corporatechameleon.iFind"

emptyAllDeviceInfo={
	u"ipNumber": u"0.0.0.0",
	u"timeOfLastChange": u"0",
	u"status": u"down",
	u"nickName": u"iphonexyz",
	u"noOfChanges": 0,
	u"hardwareVendor": u"",
	u"deviceInfo": u"",
	u"WiFi": u"",
	u"setWiFi": u"",
	u"WiFiSignal": u"",
	u"usePing": u"doNotUsePing",
	u"useWakeOnLanSecs":0,
	u"useWakeOnLanLast":0,
	u"suppressChangeMSG": u"show",
	u"deviceId": 0,
	u"deviceName": u"",
	u"fingLastUp": 0,
	u"expirationTime": 0,
	u"variableName": u""
	}
emptyindigoIpVariableData={
	u"ipNumber": u"0.0.0.0",
	u"timeOfLastChange": u"0",
	u"status": u"down",
	u"nickName": u"iphonexyz",
	u"noOfChanges": 0,
	u"hardwareVendor": u"",
	u"udeviceInfo": u"",
	u"variableName": u"",
	u"ipDevice": u"00",
	u"index": 0,
	u"WiFi": u"",
	u"WiFiSignal": u"0",
	u"usePing": u"",
	u"suppressChangeMSG": u"show"
	}
emptyEVENT ={#              -including Idevices option-------------                                                                                                                                            ----------  ------------pi beacons---------------------                   --------------  unifi ---------------------
	u"IPdeviceMACnumber"   :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"timeOfLastON"        :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"timeOfLastOFF"       :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"secondsOfLastON"     :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0, u"5": 0, u"6": 0, u"7": 0, u"8": 0, u"9": 0, u"10": 0, u"11": 0, u"12": 0, u"13": 0, u"14": 0, u"15": 0, u"16": 0, u"17": 0, u"18": 0, u"19": 0, u"20": 0, u"21": 0, u"22": 0, u"23": 0, u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"secondsOfLastOFF"    :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0, u"5": 0, u"6": 0, u"7": 0, u"8": 0, u"9": 0, u"10": 0, u"11": 0, u"12": 0, u"13": 0, u"14": 0, u"15": 0, u"16": 0, u"17": 0, u"18": 0, u"19": 0, u"20": 0, u"21": 0, u"22": 0, u"23": 0, u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"currentStatusHome"   :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"currentStatusAway"   :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"iDeviceUseForHome"   :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"iDeviceUseForAway"   :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"iDeviceAwayDistance" :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"iDeviceHomeDistance" :{u"1":u"0",u"2":u"0",u"3":u"0",u"4":u"0",u"5":u"0",u"6":u"0",u"7":u"0",u"8":u"0",u"9":u"0",u"10":u"0",u"11":u"0",u"12":u"0",u"13":u"0",u"14":u"0",u"15":u"0",u"16":u"0",u"17":u"0",u"18":u"0",u"19":u"0",u"20":u"0",u"21":u"0",u"22":u"0",u"23":u"0",u"24":u"0",u"25":u"0",u"26":u"0",u"27":u"0",u"28":u"0",u"29":u"0",u"30":u"0",u"31":u"0",u"32":u"0",u"33":u"0",u"34":u"0"},
	u"iDeviceName"         :{u"1":"" ,u"2":"" ,u"3":"" ,u"4":"" ,u"5":"" ,u"6":"" ,u"7":"" ,u"8":"" ,u"9":"" ,u"10":"" ,u"11":"" ,u"12":"" ,u"13":"" ,u"14":"" ,u"15":"" ,u"16":"" ,u"17":"" ,u"18":"" ,u"19":"" ,u"20":"" ,u"21":"" ,u"22":"" ,u"23":"" ,u"24":"" ,u"25":"" ,u"26":"" ,u"27":"" ,u"28":"" ,u"29":"" ,u"30":"" ,u"31":"" ,u"32":"" ,u"33":"" ,u"34":"" },
	u"iDistance"           :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"iSpeed"              :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"iUpdateSecs"         :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"iDistanceLast"       :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"iSpeedLast"          :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"iUpdateSecsLast"     :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"itimeNextUpdate"	   :{u"1": 0 ,u"2": 0 ,u"3": 0 ,u"4": 0,u"5": 0,u"6": 0,u"7": 0,u"8": 0,u"9": 0,u"10": 0,u"11": 0,u"12": 0,u"13": 0,u"14": 0,u"15": 0,u"16": 0,u"17": 0,u"18": 0,u"19": 0,u"20": 0,u"21": 0,u"22": 0,u"23": 0,u"24": 0 ,u"25": 0 ,u"26": 0 ,u"27": 0 ,u"28": 0 ,u"29": 0 ,u"30": 0 ,u"31": 0 ,u"32": 0 ,u"33": 0 ,u"34": 0 },
	u"iMaxSpeed"	       :{u"1":1.0,u"2":1.0,u"3":1.0,u"4":1.0,u"5":1.0,u"6":1.0,u"7":1.0,u"8":1.0,u"9":1.0,u"10":1.0,u"11":1.0,u"12":1.0,u"13":1.0,u"14":1.0,u"15":1.0,u"16":1.0,u"17":1.0,u"18":1.0,u"19":1.0,u"20":1.0,u"21":1.0,u"22":1.0,u"23":1.0,u"24":1.0,u"25":1.0,u"26":1.0,u"27":1.0,u"28":1.0,u"29":1.0,u"30":1.0,u"31":1.0,u"32":1.0,u"33":1.0,u"34":1.0},
	u"iFindMethod"         :{u"1":"" ,u"2":"" ,u"3":"" ,u"4":"" ,u"5":"" ,u"6":"" ,u"7":"" ,u"8":"" ,u"9":"" ,u"10":"" ,u"11":"" ,u"12":"" ,u"13":"" ,u"14":"" ,u"15":"" ,u"16":"" ,u"17":"" ,u"18":"" ,u"19":"" ,u"20":"" ,u"21":"" ,u"22":"" ,u"23":"" ,u"24":"" ,u"25":"" ,u"26":"" ,u"27":"" ,u"28":"" ,u"29":"" ,u"30":"" ,u"31":"" ,u"32":"" ,u"33":"" ,u"34":"" },
	u"nextTimeToCheck"	   :{u"1":1.0,u"2":1.0,u"3":1.0,u"4":1.0,u"5":1.0,u"6":1.0,u"7":1.0,u"8":1.0,u"9":1.0,u"10":1.0,u"11":1.0,u"12":1.0,u"13":1.0,u"14":1.0,u"15":1.0,u"16":1.0,u"17":1.0,u"18":1.0,u"19":1.0,u"20":1.0,u"21":1.0,u"22":1.0,u"23":1.0,u"24":1.0,u"25":1.0,u"26":1.0,u"27":1.0,u"28":1.0,u"29":1.0,u"30":1.0,u"31":1.0,u"32":1.0,u"33":1.0,u"34":1.0},
	u"oneAway": u"0",
	u"allAway": u"0",
	u"nAway": 0,
	u"allHome": u"0",
	u"oneHome": u"0",
	u"nHome": 0,
	u"distanceAwayLimit": 66666.,
	u"distanceHomeLimit": -1,
	u"minimumTimeAway": 300,
	u"minimumTimeHome": 0,
	u"enableDisable": u"0",
	u"dataFormat": u"3.0",
	u"maxLastTimeUpdatedDistanceMinutes": 900
	}
emptyWiFiMacList=[u"x",u"x","",u"x",u"x","","","","","","",""]
indigoMaxDevices = 1024
emptyWifiMacAv={u"sumSignal":{u"2GHz":0.,u"5GHz":0.},u"numberOfDevices":{u"2GHz":0.,u"5GHz":0.},u"curAvSignal":{u"2GHz":0.,u"5GHz":0.},u"curDev":{u"2GHz":0.,u"5GHz":0.},u"numberOfCycles":{u"2GHz":0.,u"5GHz":0.},u"noiseLevel":{u"2GHz": u"0",u"5GHz": u"0"}}
_debAreas = [u"Logic",u"Ping",u"Wifi",u"Events",u"piBeacon",u"Unifi",u"BC",u"Special",u"StartFi",u"all"]

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
		
		self.pluginShortName 			= u"fing"

 
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split(u"Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split(u"."))
		self.indigoVersion 				= float(major)+float(minor)/10.
		self.indigoRelease 				= release

		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= u"init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser(u"~")
		self.userIndigoDir				= self.MAChome + u"/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+u"Preferences/Plugins/"+self.pluginId+"/"
		self.indigoPluginDirOld			= self.userIndigoDir + self.pluginShortName+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +u"/plugin.log"


		formats=	{   logging.THREADDEBUG: u"%(asctime)s %(msg)s",
						logging.DEBUG:       u"%(asctime)s %(msg)s",
						logging.INFO:        u"%(asctime)s %(msg)s",
						logging.WARNING:     u"%(asctime)s %(msg)s",
						logging.ERROR:       u"%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:    u"%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: u"%Y-%m-%d %H:%M:%S",
						logging.DEBUG:       u"%Y-%m-%d %H:%M:%S",
						logging.INFO:        u"%Y-%m-%d %H:%M:%S",
						logging.WARNING:     u"%Y-%m-%d %H:%M:%S",
						logging.ERROR:       u"%Y-%m-%d %H:%M:%S",
						logging.CRITICAL:    u"%Y-%m-%d %H:%M:%S" }
		formatter = LevelFormatter(fmt=u"%(msg)s", datefmt=u"%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger(u"Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.INFO)

		self.indiLOG.log(20,u"=========================   initializing   ==============================================")

		indigo.server.log(  u"path To files:          ==================")
		indigo.server.log(  u"indigo                  {}".format(self.indigoRootPath))
		indigo.server.log(  u"installFolder           {}".format(self.indigoPath))
		indigo.server.log(  u"plugin.py               {}".format(self.pathToPlugin))
		indigo.server.log(  u"Plugin params           {}".format(self.indigoPreferencesPluginDir))

		self.indiLOG.log( 0, u"!!!!INFO ONLY!!!!  logger  enabled for   0             !!!!INFO ONLY!!!!")
		self.indiLOG.log( 5, u"!!!!INFO ONLY!!!!  logger  enabled for   THREADDEBUG   !!!!INFO ONLY!!!!")
		self.indiLOG.log(10, u"!!!!INFO ONLY!!!!  logger  enabled for   DEBUG         !!!!INFO ONLY!!!!")
		self.indiLOG.log(20, u"!!!!INFO ONLY!!!!  logger  enabled for   INFO          !!!!INFO ONLY!!!!")
		self.indiLOG.log(30, u"!!!!INFO ONLY!!!!  logger  enabled for   WARNING       !!!!INFO ONLY!!!!")
		self.indiLOG.log(40, u"!!!!INFO ONLY!!!!  logger  enabled for   ERROR         !!!!INFO ONLY!!!!")
		self.indiLOG.log(50, u"!!!!INFO ONLY!!!!  logger  enabled for   CRITICAL      !!!!INFO ONLY!!!!")

		indigo.server.log(  u"check                   {}  <<<<    for detailed logging".format(self.PluginLogFile))
		indigo.server.log(  u"Plugin short Name       {}".format(self.pluginShortName))
		indigo.server.log(  u"my PID                  {}".format(self.myPID))	 
		indigo.server.log(  u"set params for indigo V {}".format(self.indigoVersion))	 


####-----------------             ---------
	def __del__(self):
		indigo.PluginBase.__del__(self)


###########################     INIT    ## START ########################
	
####----------------- @ startup set global parameters, create directories etc ---------
	def startup(self):



		if self.pathToPlugin.find("/"+self.pluginName+".indigoPlugin/")==-1:
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"The pluginname is not correct, please reinstall or rename")
			self.errorLog(u"It should be   /Libray/....../Plugins/"+self.pluginName+".indigPlugin")
			p=max(0,self.pathToPlugin.find(u"/Contents/Server"))
			self.errorLog(u"It is: "+self.pathToPlugin[:p])
			self.errorLog(u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update")
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
			self.sleep(100000)
			self.quitNOW	= u"wrong plugin name"
			return
		self.quitNOW 		= u"INIT Startup not finished"
		self.pluginState	= u"init"
		try:

############ directory & file names ...
			self.fingDataFileName0			= u"fing.data"
			self.fingLogFileName0			= u"fing.log"
			self.fingErrorFileName0			= u"fingerror.log"
			self.fingServicesFileName0		= u"fingservices.json"
			self.fingServicesLOGFileName0	= u"fingservices.log"
			self.fingDataFileName			= self.indigoPreferencesPluginDir+self.fingDataFileName0	
			self.fingLogFileName			= self.indigoPreferencesPluginDir+self.fingLogFileName0 
			self.fingErrorFileName			= self.indigoPreferencesPluginDir+self.fingErrorFileName0 
			self.fingServicesFileName		= self.indigoPreferencesPluginDir+self.fingServicesFileName0 
			self.fingServicesLOGFileName	= self.indigoPreferencesPluginDir+self.fingServicesLOGFileName0
			self.fingServicesOutputFileName	= self.indigoPreferencesPluginDir+u"fingservices.txt"
			self.ignoredMACFile				= self.indigoPreferencesPluginDir+u"ignoredMAC"
			self.fingPasswordFileName		= self.indigoPreferencesPluginDir+u"parameter"
			self.fingSaveFileName			= self.indigoPreferencesPluginDir+u"fingsave.data"
			self.fingEXEpath				= u"/usr/local/bin/fing"

			if not os.path.exists(self.indigoPreferencesPluginDir):
				os.mkdir(self.indigoPreferencesPluginDir)
				os.mkdir(self.indigoPreferencesPluginDir+u"pings")
				os.mkdir(self.indigoPreferencesPluginDir+u"mac2Vendor")
				if os.path.exists(self.indigoPluginDirOld+u"fing.data"):
					indigo.server.log(u" moving "+ u"cp -R " + self.indigoPluginDirOld+u"* '" + self.indigoPreferencesPluginDir+u"'" )
					os.system(u"cp -R " + self.indigoPluginDirOld+u"* '" + self.indigoPreferencesPluginDir+u"'" )


			if os.path.isfile(u"/Library/Frameworks/Python.framework/Versions/Current/bin/python3"):
				self.pythonPath				= u"/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
			elif os.path.isfile(u"/usr/local/bin/python"):
				self.pythonPath				= u"/usr/local/bin/python"
			elif os.path.isfile(u"/usr/bin/python2.7"):
				self.pythonPath				= u"/usr/bin/python2.7"
			else:
				self.indiLOG.log(40,u"FATAL error:  none of python versions 2.7 3.x is installed  ==>  stopping INDIGOplotD")
				self.quitNOW = "none of python versions 2.7 3.x is installed "
				return
			self.indiLOG.log(30,u"using '" +self.pythonPath +"' for utily programs")



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
			self.myPID						= unicode(os.getpid())
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

			self.executionMode				= u"noInterruption"  ## interrupted by plugin/fingscan/configuration
			self.signalDelta				= {u"5":{u"2GHz":0,u"5GHz":0},u"2":{u"2GHz":0,u"5GHz":0},u"1":{u"2GHz":0,u"5GHz":0}}
			self.theNetwork					= u"0.0.0.0"

		except Exception as e:
			self.exceptionHandler(40, e)

		self.checkcProfile()


		return


####----------------- @ startup set global parameters, ---------
	def initConfig(self):

		try:

############ startup message
			self.debugLevel			= []
			for d in _debAreas:
				if self.pluginPrefs.get(u"debug"+d, False): self.debugLevel.append(d)
			self.myLog( text=u"myLogSet setting parameters --  debug settings :{} ".format(self.debugLevel) , destination="standard")
			 
			indigo.server.log(u"FINGSCAN--   initializing     will take ~ 2 minutes..")

############ set basic parameters to default before we use them

			try: self.enableBroadCastEvents  = self.pluginPrefs.get(u"enableBroadCastEvents","0")
			except: self.enableBroadCastEvents = "0"
			self.sendBroadCastEventsList    = []


########### try to setup folders, create directories if they do not exist
			try:
				ret = self.readPopen(u"mkdir '"+  self.indigoPreferencesPluginDir + u"'  > /dev/null 2>&1 &")
				ret = self.readPopen(u"mkdir '"+  self.indigoPreferencesPluginDir+u"pings'" + "  > /dev/null 2>&1 &")
			except:
				pass

			
############ if there are PING jobs left from last run, kill them
			self.killPing(u"all")
			
			
############ get plugin prefs parameters
			
			self.inbetweenPingType = self.pluginPrefs.get(u"inbetweenPingType",u"0")
			self.sleepTime = int(self.pluginPrefs.get(u"sleepTime", 1))
			self.newSleepTime = self.sleepTime


############ get & setup WiFi parameters
			self.badWiFiTrigger = {u"minSignalDrop":10,u"numberOfSecondsBad":0,u"minNumberOfDevicesBad":3,u"minNumberOfSecondsBad":200,u"minWiFiSignal":-90,u"trigger":0}
			try:
				self.badWiFiTrigger[u"minSignalDrop"]			= float(self.pluginPrefs.get(u"minSignalDrop"		 ,self.badWiFiTrigger[u"minSignalDrop"]))
				self.badWiFiTrigger[u"minNumberOfDevicesBad"]	= float(self.pluginPrefs.get(u"minNumberOfDevicesBad",self.badWiFiTrigger[u"minNumberOfDevicesBad"]))
				self.badWiFiTrigger[u"minNumberOfSecondsBad"]	= float(self.pluginPrefs.get(u"minNumberOfSecondsBad",self.badWiFiTrigger[u"minNumberOfSecondsBad"]))
				self.badWiFiTrigger[u"minWiFiSignal"]			= float(self.pluginPrefs.get(u"minWiFiSignal"		 ,self.badWiFiTrigger[u"minWiFiSignal"]))
			except:
				self.indiLOG.log(30,u"leaving WiFi parameters at default, not configured in 'fingscan/Configure...'")

			self.initIndigoParms()

			self.acceptNewDevices = self.pluginPrefs.get(u"acceptNewDevices",u"0") == u"1"
			self.getIgnoredMAC()

############ get password
			self.indiLOG.log(20,u"getting password")
			test = self.getPWD(u"fingscanpy")
			if test == u"0":  # no password stored in keychain, check config file
				self.yourPassword = self.pluginPrefs.get(u"password", u"yourPassword")

				if True:												self.passwordOK = u"1"  # a password has been entered before
				if self.yourPassword == u"yourPassword": 				self.passwordOK = u"0"  # nothing changed from the beginning
				if self.yourPassword == u"password is already stored":	self.passwordOK = u"2"  ## password was entered and was stored into keychain

				
				if self.passwordOK == u"1":
					self.storePWD(self.yourPassword,u"fingscanpy")
					self.pluginPrefs[u"password"] = u"password is already stored"  # set text to everything ok ...
					self.passwordOK = u"2"
			
				## wait for password

				if self.passwordOK == u"0":
					for ii in range(10):
						self.indiLOG.log(40,u"no password entered:  please do plugin/fingscan/configure and enter your password ")
						self.sleep(5)
						if self.passwordOK != u"1": break
				## password entered, check if it is NOW in keychain

				test = self.getPWD(u"fingscanpy")
				if test != u"0":	## password is in keychain
					self.pluginPrefs[u"password"] = u"password is already stored"  # set text to everything ok ...
					self.yourPassword = test
					self.passwordOK = u"2"
					self.quitNOW = u"no"

				else:  ## no password in keychain error exit, stop plugin
					self.passwordOK = u"0"
					self.pluginPrefs[u"password"] = u"yourPassword"  # set text enter password
					self.indiLOG.log(40,u"password error please enter password in configuration menue, otherwise FING can not be started ")
					self.sleep(20)
					self.quitNOW = u"wait noPassword"

			else:  # password is in keychain, done
				self.yourPassword = test
				self.pluginPrefs[u"password"] = u"password is already stored"  # set text to everything ok ...
				self.quitNOW = u"no"
				self.passwordOK = u"2"
			self.indiLOG.log(20,u"get password done;  checking if FING is installed ")

############ install FING executables, set rights ... 
			self.setupFingPgm()
	
############ get WIFI router info if available
			self.routerType	= self.pluginPrefs.get(u"routerType","0")
			self.routerPWD	= u""
			self.routerUID	= u""
			self.routerIPn	= u""
			if self.routerType != u"0":
				self.routerUID	= self.pluginPrefs.get(u"routerUID",u"0")
				self.routerIPn	= self.pluginPrefs.get(u"routerIPn",u"0")
				
				test = self.getPWD(u"fingrt")
				if test != u"0":
					self.routerPWD	= test
				else:
					self.routerType = u"0"
					self.routerPWD	= ""

				self.checkWIFIinfo()

############ kill old pending PING jobs
			self.killPing(u"all")

############ here we get stored setup etc
			self.refreshVariables()
			self.getIndigoIpVariablesIntoData()		# indigo variable data to  into self.indigoIpVariableData
			self.updateallDeviceInfofromVariable()	# self.indigoIpVariableData  to self.allDeviceInfo
			self.getIndigoIpDevicesIntoData()       # indigo dev data to self.allDeviceInfo
			self.checkDEVICES()
			self.checkIfDevicesChanged()
			self.updateAllIndigoIpVariableFromDeviceData()
			self.indiLOG.log(20,u"loaded indigo data")

############ get network info
			

			try:
				self.netwType   = u"{}".format(int(self.pluginPrefs.get(u"netwType",u"24")))
			except:
				self.netwType = u"24"
			if unicode(self.netwType) ==  u"8":
				self.netwType = u"24"
			
			self.theNetwork         = self.pluginPrefs.get(u"network",u"192.168.1.0")
			if not self.isValidIP(self.theNetwork):
				self.theNetwork ="192.168.1.0"

			try: 
				aa = self.theNetwork+u"/"+self.netwType
				self.netwInfo = self.IPCalculator(self.theNetwork, self.netwType)
			except Exception as e:
				self.exceptionHandler(40, e)
				self.netwInfo = {u'netWorkId': u'192.168.1.0', u'broadcast': u'192.168.1.255', u'netMask': u'255.255.255.0', u'maxHosts': 254, u'hostRange': u'192.168.1.1 - 192.168.1.254'}
			self.indiLOG.log(30,u"network info: {}, netwType:{}".format(self.netwInfo, self.netwType))
			self.broadcastIP = self.netwInfo[u"broadcast"]

			self.pluginPrefs[u"network"]  	= self.theNetwork
			self.pluginPrefs[u"netwType"] 	= self.netwType



############ for triggers:
			self.currentEventN = u"0"
			try:
				xxx = u""
				xxx = self.pluginPrefs[u"EVENTS"]
				self.EVENTS=json.loads(xxx)
			except:
				self.EVENTS = {}
				self.indiLOG.log(30,u"empty or bad read of EVENT from prefs file: len(data): {}; \ndata: {} .. {}".format(len(xxx), xxx[0:100],xxx[-100:]) )

			timeNow = time.time()
			self.checkTriggerInitialized =False
		  



############ check if FMID is enabled
			self.IDretList=[]
			self.iFindStuffPlugin = u"com.corporatechameleon.iFindplugBeta"
			self.checkIfiFindisEnabled()

############ en/ disable mac to vendor lookup
		
			self.enableMACtoVENDORlookup    = self.pluginPrefs.get(u"enableMACtoVENDORlookup",u"21")
			try: int(self.enableMACtoVENDORlookup)
			except: self.enableMACtoVENDORlookup = u"0"
			self.waitForMAC2vendor = False
			if self.enableMACtoVENDORlookup != u"0":
				self.M2V = M2Vclass.MAP2Vendor( pathToMACFiles=self.indigoPreferencesPluginDir+u"mac2Vendor/", refreshFromIeeAfterDays = int(self.enableMACtoVENDORlookup), myLogger = self.indiLOG.log )
				self.waitForMAC2vendor = self.M2V.makeFinalTable(quiet=True)


############ check for piBeacon plugin devcies
			try:
				self.piBeaconDevices=json.loads(self.pluginPrefs[u"piBeacon"])
			except:
				self.piBeaconDevices = {}
			self.cleanUppiBeacon()


			self.enablepiBeaconDevices = self.pluginPrefs.get(u"enablepiBeaconDevices","0")
			self.piBeaconIsAvailable = False
			self.piBeaconDevicesAvailable = []
			self.getpiBeaconAvailable()
			if self.piBeaconIsAvailable:
				self.pluginPrefs[u"piBeaconEnabled"] = True
				self.updatepiBeacons()
			else:
				self.pluginPrefs[u"piBeaconEnabled"] = False
############ check for UNIFI plugin devcies
			try:
				self.unifiDevices=json.loads(self.pluginPrefs[u"UNIFI"])
			except:
				self.unifiDevices = {}
			self.cleanUpUnifi()
			self.enableUnifiDevices = self.pluginPrefs.get(u"enableUnifiDevices","0")
			self.unifiAvailable = False
			self.unifiDevicesAvailable = []
			self.getUnifiAvailable()
			if self.unifiAvailable:
				self.pluginPrefs[u"unifiEnabled"] = True
				self.updateUnifi()
			else:
				self.pluginPrefs[u"unifiEnabled"] = False



############ setup mac / devname /number selection list
			self.IPretList=[]
			for theMAC in self.allDeviceInfo:
				theString = self.allDeviceInfo[theMAC][u"deviceName"] +u"-" +self.allDeviceInfo[theMAC][u"ipNumber"] + u"-"+theMAC
				self.IPretList.append(( theMAC,theString ))
			self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
			self.IPretList.append((1,u"Not used"))


############ check if version 1 if yes, upgrade to version 2
			retCode = self.checkIndigoVersion()

			try:
				indigo.variable.create(u"averageWiFiSignal_GHz",folder=self.indigoVariablesFolderID)
				indigo.variable.create(u"averageWiFiSignal_5GHz",folder=self.indigoVariablesFolderID)
			except:
				pass


############ create indigo Event variables  and initialize ..
				
			self.cleanUpEvents()
			self.setupEventVariables(init=True)
	 

############ initialize indigo settings ..
			self.indiLOG.log(20,u"Initializing parameters for FING")
			retCode = self.initFing(1)
			if retCode != 1:
				self.indiLOG.log(40,u" FING not running... quit")
				self.quitNOW = u"FING not running; wait with reboot"
				self.passwordOK = u"0"
			else:
				pass

############ print info to indigo logfile
			self.printConfig()
			self.printEvents()
			if self.routerType != u"0":
				errorMSG = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, rType=self.routerType)
				if errorMSG != u"ok":
					self.indiLOG.log(40, u"Router wifi not reachable, userid, password or ipnumber wrong?\n{}".format(errorMSG))
				self.printWiFi()
			self.printpiBeaconDevs()
			self.printUnifiDevs()
			

############ try to find hw vendor 
			self.indiLOG.log(10,u"getting vendor info ")
			self.MacToNamesOK = True
			for theMAC in self.allDeviceInfo:
				for item in emptyAllDeviceInfo:
					if item not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC][item] = copy.copy(emptyAllDeviceInfo[item])

				if not self.MacToNamesOK: continue 
				update = 0
				if self.allDeviceInfo[theMAC][u"hardwareVendor"].find(u"\n") >-1: 
					update = 1
					self.allDeviceInfo[theMAC][u"hardwareVendor"] = self.allDeviceInfo[theMAC][u"hardwareVendor"].strip(u"\n").strip()
				if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"{}  devID:{} existingVendor >>{}<<".format(theMAC, self.allDeviceInfo[theMAC][u"deviceId"], self.allDeviceInfo[theMAC][u"hardwareVendor"]) )
				if self.allDeviceInfo[theMAC][u"deviceId"] !=0:             
					if len(self.allDeviceInfo[theMAC][u"hardwareVendor"]) < 3 or  (self.allDeviceInfo[theMAC][u"hardwareVendor"].find(u"<html>")) > -1 :
						vend = self.getVendortName(theMAC)
						if vend == None: vend = ""
						if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"{}  Vendor info  >>{}<<".format(theMAC,vend ) )
						if vend != ""  or self.allDeviceInfo[theMAC][u"hardwareVendor"].find("<html>") > -1: 
							update = 2

				if update > 0:
					if update == 1: 
						vend = self.allDeviceInfo[theMAC][u"hardwareVendor"].strip(u"\n")
						if vend == None: vend = ""
					try: 
						self.indiLOG.log(10,u" updating :{}  {}  to >>{}<<".format(theMAC, self.allDeviceInfo[theMAC][u"deviceId"], vend))
						self.allDeviceInfo[theMAC][u"hardwareVendor"]  = vend
						dev = indigo.devices[self.allDeviceInfo[theMAC][u"deviceId"]]
						dev.updateStateOnServer(u"hardwareVendor",vend)
					except Exception as e:
						self.exceptionHandler(40, e)
						
			self.MacToNamesOK = True
				

		except Exception as e:
				self.exceptionHandler(40, e)
				self.quitNOW = u"restart required; {}".format(e) 
				self.sleep(20)


		return


########################################
	def setupFingPgm(self):
		try:

			#paths for fing executables files to be installed
			if self.passwordOK == u"2": 
				try:
					ret, err = self.readPopen(u"echo '"+self.yourPassword+ u"' | sudo -S  /bin/mkdir /usr/local/  ")
					if len(ret) > 1 and ret.find("File exists") ==-1 :
						self.indiLOG.log(20,u"mk fing dir:   "+ret.strip(u"\n"))
						if ret.find(u"incorrect password") >-1  or ret.find(u"Sorry, try again") >-1: 
							self.indiLOG.log(30,u"please corrrect password in config and reload plugin , skipping fing install")
							self.passwordOK = u"0"
							self.sleep(2)
				except:
					pass

				cmd = u"cd '"+self.indigoPreferencesPluginDir+u"'; echo '"+self.yourPassword+ u"' | sudo /usr/sbin/chown "+self.MACuserName+" *"
				os.system(cmd) 
				cmd = u"cd '"+self.indigoPreferencesPluginDir+u"'; echo '"+self.yourPassword+ u"' | sudo /bin/chmod -R 777 *"
				os.system(cmd) 
				if not os.path.isfile(self.fingDataFileName):
					subprocess.Popen( u"echo 0 > '"+ self.fingDataFileName+ u"' &",shell=True )
					self.sleep(0.2)
					if not os.path.isfile(self.fingDataFileName):
						self.indiLOG.log(40, u"could not create file: "+self.fingDataFileName+u" stopping program")
						#self.quitNOW = u"directory /  file problem"
						#return


			if self.passwordOK == u"2": 
				# set proper attributes for catalina 
				ret, err = self.readPopen(u"echo '"+self.yourPassword+ u"' | sudo -S /usr/bin/xattr -rd com.apple.quarantine '"+self.indigoPath+"Plugins/fingscan.indigoPlugin/Contents/Server Plugin/fingEXE/fing'")

				### set proper attributes for >= catalina OS 
				cmd = u"echo '"+self.yourPassword+ u"' | sudo -S /usr/bin/xattr -rd com.apple.quarantine '"+self.fingEXEpath+"'"
				ret, err = self.readPopen(cmd)
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"setting attribute for catalina+  with:  {}".format(cmd))
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"setting attribute for catalina+  result:{}".format(ret))
				cmd = u"echo '"+self.yourPassword+ u"' | sudo -S /usr/bin/xattr -rd com.apple.quarantine  /usr/local/lib/fing/*"
				ret, err = self.readPopen(cmd)
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"setting attribute for catalina+  with:  {}".format(cmd))
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"setting attribute for catalina+  result:{}".format(ret))
				self.indiLOG.log(20,u"fing install check done")

				self.opsys, self.fingVersion = self.checkVersion()
				if self.opsys >= 10.15 and self.fingVersion < 5 and self.fingVersion >0 :
					self.indiLOG.log(50,u"\nmiss match version of opsys:{} and fing:{} you need to upgrade / install FING to 64 bit version (>=5). Download from\nhttps://www.fing.com/products/development-toolkit  use OSX button"+\
					u"\nor use\nCLI_macOSX_5.4.0.zip\n included in the plugin download to install\nthen delete fing.log and fing.data in the indigo preference directory and reload the plugin".format(self.opsys, self.fingVersion))
					for ii in range(1000):			
						time.sleep(2)
				if self.fingVersion  ==-1 :
					self.indiLOG.log(50,u"\nmiss match version of opsys:{} and fing:{} you need to upgrade / imstall FING to 64 bit version (>=5). Download from\nhttps://www.fing.com/products/development-toolkit  use OSX button")
					self.indiLOG.log(50,u"or use\nCLI_macOSX_5.4.0.zip\n included in the plugin download to install\nthen delete fing.log and fing.data in the indigo preference directory and reload the plugin".format(self.opsys, self.fingVersion))
					self.indiLOG.log(50,u"\n and try:")
					self.indiLOG.log(50,u"sudo /usr/bin/xattr -rd com.apple.quarantine  /usr/local/lib/fing/*")
					self.indiLOG.log(50,u"sudo /usr/bin/xattr -rd com.apple.quarantine  /usr/local/bin/fing")
					for ii in range(1000):			
						time.sleep(2)
			
		except Exception as e:
			self.exceptionHandler(40, e)
		return	



########################################
	def checkVersion(self):
		import platform
		try:
			opsys		= platform.mac_ver()[0].split(u".")
			opsys		= float(opsys[0]+u"."+opsys[1])
			cmd 		= u"echo '"+self.yourPassword+ u"' | sudo -S "+self.fingEXEpath+" -v"
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"testing versiosn w  {}".format(cmd))
			ret, err = self.readPopen(cmd)
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"testing verions w  {} ==> {} - {}, opsys:{}".format(cmd, ret, err, opsys))
			ret 		= ret.strip("\n").split(".")
			if len(ret) > 1:
				fingVersion	= float(ret[0]+"."+ret[1])
			else:
				self.indiLOG.log(40, u"error in get fing version#: seems that either {} in not installed or password>>{}<< not correct,\nreturned text from fing probe:{}:  {}-{}".format(self.fingEXEpath, self.yourPassword, cmd, ret, err))
				fingVersion	= -1.0
			return opsys, fingVersion
		except Exception as e:
			self.exceptionHandler(40, e)
		return 0, -1.0			


########################################
	def refreshVariables(self):
		try:    indigo.variable.create(u"ipDevsLastUpdate",u"",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create(u"ipDevsLastDevChangedIndigoName",u"",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create(u"ipDevsNewDeviceNo",u"",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create(u"ipDevsNewIPNumber",u"",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create(u"ipDevsNoOfDevices",u"",self.indigoVariablesFolderID)	
		except: pass
		try:    indigo.variable.create(u"ipDevsOldNewIPNumber",u"",u"")	
		except: pass
		return
		
########################################
	def setupEventVariables(self,init=False):
		try:
			try:
				indigo.variables.folder.create(u"FINGscanEvents")
				self.indiLOG.log(20,u"FINGscanFolder folder created")
			except:
				pass
			self.FINGscanFolderID = indigo.variables.folders[u"FINGscanEvents"].id
			for i in self.EVENTS:
				try: 	indigo.variable.create(u"allHome_{}".format(i),u"",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create(u"oneHome_{}".format(i),u"",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create(u"nHome_{}".format(i),u"",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create(u"allAway_{}".format(i),u"",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create(u"oneAway_{}".format(i),u"",folder=self.FINGscanFolderID)
				except:	pass
				try: 	indigo.variable.create(u"nAway_{}".format(i),u"",folder=self.FINGscanFolderID)
				except:	pass

			
			try:
				indigo.variable.create(u"FingEventDevChangedIndigoId",folder=self.FINGscanFolderID)
			except: pass



			for nEvent in self.EVENTS:
				evnt = self.EVENTS[nEvent]
				if u"oneHome" not in evnt: continue
				xx =  unicode(indigo.variables[u"oneHome_"+nEvent].value)
				if evnt[u"oneHome"]  !=  xx:                	indigo.variable.updateValue(u"oneHome_"+nEvent,evnt[u"oneHome"])
				xx =  unicode(indigo.variables[u"allHome_"+nEvent].value)
				if evnt[u"allHome"]  !=  xx:               		indigo.variable.updateValue(u"allHome_"+nEvent,evnt[u"allHome"])
				xx =  unicode(indigo.variables[u"allHome_"+nEvent].value)
				if evnt[u"nHome"]  !=  xx:                  	indigo.variable.updateValue(u"nHome_"+nEvent,unicode(evnt[u"nHome"]))
				xx =  unicode(indigo.variables[u"oneAway_"+nEvent].value)
				if evnt[u"oneAway"]  !=  xx:                  	indigo.variable.updateValue(u"oneAway_"+nEvent,evnt[u"oneAway"])
				xx =  unicode(indigo.variables[u"allAway_"+nEvent].value)
				if evnt[u"allAway"]  !=  xx:             		indigo.variable.updateValue(u"allAway_"+nEvent,evnt[u"allAway"])
				xx =  unicode(indigo.variables[u"nAway_"+nEvent].value)
				if evnt[u"nAway"]  !=  xx:                    	indigo.variable.updateValue(u"nAway_"+nEvent,unicode(evnt[u"nAway"]))
		except Exception as e:
			self.exceptionHandler(40, e)
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
		ipN= self.allDeviceInfo[MAC][u"ipNumber"]
		Wait = ""
		if waitForPing != "": 
			Wait = u"-W {}".format(waitForPing)
		Count = u"-c 1"
		if countPings != "":
			Count = u"-c {}".format(countPings)
		if nPings == 1:
			waitAfterPing =0.

		retCode = 1
		for nn in range(nPings):            
			retCode = subprocess.call(u'/sbin/ping -o {} {} -q {} >/dev/null'.format(Wait, Count, ipN),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # "call" will wait until its done and deliver retcode 0 or >0
			if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"ping resp:{}: {}".format(ipN, retCode) )
			if retCode ==0: return 0
			if nn != nPings-1: self.sleep(waitAfterPing)
		return retCode

########################################
	def sendWakewOnLan(self, MAC, calledFrom=""):
		try:
			data = ''.join([u'FF' * 6, MAC.replace(u':', '') * 16])
			if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"sendWakewOnLan for {};  called from {};  bc ip: {}".format(MAC, calledFrom, self.broadcastIP) )
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			sock.sendto(data.decode(u"hex"), (self.broadcastIP, 9))
		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40,u"sendWakewOnLan for {};  called from {};  bc ip: {}".format(MAC, calledFrom, self.broadcastIP) )

########################################
	def checkIfiFindisEnabled(self):
		try:
			self.iDevicesEnabled =False
			self.getiFindFile()
			if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
				for dev in indigo.devices.iter(self.iFindStuffPlugin):
					#if  dev.pluginId.find(self.iFindStuffPlugin) == -1 :continue
					if dev.deviceTypeId!=u"iAppleDeviceAuto": continue
					self.iDevicesEnabled =True
					self.pluginPrefs[u"iDevicesEnabled"] =True
					return
			self.pluginPrefs[u"iDevicesEnabled"] =False
		except Exception as e:
			self.exceptionHandler(40, e)
		return

########################################
	def getiFindFile(self):
		try:
			line, err = self.readPopen(u"ls '{}Preferences/Plugins/' | grep  '{}' | grep -v grep".format(self.indigoPath, iFindPluginMinText))
			if len(line) > 0:
				self.iFindStuffPlugin = line.split(u".indiPref")[0]
			self.indiLOG.log(20,u"ifind plugin: {}".format(self.iFindStuffPlugin))

		except Exception as e:
			self.exceptionHandler(40, e)
		return
########################################
	def getpiBeaconAvailable(self):
		try:
			self.piBeaconDevicesAvailable=[]
			if  indigo.server.getPlugin(u"com.karlwachs.piBeacon").isEnabled():
				for dev in indigo.devices.iter(u"com.karlwachs.piBeacon"):
						self.piBeaconIsAvailable =True
						if u"Pi_0_Signal" in dev.states and u"status" in dev.states: # only interested in iBeacons
							self.piBeaconDevicesAvailable.append((dev.id, dev.name))
							if dev.states[u"status"] == u"up" or dev.states[u"status"] == u"1":
															status= u"up"
							else:                           status= u"0"
							if unicode(dev.id) not in self.piBeaconDevices:
								self.piBeaconDevices[unicode(dev.id)]={"currentStatus":status,"lastUpdate":time.time(),"name":dev.name,"used": "0"}
							else:
								self.piBeaconDevices[unicode(dev.id)][u"name"]=dev.name
								self.piBeaconDevices[unicode(dev.id)][u"currentStatus"]=status
							
			## remove devices that do not exist anymore
			delList=[]
			list=unicode(self.piBeaconDevicesAvailable)
			for nDev in self.piBeaconDevices:
				if list.find(nDev)==-1 : delList.append(nDev)
			for d in delList:
				del self.piBeaconDevices[d] 
			self.piBeaconDevicesAvailable= sorted(self.piBeaconDevicesAvailable, key=lambda tup: tup[1])    
			self.piBeaconDevicesAvailable.append((1,u"do not use"))
		except Exception as e:
			self.exceptionHandler(40, e)
		return
########################################
	def getUnifiAvailable(self):
		try:
			self.unifiDevicesAvailable=[]
			if  indigo.server.getPlugin(u"com.karlwachs.uniFiAP").isEnabled():
				for dev in indigo.devices.iter(u"com.karlwachs.uniFiAP"):
					#if  dev.pluginId.find("com.karlwachs.uniFiAP") > -1 :
						self.unifiAvailable =True
						self.unifiDevicesAvailable.append((dev.id,dev.name))
						if u"status" in dev.states:
							if dev.states[u"status"] == u"up" or dev.states[u"status"] ==u"1":
															state = u"up"
							else:                           state = u"0"
							if unicode(dev.id) not in self.unifiDevices:
								self.unifiDevices[unicode(dev.id)] = {u"currentStatus": u"0",u"lastUpdate":time.time(),u"name":dev.name,u"used": u"0"}
							else:
								self.unifiDevices[unicode(dev.id)][u"name"] = dev.name
								self.unifiDevices[unicode(dev.id)][u"currentStatus"] = state
			## remove devices that do not exist anymore
			#self.indiLOG.log(30,unicode(self.unifiDevicesAvailable))
			#self.indiLOG.log(30,unicode(self.unifiDevices))
			delList=[]
			list=unicode(self.unifiDevicesAvailable)
			for nDev in self.unifiDevices:
				if list.find(nDev)==-1 : delList.append(nDev)
			for d in delList:
				del self.unifiDevices[d]
			self.unifiDevicesAvailable= sorted(self.unifiDevicesAvailable, key=lambda tup: tup[1])                
			self.unifiDevicesAvailable.append((1,u"do not use"))
		except Exception as e:
			self.exceptionHandler(40, e)
		return


########################################
	def printConfig(self):
		try:
			self.indiLOG.log(10,u"settings:  iDevicesEnabled              {}".format(self.iDevicesEnabled))
			self.indiLOG.log(10,u"settings:  inbetweenPingType            {}".format(self.inbetweenPingType))
			self.indiLOG.log(10,u"settings:  wifiRouter                   {}".format(self.routerType))
			self.indiLOG.log(10,u"settings:  wait seconds between cycles  {}".format(self.sleepTime))
			self.indiLOG.log(10,u"settings:  password entered             {}".format(self.passwordOK=="2"))
			self.indiLOG.log(10,u"settings:  debugLevel                   {}".format(self.debugLevel))
			try:
				nwP= self.theNetwork.split(".")
				self.indiLOG.log(10,u"settings:  FINGSCAN will scan Network    broadCast{} ".format(self.broadcastIP))
			except:
				pass
			self.indiLOG.log(10,u"\n")
		except Exception as e:
			self.exceptionHandler(40, e)


########################################
	def deviceDeleted(self,dev):
		try:
			devID= dev.id
			for theMAC in self.allDeviceInfo:
				if self.allDeviceInfo[theMAC][u"deviceId"] ==dev.id:
					self.deleteIndigoIpDevicesData(theMAC)
					return
		except Exception as e:
			self.exceptionHandler(40, e)

########################################
	def deviceStartComm(self, dev):
		try:
			if self.pluginState == u"init":
				dev.stateListOrDisplayStateIdChanged()  # update device.xml info if changed
			else:
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"dev start called for "+dev.name)
			return
		except Exception as e:
			self.exceptionHandler(40, e)
	
########################################
	def deviceStopComm(self, dev):
		if self.pluginState != u"init":
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"dev Stop called for "+dev.name)
		
		
########################################
	def intToBin(self,iNumber):
		try:
			nBinString=""
			for i in range(17):
				j=16-i
				k=int(math.pow(2,j))
				if iNumber >=k:
					iNumber -= k
					nBinString  += u"1"
				else:nBinString += u"0"
			return nBinString
		except Exception as e:
			self.exceptionHandler(40, e)


########################################
	def shutdown(self):
		self.indiLOG.log(30,u"shutdown called")
		retCode = self.killFing(u"all")
		retCode = self.killPing(u"all")


########################################
	def stopConcurrentThread(self):
		self.stopConcurrentCounter +=1
		self.indiLOG.log(30,u"stopConcurrentThread called " + unicode(self.stopConcurrentCounter))
		if self.stopConcurrentCounter ==1:
			self.stopThread = True


########################################
	def CALLBACKIPdeviceMACnumber1(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"1")
	def CALLBACKIPdeviceMACnumber2(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"2")
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
		return self.CALLBACKIPdevice(valuesDict,u"10")
	def CALLBACKIPdeviceMACnumber11(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"11")
	def CALLBACKIPdeviceMACnumber12(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"12")
	def CALLBACKIPdeviceMACnumber13(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"13")
	def CALLBACKIPdeviceMACnumber14(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"14")
	def CALLBACKIPdeviceMACnumber15(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"15")
	def CALLBACKIPdeviceMACnumber16(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"16")
	def CALLBACKIPdeviceMACnumber17(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"17")
	def CALLBACKIPdeviceMACnumber18(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"18")
	def CALLBACKIPdeviceMACnumber19(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"19")
	def CALLBACKIPdeviceMACnumber20(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"20")
	def CALLBACKIPdeviceMACnumber21(self, valuesDict,typeId=""):
		return self.CALLBACKIPdevice(valuesDict,u"21")

########################################
	def CALLBACKIPdevice(self, valuesDict,nDev):
		try:
			self.currentEventN=unicode(valuesDict[u"selectEvent"])
			if self.currentEventN == u"0":
				return valuesDict
			imac= valuesDict[u"IPdeviceMACnumber"+nDev]
			if imac == u"0" or imac== u"1" or imac == "":
				valuesDict[u"iDevicesEnabled"+nDev] =False
				return valuesDict
				
			if self.iDevicesEnabled:
				valuesDict[u"iDevicesEnabled"+nDev] =True
			else:
				valuesDict[u"iDevicesEnabled"+nDev] =False
				valuesDict[u"iDevicesEnabled"+nDev+"a"] =False
			
		
		except Exception as e:
			self.exceptionHandler(40, e)
		return valuesDict


########################################
	def CALLBACKIdevice1Selected(self, valuesDict,typeId=""):
		return self.CALLBACKIdeviceSelected(valuesDict,u"1")
	def CALLBACKIdevice2Selected(self, valuesDict,typeId=""):
		return self.CALLBACKIdeviceSelected(valuesDict,u"2")
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
###		self.indiLOG.log(20,u"currentEventN{}".format(self.currentEventN)+"  ndev{}".format(nDev)+"  iDeviceName"+valuesDict[u"iDeviceName"+nDev])
		try:
			if self.currentEventN == u"0":
				return valuesDict
			if self.iDevicesEnabled:
				if 	not ( valuesDict[u"iDeviceName"+nDev] =="1" or valuesDict[u"iDeviceName"+nDev] ==""):
					valuesDict[u"iDevicesEnabled"+nDev+"a"] =True
				else:
					valuesDict[u"iDevicesEnabled"+nDev+"a"] =False
			else:
				valuesDict[u"iDevicesEnabled"+nDev+"a"] =False
		
		except Exception as e:
			self.exceptionHandler(40, e)
		return valuesDict


########################################
	def CALLBACKevent(self, valuesDict,typeId=""):

		try:
			self.getUnifiAvailable()
			self.getpiBeaconAvailable()
			
			self.currentEventN=unicode(valuesDict[u"selectEvent"])
			#self.indiLOG.log(20,u"CALLBACKevent currentEventN = " +self.currentEventN)
			if self.currentEventN == u"0":
				errorDict = valuesDict
				return valuesDict
			
			if not self.currentEventN in self.EVENTS:
				self.EVENTS[self.currentEventN]= copy.deepcopy(emptyEVENT)
				
			for nDev in self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"]:
				#self.indiLOG.log(20,u"CALLBACKevent checking  nDev:"+nDev+ u";  self.EVENTS[self.currentEventN][IPdeviceMACnumber][nDev]:{}".format(self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nDev]) )
				valuesDict[u"IPdeviceMACnumber"+nDev]	=	self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nDev]
				valuesDict[u"iDeviceName"+nDev]	        =	self.EVENTS[self.currentEventN][u"iDeviceName"][nDev]
				#if nDev== u"1": self.indiLOG.log(20,u"CALLBACKevent  IPdeviceMACnumber= " +valuesDict[u"IPdeviceMACnumber"+nDev])
				#idevD,idevName,idevId = self.getIdandName(unicode(self.EVENTS[self.currentEventN][u"iDeviceName"][nDev]))
				#if idevName != "0":
				#    valuesDict[u"iDeviceName"+nDev]			=	unicode(idevId)
				valuesDict[u"iDeviceUseForHome"+nDev]	=	self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]
				valuesDict[u"iDeviceUseForAway"+nDev]	=	self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]
				imac= valuesDict[u"IPdeviceMACnumber"+nDev]
				if imac == u"0" or imac== u"1" or imac == "":
					valuesDict[u"iDevicesEnabled"+nDev] =False
				else:
					if self.iDevicesEnabled and (self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev] == u"1" or self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev] == u"1"):
						valuesDict[u"iDevicesEnabled"+nDev] =True
						valuesDict[u"iDevicesEnabled"+nDev+"a"] = True
					else:
						valuesDict[u"iDevicesEnabled"+nDev] = False
						valuesDict[u"iDevicesEnabled"+nDev+"a"] = False

		
			valuesDict[u"minimumTimeHome"]				    	=	unicode(int(float(self.EVENTS[self.currentEventN][u"minimumTimeHome"])))
			valuesDict[u"minimumTimeAway"]				    	=	unicode(int(float(self.EVENTS[self.currentEventN][u"minimumTimeAway"])))
			valuesDict[u"distanceAwayLimit"]				    =	unicode(int(float(self.EVENTS[self.currentEventN][u"distanceAwayLimit"])))
			valuesDict[u"distanceHomeLimit"]				    =	unicode(int(float(self.EVENTS[self.currentEventN][u"distanceHomeLimit"])))
			valuesDict[u"maxLastTimeUpdatedDistanceMinutes"]	=   unicode(int(float(self.EVENTS[self.currentEventN][u"maxLastTimeUpdatedDistanceMinutes"])))
			valuesDict[u"enableDisable"]					    =	self.EVENTS[self.currentEventN][u"enableDisable"]

			if self.iDevicesEnabled:	valuesDict[u"iDevicesEnabled"]   = True
			else:						valuesDict[u"iDevicesEnabled"]   = False
				
				
			if self.piBeaconIsAvailable:	
				valuesDict[u"piBeaconEnabled"]     = True
				for npiBeacon in (u"25",u"26",u"27",u"28",u"29"):
					valuesDict[u"IPdeviceMACnumber"+npiBeacon]=self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][npiBeacon]
			else:	
				valuesDict[u"piBeaconEnabled"]     = False

			if self.unifiAvailable:	
				valuesDict[u"unifiEnabled"]     = True
				for nUnifi in (u"30","31","32","33","34"):
					valuesDict[u"IPdeviceMACnumber"+nUnifi]=self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nUnifi]
			else:	
				valuesDict[u"unifiEnabled"]     = False

		
		except Exception as e:
			self.exceptionHandler(40, e)
		#self.indiLOG.log(20,u"CALLBACKevent valuesDict:{}".format(valuesDict))
		self.updatePrefs = True
		return valuesDict

########################################
	def doPing(self, theMAC):
		try:
			ipn= self.allDeviceInfo[theMAC][u"ipNumber"]
			ret, err = self.readPopen('/sbin/ping -c3 '+ipn)
			if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"pinging device "+ self.allDeviceInfo[theMAC][u"deviceName"]+u" " +self.allDeviceInfo[theMAC][u"ipNumber"])
			lines = ret.split(u"\n")
			for line in lines:
				if self.decideMyLog(u"Ping"): self.indiLOG.log(20,unicode(line))
		except Exception as e:
			self.exceptionHandler(40, e)

########################################
	def pingCALLBACKaction(self, action):

		theMAC= action.props[u"pingIpDevice"]
		self.doPing(theMAC)



		
########################################
	def actionFromCALLBACKaction(self, action):
		#if self.decideMyLog(u"iFind"): self.indiLOG.log(20,u" actionFromCALLBACK --{}".format(action))
		try:
			self.callingPluginName.append(action.props[u"from"])
			self.callingPluginCommand.append(action.props[u"msg"])
		except:
			pass
			self.indiLOG.log(40,  u"actionFrom no plugin call back given" )
			return
		self.triggerFromPlugin=True
		return

########################################
	def piBeaconUpdateCALLBACKaction(self, action):
		#if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u" self.piBeaconDevices {}".format(self.piBeaconDevices))
		try:
			if u"deviceId" in  action.props:
				for devId in action.props[u"deviceId"]:
					devS=unicode(devId)
					if devS not in self.piBeaconDevices:
						if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"piBeacon deviceId not used in fingscan: "+devS)
						continue
					dev=indigo.devices[int(devId)]
					mdevName=dev.name
					try:
						try:
							status= dev.states[u"status"].lower()
							if status == u"1": status= u"up"
						except:
							status = u"notAvail"
						
						if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u" devName "+mdevName+u"  Status "+status )
						if self.piBeaconDevices[devS][u"currentStatus"] !=status:
							if self.piBeaconDevices[devS][u"used"] == u"1":
								self.newSleepTime=0.
								self.piBeaconUpDateNeeded = True
							self.piBeaconDevices[devS][u"lastUpdate"] = time.time()
						self.piBeaconDevices[devS][u"currentStatus"] = status
						self.piBeaconDevices[devS][u"name"] = mdevName
					except:
						if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"status data not ready:{}".format(status))
		
			else:
				if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u" error from piBeacon, deviceId not in action: {}".format(action))
				return
		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, unicode(action))
			return
		self.pluginPrefs[u"piBeacon"]	=	json.dumps(self.piBeaconDevices)
		return
		

########################################
	def UnifiUpdateCALLBACKaction(self, action):
		if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u"self.unifiDevices {}".format(self.unifiDevices))
		try:
			if u"deviceId" in  action.props:
				for devId in action.props[u"deviceId"]:
					devS=unicode(devId)
					if devS not in self.unifiDevices:
						if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u"unifi deviceId not used in fingscan: "+devS)
						continue
					dev=indigo.devices[int(devId)]
					mdevName=dev.name
					try:
						try:
							status= dev.states[u"status"]
						except:
							status = u"notAvail"
						
						if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u" devName "+mdevName+u"  status "+status )
						if self.unifiDevices[devS][u"currentStatus"] !=status:
							if self.unifiDevices[devS][u"used"] == u"1":
								self.newSleepTime=0.
								self.unifiUpDateNeeded=True
							self.unifiDevices[devS][u"lastUpdate"] = time.time()
						self.unifiDevices[devS][u"currentStatus"] = status
						self.unifiDevices[devS][u"name"] = mdevName
					except:
						if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u"status data not ready:"+status)
		
			else:
				if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u" error from unifi, deviceId not in action: {}".format(action))
				return
		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, unicode(action))
			return
		self.pluginPrefs[u"UNIFI"]	=	json.dumps(self.unifiDevices)
		return


########################################
	def updatepiBeacons(self):
		try:
			status = u"not initialized"
			for deviceId in  self.piBeaconDevices:
				currentState= self.piBeaconDevices[deviceId][u"currentStatus"]
				lastUpdate= self.piBeaconDevices[deviceId][u"lastUpdate"]
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
						status= dev.states[u"status"]
						if status == u"1": status = u"up"
					except:
						status = u"notAvail"

					if currentState !=status:
						if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"updating piBeacon:  devName "+mdevName+u"  status "+status)
						self.piBeaconUpDateNeeded=True
						self.piBeaconDevices[deviceId][u"currentStatus"]= status
						self.piBeaconDevices[deviceId][u"lastUpdate"] 	= time.time()
						self.piBeaconDevices[deviceId][u"name"] 		= mdevName
						if self.piBeaconDevices[devS][u"used"] == u"1":
							self.newSleepTime=0.
				except:
						if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"updating piBeacon:  devName {}".format(mdevName)+u"  status {}".format(status) +u" not ready"  )
	
		
		except Exception as e:
			self.exceptionHandler(40, e)
			self.piBeaconDevices={}
		return

########################################
	def updateUnifi(self):
		try:
			Presence = u"not initialized"
			for deviceId in  self.unifiDevices:
				currentState  = self.unifiDevices[deviceId][u"currentStatus"]
				lastUpdate    = self.unifiDevices[deviceId][u"lastUpdate"]
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
						Status= dev.states[u"status"]
					except:
						Status = u"notAvail"

					if currentState !=Presence:
						if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u"updating unifi:  devName "+mdevName+u"  Status "+Status)
						self.unifiUpDateNeeded=True
						self.unifiDevices[deviceId][u"currentStatus"] = Status
						self.unifiDevices[deviceId][u"lastUpdate"] 	= time.time()
						self.unifiDevices[deviceId][u"name"] 		= mdevName
						if self.unifiDevices[devS][u"used"] == u"1":
							self.newSleepTime=0.
				except:
						if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u"updating unifi:  devName {}".format(mdevName)+u"  Status {}".format(Status) +u" not ready"  )
	
		
		except Exception as e:
			self.exceptionHandler(40, e)
			self.unifiDevices={}
		return

##

########################################
	def buttonConfirmAddIgnoredMACsCALLBACK(self, valuesDict,typeId=""):
		theMAC = valuesDict[u"selectedMAC"]
		if theMAC not in self.ignoredMAC:
			info = theMAC
			if theMAC in self.allDeviceInfo:
				info = theMAC+u"-"+self.allDeviceInfo[theMAC][u"deviceName"]+u"-"+self.allDeviceInfo[theMAC][u"ipNumber"]
			self.ignoredMAC[theMAC] = info
			self.saveIgnoredMAC()
		return valuesDict
########################################
	def buttonConfirmRemoveIgnoredMACsCALLBACK(self, valuesDict,typeId=""):
		theMAC = valuesDict[u"selectedMAC"]
		if theMAC in self.ignoredMAC:
			del self.ignoredMAC[theMAC]
			self.saveIgnoredMAC()
		return valuesDict


########################################
	def filterIgnoredMACs(self, filter=u"self", valuesDict=None, typeId="", targetId=0):
		retList =[]
		for theMAC in self.ignoredMAC:
			retList.append((theMAC,self.ignoredMAC[theMAC]))
		retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text
		return retList
########################################
	def filterNotIgnoredMACs(self, filter=u"self", valuesDict=None, typeId="", targetId=0):
		retList =[]
		for theMAC in self.allDeviceInfo:
			if theMAC not in self.ignoredMAC:
				retList.append((theMAC,theMAC+u"-"+self.allDeviceInfo[theMAC][u"deviceName"]+"-"+self.allDeviceInfo[theMAC][u"ipNumber"]))
		retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text
		return retList

########################################
	def filterListIpDevices(self, filter=u"self", valuesDict=None, typeId="", targetId=0):
		retList =[]
		for theMAC in self.allDeviceInfo:
			devI=self.allDeviceInfo[theMAC]
			retList.append((theMAC,devI[u"deviceName"]+u"-"+devI[u"ipNumber"]+u"-"+devI[u"status"]))

		retList	= sorted(retList, key=lambda tup: tup[1]) #sort string, keep mac numbers with the text

		return retList


########################################
	def selectiDeviceFilter(self, filter=u"self", valuesDict=None,typeId=""):
		try:
			self.IDretList=[]
			if  indigo.server.getPlugin(self.iFindStuffPlugin).isEnabled():
				self.iDevicesEnabled = True
				for dev in indigo.devices.iter(self.iFindStuffPlugin):
					if dev.deviceTypeId != u"iAppleDeviceAuto": continue
					self.IDretList.append((dev.id,dev.name))
				self.IDretList	= sorted(self.IDretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
				self.IDretList.append((1,u"do not use iDevice"))
			else:
				self.iDevicesEnabled = False
			#self.indiLOG.log(20, u"selectiDeviceFilter called" )
			
			return self.IDretList
		except Exception as e:
			self.indiLOG.log(40,  u"in Line '%s' has error='%s'" % (sys.exc_info()[2].tb_lineno, e) )

	   

########################################
	def IPdeviceMACnumberFilter(self, filter=u"self", valuesDict=None,typeId=""):
		try:
			self.IPretList=[]
			for theMAC in self.allDeviceInfo:
				devI=self.allDeviceInfo[theMAC]
				theString = devI[u"deviceName"]+u"-"+devI[u"ipNumber"]+u"-"+theMAC
				self.IPretList.append(( theMAC,theString ))
			self.IPretList	= sorted(self.IPretList, key=lambda tup: tup[1]) #sort string, keep mac number with the text
			self.IPretList.append((1,u"Not used"))
		except Exception as e:
			self.exceptionHandler(40, e)
		#self.indiLOG.log(20, u"IPdeviceMACnumberFilter called" )
		return self.IPretList


########################################
	def piBeaconFilter(self, filter=u"self", valuesDict=None,typeId=""):
		#self.indiLOG.log(20, u"piBeaconFilter called" )
		try:
			retList =copy.deepcopy(self.piBeaconDevicesAvailable)
		except Exception as e:
			self.exceptionHandler(40, e)
			return [(0,0)]
		return retList

########################################
	def unifiFilter(self, filter=u"self", valuesDict=None,typeId=""):
		#self.indiLOG.log(20, u"unifiFilter called" )
		try:
			retList =copy.deepcopy(self.unifiDevicesAvailable)
		except Exception as e:
			self.exceptionHandler(40, e)
			return [(0,0)]
		return retList


########################################
	def buttonConfirmDevicesCALLBACK(self, valuesDict,typeId=""):
		errorDict=indigo.Dict()

		try:
			self.currentEventN=unicode(valuesDict[u"selectEvent"])
			if self.currentEventN == u"0" or  self.currentEventN =="":
	#			errorDict = valuesDict
				return valuesDict


	########  do piBeacon stuff needed later in EVENTS
			for npiBeacon in (u"22",u"23",u"24",u"25",u"26",u"27",u"28",u"29"):
				mId=unicode(valuesDict[u"IPdeviceMACnumber"+npiBeacon])
				if mId == u"0":
					mId = self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][npiBeacon]
				elif mId == u"1":
					mId = ""

				self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][npiBeacon]	= mId
				if mId != u"" and mId != u"0"and mId != u"1":
					try:
						mdevName=indigo.devices[int(mId)].name
						if mId not in self.piBeaconDevices:
							if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"piBeacon mId 3 {}".format(mId) + u"  {}".format(npiBeacon))
					except:
						pass


			## clean up piBeacon list
			keep=[]
			for nEvent in self.EVENTS:
				for npiBeacon in (u"25",u"26",u"27",u"28",u"29"):
					mId=self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][npiBeacon]
					if  mId !="" and mId != u"0":
						keep.append(mId)

			deleteM=[]
			for piBeaconId in self.piBeaconDevices:
				if piBeaconId not in keep: deleteM.append(piBeaconId)
			for piBeaconId in deleteM:
				del self.piBeaconDevices[piBeaconId]



	########  do unifi stuff needed later in EVENTS
			for nUnifi in (u"30",u"31",u"32",u"33",u"34"):
				mId=unicode(valuesDict[u"IPdeviceMACnumber"+nUnifi])
				if mId == u"0":
					mId = self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nUnifi]
				elif mId == u"1":
					mId = ""

				self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nUnifi]	= mId
				if mId !="" and mId !="0"and mId != u"1":
					try:
						mdevName=indigo.devices[int(mId)].name
						if mId not in self.piBeaconDevices:
							if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"unifi mId 3 {}".format(mId) + u"  {}".format(nUnifi))
					except:
						pass


			## clean up unifi list
			keep=[]
			for nEvent in self.EVENTS:
				for nUnifi in (u"30",u"31",u"32",u"33",u"34"):
					mId=self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nUnifi]
					if  mId !="" and mId !="0":
						keep.append(mId)

			deleteM=[]
			for unifiId in self.unifiDevices:
				if unifiId not in keep: deleteM.append(unifiId)
			for unifiId in deleteM:
				del self.unifiDevices[unifiId]







			if not self.currentEventN in self.EVENTS:
				self.EVENTS[self.currentEventN]= copy.deepcopy(emptyEVENT)

			if valuesDict[u"DeleteEvent"]:
				for nDev in self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"]:
					iDev= int(nDev)
					valuesDict[u"IPdeviceMACnumber"+nDev]	= u"0"
					if iDev <= nOfIDevicesInEvent:
						valuesDict[u"iDeviceName"+nDev]			= ""
						valuesDict[u"iDeviceUseForHome"+nDev]	= u"0"
						valuesDict[u"iDeviceUseForAway"+nDev]	= u"0"
				valuesDict[u"DeleteEvent"] 		= False
				valuesDict[u"distanceAwayLimit"]	= unicode(copy.deepcopy(emptyEVENT[u"distanceAwayLimit"]))
				valuesDict[u"distanceHomeLimit"]	= unicode(copy.deepcopy(emptyEVENT[u"distanceHomeLimit"]))
				valuesDict[u"minimumTimeAway"]	= unicode(copy.deepcopy(emptyEVENT[u"minimumTimeAway"]))
				valuesDict[u"enableDisable"] 	= False
				self.EVENTS[self.currentEventN] = copy.deepcopy(emptyEVENT)
				self.currentEventN = u"0"
				valuesDict[u"selectEvent"] = u"0"
				valuesDict[u"EVENT"] =json.dumps(self.EVENTS)
				return valuesDict

	##### not delete
			if valuesDict[u"enableDisable"]      != "": self.EVENTS[self.currentEventN][u"enableDisable"] 	= valuesDict[u"enableDisable"]
			else: self.EVENTS[self.currentEventN][u"enableDisable"] = emptyEVENT[u"enableDisable"]; valuesDict[u"enableDisable"] =  emptyEVENT[u"enableDisable"];errorDict[u"enableDisable"]=emptyEVENT[u"enableDisable"]

			if valuesDict[u"minimumTimeHome"]    != "": self.EVENTS[self.currentEventN][u"minimumTimeHome"] 	= float(valuesDict[u"minimumTimeHome"])
			else: self.EVENTS[self.currentEventN][u"minimumTimeHome"] = emptyEVENT[u"minimumTimeHome"]; valuesDict[u"minimumTimeHome"] =  emptyEVENT[u"minimumTimeHome"];errorDict[u"minimumTimeHome"]=emptyEVENT[u"minimumTimeHome"]

			if valuesDict[u"minimumTimeAway"]    != "": self.EVENTS[self.currentEventN][u"minimumTimeAway"]	= float(valuesDict[u"minimumTimeAway"])
			else: self.EVENTS[self.currentEventN][u"minimumTimeAway"] = emptyEVENT[u"minimumTimeAway"]; valuesDict[u"minimumTimeAway"] =  emptyEVENT[u"minimumTimeAway"];errorDict[u"minimumTimeAway"]=emptyEVENT[u"minimumTimeAway"]

			if self.iDevicesEnabled:
				if valuesDict[u"distanceAwayLimit"]  != "": 
						self.EVENTS[self.currentEventN][u"distanceAwayLimit"] = int(float(valuesDict[u"distanceAwayLimit"]))
				else:   self.EVENTS[self.currentEventN][u"distanceAwayLimit"] = emptyEVENT[u"distanceAwayLimit"]; valuesDict[u"distanceAwayLimit"] =  emptyEVENT[u"distanceAwayLimit"];errorDict[u"distanceAwayLimit"]=emptyEVENT[u"distanceAwayLimit"]

				if valuesDict[u"distanceHomeLimit"]  != "": 
						self.EVENTS[self.currentEventN][u"distanceHomeLimit"] = int(float(valuesDict[u"distanceHomeLimit"]))
				else:   self.EVENTS[self.currentEventN][u"distanceHomeLimit"] = emptyEVENT[u"distanceHomeLimit"]; valuesDict[u"distanceHomeLimit"] =  emptyEVENT[u"distanceHomeLimit"];errorDict[u"distanceHomeLimit"]=emptyEVENT[u"distanceHomeLimit"]

				if valuesDict[u"maxLastTimeUpdatedDistanceMinutes"]!="":	
						self.EVENTS[self.currentEventN][u"maxLastTimeUpdatedDistanceMinutes"] =float(valuesDict[u"maxLastTimeUpdatedDistanceMinutes"])
				else:   self.EVENTS[self.currentEventN][u"maxLastTimeUpdatedDistanceMinutes"] =float(emptyEVENT[u"maxLastTimeUpdatedDistanceMinutes"]);errorDict[u"maxLastTimeUpdatedDistanceMinutes"]=unicode(emptyEVENT[u"maxLastTimeUpdatedDistanceMinutes"])

			for lDev in range(1,nOfDevicesInEvent+1):
				nDev= unicode(lDev)
				if "IPdeviceMACnumber"+nDev not in valuesDict: continue
				selectedMAC = valuesDict[u"IPdeviceMACnumber"+nDev]
				if selectedMAC == u"1" or selectedMAC == "":
					self.EVENTS[self.currentEventN][u"iDeviceName"][nDev]		= ""
					self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]	= u"0"
					self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]	= u"0"
					self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nDev]	= u"0"
					self.EVENTS[self.currentEventN][u"currentStatusAway"][nDev]	= u"0"
					self.EVENTS[self.currentEventN][u"currentStatusHome"][nDev]	= u"0"
					continue
				else:
					self.EVENTS[self.currentEventN][u"secondsOfLastON"][nDev]			= int(time.time()+20.)
					self.EVENTS[self.currentEventN][u"secondsOfLastOFF"][nDev]			= int(time.time()+20.)
					idevName = u"0" # default, dont change..


					if  self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nDev]!= selectedMAC:
						self.EVENTS[self.currentEventN][u"IPdeviceMACnumber"][nDev] = selectedMAC


					if self.iDevicesEnabled:
						if not (unicode(valuesDict[u"iDeviceName"+nDev]) =="1" or unicode(valuesDict[u"iDeviceName"+nDev]) == u"0" or unicode(valuesDict[u"iDeviceName"+nDev]) == u"-1"):
							idevD,idevName,idevId = self.getIdandName(valuesDict[u"iDeviceName"+nDev])
							self.EVENTS[self.currentEventN][u"iDeviceName"][nDev]= unicode(idevId)

							if valuesDict[u"iDeviceUseForHome"+nDev]=="":self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]	= u"0";errorDict[u"iDeviceUseForHome"]=emptyEVENT[u"iDeviceUseForHome"]
							else:										self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]	=valuesDict[u"iDeviceUseForHome"+nDev]

							if valuesDict[u"iDeviceUseForAway"+nDev]=="":self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]	= u"0";errorDict[u"iDeviceUseForAway"]=emptyEVENT[u"iDeviceUseForAway"]
							else:										self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]	=valuesDict[u"iDeviceUseForAway"+nDev]

						elif unicode(valuesDict[u"iDeviceName"+nDev]) =="1" or unicode(valuesDict[u"iDeviceName"+nDev]) =="-1":
							idevName = ""
						else:
							if valuesDict[u"iDeviceUseForHome"+nDev]=="":self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]	= u"0";errorDict[u"iDeviceUseForHome"]=emptyEVENT[u"iDeviceUseForHome"]
							else:										self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]	=valuesDict[u"iDeviceUseForHome"+nDev]

							if valuesDict[u"iDeviceUseForAway"+nDev]=="":self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]	= u"0";errorDict[u"iDeviceUseForAway"]=emptyEVENT[u"iDeviceUseForAway"]
							else:										self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]	=valuesDict[u"iDeviceUseForAway"+nDev]
						if  idevName == "" :
							self.EVENTS[self.currentEventN][u"iDeviceName"][nDev]	    = ""
							self.EVENTS[self.currentEventN][u"iDeviceUseForHome"][nDev]	=  u"0"
							self.EVENTS[self.currentEventN][u"iDeviceUseForAway"][nDev]	=  u"0"





			valuesDict[u"EVENTS"]	=	json.dumps(self.EVENTS)


			valuesDict[u"piBeacon"]	=	json.dumps(self.piBeaconDevices)
			if self.decideMyLog(u"piBeacon"): self.indiLOG.log(20,u"self.piBeaconDevices  {}".format(self.piBeaconDevices))
			if valuesDict[u"piBeaconEnabled"]: self.updatepiBeacons()

			valuesDict[u"UNIFI"]	=	    json.dumps(self.unifiDevices)
			if self.decideMyLog(u"Unifi"): self.indiLOG.log(20,u"self.unifiDevices  {}".format(self.unifiDevices))
			if valuesDict[u"unifiEnabled"]: self.updateUnifi()

			self.savePrefs = 1
		except Exception as e:
			self.exceptionHandler(40, e)
		if len(errorDict) > 0: return  valuesDict, errorDict
		return  valuesDict




########################################
	def validatePrefsConfigUi(self, valuesDict):
		try:
			self.updatePrefs =True
			rebootRequired   = False
			
			self.debugLevel			= []
			for d in _debAreas:
				if u"debug"+d in valuesDict and valuesDict[u"debug"+d]: self.debugLevel.append(d)

			self.enableBroadCastEvents  = valuesDict[u"enableBroadCastEvents"]
			if self.enableBroadCastEvents not in ["0","all","individual"]:
				self.enableBroadCastEvents  = "0"

			xx   = valuesDict[u"indigoDevicesFolderName"]
			if xx != self.indigoDevicesFolderName:
				self.indigoDevicesFolderName    = xx
				try:
					indigo.devices.folder.create(self.indigoDevicesFolderName)
					self.indiLOG.log(20,self.indigoDevicesFolderName+ u" folder created")
				except:
					pass
				self.indigoDeviceFolderID = indigo.devices.folders[self.indigoDevicesFolderName].id

			xx   = valuesDict[u"indigoVariablesFolderName"]
			if xx != self.indigoVariablesFolderName:
				self.indigoVariablesFolderName    = xx
				if self.indigoVariablesFolderName not in indigo.variables.folders:
					self.indigoVariablesFolderID=indigo.variables.folder.create(self.indigoVariablesFolderName).id
					self.indiLOG.log(20,self.indigoVariablesFolderName+ u" folder created")
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
			network = valuesDict[u"network"]
			try:    unicode(int(netwT))
			except: netwT = "24"

			if not self.isValidIP(network):
				ok = False
			else:
				ok = True


			if ok and (self.netwType != netwT or network != self.theNetwork) :
				self.quitNOW = u"new Network"
				self.theNetwork = network
				self.netwType   = netwT
				valuesDict[u"netwType"]	= self.netwType
				valuesDict[u"network"]	= self.theNetwork
				self.netwInfo			= self.IPCalculator(self.theNetwork, self.netwType)
				self.broadcastIP		= self.netwInfo[u"broadcast"]
				self.netwInfo = {u'netWorkId': u'192.168.1.0', u'broadcast': u'192.168.1.255', u'netMask': u'255.255.255.0', u'maxHosts': 254, u'hostRange': u'192.168.1.1 - 192.168.1.254'}
				self.indiLOG.log(30,u"network setings changed, will auto restart plugin in a minute  new defs: {}".format(self.netwInfo))


			error = u"no"
			if pwdis == u"yourPassword":
				self.passwordOK ="0"
				self.quitNOW = u"no password"
				self.indiLOG.log(30,u"getting password.. not entered")
			else:
				valuesDict[u"password"] = u"password is already stored"
				self.passwordOK = u"2"
				if pwdis ==  u"password is already stored":
					self.yourPassword  = self.getPWD( u"fingscanpy")
					if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"getting password.. was already in system")

				else:  ## new password entered, store and send sucess message back
					self.yourPassword = pwdis
					valuesDict[u"password"] =  u"password is already stored"
					if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"password entered(&a3reversed#5B)=" +self.yourPassword)
					self.storePWD(self.yourPassword,"fingscanpy")

			self.routerType = valuesDict[u"routerType"]
			if self.routerType != u"0":
				try:
					rtPW = valuesDict[u"routerPWD"]
					if rtPW == u"your router password here":
						self.routerPWD	= u""
						self.routerType = u"0"
					elif rtPW == u"password is already stored":
						self.routerPWD = self.getPWD(u"fingrt")
					else:
						self.routerPWD	= rtPW
						self.storePWD(rtPW,u"fingrt")
						valuesDict[u"routerPWD"] = u"password is already stored"
					self.routerUID	= valuesDict[u"routerUID"]
					self.routerIPn	= valuesDict[u"routerIPn"]
					self.badWiFiTrigger[u"minSignalDrop"]			= float(valuesDict[u"minSignalDrop"])
					self.badWiFiTrigger[u"minNumberOfDevicesBad"]	= float(valuesDict[u"minNumberOfDevicesBad"])
					self.badWiFiTrigger[u"minNumberOfSecondsBad"]	= float(valuesDict[u"minNumberOfSecondsBad"])
					self.badWiFiTrigger[u"minWiFiSignal"]			= float(valuesDict[u"minWiFiSignal"])
				except:
					self.routerType =0
					if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u" router variables not initialized, bad data entered ")
		
				self.checkWIFIinfo()
				self.checkIfBadWiFi()
				self.checkDEVICES()
			else:
				self.wifiMacList={}
				self.oldwifiMacList={}
				valuesDict[u"wifiMacList"] = ""



			if self.enableMACtoVENDORlookup != valuesDict[u"enableMACtoVENDORlookup"] and self.enableMACtoVENDORlookup == u"0":
				rebootRequired                         = True
			self.enableMACtoVENDORlookup               = valuesDict[u"enableMACtoVENDORlookup"]

			self.acceptNewDevices = valuesDict[u"acceptNewDevices"] == u"1"

	# clean up empty events
			self.cleanUpEvents()
	# save to indigo
			valuesDict[u"EVENTS"]	=	json.dumps(self.EVENTS)
			valuesDict[u"UNIFI"]	=	json.dumps(self.unifiDevices)
			valuesDict[u"piBeacon"]	=	json.dumps(self.piBeaconDevices)

			self.printWiFi()
			self.printConfig()

		except Exception as e:
			self.exceptionHandler(40, e)
		return True, valuesDict



########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, devId):
		for theMAC in self.allDeviceInfo:
			if int(self.allDeviceInfo[theMAC][u"deviceId"]) == devId:
				self.allDeviceInfo[theMAC][u"hardwareVendor"]	= valuesDict[u"setHardwareVendor"]
				self.allDeviceInfo[theMAC][u"deviceInfo"]		= valuesDict[u"setDeviceInfo"]
				self.allDeviceInfo[theMAC][u"useWakeOnLanSecs"]	= int(valuesDict[u"setuseWakeOnLan"])
				if u"useWakeOnLanLast" not in self.allDeviceInfo[theMAC]:
					self.allDeviceInfo[theMAC][u"useWakeOnLanLast"]		= 0
				self.allDeviceInfo[theMAC][u"setWiFi"]			= valuesDict[u"setWiFi"]
				self.allDeviceInfo[theMAC][u"usePing"]			= valuesDict[u"setUsePing"]
				self.allDeviceInfo[theMAC][u"exprirationTime"]	= float(valuesDict[u"setExpirationTime"])
				self.allDeviceInfo[theMAC][u"suppressChangeMSG"]	= valuesDict[u"setSuppressChangeMSG"]
				self.updateIndigoIpDeviceFromDeviceData(theMAC,[u"hardwareVendor",u"deviceInfo",u"WiFi",u"usePing",u"suppressChangeMSG"])
				self.updateIndigoIpVariableFromDeviceData(theMAC)
		return (True, valuesDict)




########################################
	def	cleanUppiBeacon(self):
	
		for nDev in self.piBeaconDevices:
			if u"used" not in self.piBeaconDevices[nDev]:
				self.piBeaconDevices[nDev][u"used"] = u"0"

########################################
	def	cleanUpUnifi(self):
	
		for nDev in self.unifiDevices:
			if u"used" not in self.unifiDevices[nDev]:
				self.unifiDevices[nDev][u"used"] = u"0"


########################################
	def	cleanUpEvents(self):
	
		try:
			
			for n in range(1,nEvents+1):
				nev= unicode(n)
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
					nDev= unicode(i)
					if nDev not in self.EVENTS[n][u"IPdeviceMACnumber"]:
						for prop in emptyEVENT:
							try:
								self.EVENTS[n][prop][nDev]		= copy.deepcopy(emptyEVENT[prop][u"1"])
							except: 
								pass                               
												
					if int(nDev) >= piBeaconStart:#  here the mac number is the indigo device # , remove it if the indigo device is gone
						if self.EVENTS[n][u"IPdeviceMACnumber"][nDev] != u"" and self.EVENTS[n][u"IPdeviceMACnumber"][nDev] != u"0":
							try:
								indigo.devices[int(self.EVENTS[n][u"IPdeviceMACnumber"][nDev])]
							except Exception as e:
								self.exceptionHandler(40, e)
								self.indiLOG.log(40, u"cleanupEVENTS:  please remove device from EVENTS as indigo device does not exist: {}".format(self.EVENTS[n][u"IPdeviceMACnumber"][nDev]) ) 
								continue
								# dont auto delete let user remove from event listing
								self.EVENTS[n][u"IPdeviceMACnumber"][nDev] = u"0"   

				
					if  int(nDev) <= piBeaconStart and int(nDev) < unifiStart:
						if self.EVENTS[n][u"IPdeviceMACnumber"][nDev] !="" and  self.EVENTS[n][u"IPdeviceMACnumber"][nDev] !="0":
							if self.EVENTS[n][u"IPdeviceMACnumber"][nDev] in self.piBeaconDevices:
								self.piBeaconDevices[self.EVENTS[n][u"IPdeviceMACnumber"][nDev]][u"used"]="1"
				
					elif int(nDev) >= unifiStart:
						if self.EVENTS[n][u"IPdeviceMACnumber"][nDev] !="" and  self.EVENTS[n][u"IPdeviceMACnumber"][nDev] !="0":
							if self.EVENTS[n][u"IPdeviceMACnumber"][nDev] in self.unifiDevices:
								self.unifiDevices[self.EVENTS[n][u"IPdeviceMACnumber"][nDev]][u"used"]="1"
				
				if self.EVENTS[n][u"distanceHomeLimit"]=="": self.EVENTS[n][u"distanceHomeLimit"]	= copy.deepcopy(emptyEVENT[u"distanceHomeLimit"])
				if self.EVENTS[n][u"distanceAwayLimit"]=="": self.EVENTS[n][u"distanceAwayLimit"]	= copy.deepcopy(emptyEVENT[u"distanceAwayLimit"])
				if self.EVENTS[n][u"minimumTimeHome"]=="":   self.EVENTS[n][u"minimumTimeHome"]	= copy.deepcopy(emptyEVENT[u"minimumTimeHome"])

			try:
				del self.EVENTS[u"0"]
			except:
				pass
			try:
				del self.EVENTS[u""]
			except:
				pass

			for nev in self.EVENTS:
				if u"0" in self.EVENTS[nev][u"IPdeviceMACnumber"]:
					del  self.EVENTS[nev][u"IPdeviceMACnumber"][u"0"]
				for lll in range(1,nOfIDevicesInEvent+1):
					lDev=unicode(lll)
					idevD,idevName,idevId = self.getIdandName(self.EVENTS[nev][u"iDeviceName"][lDev])
					self.EVENTS[nev][u"iDeviceName"][lDev]= unicode(idevId)
					
		except Exception as e:
			self.exceptionHandler(40, e)
			
########################################
	def	resetEvents(self):
		try:
			self.EVENTS = {}
			self.cleanUpEvents()
			self.pluginPrefs[u"EVENTS"]	= json.dumps(self.EVENTS)
			indigo.server.savePluginPrefs() 
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"ResetEVENTS done")
		except Exception as e:
			self.exceptionHandler(40, e)
		return
########################################
	def	resetDevices(self):
		try:
			List =[]
			for dev in indigo.devices.iter(u"com.karlwachs.fingscan"):
				#if dev.pluginId.upper().find("FINGSCAN")>-1:  # put your plugin name here
					List.append((dev.id,dev.name))
			self.indiLOG.log(30,u"deleting devices:{}".format(List))
			for devId in List:
				indigo.device.delete(devId[0])
	#		self.quitNOW = u"loading data from file after Device reset"

			if not os.path.exists(self.fingSaveFileName):
				self.writeToFile()
			else:
				shutil.copy(self.fingSaveFileName,self.fingSaveFileName+unicode(time.time()))
				
			self.doLoadDevices()


			if self.decideMyLog(u"WiFi"): self.indiLOG.log(30,u"ResetDEVICES done")
		except Exception as e:
			self.exceptionHandler(40, e)
		return

########################################
	def printEvents(self,printEvents="all"):
		try:
			if len(self.EVENTS) ==0:
				self.indiLOG.log(20,u"printEvents: no EVENT defined \n")
				return


			out ="\nEVENT defs::::::::::::::::::\n"
			eventsToPrint=[]
			if printEvents=="all":
				for i in range(1,nEvents+1):
					eventsToPrint.append(unicode(i))
			else:
				eventsToPrint.append(printEvents)
			eventsToPrint=sorted(eventsToPrint)
			
			timeNowSecs = unicode(int(time.time()))
			timeNowHMS = datetime.datetime.now().strftime("%H:%M:%S")
			
			for nEvent in eventsToPrint:
				if nEvent not in self.EVENTS: continue
				listOfDevs=[]
				evnt=self.EVENTS[nEvent]
				prntDist=False
				for nDev in evnt[u"IPdeviceMACnumber"]:
					try:
						if evnt[u"IPdeviceMACnumber"][nDev] =="": continue
						if evnt[u"IPdeviceMACnumber"][nDev] =="0": continue
						if evnt[u"iDeviceUseForHome"][nDev] =="1":prntDist=True
						listOfDevs.append(int(nDev))
					except:
						continue
				if len(listOfDevs) ==0: continue
				out+= u"EVENT:------------- "+nEvent.rjust(2)+"  --------------------------------------------------------------------------------------------------"+"\n"
				for iDev in range(1,nOfDevicesInEvent+1):
					if iDev not in listOfDevs: continue
					nDev = unicode(iDev)
					#sout+= unicode(evnt[u"IPdeviceMACnumber"]))
					try:
						theMAC = evnt[u"IPdeviceMACnumber"][nDev]
					except:
						continue
					
					if int(nDev) < piBeaconStart:
						try:
							devI = self.allDeviceInfo[theMAC]
						except: 
							out = u"{}  is not defined, please remove from event# {}".format(theMAC, nEvent)
							continue
						out+= u"dev#: {}".format(nDev).rjust(2)+u" -- devNam:"+devI[u"deviceName"].ljust(25)[:25] +u" -- MAC#:"+theMAC+u" -- ip#:"+devI[u"ipNumber"].ljust(15)+u" -- status:"+devI[u"status"].ljust(8)+u" -- WiFi:"+devI[u"WiFi"]+u"\n"
					elif int(nDev) < piBeaconStart:
						pass
					elif int(nDev) < unifiStart:  # next section is pibeacon 
						try:
							name= 	self.piBeaconDevices[theMAC][u"name"]
						except:
							self.getpiBeaconAvailable()
							self.updatepiBeacons()
							try:
								name= 	self.piBeaconDevices[theMAC][u"name"]
							except:
								out+= u" piBeacon device IndigoID# "+theMAC+ " does not exist, check you piBeacon plugin" +"\n"
								continue
						status= self.piBeaconDevices[theMAC][u"currentStatus"]
						out+= u"dev#: {}".format(nDev)+u" -- devNam:"+name.ljust(25)[:25] +u" -- IND#:"+theMAC.ljust(17)+u" --     "+u" ".ljust(15)+u" -- status:"+status.ljust(8)+u"\n"
					else:
						try:
							name= 	self.unifiDevices[theMAC][u"name"]
						except:
							self.getUnifiAvailable()
							self.updateUnifi()
							try:
								name= 	self.unifiDevices[theMAC][u"name"]
							except:
								self.indiLOG.log(40, u" unifi device IndigoID# "+theMAC+ u" does not exist, check your unifi plugin" )
								continue
						status= self.unifiDevices[theMAC][u"currentStatus"]
						out+= u"dev#: {}".format(nDev)+u" -- devNam:"+name.ljust(25)[:25] +u" -- IND#:"+theMAC.ljust(17)+u" --     "+u" ".ljust(15)+u" -- status:"+status.ljust(8)+u"\n"
					


				out+= self.printEventLine(u"currentStatusHome"	 		,u"currentStatusHome"		,nEvent,listOfDevs)
				out+= self.printEventLine(u"currentStatusAway"	 		,u"currentStatusAway"		,nEvent,listOfDevs)
				if prntDist:
					out+= self.printEventLine(u"iDeviceName"			,u"iDevice Name"				,nEvent,listOfDevs)
					out+= self.printEventLine(u"iDeviceUseForHome"		,u"iDeviceUseForHome"		,nEvent,listOfDevs)
					out+= self.printEventLine(u"iDeviceUseForAway"		,u"iDeviceUseForAway"		,nEvent,listOfDevs)
					out+= self.printEventLine(u"iDeviceAwayDistance"	,u"iDeviceCurrntAwayDist"	,nEvent,listOfDevs)
					out+= self.printEventLine("iDeviceHomeDistance"		,u"iDeviceCurrntHomeDist"	,nEvent,listOfDevs)
				out+= self.printEventLine(	u"timeOfLastOFF"			,u"time WhenLast DOWN"		,nEvent,listOfDevs)
				out+= self.printEventLine(	u"timeOfLastON"				,u"time WhenLast UP"			,nEvent,listOfDevs)
				out+= self.printEventLine(	u"secondsOfLastON"			,u"seconds WhenLast UP"		,nEvent,listOfDevs)
				out+= self.printEventLine(	u"secondsOfLastOFF"			,u"seconds WhenLast DOWN"	,nEvent,listOfDevs)
				if prntDist:
					pass
					#self.printEventLine("iDeviceInfoTimeStamp"	,"iDeviceInfoTimeStamp"		,nEvent,listOfDevs)
				out+=   	u"Time right now:          :"+timeNowHMS.rjust(12)+"\n"
				out+=   	u"ALL Devices         Home :{}".format(evnt[u"allHome"]).rjust(12)+u"  -- reacts after minTimeNotHome"+"\n"
				out+=   	u"AtLeast ONE Device  Home :{}".format(evnt[u"oneHome"]).rjust(12)+u"  -- reacts after minTimeNotHome"+"\n"
				out+=   	u"n Devices           Home :{}".format(evnt[u"nHome"]).rjust(12)  +u"  -- reacts after minTimeNotHome"+"\n"
				out+=   	u"ALL Devices         Away :{}".format(evnt[u"allAway"]).rjust(12)+u"  -- reacts minTimeAway bf Trig"+"\n"
				out+=   	u"AtLeast ONE Device  Away :{}".format(evnt[u"oneAway"]).rjust(12)+u"  -- reacts minTimeAway bf Trig"+"\n"
				out+=   	u"n Devices           Away :{}".format(evnt[u"nAway"]).rjust(12)  +u"  -- reacts minTimeAway bf Trig"+"\n"
				if prntDist:
					out+=  u"minDist.toBeAway         :{}".format(u"%5.2f"%float(evnt[u"distanceAwayLimit"])).rjust(12)+u"\n"
					out+=  u"minDist.toBeNotHome      :{}".format(u"%5.2f"%float(evnt[u"distanceHomeLimit"])).rjust(12)+u"\n"
					out+=  u"max age of dist info     :{}".format(evnt[u"maxLastTimeUpdatedDistanceMinutes"]).rjust(12)+u"\n"
				out+=      u"minTimeAway bf Trig      :{}".format(u"%5.0f"%float(evnt[u"minimumTimeAway"])).rjust(12)+u"\n"
				out+=      u"minTimeNotHome bf re-Trig:{}".format(u"%5.0f"%float(evnt[u"minimumTimeHome"])).rjust(12)+u"\n"
				out+=      u"Event enabled            :{}".format(evnt[u"enableDisable"]).rjust(12)+u"\n"
				out+=      u"dataFormat               :{}".format(evnt[u"dataFormat"]).rjust(12)+u"\n"
			self.indiLOG.log(10,out+u"\n")
		except Exception as e:
			self.exceptionHandler(40, e)
		return
########################################
	def printEventLine(self, name,nameText,nEvent,listOfDevs):
		out=""
		try:
			list ="" 
			for iDev in range(1,nOfDevicesInEvent+1):
				if iDev not in listOfDevs: continue
				nDev = unicode(iDev)
				if name == u"secondsOfLastON" or  name == u"secondsOfLastOFF" :
					list +=u"#"+nDev.rjust(2)+":{}".format( int(time.time()) - int(self.EVENTS[nEvent][name][nDev]) ).rjust(15)+"  "
				elif name == u"iDeviceName" :
					idevD,idevName,idevId = self.getIdandName(unicode(self.EVENTS[nEvent][name][nDev]))
					list +=u"#"+nDev.rjust(2)+":"+idevName.rjust(15)+"  "
				else:
					list +=u"#"+nDev.rjust(2)+":{}".format(self.EVENTS[nEvent][name][nDev]).rjust(15)+"  "
			out = (nameText+":").ljust(22) + list.strip("  ")
		except Exception as e:
			self.indiLOG.log(40, u"error in  Line '%s' ;  error='%s'" % (sys.exc_info()[2].tb_lineno, e)+"\n{}".format(self.EVENTS[nEvent]))
		return out+"\n"

#		self.indiLOG.log(10,u"<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )
########################################
	def	printWiFi(self,printWiFi=u"all"):
		out ="\n"
		try:
			if len(self.wifiMacList) ==0:
				self.indiLOG.log(20,u"printWiFi: no WiFi devices defined")
				return
			if self.routerType !=0:
				self.updateDeviceWiFiSignal()
				out+= u"WiFi info router type:"+ self.routerType + "-- IP#/page: "+self.routerIPn+"   .....ACTIVE Wifi device list:" + "\n"
				out+= u"---- MAC # ------ ---- device Name ----- ------ ip# ----- -WiFi- -Signal- -aveSign -Associated Authorized" + "\n"
				self.printWiFiDevs(u"5GHz",Header=True)
				self.printWiFiDevs(u"2GHz")
				self.printWiFiDevs("")
				out+= u"\n"
				out+= self.printWiFiAve(u"2GHz",Header=True)
				out+= self.printWiFiAve(u"5GHz")
				out+= u"\n"
				out+= u"settings for badWiFiSignalTrigger "+ u"\n"
				out+= u" minNumberOfSecondsBad: %5.1f"%(self.badWiFiTrigger[u"minNumberOfSecondsBad"])+ u"\n"
				out+= u" minNumberOfDevicesBad: %5.1f"%(self.badWiFiTrigger[u"minNumberOfDevicesBad"])+ u"\n"
				out+= u" minSignalDrop:         %5.1f"%(self.badWiFiTrigger[u"minSignalDrop"])+ u"\n"
				out+= u" minWiFiSignal:         %5.1f"%(self.badWiFiTrigger[u"minWiFiSignal"])+ u"\n"
				out+= u"-------------------------------------------------------------------------------------------------------- "+ "\n"
				self.indiLOG.log(10,out)
		except Exception as e:
			self.exceptionHandler(40, e)

		return
########################################
	def printpiBeaconDevs(self):
		try:
			## refresh piBeacon cokkies
			self.getpiBeaconAvailable()
			if len(self.piBeaconDevices) ==0: return
			out = u"\n"
			
			out+= u"===      piBeacon devices  available  to fingscan    ===        START"+"\n"
			#				 123456789012345678901234567890123412345678123456789012
			out+= u"--Device Name------        indigoID--    --Status  lastUpdate  used"+"\n"
			list=[]
			for theMAC in self.piBeaconDevices:
				list.append((theMAC,self.piBeaconDevices[theMAC][u"name"]))
			list = sorted(list, key=lambda tup: tup[1])
			for ii in range(len(list)):
				theMAC = list[ii][0]
				if theMAC in self.piBeaconDevices:
					try:
						theString = self.piBeaconDevices[theMAC][u"name"].ljust(27)
						theString+= theMAC.ljust(14)
						theString+= self.piBeaconDevices[theMAC][u"currentStatus"].rjust(8)
						lastUpdate= datetime.datetime.fromtimestamp(self.piBeaconDevices[theMAC][u"lastUpdate"]).strftime('%H:%M:%S')
						theString+= unicode(lastUpdate).rjust(12)
						theString+= self.piBeaconDevices[theMAC][u"used"].rjust(6)
					
						out+= theString + u"\n"
					except:
						self.indiLOG.log(40, u" data wrong for {}".format(theMAC) +"    {}".format(self.piBeaconDevices))
			out+= u"===      piBeacon devices  available  to fingscan    ===        END"+"\n"
			self.indiLOG.log(10,out)
	
		except Exception as e:
			self.exceptionHandler(40, e)

########################################
	def printUnifiDevs(self):
		try:
			## refresh piBeacon cokkies
			self.getUnifiAvailable()
			if len(self.unifiDevices) ==0: return
			out = u"\n"
			out+= u"===      Unifi   devices  available  to fingscan    ===        START"+"\n"
			#				 123456789012345678901234567890123412345678123456789012
			out+= u"--Device Name------        indigoID--    --Status  lastUpdate  used"+"\n"
			list=[]
			for theMAC in self.unifiDevices:
				list.append((theMAC,self.unifiDevices[theMAC][u"name"]))
			list = sorted(list, key=lambda tup: tup[1])
			for ii in range(len(list)):
				theMAC = list[ii][0]
				if theMAC in self.unifiDevices:
					try:
						theString = self.unifiDevices[theMAC][u"name"].ljust(27)
						theString+= theMAC.ljust(14)
						theString+= self.unifiDevices[theMAC][u"currentStatus"].rjust(8)
						lastUpdate= datetime.datetime.fromtimestamp(self.unifiDevices[theMAC][u"lastUpdate"]).strftime(u'%H:%M:%S')
						theString+= unicode(lastUpdate).rjust(12)
						theString+= self.unifiDevices[theMAC][u"used"].rjust(6)
						out+= theString + u"\n"
						
					except Exception as e:
						self.exceptionHandler(40, e)
						self.indiLOG.log(40, u" data wrong for {}".format(theMAC) +"    {}".format(self.unifiDevices[theMAC]))
			out+= u"===      unifi devices  available  to fingscan    ===        END"
			self.indiLOG.log(10,out)
	
		except Exception as e:
			self.exceptionHandler(40, e)


########################################
	def printWiFiDevs(self, ghz,Header=False):
		out =""
		try:
			for theMAC in self.wifiMacList:
				if theMAC in self.allDeviceInfo:
					devI=self.allDeviceInfo[theMAC]
					if devI[u"WiFi"] != ghz: continue
					theString = theMAC
					theString+= u" "		+devI[u"deviceName"].ljust(22)
					theString+= u" "		+devI[u"ipNumber"].ljust(17)
					theString+= u" "		+devI[u"WiFi"].ljust(4)
					try:
						theString+= u"  %7.0f"%(self.wifiMacList[theMAC][2])
					except:
						theString+= u"  {}".format(self.wifiMacList[theMAC][2]).ljust(7)
					try:
						theString+= u"   %7.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))
					except:
						theString+= u"   0      "
					theString+= u"  "	+self.wifiMacList[theMAC][0].rjust(7)
					theString+= u"    "	+self.wifiMacList[theMAC][1].rjust(7)
					if devI[u"deviceName"].find(u"unidentifiedWiFiDevice") > -1:
						theString += u" some times devices with wifi AND ethernet show this behaviour"
					out+= theString+u"\n"
				else:
					out+= theMAC+u" -device is expired, not in dev list any more- {}".format(self.wifiMacList[theMAC]) +u" some times devices with wifi AND ethernet show this behaviour"+"\n"
		except Exception as e:
			self.exceptionHandler(40, e)
		return out
########################################
	def printWiFiAve(self, ghz,Header=False):
		out=""
		try:
			if Header: out+=u"overall WiFi stats:"+"\n"
			out+= u" "+ghz+u": ave.Signal[dBm]%4.0f,  curr.Signal:%4.0f,  NumberOfMeasurements:%6.0f,  NumberOfCycles:%6.0f, ave.NumberofDevices:%2.0f, curr.NumberOfDevicesConnected:%2.0f,  noiseLevel: %s"\
				%( (self.wifiMacAv[u"sumSignal"][ghz]/max(1.0,self.wifiMacAv[u"numberOfDevices"][ghz]))
				 , self.wifiMacAv[u"curAvSignal"][ghz]
				 , self.wifiMacAv[u"numberOfDevices"][ghz]
				 , self.wifiMacAv[u"numberOfCycles"][ghz]
				 , self.wifiMacAv[u"numberOfDevices"][ghz]/max(1.0,self.wifiMacAv[u"numberOfCycles"][ghz])
				 , self.wifiMacAv[u"curDev"][ghz]
				 , self.wifiMacAv[u"noiseLevel"][ghz])
				 
		except Exception as e:
			self.exceptionHandler(40, e)
		return out+"\n"
		

##### execute triggers:

######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

	def triggerStartProcessing(self, trigger):
#		if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )iDeviceHomeDistance
		self.triggerList.append(trigger.id)
#		if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"exiting triggerStartProcessing -->>")

	def triggerStopProcessing(self, trigger):
#		if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"<<-- entering triggerStopProcessing: %s (%d)" % (trigger.name, trigger.id))
		if trigger.id in self.triggerList:
#			if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"TRIGGER FOUND")
			self.triggerList.remove(trigger.id)
#		if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"exiting triggerStopProcessing -->>")

	#def triggerUpdated(self, origDev, newDev):
	#	self.logger.log(4, u"<<-- entering triggerUpdated: %s" % origDev.name)
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

	def triggerEvent(self, eventId):
		try:
			if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"triggerEvent: %s " % eventId)
			for trigId in self.triggerList:
				trigger = indigo.triggers[trigId]
				if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"testing trigger id: {}".format(trigId).rjust(12)+u"; eventId:{}".format(eventId).rjust(12)+";  {}".format(trigger.pluginTypeId))
				if trigger.pluginTypeId == eventId:
					if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"firing trigger id : {}".format(trigId))
					indigo.trigger.execute(trigger)
		except Exception as e:
			self.exceptionHandler(40, e)
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
		except Exception as e:
			self.exceptionHandler(40, e)

########################################
	def getPWD(self,name):
		try:
			## get pwd from keychain
			ret, storePassword = self.readPopen([u"security",u"find-generic-password",u"-gl",name])
			if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"password entered (&a3reversed#5B)=" +unicode(storePassword))
			try:
				storePassword.index("password")  # if the return text contains "password" its ok, continue
				storePassword= unicode(storePassword).split('"')[1]
				return storePassword[3:-3][::-1] ## 1. drop fist and last 3 characaters, then reverse string
			except:  # bad return, no password stored, return "0"
				return "0"
		except Exception as e:
			self.exceptionHandler(40, e)


########################################
	def inpDummy(self):
		return
########################################
########################################
	def pickDeviceCALLBACK(self,valuesDict,typeId):
		devId=int(valuesDict[u"device"])
		if devId >0:
			dev =indigo.devices[devId]
			devName= dev.name
			if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u" device selected:{}".format(devId)+"/"+devName)
		else:
			if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u" device selected:"+ " all")
			
		return True
########################################
	def pickDeviceFilter(self,filter=None,valuesDict=None,typeId=0):
		retList =[]
		for dev in indigo.devices.iter("com.karlwachs.fingscan"):
#			if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,dev.pluginId+" "+dev.name)
			#if dev.pluginId.upper().find("FINGSCAN")>-1:  # put your plugin name here
#				if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u" adding "+dev.name)
				retList.append((dev.id,dev.name))
		retList.append((0,u"all devices"))
		return retList
########################################
	def triggerEventCALLBACK(self,valuesDict,typeId):
		self.indiLOG.log(10,u"received trigger event from menu: {}".format(valuesDict))
		self.triggerEvent(valuesDict[u"triggerEvent"])
		return



########### menue in and out ###########
	def getMenuActionConfigUiValues(self, menuId):
		#indigo.server.log(u'Called getMenuActionConfigUiValues(self, menuId):')
		#indigo.server.log(u'     (' + unicode(menuId) + u')')

		valuesDict = indigo.Dict()
		valuesDict[u"selectEvent"] = u"0"  
		errorMsgDict = indigo.Dict()
		return (valuesDict, errorMsgDict)
########################################
	def inpPrintEVENTS(self):
		self.indigoCommand = u"PrintEVENTS"
		self.indiLOG.log(10,u"command: Print EVENTS and configuration")
		return

########################################
	def inpPrintWiFi(self):
		self.indigoCommand = u"PrintWiFi"
		self.indiLOG.log(10,u"command: Print WiFi information and configuration")
		return
########################################
	def inpPrintpiBeacon(self):
		self.indigoCommand = u"PrintpiBeacon"
		self.indiLOG.log(10,u"command: Print piBeacon information")
		return
########################################
	def inpPrintUnifi(self):
		self.indigoCommand = u"PrintUnifi"
		self.indiLOG.log(10,u"command: Print unifi information")
		return


########################################
	def inpResetEVENTS(self):
		self.indigoCommand = u"ResetEVENTS"
		self.indiLOG.log(10,u"command: ResetEVENTS")
		return
########################################
	def inpResetDEVICES(self):
		self.indigoCommand = u"ResetDEVICES"
		self.indiLOG.log(10,u"command: ResetDEVICES")
		return
########################################  not used anymore
	def inpEVENTAway1(self):
		self.indigoCommand = u"EVENT_Away_1"
		self.indiLOG.log(10,u"command: EVENT_Away_1")
		return
########################################  not used anymore
	def inpEVENTHome1(self):
		self.indigoCommand = u"EVENT_Home_1"
		self.indiLOG.log(10,u"command: EVENT_Home_1")
		return

########################################
	def inpSaveData(self):
		self.indigoCommand = u"save"
		self.indiLOG.log(10,u"command: save")
		retCode = self.writeToFile()
		self.indigoCommand = u"none"
		self.indiLOG.log(10,u"save done")
		return
		

########################################
	def inpLoadDevices(self):
		self.indigoCommand = u"loadDevices"
		self.indiLOG.log(10,u"command: loadDevices")
		return


########################################
	def inpSortData(self):
		self.indigoCommand = u"sort"
		self.indiLOG.log(10,u"command: sort")
		return

########################################
	def inpDetails(self):
		self.indigoCommand = u"details"
		self.indiLOG.log(10,u"command: log IP-Services of your network")
		return

########################################
	def inpSoftrestart(self):
		self.quitNOW = u"softrestart"
		self.indiLOG.log(10,u"command: softrestart")
		return


########################################


########################################
	def doLoadDevices(self):
		try:
			retcode = self.deleteIndigoIpDevicesData(u"all")
			self.sleep(1)
			retCode= self.readFromFile()
			self.sleep(1)
			retCode = self.getIndigoIpVariablesIntoData()
			self.sleep(1)
			retCode = self.updateallDeviceInfofromVariable()
			self.sleep(1)
			retcode = self.updateAllIndigoIpDeviceFromDeviceData()
			self.sleep(1)
			self.indiLOG.log(10,u"       restore done")
		except Exception as e:
			self.exceptionHandler(40, e)
		return


########################################
	def doSortData(self):
		self.indiLOG.log(10,u"sorting ipDevices with IP Numbers")
		retCode = self.getIndigoIpVariablesIntoData()
		retCode = self.sortIndigoIndex()
		retCode = self.getIndigoIpVariablesIntoData()
		self.indiLOG.log(10,u" sorting  done")
		return

########################################
	def doDetails(self):

		self.indiLOG.log(10,u"starting log IP-Services of your network, might take several minutes, it will test each port on each ip-device, output to plugin.log and:{}".format(self.fingServicesOutputFileName))
		## ask fing to produce details list of services per ip number
		ret=""
## cd '/Library/Application Support/Perceptive Automation/Indigo 7.4/Preferences/Plugins/com.karlwachs.fingscan/';echo 'your osx password here.. no quotes' | sudo -S /usr/local/bin/fing  -s 192.168.1.0/24 -o json,fingservices.json > fingservices.log
		try:

			cmd ="echo '" +self.yourPassword + "' | sudo -S /bin/rm '"+self.fingServicesFileName+"'"
			ret, err = self.readPopen(cmd)
			if self.decideMyLog(u"Special"): self.indiLOG.log(20,u" del cmd: {}, ret: {}- {}".format(cmd, ret, err) )
			if self.opsys >= 10.15:
				cmd ="cd '"+self.indigoPreferencesPluginDir+"';echo '"+self.yourPassword+"' | sudo -S "+self.fingEXEpath+"  -s "+self.theNetwork+"/{}".format(self.netwType)+" -o json > "+self.fingServicesFileName0
			else:
				cmd ="cd '"+self.indigoPreferencesPluginDir+"';echo '"+self.yourPassword+"' | sudo -S "+self.fingEXEpath+"  -s "+self.theNetwork+"/{}".format(self.netwType)+" -o json,"+self.fingServicesFileName0+" > "+self.fingServicesLOGFileName0
		

			self.indiLOG.log(20,u"fing network scan: "+self.theNetwork+u"/{}".format(self.netwType))
			if self.decideMyLog(u"Special"): self.indiLOG.log(20,u"fing under opsys: {} command: {}".format(self.opsys, cmd) )
			ret, err = self.readPopen(cmd)
			

		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, u"  fing details failed: fing returned an error: {}- err".format(ret, err))
			return

		## read fing output file
		fingOut = ""
		try:
			f = open(self.fingServicesFileName,"r")
			fingOut = f.read()
			f.close()
			#self.indiLOG.log(20, u"  json fingOut {}".format(fingOut))
			if fingOut.find("> Service scan starting.") > -1:
				ff = fingOut.find("\n[") 
				fingOut = fingOut[ff+1:]
		except Exception as e:
			self.indiLOG.log(40, u"  fing details failed , output file: {}".format(fingOut))
			self.exceptionHandler(40, e)
			return
			
		## now get the list into theServices
		try:
		
			self.theServices=json.loads(fingOut.replace(",},","},").replace("},]","}]").replace("':",'":').replace(":'",':"').replace("','",'","').replace("{'",'{"').replace("'}",'"}'))
			#self.theServices=json.loads(fingOut.replace("'",'"').replace(",},","},").replace("},]","}]"))  ## this replaces ' with " and removes comas:  ,} and },], json does not like these empty fields
#			self.indiLOG.log(10,u"  {}".format(self.theServices[6]))
		except:
			self.indiLOG.log(40, u"  fing details failed: json command went wrong ")
			self.indiLOG.log(40, unicode(fingOut))
			return
		
		retCode = self.getIndigoIpVariablesIntoData()  ## refresh indigo data

		out =""
		out+="IP-Device Number, Name, Vendor,.."+u"IP-Device port scan on  "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

##self.fingServicesOutputFileName
####
# now put the results into the logfile
		theLength1 = len(self.theServices)
		macIndex=[]
		for ii in range(0,theLength1):
			ipNo =unicode(self.theServices[ii][u"Address"])
				
			scanResult =unicode(self.theServices[ii][u"ScanResult"])
			## have all indexes , merge indigo and fing info
			
			if scanResult !=u"OK": continue
			try:
				theMAC =unicode(self.theServices[ii][u"HardwareAddress"])
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
			out+=u"IP-Device Number, Name, Vendor,..."+"------------------------------------------------------------------------ "+"\n"
			theLength2 = len(self.theServices[ii][u"Services"])
			if theLength2 >0:
				out+=u"IP-Device Number, Name, Vendor,..."+ self.theServices[ii][u"Address"].ljust(17)+theMAC+u" "+self.theServices[ii][u"Hostname"].ljust(24)+nickname.ljust(35)+u"firewall:" + unicode(self.theServices[ii][u"FirewallDetected"])+u"\n"
				for kk in range(0,theLength2):
					out+=u"..... service Port, Name, Comment:" +u"    {}".format(self.theServices[ii][u"Services"][kk][u"Port"]).ljust(7)+ unicode(self.theServices[ii][u"Services"][kk][u"Name"]).ljust(18)	+unicode(self.theServices[ii][u"Services"][kk][u"Description"])+u"\n"
			else:
				out+= u"IP-Device Number, Name, Vendor,..."+self.theServices[ii][u"Address"].ljust(17)+theMAC+" "+self.theServices[ii][u"Hostname"].ljust(24)+nickname.ljust(35)+u"firewall:" + unicode(self.theServices[ii][u"FirewallDetected"])+u"\n"
				out+= u"..... service Port, Name, Comment:" +u"    "+ u"00000  Port Responding   No Answer from Device"+u"\n"
	
# not found in fing scan use indigo data only
		out+= u"IP-Device Number, Name, Vendor,..."+u"------------------------------------------------------------------------ "+"\n"
		out+= u"IP-Device Number, Name, Vendor,..."+u"no FING info for devices: "+"\n"
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
				if n3 == u"-":n3=""
				nickname= (n1+u" "+n2+u" "+n3)
				out+= u"IP-Device Number, Name, Vendor,..."+ devI[u"ipNumber"].ljust(17)+theMAC.ljust(19)+n4.ljust(17)+nickname+u"\n"
		out+= u"IP-Device Number, Name, Vendor,..."+u"------------------------------------------------------------------------ "
		self.indiLOG.log(10,out+u"         log IP-Services of your network, .......  done")
		fout=open(self.fingServicesOutputFileName,"w")
		fout.write(out.encode("utf8"))
		fout.close()
		return
	
	
########################################
	def writeToFile(self):
		
		self.indiLOG.log(10,u"saving indigo data to file")
		f = open ( self.fingSaveFileName , u"w")
		nwrite= min( len(self.indigoDevicesNumbers),self.indigoNumberOfdevices )
		for kk in range(nwrite):
				writestring = unicode(self.indigoDevicesNumbers[kk] )+u";"+self.indigoDevicesValues[kk]+u"\n"
				f.write(writestring.encode("utf8"))
		f.close()
		self.indiLOG.log(10,u" saved")
		
		return 0


########################################
	def readFromFile(self):
		self.indiLOG.log(10,u"restore indigo data from file")
		f= open ( self.fingSaveFileName , u"r")
		lastD=0
		self.indigoDevicesNumbers = []
		for line in f.readlines():
			ipDevNumber = line[:2]
			if len(ipDevNumber) >1 :
				lastD+=1
				kk00=self.int2hexFor2Digit(lastD)
				self.indigoDevicesNumbers.append(kk00)

				self.indiLOG.log(10,u" create re-store indigo data from file")
				try:
					test = indigo.variable.updateValue(u"ipDevice"+kk00,line[3:])
					self.indiLOG.log(10,u" updated variable:"+kk00 )
				except:
					test = indigo.variable.create(u"ipDevice"+kk00,line[3:],folder=self.indigoVariablesFolderID)
					self.indiLOG.log(10,u" created variable:"+kk00+u" folder:{}".format(self.indigoVariablesFolderID))
		f.close()
		test = indigo.variable.updateValue(u"ipDevsNoOfDevices",unicode(lastD))
		
		for kk in range(lastD,indigoMaxDevices):
			kk00 = self.int2hexFor2Digit(kk+1)						# make it 01 02 ..09 10 11 ..99
			try:
				indigo.variable.delete(u"ipDevice"+kk00)  # delete any entry > # of devices
			except:
				pass
		
#		self.indiLOG.log(10,u"  restored")
		
		return 0
	
########################################
	def int2hexFor2Digit(self,numberIn):
		if numberIn < 10: return u"0{}".format(numberIn)
		if numberIn <100: return unicode(numberIn)
		nMod = unicode(numberIn%100)
		if len(nMod) <2: nMod = u"0"+nMod  # 105 ==> A05; 115 ==> A15 205 ==> B05;  215 ==> B15
		x = numberIn//100
		if x ==1: return u"A"+nMod
		if x ==2: return u"B"+nMod
		if x ==3: return u"C"+nMod
		if x ==4: return u"D"+nMod
		if x ==5: return u"E"+nMod
		return u"F"+nMod


########################################
	def getIgnoredMAC(self):
		self.ignoredMAC ={}
		try:
			f = open (self.ignoredMACFile , "r")
			xx =json.loads(f.read())
			f.close()
			# now make it all upper case
			for mm in xx:
				self.ignoredMAC[mm.upper()] = 1
		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, u"getIgnoredMAC file read:{}".format(xx))
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
			self.indiLOG.log(10,self.indigoDevicesFolderName+ u" folder created")
		except:
			pass
		self.indigoDeviceFolderID = indigo.devices.folders[self.indigoDevicesFolderName].id
		self.pluginPrefs[u"indigoDeviceFolderID"] = self.indigoDeviceFolderID


		self.indigoVariablesFolderName = self.pluginPrefs.get(u"indigoVariablesFolderName", u"IP devices")
		if len(self.indigoVariablesFolderName) < 2: self.indigoVariablesFolderName  = u"IP devices"
		if self.indigoVariablesFolderName not in indigo.variables.folders:
			self.indigoVariablesFolderID=indigo.variables.folder.create(self.indigoVariablesFolderName).id
			self.indiLOG.log(10,self.indigoVariablesFolderName+ u" folder created")
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

		self.indiLOG.log(10,u"indigo variables initialized" )


		return 0
	
	
	
########################################
	def initFing(self, restartFing):
		try:
			if self.passwordOK != u"2": return -1
			self.fingRestartCount +=1

			if self.fingRestartCount > 5:  # starts # 1
				self.indiLOG.log(30,u"  (re)started FING 5 times, quiting ... reloading the plugin ")
				self.quitNOW = u"FING problem"
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
				retCode = self.killFing(u"all")
			else:
				pids, parentPids = self.testFing()
				if len(pids) == 1 : return 1
				if len(pids) > 1 :
					retCode = self.killFing(u"onlyParents")
					return 1

 
			# start fing, send to background, dont wait, create 2 output files:  one table format file and one logfile
			if self.decideMyLog(u"StartFi"):	deblevelForStartFing = 20
			else:								deblevelForStartFing = 0
			
			params =  {"ppp":"&a3"+self.yourPassword[::-1]+"#5B", "theNetwork":self.theNetwork, "netwType":self.netwType,"logLevel": deblevelForStartFing, "fingEXEpath":self.fingEXEpath,"macUser":self.MACuserName, "pythonPath":self.pythonPath}
			f = open(self.indigoPreferencesPluginDir+"paramsForStart","w")
			f.write(json.dumps(params))
			f.close()
			cmd = u"'{}' '{}startfing.py' '{}paramsForStart'  &".format(self.pythonPath, self.pathToPlugin, self.indigoPreferencesPluginDir)

			if self.decideMyLog(u"StartFi"): self.indiLOG.log(20,u"FING cmd= {}".format(cmd) )
			os.system(cmd)
			self.sleep( 1 )
			self.killFing(u"onlyParents")

			self.indiLOG.log(20,u"Waiting for first data from FING")

			found = False
			for ii in range(5):
				for kk in range(20):
					self.sleep( 1 )
				try:	gtime = os.path.getmtime(self.fingDataFileName)
				except: continue
				self.indiLOG.log(20,u"Checking if FING created output, old timeStamp:{}; new timeStamp:{}".format(dataFileTimeOld, gtime) )
				if dataFileTimeOld != os.path.getmtime(self.fingDataFileName):
					found = True
					self.indiLOG.log(20,u"Initializing ..  FING created new data   waiting ~ 1 minute for stable operation")
					break
			if not found: 
				self.indiLOG.log(20,u"Initializing .. FING data file not created, return")
				return 0

		
			#test if it is actually running
			pids, parentPids = self.testFing()
			self.indiLOG.log(20,u"FING Pids active after step3 = {}".format(pids))
			if len(pids) > 0:
				self.indiLOG.log(20,u"  (re)started FING, initialized")
				return 1

			self.indiLOG.log(30,u"  (re)start FING not successful ")

			return 0 #  not successful
		except Exception as e:
			self.exceptionHandler(40, e)
	
	
	
	
	
	
########################################
	def killFing(self,whomToKill):
		# all="all": kill fing and parents, if not just parents

		pids, parentPids = self.testFing()

		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"  killing FING Processes pids   " +whomToKill + " - " +unicode(pids))
		
		lenPid = len(pids)
		lenPidP = len(parentPids)

		pidsToKill =" "
		for kk in range (lenPidP):
			if parentPids[kk] != u"1": pidsToKill += u" "+parentPids[kk]
		
		if whomToKill ==  u"all":
			for kk in range(lenPid):
				if pids[kk] != u"1": pidsToKill += u" "+pids[kk]


		if pidsToKill != " ":
			cmd = "echo '" + self.yourPassword + "' | sudo -S /bin/kill -9 " + pidsToKill +" > /dev/null 2>&1 &"
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"  FING kill cmd:" + cmd)
			ret, err = self.readPopen(cmd)
			#if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"  FING kill ret= " +  unicode(ret))
			self.sleep(1)

		# check if successfull killed,  ps ... should return nothing
		pids, parentPids = self.testFing()
		if len(pids) >0:
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"  FING still running,  pids = " +  unicode(pids)+u"--{}".format(parentPids))
			return 0
		return 1
		
		
########################################
	def killPing(self,whomToKill, ipnumber=u"0.0.0.0"):
		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"killing ping jobs: {}".format(whomToKill))
		
		if whomToKill == u"all":
			for theMAC in self.pingJobs:
				pid = self.pingJobs[theMAC]
				if int(pid) < 10 : continue
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"killing PID: {} - {}".format(theMAC, pid))
				ret, err = self.readPopen("/bin/kill {}".format(pid))
				self.pingJobs[theMAC] =-1

			ret, err = self.readPopen("ps -ef | grep 'do /sbin/ping' | grep -v grep | awk '{print$2}'")
			pids =ret.split()
				
			for pid  in pids:
				if int(pid) < 10: continue
				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"killing PID: {}".format(pid))
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
					if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"killing : "+whomToKill +"-" +unicode(pid))
					ret, err = self.readPopen("/bin/kill {}".format(pid))
					self.pingJobs[whomToKill] =-1
			if ipnumber != u"0.0.0.0":
				try:
					fname= ipnumber.split(u".")[3]
					os.remove("{}pings/{}.ping".format(self.indigoPreferencesPluginDir, fname))
				except:
					pass

		return
		
########################################
	def killPGM(self,whomToKill):
		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"killing pgm: {}".format(whomToKill))

		ret, err = self.readPopen("ps -ef | grep '{}' | grep -v grep | awk '{{print$2}}'".format(whomToKill))
		pids =ret.split()
			
		for pid  in pids:
			if int(pid) < 10: continue
			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"killing PID: {}".format(pid))
			ret, err = self.readPopen( "echo '{}' | sudo -S /bin/kill -9 {}".format(self.yourPassword, pid))
		return 	
		
########################################
	def testFing(self):
		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"testing if FING is running ")


		ret, err = self.readPopen("ps -ef | grep fing.bin | grep -v grep | grep -v fingscan| grep -v Indigo | awk '{print$2,$3}'")
		pids =ret.strip(u"\n")
		pids = pids.split(u"\n")
		fingPids=[]
		parentPids=[]
		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"  FING running pids2= ".format(pids))
		
		for kk in range(len(pids)):
			p = pids[kk].split(u" ")
			if len(p)==0: continue
			fingPids.append(p[0])
			if len(p)!=2: continue
			if p[1] == u"1": continue
			if p[1] == u"0": continue
			if p[1] == u" ": continue
			parentPids.append(p[1])
			# pids has the process ids #  of fing and parent shell as simple string have removed PID # 1 = the root
		return fingPids, parentPids
	
	
	
	
########################################
	def getfingLog(self):
		## get size of finglog file to check if there is new data
		try:
			if not os.path.isfile(self.fingLogFileName): return 
			self.fingLogFileSizeNEW = int(os.path.getsize(self.fingLogFileName))
			if  self.decideMyLog(u"Logic"): 
				if self.fingLogFileSizeold == self.fingLogFileSizeNEW:
					self.indiLOG.log(20,u"  FING LOG data ==> no change  file size: {}".format(self.fingLogFileSizeNEW))
			if self.fingLogFileSizeold != self.fingLogFileSizeNEW:
				self.fingLogFileSizeold = self.fingLogFileSizeNEW
				if  self.decideMyLog(u"Logic"): 
					self.indiLOG.log(20,u"  FING LOG data ==> changed    file size: {}".format(self.fingLogFileSizeNEW))
			
			## get last line of finglog file

				lines, err = self.readPopen(["tail", "-1", self.fingLogFileName])
				self.fingData =[ line.split(u";") for line in lines ]
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
					if self.fingMACNumbers[kk] in self.inbetweenPing:	# if this is listed as down in inbetween pings, remove as we have new info.
						if self.fingStatus[kk] == u"up":
							del self.inbetweenPing[self.fingMACNumbers[kk]]

					if self.fingStatus[kk] == u"down":
						theMAC = self.fingMACNumbers[kk]
						if theMAC in self.allDeviceInfo and self.allDeviceInfo[theMAC][u"useWakeOnLanSecs"] > 0:  
							if self.sendWakewOnLanAndPing(theMAC,nBC= 2, waitForPing=500, countPings=2, waitBeforePing = 0.5, waitAfterPing = 0.1, calledFrom="getfingLog") ==0:
								self.fingStatus[kk] == u"up"

					self.fingDate[kk] =self.fingDate[kk].replace(u"/",u"-")
				return 1
			else:
				return 0
		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40,u"{}".format(self.fingData))
			self.finglogerrorCount +=1
			if self.finglogerrorCount > 40 and self.totalLoopCounter > 100 :
				self.indiLOG.log(40,u"fing.log file does not exist or is empty \n    trying to stop and restart fing  " )
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
					self.fingDate[kk] =self.fingDate[kk].replace(u"/",u"-")

					if self.fingStatus[kk] == u"down" and len(self.fingDate[kk]) > 5:
						if theMAC in self.allDeviceInfo: 
							if u"useWakeOnLanSecs" in self.allDeviceInfo[theMAC]:
								if self.allDeviceInfo[theMAC][u"useWakeOnLanSecs"] > 0:  
									if self.sendWakewOnLanAndPing(theMAC,nBC= 1, waitForPing=500, countPings=1, waitBeforePing = 0.2, waitAfterPing = 0.0, calledFrom="getfingData") ==0:
										self.fingStatus[kk] == u"up"
										self.fingDate[kk] = nowdate.strftime(u"%Y-%m-%d %H:%M:%S")
							else:
								self.indiLOG.log(30,u"error: useWakeOnLanSecs not in devI for MAC#:"+ theMAC+" devI=\n{}".format(self.allDeviceInfo[theMAC])) 
								
						deltaseconds = (  nowdate - datetime.datetime.strptime(self.fingDate[kk],u"%Y-%m-%d %H:%M:%S")  ).total_seconds() 
						if deltaseconds > 70 : 
							removeMAC.append(kk)
							#self.indiLOG.log(20,u"down > 70 secs for "+ self.fingMACNumbers[kk] +"  {}".format(deltaseconds)) 

				for kk in removeMAC[::-1]:
					del self.fingVendor[kk]
					del self.fingIPNumbers [kk]
					del self.fingStatus[kk]
					del self.fingDate[kk]
					del self.fingDeviceInfo[kk]
					del self.fingMACNumbers[kk]
				self.fingNumberOfdevices = len(self.fingVendor) 
				 
				return 1
		except Exception as e:
			self.exceptionHandler(40, e)
			self.fingDataErrorCount +=1
			if self.fingDataErrorCount > 1 :
				self.indiLOG.log(30,u"fing.data file does not exist \n    trying {}".format(5-self.fingDataErrorCount)+u" more times")
				if self.fingDataErrorCount == 5:
					self.indiLOG.log(30,u"   trying to stop and restart fing  " )
					self.initFing(1)  # restarting fing
					self.indiLOG.log(30,u"   restarted fing  " )
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
			self.indiLOG.log(40, u" ERROR:  FING message -- network is not working  codes  0/0 hosts .. error codes:   " + unicode(fingOK1) + unicode(fingOK2) )
			if self.fingDataErrorCount2 > 1:
				self.indiLOG.log(40, u"  relaunching plugin")
				self.quitNOW = u"FING problem 2"
		else:
			self.fingDataErrorCount2 =0
		

		return fingOK1 +  fingOK2
	
########################################
	def checkIndigoVersion(self):

		try:  ## test if any data and if version 2, if yes, return
			theTest = indigo.variables[u"ipDevice01"]
			theTest = theTest.value
			if len (theTest) < 5:  # variable exists, but empty or too short  should be 8 or 9
				self.quitNOW = u"Indigo variable error 1"
				self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice01 \n    please check if it has bad data, in doubt delete and let the program recreate  \n    stopping fingscan " )
				return 1
			theValue = theTest.split(u";")
			if theValue[0].strip().count(u":") == 5:
				test = self.getIndigoIpVariablesIntoData()
				return 0  ## version 2 nothing to do
		except Exception as exc:
			return ## no data nothing to do


		## this must be version 1  we have to convert the data

		for ii in range(1,indigoMaxDevices):
			ii00 = self.int2hexFor2Digit(ii)
			skip = 0
			try:
				theTest = indigo.variables[u"ipDevice"+ii00]
				skip = 1
				theTest = theTest.value
				if len (theTest) < 5:  # that is minimum, should be 8 or 9
					skip = 1
					self.quitNOW = u"Indigo variable error 2"
					self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice" + ii00 +u"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				theValue = theTest.split(";")
				macNO = theValue[1].strip()
				if macNO.count(":") != 5:
					self.quitNOW = u"Indigo variable error 3"
					self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice" + ii00  +u"\n  MAC number does not seem to be real MAC number" + theValue[0].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				ipNO =theValue[2].strip()
				if ipNO.count(".") != 3:
					self.quitNOW = u"Indigo variable error 4"
					self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice" + ii00 +u"\n  IP number does not seem to be real IP number" + theValue[1].strip() +"\n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan  " )
					break
				nick  = self.padNickName(theValue[0].strip())
				macNO = self.padMAC(macNO)
				ipNO  = self.padIP(ipNO)
				vend  = self.padVendor(theValue[3].strip())
				stat  = theValue[4].strip()
				dat	  = self.padDateTime(theValue[5].strip())
				nofch = self.padStatus(stat) + self.padNoOfCh(theValue[6].strip())
				devinf= self.padDeviceInfo(theValue[7].strip())
				updateString = macNO+u";"+ipNO+u";"+dat+u";"+stat+u";"+nofch+u";"+nick+u";"+vend+u";"+devinf+u"; "
				indigo.variable.updateValue(u"ipDevice"+ii00, updateString)
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
					theTest = indigo.variables[u"ipDevice"+ii00]
				except Exception as exc:
					self.indigoEmpty.append(ii00)
					self.indigoIndexEmpty += 1
					continue
				skip = 1
				theTest = theTest.value
				if len (theTest) < 5:  # that is minimum, should be 8 or 9
					skip = 1
					self.quitNOW = u"Indigo variable error 6"
					self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice" + ii00 +u";  deleting and letting the program recreate " )
					indigo.variable.delete(u"ipDevice"+ii00)
					continue
				theValue = theTest.split(u";")

				while len(theValue) < 10:
					theValue.append("")

				skip = u"no"
				self.indigoNumberOfdevices += 1
				self.indigoDevicesValues.append(theTest)
				self.indigoDevicesNumbers.append(ii00)
				theMAC =theValue[0].strip()
				if theValue[0].strip().count(u":") != 5:
					skip = 1
					self.quitNOW = u"Indigo variable error 7"
					self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice" + ii00 +u"  MAC number does not seem to be real MAC number>>" + theValue[0].strip() +u"<<  deleting and letting the program recreate " )
					indigo.variable.delete(u"ipDevice"+ii00)
					continue



				if theValue[1].strip().count(".") != 3:
					skip = 1
					self.quitNOW = u"Indigo variable error 8"
					self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevice" + ii00 +u"  IP number does not seem to be real IP number>>" + theValue[1].strip() +u"<<\  deleting and letting the program recreate  " )
					indigo.variable.delete(u"ipDevice"+ii00)
					continue

				self.indigoIpVariableData[theMAC]=copy.deepcopy(emptyindigoIpVariableData)
				devV = self.indigoIpVariableData[theMAC]
				devV[u"ipNumber"]			= theValue[1].strip()
				devV[u"timeOfLastChange"]	= theValue[2].strip()
				devV[u"status"]				= theValue[3].strip()
				try:
					devV[u"noOfChanges"]	= int(theValue[4].strip())
				except:
					devV[u"noOfChanges"]	= 0
				devV[u"nickName"]			= theValue[5].strip()
				devV[u"hardwareVendor"]		= theValue[6].strip()
				devV[u"deviceInfo"]			= theValue[7].strip()
				try:
					devV[u"WiFi"]			= theValue[8].strip()
				except:
					devV[u"WiFi"]			= ""
				try:
					devV[u"usePing"]		= theValue[9].strip()
				except:
					devV[u"usePing"]		= u"noPing-0"
				
				devV[u"ipDevice"]			= ii00
				devV[u"index"]				= self.indigoNumberOfdevices-1
				

			try:
				self.indigoStoredNoOfDevices = indigo.variables[u"ipDevsNoOfDevices"]
			except Exception as e:
				self.quitNOW = u"Indigo variable error 9"  ## someting must be wrong, lets restart
				self.indiLOG.log(40, u"getting data from indigo: bad variable ipDevsNoOfDevices \n   please check if it has bad data, in doubt delete and let the program recreate  \n   stopping fingscan \n exec return code" +unicode(e) )
		except Exception as e:
			self.exceptionHandler(40, e)


		return
########################################
	def doInbetweenPing(self,force = False):
		try:
			sleepT = max(self.sleepTime/2., 1)
			pingWait = 900  #milli seconds
			maxOldTimeStamp = max(sleepT +pingWait/1000. +0.5,2)
			maxPingsBeforeReset= int(5.*60./(pingWait/1000.+sleepT)) # around 5 minutes equiv
	#		if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"doInbetweenPing force= {}".format(force))
	#		if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"ping parameters: %5.2f   %5.2f   %5.2f   %5.2f "%(sleepT,pingWait,maxOldTimeStamp,maxPingsBeforeReset))
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
				if devI[u"status"] == u"down": 
					if devI[u"usePing"] in [u"usePingifDown",u"usePingifUPdown"]:
						retcode = 1
						if devI[u"useWakeOnLanSecs"] > 0:
							devI[u"useWakeOnLanLast"] = time.time()
							self.sendWakewOnLan(theMAC, calledFrom=u"doInbetweenPing")
							self.sleep(0.5)
						retCode = self.checkPing(theMAC, waitForPing=pingWait, countPings=2, waitAfterPing = 0.1 )
						if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u"pinged "+ theMAC+u"; retcode={}".format(retCode)+u";  useWakeOnLan:{}".format(devI[u"useWakeOnLanSecs"]) )
						if retcode !=0: 
							self.inbetweenPing[theMAC] = u"down"
						else:
							devI[u"status"] = u"up"
							self.inbetweenPing[theMAC] = u"up"
						continue

				if devI[u"status"] == u"up" and devI[u"usePing"] in [u"usePingifUP",u"usePingifUPdown"]:
					ipN = devI[u"ipNumber"].split("-")[0]# just in case ...it is "-changed"
					nPing +=1
					if self.inbetweenPingType == u"parallel":
						cmd = "for ((i=0;i<{};i++)); do /sbin/ping -c 2 -W {} -o {} &>/dev/null  && echo up > '{}pings/{}.ping' && sleep {}; done".format(maxPingsBeforeReset, pingWait, ipN, self.indigoPreferencesPluginDir, ipN.split(".")[3], sleepT)
						if theMAC in self.pingJobs:
							pingPid = self.pingJobs[theMAC]
							if pingPid >0:
								try:
									if time.time() - os.path.getmtime(self.indigoPreferencesPluginDir+"pings/"+ipN.split(".")[3]+".ping") < maxOldTimeStamp: # this will "except if it does not exist
										self.inbetweenPing[theMAC] = u"up"
										self.excludeMacFromPing[theMAC] = -99999999 # it answered at least once, never never firewall again
										continue # all done still up
									resp, err = self.readPopen("ps -ef  | grep ' {} ' | grep {} | grep -v grep".format(pingPid, ipN))
									ok = resp.find(cmd[:50]) > -1
									if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u" ping cheking if ping is running for {} grep  result:\n{}".format(ipN, resp))
									if ok:
										if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u" ping file for {} older than  : {} secs".format(ipN, maxOldTimeStamp))
										self.inbetweenPing[theMAC] = u"down"
										self.updateIndigoIpDeviceFromDeviceData(theMAC, [u"status"],justStatus=u"down")
										oneDown =  True
										self.killPing (theMAC,ipnumber =ipN)
										pingPid = -1
										continue
								except:
									resp, err = self.readPopen("ps -ef  | grep ' {} ' | grep {} | grep -v grep".format(pingPid, ipN) )
									ok = resp.find(cmd[:50]) > -1
									if ok: # still running?
											if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u" ping file  not created , device is down "+ipN)
											self.killPing (theMAC)# yes, kill it
											if self.excludeMacFromPing[theMAC] <0: continue
											if self.checkIfFirewalled(devI[u"deviceName"],theMAC, ipN) > 0: continue
									else:
											if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u" ping shell loop not running: {}".format(cmd[:50]))
										
						pid = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).pid
						self.pingJobs[theMAC] = pid
						if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u"launching ping cmd:"+cmd)
						if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u" ... {} pid= {} theMAC= {} timestamp={}".format(ipN, pid, theMAC, datetime.datetime.now().strftime(u"%M:%S")))
						continue
					
						
					if self.inbetweenPingType == u"sequential":
					   #if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"launching ping for : "+ipN +"  theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
						looptimes.append(time.time()-lptime)
						lptime=time.time()
						npTime=time.time()
						#   c 1: do 1 ping;  w: wait 800 msec; o: short output, q: quit if one response
						retCode = self.checkPing(theMAC, waitForPing=pingWait, countPings=2, waitAfterPing = 0.1)
						pingtimes.append(time.time()-npTime)
						if retCode > 0:  # ret code = 2 : no response ==> "down"
							#if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u" ping response: {}".format(resp).strip() )
							if self.excludeMacFromPing[theMAC] >=0:
								msg=False
								if self.checkIfFirewalled(devI[u"deviceName"],theMAC, ipN) >0: continue
							if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u" ping for  IP "+ipN +u"  theMAC="  +theMAC +u" timed out, status DOWN")
							self.inbetweenPing[theMAC] = u"down"
							self.updateIndigoIpDeviceFromDeviceData(theMAC, [u"status"], justStatus=u"down")
							oneDown=True
						else:
							self.inbetweenPing[theMAC] = u"up"
							self.excludeMacFromPing[theMAC] = -99999999 # it answered at least once, never test never firewall again
					#						if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u" ping ok : "+ipN +"  theMAC="  +theMAC +" timestamp="+datetime.datetime.now().strftime("%M:%S"))
					continue
						
						
	#		looptimes.append(time.time()-lptime)
	#		del looptimes[0]
			totalTime = time.time()-ticks
			if totalTime < 2  and msg: self.throttlePing = 0
			if totalTime > 4  and msg: self.throttlePing = 1
			if totalTime > 8  and msg: self.throttlePing = 2
			if totalTime > 12 and msg: self.throttlePing = 4
			if totalTime > 25 and msg: self.throttlePing = 8
	#		if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u" nPings      : {}".format(nPing) + "         seconds used: {}".format(totalTime) + " throttlePing: " + unicode(self.throttlePing))
	#		if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u" nPings      : {}".format(nPing) + "         seconds used: {}".format(totalTime) + " throttlePing: " + unicode(self.throttlePing)+" {}".format(max(pingtimes)))
	#		if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u" seconds loop: {}".format( [("%1.2f" %looptimes[k]) for k in range(len(looptimes)) ] )  )
	#		if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u" seconds ping: {}".format( [("%1.2f" %pingtimes[k]) for k in range(len(pingtimes))])  )
			if self.inbetweenPingType == u"sequential" and len(pingtimes) >0: 
				if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u"time used for PINGing {}".format(nPing) + u" times: %2.2f"%totalTime+" seconds needed;   max ping time: %2.2f"%max(pingtimes) )



		except Exception as e:
			self.exceptionHandler(40, e)
		
		return oneDown


########################################
	def checkIfFirewalled(self, devName,theMAC, ipN):
		try:
			if theMAC not in self.excludeMacFromPing: self.excludeMacFromPing[theMAC] =0 # start the counter
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u"testing if  "+devName+"/"+theMAC +"/"+ipN+"  is firewalled, does not answer to PINGs (%1d"%(self.excludeMacFromPing[theMAC]+1)+"/3 tests)" )
			ret, err = self.readPopen("echo '"+self.yourPassword+"' | sudo -S '"+self.fingEXEpath+"' -s "+ipN)
			if ret.find("incorrect password attempt")>-1:
				self.indiLOG.log(40, "incorrect password  in config, please correct")
				return 3
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10,unicode(ret).replace("--","").replace("  ","") )
			if ret.find("host unreachable") >-1:
				self.excludeMacFromPing[theMAC] +=1
				return 1
			if ret.find(u"no service found, firewalled")>-1 or(
			   ret.find(u"Non positive scan results")>-1 and ret.find(u"no service found")>-1) or(
			   ret.find(u"Detected firewall")>-1):
				self.excludeMacFromPing[theMAC] +=1
				if self.excludeMacFromPing[theMAC] > 2:
					if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u"excluding "+devName+u"/"+theMAC +u"/"+ipN+u" from PING test as it is firewalled or does not answer on any port(%1d"%(self.excludeMacFromPing[theMAC])+"/3 tests)" )
					return 3
				return 1

		except Exception as e:
			self.exceptionHandler(40, e)

		return 0



########################################
	def getIdandName(self,name):
		if name==u"0": return "",u"0",u"0"
		if name==u"1": return "",u"1",u"1"
		
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
				if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"trigger actionFrom  :  {}".format(self.callingPluginName[ii])+ " {}".format(self.callingPluginCommand[ii]))
				plug = indigo.server.getPlugin(self.callingPluginName[ii])
				if not plug.isEnabled():
					if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"trigger actionFrom Plugin  not enabled:  {}".format(plug)+ " {}".format(self.callingPluginCommand))
					continue
				try:
					idevId= self.callingPluginCommand[ii]
				except:
					if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"triggerFromPlugin  no msg:  {}".format(plug)+ " {}".format(self.idevId))
					continue

				idevD,idevName,idevId = self.getIdandName(idevId)
				
				if idevName =="":
					if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"params for iFind  idevName empty" )
					continue
				try:
					distance					= float(idevD.states[u"distanceHome"])			# distance from home
					distanceUnits				= idevD.states[u"distanceUnits"]					# convert to meters if needed, find ft or m and if display different from number
					deviceTimeChecked			= time.mktime(time.strptime(idevD.states[u"deviceTimeChecked"],u"%a %b %d %H:%M:%S %Y")) # format:  Thu Mar  3 07:32:49 2016  deviceTimeChecked of "iphone " in seconds
					timeNextUpdate				= float(idevD.states[u"timeNextUpdate"])			#  time in secs of next check
					iFindMethod					= idevD.states[u"calculateMethod"]				#  using avriable input or iFind nternal method
				except:
					if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"get params from iFind   not working:")
					continue
				if distanceUnits.find(u"kilometres")>-1:	distance *=  kmMeters
				elif distanceUnits.find(u"miles")>-1:	distance *= milesMeters

				found = False
				#if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"testing: iDeviceName  " +unicode(idevName) +" {}".format(idevId) )
				for n in self.EVENTS:
					evnt= self.EVENTS[n]
					found =0
					for nDev in evnt[u"iDeviceName"]:
						if evnt[u"iDeviceName"][nDev]=="": continue
						if unicode(evnt[u"iDeviceName"][nDev])== u"-1": continue
						found +=1
						#if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"trying iDeviceName  " +unicode(evnt[u"iDeviceName"][nDev]) +";  nDev{}".format(nDev) +";  nEvent{}".format(n) )
					
						if  unicode(evnt[u"iDeviceName"][nDev]) == unicode(idevId) or unicode(evnt[u"iDeviceName"][nDev]) == unicode(idevName):
							found =10000
							break
					if  found > 0 and  found < 10000:
						#if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"iDeviceName not found:  " +unicode(idevName) +" {}".format(idevId) )
						continue
					if  found  == 0: continue
					#if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"iDeviceName  found:  " +unicode(idevName) +" {}".format(idevId) +";  nDev{}".format(nDev) +";  nEvent{}".format(n)+";  iDeviceName"+  unicode(evnt[u"iDeviceName"][nDev]))
					
					if deviceTimeChecked > float(evnt[u"iUpdateSecs"][nDev]) +1 :  # new info
						
						evnt[u"iSpeedLast"][nDev]		= evnt[u"iSpeed"][nDev]
						evnt[u"iDistanceLast"][nDev]	= evnt[u"iDistance"][nDev]
						evnt[u"iUpdateSecsLast"][nDev]	= evnt[u"iUpdateSecs"][nDev]
						evnt[u"iDistance"][nDev]		= distance
						evnt[u"iUpdateSecs"][nDev]		= deviceTimeChecked
						evnt[u"itimeNextUpdate"][nDev]	= timeNextUpdate
						dTime 							= evnt[u"iUpdateSecs"][nDev]  - evnt[u"iUpdateSecsLast"][nDev]
						dDist							= evnt[u"iDistance"][nDev]    - evnt[u"iDistanceLast"][nDev]  
						speed							= dDist  /   max(dTime,1.)
						evnt[u"iSpeed"][nDev]			= speed
						if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"iFind old:  distance " +"%6.1f"%(evnt[u"iDistanceLast"][nDev])+ "; deviceTimeChecked " +"%6.1f"%(time.time()-evnt[u"iUpdateSecsLast"][nDev])+ ";  speed " +"%6.2f"%(evnt[u"iSpeedLast"][nDev])+";  ndev# {}".format(nDev))
						if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"      new:  distance " +"%6.1f"%(evnt[u"iDistance"][nDev])    + "; deviceTimeChecked " +"%6.1f"%(time.time()-evnt[u"iUpdateSecs"][nDev])    + ";  speed " +"%6.2f"%(evnt[u"iSpeed"][nDev])    +";  dDist " +"%6.2f"%(dDist)+";  dTime " +"%6.0f"%(dTime))
					else:
						if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"iFind trigger delivered no new data")
					evnt[u"iFindMethod"][nDev]			= iFindMethod
					
						
		except Exception as e:
			self.exceptionHandler(40, e)

		self.triggerFromPlugin		= False
		self.callingPluginName=[]
		self.callingPluginCommand=[]
		return

########################################
	def checkTriggers(self):
		try:
	#		if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"<<<--- entering checkTriggers")
			for nEvent in self.EVENTS:
				timeNowNumberSecs = time.time()
				timeNowm2 = int(timeNowNumberSecs-2.) ## drop the 10th of seconds
				timeNowHMS = datetime.datetime.now().strftime(u"%H:%M:%S")
				ticks = time.time()
				evnt=self.EVENTS[nEvent]
				InfoTimeStampSecs =0
	#			if self.decideMyLog(u"Events"): self.indiLOG.log(10,
	#			" nevents "+nEvents+
	#			" EVENTS{}".format(self.EVENTS[nEvent])
	#			)
				if nEvent == u"0": continue
				if evnt == u"0": continue
				if evnt == "": continue
				if evnt[u"enableDisable"] != u"1": continue
				minTime ={}
	#			evnt[u"oneHome"] ="0"
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

				evnt[u"nHome"]  = 0		
				evnt[u"nAway"]  = 0		

				for nDev in evnt[u"IPdeviceMACnumber"]:
					if evnt[u"IPdeviceMACnumber"][nDev] == u"0": continue
					if evnt[u"IPdeviceMACnumber"][nDev] == "": continue
					self.metersAway[nDev]	= -99999999999.
					self.metersHome[nDev]	= -99999999999.
					AwayTime[nDev]			=  999999999123
					HomeTime[nDev]			=  999999999123
					AwayStat[nDev]			=  False
					HomeStat[nDev]			=  False
					AwayDist[nDev]			=  True
					HomeDist[nDev]			=  False


				for nDev in evnt[u"IPdeviceMACnumber"]:
					AwayTime[nDev] = timeNowm2-float(evnt[u"secondsOfLastOFF"][nDev])
					#self.indiLOG.log(10,u"nDev {}".format(nDev) +" AwayTime[nDev]{}".format(AwayTime[nDev]) )
					minAwayTime = min(minAwayTime,AwayTime[nDev])  #################### need to check
					maxAwayTime = max(maxAwayTime,AwayTime[nDev])
					HomeTime[nDev] = timeNowm2-float(evnt[u"secondsOfLastON"][nDev])
					minHomeTime = min(minHomeTime,HomeTime[nDev])
					maxHomeTime = max(maxHomeTime,HomeTime[nDev])

				for nDev in evnt[u"IPdeviceMACnumber"]:
					status = u"0"
					if evnt[u"IPdeviceMACnumber"][nDev] == u"0": continue
					if evnt[u"IPdeviceMACnumber"][nDev] == "": continue
					iDev = int(nDev)
					theMAC =evnt[u"IPdeviceMACnumber"][nDev]
					##self.indiLOG.log(10,u" in trigger idev"+ nDev+"  "+ theMAC)
					if iDev< piBeaconStart:
						if len(theMAC) < 16:
							if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"theMAC=0")
							continue
						if not theMAC in self.allDeviceInfo:
							if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"mac number "+theMAC+u"\n   not present in data, deleting EVENT/device source for trigger" )
							evnt[u"IPdeviceMACnumber"][nDev] = u"0"
							break
						devI= self.allDeviceInfo[theMAC]
						status		= devI[u"status"]
					elif iDev< piBeaconStart:
						status = u"0"

					elif iDev< unifiStart:  ## check piBeacon devices
						try:
							status		= self.piBeaconDevices[theMAC][u"currentStatus"]
						except:
							self.getpiBeaconAvailable()
							self.updatepiBeacons()
							if len(self.piBeaconDevices) ==0:
								status = u"0"
							else:
								try:
									status = self.piBeaconDevices[theMAC][u"currentStatus"]
								except:
									self.exceptionHandler(40, e)
									self.indiLOG.log(40, u"error in checkTriggers, indigoID# "+theMAC+u" not in piBeacondevices  :  " + unicode(self.piBeaconDevices)[0:100]+u" ..  is  piBeacon plugin active? " )
									status = u"0"
									del self.piBeaconDevices[theMAC]
					elif iDev >= unifiStart:  ## check unifi devices
						try:
							status		= self.unifiDevices[theMAC][u"currentStatus"]
							#self.indiLOG.log(20,u" in trigger ndev, status"+ nDev+ "  "+ status)
						except:
							self.getUnifiAvailable()
							self.updateUnifi()
							if len(self.unifiDevices) ==0:
								status = u"0"
							else:
								try:
									status = self.unifiDevices[theMAC][u"currentStatus"]
								except Exception as e:
									self.exceptionHandler(40, e)
									self.indiLOG.log(40, u"error in checkTriggers, indigoID# "+theMAC+u" not in unifidevices  :  " + unicode(self.unifiDevices)[0:100]+u" ..  is  unifi plugin active? " )
									del self.unifiDevices[theMAC]
									status =  u"0"
	 #				if self.decideMyLog(u"Events"): self.indiLOG.log(20,u"Status from devI: "+theMAC+"-"+status)



					## check iFind devcies
					metersH = -8888888888
					metersA = -1.
					if len(evnt[u"iDeviceName"][nDev]) > 1 and (
						evnt[u"iDeviceUseForAway"][nDev] == u"1" or
						evnt[u"iDeviceUseForHome"][nDev] == u"1"): 
						plug = indigo.server.getPlugin(self.iFindStuffPlugin)  #  get i distance info and may be force a manual update of the distance..
						if plug.isEnabled():
							idevD,idevName,idevId = self.getIdandName(evnt[u"iDeviceName"][nDev])
							speed				= float(evnt[u"iSpeed"][nDev])
							distance			= float(evnt[u"iDistance"][nDev])
							pluginUpdateSecs	= float(evnt[u"iUpdateSecs"][nDev])
							timeNextUpdate		= float(evnt[u"itimeNextUpdate"][nDev])
							distance = max(0.1,distance)
							metersH = distance  # get the current meters away from home.
							metersA = distance
							try:
								varname=  idevD.name.replace(u" ","").replace("'","").encode('ascii', 'ignore').upper()+u'FREQ'
								xx= indigo.variables[varname].value 
							except:
								try:
									indigo.variable.create(varname,u"99")
								except Exception as e:    
									self.exceptionHandler(40, e)
									self.indiLOG.log(40, u"could not read or create variable  "+varname+u" for iFind communication, ignoring iFind communication")
									continue
							
							
							nextTimeToCheck= evnt[u"nextTimeToCheck"][nDev] # set to some default
							if status != u"up":  # if not in IP range use iFind
								evnt[u"iMaxSpeed"][nDev]=min(50.,max(abs(speed),evnt[u"iMaxSpeed"][nDev],1.001) ) 
								if (distance-float(evnt[u"distanceHomeLimit"])) > 0:  # not home
									if speed < -0.5:	# m / sec moving towards home , not standing, but faster than 0.5m/sec
										nextTimeToCheck=  (distance-float(evnt[u"distanceHomeLimit"]))  / evnt[u"iMaxSpeed"][nDev]
									elif speed < 0.5:	#slow moving
										nextTimeToCheck=  (distance-float(evnt[u"distanceHomeLimit"])) / max(2., min(evnt[u"iMaxSpeed"][nDev]/2.,5))  # assuming max speed towards/away home is slow ~ 2m/sec
									elif speed  <2 : # moving away slowly
										nextTimeToCheck=  (distance-float(evnt[u"distanceHomeLimit"])) / max(1., min(evnt[u"iMaxSpeed"][nDev]/4.,10))       # assuming max speed away home is < 2m/sec = 7km/h = fast walking speed
									
									else : # moving away fast > 7 km/h
										nextTimeToCheck=  (distance-float(evnt[u"distanceHomeLimit"])) *2.  # assuming max speed away from home is > 7km/h
									if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind after speed calc  nextTimeToCheck: {}".format(nextTimeToCheck)+" speed: {}".format(speed)+" iMaxSpeed: {}".format(evnt[u"iMaxSpeed"][nDev])  )
										 
									nextTimeToCheck = min(813.,nextTimeToCheck) 
									nextTimeToCheck = max( 10.,nextTimeToCheck*0.9 ) # between 10 and 720 seconds
									evnt[u"nextTimeToCheck"][nDev]=  nextTimeToCheck

								else:  # home
									pass
								
							else:  # in IP range take it slow
								evnt[u"iMaxSpeed"][nDev]=1.002
								if evnt[u"iFindMethod"][nDev] !="Calculated":
									plug.executeAction("refreshFrequencyOff", idevId)
								evnt[u"iMaxSpeed"][nDev]=1.004 # reset to walking speed as we are home
						   
								
							if distance > 20000.:  # we are far away (> 20km) leave it to the default timing
								if evnt[u"iFindMethod"][nDev] != u"Calculated":
									if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : switching method to OFF")
									if evnt[u"iFindMethod"][nDev] !="Calculated":
										if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : switching method to OFF (2)")
										plug.executeAction("refreshFrequencyOff", idevId)
										evnt[u"iFindMethod"][nDev] = u"Calculated"
							
											
							elif distance > float(evnt[u"distanceHomeLimit"]): ## not FAR AWAY, but not home 
									if indigo.variables[varname].value != unicode(int(nextTimeToCheck)):
										indigo.variable.updateValue(varname,unicode(int(nextTimeToCheck)))
									if   nextTimeToCheck < timeNextUpdate -time.time() :
										if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : switching method to Variable (On)")
										plug.executeAction("refreshFrequencyOn", idevId)
										evnt[u"iFindMethod"][nDev] = u"Variable"
									else:
										if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : no need to refresh")

							else:  # we are at home do things slowly ..
									if status != u"up" :# if the other indicators believe it is away do an iFind update
										if time.time() - float(evnt[u"secondsOfLastOFF"][nDev]) > 600: #after 15 minutes switch back to calculated
											if evnt[u"iFindMethod"][nDev] == u"Variable":
												evnt[u"iFindMethod"][nDev] = u"Calculated"
												if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : switching method to OFF (1)")
												plug.executeAction("refreshFrequencyOff", idevId)
												if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : at home, do it slowly (1)")
										else:  # check ifind, then set nextTime to 60 secs, see how it works
											if evnt[u"iFindMethod"][nDev] != u"Variable":  
												evnt[u"iFindMethod"][nDev] = u"Variable"
												if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : at home, but do a refresh iFind as wifi just turned off  secondsOfLastOFF: " + unicode(evnt[u"secondsOfLastOFF"][nDev])+ ";  iUpdateSecs: {}".format(evnt[u"iUpdateSecs"][nDev]) )
												nextTimeToCheck =60 #set to 1 minutes
												evnt[u"nextTimeToCheck"][nDev]=  nextTimeToCheck
												if indigo.variables[varname].value != unicode(int(nextTimeToCheck)): indigo.variable.updateValue(varname,unicode(int(nextTimeToCheck)))
												plug.executeAction("refreshFrequencyOn", idevId)
									else:
											evnt[u"iMaxSpeed"][nDev]=1.003
											if evnt[u"iFindMethod"][nDev] != u"Calculated":
												if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : switching method to OFF (2)")
												evnt[u"iFindMethod"][nDev] = u"Calculated"
												plug.executeAction("refreshFrequencyOff", idevId)
											if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind time : at home, do it slowly (2)")


							if self.decideMyLog(u"iFind"): self.indiLOG.log(10,
									 u"ifind time UpdSec: "		+ unicode(int( time.time() - float(pluginUpdateSecs) ))
									+u";  lastUpdLast: "		+ unicode(int( time.time() - float(evnt[u"iUpdateSecs"][nDev]) ))
									+u";  speed: "				+ u"%7.3f"%speed
									+u";  iMaxSpeed: "			+ u"%7.3f"%evnt[u"iMaxSpeed"][nDev]
									+u";  nextTimeToCheck: "	+ unicode(int(nextTimeToCheck))
									+u";  timeNextUpdate: "		+ unicode(int(timeNextUpdate -time.time()))
									+u";  secondsOfLastOFF: "	+ unicode(int(time.time()- float(evnt[u"secondsOfLastOFF"][nDev])))
									+u";  newDistance: "		+ unicode(int(distance))
									+u";  status: "				+ unicode(status	)
									+u";  iFindMethod: "		+ unicode(evnt[u"iFindMethod"][nDev]	)
									)

						else:
							if self.decideMyLog(u"iFind"): self.indiLOG.log(20,u"iFind is not enabled, please enable plugin or disable use of iFind in FINGSCAN")
							metersH=-7777777777
							metersA=-2.
					else:
						metersH=-6666666666
						metersA=-3.
					if evnt[u"iDeviceUseForAway"][nDev] == u"1": self.metersAway[nDev]	= metersA
					else:										 self.metersAway[nDev]	= -4.
					if evnt[u"iDeviceUseForHome"][nDev] == u"1": self.metersHome[nDev]	= metersH
					else:										 self.metersHome[nDev]	= -555555555.

					if float(self.metersHome[nDev]) >0. and float(self.metersHome[nDev]) <= float(evnt[u"distanceHomeLimit"]):
						HomeDist[nDev] = True
					#if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind  metersHome: {}".format(self.metersHome[nDev]) + ";  distanceHomeLimit: {}".format(evnt[u"distanceHomeLimit"])+ ";  HomeDist[nDev]: {}".format(HomeDist[nDev]))
					
					if (float(self.metersAway[nDev]) >0  and float(self.metersAway[nDev])  <= float(evnt[u"distanceAwayLimit"])):
						evnt[u"secondsOfLastOFF"][nDev] = timeNowm2
						evnt[u"timeOfLastOFF"][nDev]= timeNowHMS
						AwayDist[nDev] = False
					#if self.decideMyLog(u"iFind"): self.indiLOG.log(10,u"ifind  metersAway: {}".format(self.metersAway[nDev]) + ";  distanceAwayLimit: {}".format(evnt[u"distanceAwayLimit"])+ ";  AwayDist[nDev]: {}".format(AwayDist[nDev]))

					if status == u"up":
						HomeStat[nDev] = True
						#evnt[u"secondsOfLastOFF"][nDev] = timeNowm2
						#evnt[u"timeOfLastOFF"][nDev]= timeNowHMS
					else:
						AwayStat[nDev] = True
					AwayTime[nDev] = timeNowm2-float(evnt[u"secondsOfLastOFF"][nDev])
					minAwayTime = min(minAwayTime,AwayTime[nDev])
					maxAwayTime = max(maxAwayTime,AwayTime[nDev])
					HomeTime[nDev] = timeNowm2-float(evnt[u"secondsOfLastON"][nDev])
					minHomeTime = min(minHomeTime,HomeTime[nDev])
					maxHomeTime = max(maxHomeTime,HomeTime[nDev])



				#if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"minHomeTime {}".format(minHomeTime)+ " " + unicode(HomeTime))
				#if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"minAwayTime {}".format(minAwayTime)+ " " + unicode(AwayTime))
				#if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"Dist: AWAY-{}".format(AwayDist)+"-- HOME-{}".format(HomeDist))
				#if self.decideMyLog(u"Events"): self.indiLOG.log(10,u"Stat: AWAY-{}".format(AwayStat)+"-- HOME-{}".format(HomeStat))
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

				out = u"checkTrigger\n"
				if self.decideMyLog(u"Events"): out+="EVENT# {}".format(nEvent).ljust(2)+u"  Dev#  HomeStat".ljust(15)                         +"HomeTime".ljust(12)           +"HomeDist".ljust(13)          +"AwayStat".ljust(12)         +"AwayTime".ljust(12)           +"AwayDist".ljust(11)           +" oneHome"            +" allHome"             +"  oneAway"           +" allAWay"+"\n"
				for nDev in evnt[u"IPdeviceMACnumber"]:
					if evnt[u"IPdeviceMACnumber"][nDev] == u"0": continue
					if evnt[u"IPdeviceMACnumber"][nDev] ==  "": continue
					evnt[u"iDeviceAwayDistance"][nDev]= u"%5.3f"%self.metersAway[nDev]
					evnt[u"iDeviceHomeDistance"][nDev]= u"%5.3f"%self.metersHome[nDev]
					if AwayStat[nDev] and evnt[u"currentStatusAway"][nDev] == "0" and (minAwayTime < 30 and False):  ### need to fix 
						out+="          "+  u"nDev{}".format(nDev)+u" AwayStat[nDev]{}".format(AwayStat[nDev])+u" evnt[currentStatusAway][nDev]" + unicode(evnt[u"currentStatusAway"][nDev])+" minAwayTime" + unicode(minAwayTime)+"\n"
						self.redoAWAY= 10  # increase frequency of up/down test to 1 per second for 10 seconds
	#### away status
					if evnt[u"currentStatusAway"][nDev] == u"0":
						if (AwayStat[nDev] and AwayDist[nDev]) :
							if float(evnt[u"minimumTimeAway"]) >0.:
								evnt[u"currentStatusAway"][nDev]	= u"startedTimer"
								allAway = False  # added , was missing 
							else:
								evnt[u"currentStatusAway"][nDev]	= u"AWAY"
								oneAway = True
								self.redoAWAY= 0
							evnt[u"secondsOfLastOFF"][nDev]= timeNowm2
							evnt[u"timeOfLastOFF"][nDev]= timeNowHMS
						else:
							allAway = False
					elif evnt[u"currentStatusAway"][nDev] == "startedTimer":
							if (AwayStat[nDev] and AwayDist[nDev]):
								if AwayTime[nDev] >= float(evnt[u"minimumTimeAway"]):
									evnt[u"currentStatusAway"][nDev] = u"AWAY"
								else:    
									allAway = False
							else:    
								evnt[u"currentStatusAway"][nDev] = u"0"
								allAway = False
					 
					if evnt[u"currentStatusAway"][nDev] == u"AWAY":
						if (AwayStat[nDev] and AwayDist[nDev]):
							oneAway = True
							if AwayTime[nDev] >= float(evnt[u"minimumTimeAway"]):
								oneAwayTrigger =True
							if minAwayTime >= float(evnt[u"minimumTimeAway"]):
								allAwayTrigger =True
					
						else:
							allAway = False
							evnt[u"currentStatusAway"][nDev]	= u"0"
							evnt[u"secondsOfLastOFF"][nDev]= timeNowm2
					if evnt[u"currentStatusAway"][nDev] == u"AWAY":
						evnt[u"nAway"] += 1


	#### home status
					if evnt[u"currentStatusHome"][nDev] == u"0": # was not home
						if (HomeStat[nDev] or HomeDist[nDev]):
							evnt[u"currentStatusHome"][nDev]	= u"HOME"
							evnt[u"secondsOfLastON"][nDev]= timeNowm2
							evnt[u"timeOfLastON"][nDev]= timeNowHMS
							oneHome = True
							if minHomeTime >= float(evnt[u"minimumTimeHome"]):
								oneHomeTrigger =True
							if maxHomeTime >= float(evnt[u"minimumTimeHome"]):
								allHomeTrigger =True
						else:
							allHome = False
					else:  # it is or was  home
						if (HomeStat[nDev] or HomeDist[nDev]): # still home: restart timer
							evnt[u"timeOfLastON"][nDev]= timeNowHMS
							evnt[u"secondsOfLastON"][nDev]= timeNowm2
							evnt[u"currentStatusHome"][nDev]	= u"HOME"
							oneHome = True
							# this is wrong:
							#if minHomeTime >= float(evnt[u"minimumTimeHome"]):
							#    oneHomeTrigger =True
							#if maxHomeTime >= float(evnt[u"minimumTimeHome"]):
							#    allHomeTrigger =True
						else:
							evnt[u"currentStatusHome"][nDev]	= u"0"
							allHome = False
					if evnt[u"currentStatusHome"][nDev]	== u"HOME":
						evnt[u"nHome"] += 1
					if self.decideMyLog(u"Events"): out+="EVENT# {}".format(nEvent).ljust(2)+u"  {}".format(nDev).rjust(3)+"   " +unicode(HomeStat[nDev]).ljust(12)+ unicode(HomeTime[nDev]).ljust(12) + unicode(HomeDist[nDev]).ljust(12)+ unicode(AwayStat[nDev]).ljust(12)+ unicode(AwayTime[nDev]).ljust(12)+ unicode(AwayDist[nDev]).ljust(12) + unicode(oneHome).ljust(8)+ unicode(allHome).ljust(8)+ unicode(oneAway).ljust(8)+ unicode(allAway).ljust(8) +"\n"


				if self.decideMyLog(u"Events"): out+="EVENT# {}".format(nEvent).ljust(2)+u"  "+u"oneHome:" + evnt[u"oneHome"]+"; allHome:" + evnt[u"allHome"]+"; oneAway:" + evnt[u"oneAway"]+"; allAway:" + evnt[u"allAway"] +"\n"
				if time.time() - self.timeOfStart > 100:
					if oneHome:
						if evnt[u"oneHome"] != u"1" :
							if oneHomeTrigger:
								evnt[u"oneHome"] = u"1"
								self.updatePrefs = True
								indigo.variable.updateValue(u"oneHome_"+nEvent,u"1")
								if self.checkTriggerInitialized:
									try:indigo.variable.updateValue(u"FingEventDevChangedIndigoId",unicode(self.allDeviceInfo[evnt[u"IPdeviceMACnumber"][oneHomeTrigger]][u"deviceId"]))
									except: pass
									self.triggerEvent(u"EVENT_"+nEvent+"_oneHome")
					else:
						if evnt[u"oneHome"] != u"0":
							evnt[u"oneHome"] = u"0"
							indigo.variable.updateValue(u"oneHome_"+nEvent,u"0")
							self.updatePrefs = True
					if allHome:
						if evnt[u"allHome"] != u"1":
							if allHomeTrigger:
								evnt[u"allHome"] = u"1"
								self.updatePrefs = True
								indigo.variable.updateValue(u"allHome_"+nEvent,u"1")
								if self.checkTriggerInitialized:
									try: indigo.variable.updateValue(u"FingEventDevChangedIndigoId",unicode(self.allDeviceInfo[evnt[u"IPdeviceMACnumber"][allHomeTrigger]][u"deviceId"]))
									except: pass
									self.triggerEvent(u"EVENT_"+nEvent+u"_allHome")
					else:
						if evnt[u"allHome"] != u"0":
							evnt[u"allHome"] = u"0"
							indigo.variable.updateValue(u"allHome_"+nEvent,u"0")
							self.updatePrefs = True



					if allAway:
						if evnt[u"allAway"] != u"1":
							if allAwayTrigger:
								self.updatePrefs = True
								evnt[u"allAway"] = u"1"
								indigo.variable.updateValue(u"allAway_"+nEvent,u"1")
								if self.checkTriggerInitialized:
									try: indigo.variable.updateValue(u"FingEventDevChangedIndigoId",unicode(self.allDeviceInfo[evnt[u"IPdeviceMACnumber"][allAwayTrigger]][u"deviceId"]))
									except: pass
									self.triggerEvent(u"EVENT_"+nEvent+"_allAway")
					else:
						if evnt[u"allAway"] != u"0":
							evnt[u"allAway"] = u"0"
							indigo.variable.updateValue(u"allAway_"+nEvent,u"0")
							self.updatePrefs = True

					if oneAway:
						if evnt[u"oneAway"] != u"1":
							if oneAwayTrigger:
								self.updatePrefs = True
								evnt[u"oneAway"] = u"1"
								indigo.variable.updateValue(u"oneAway_"+nEvent,u"1")
								if self.checkTriggerInitialized:
									try: indigo.variable.updateValue(u"FingEventDevChangedIndigoId",unicode(self.allDeviceInfo[evnt[u"IPdeviceMACnumber"][allAwayTrigger]][u"deviceId"]))
									except: pass
									self.triggerEvent(u"EVENT_"+nEvent+u"_oneAway")
					else:
						if evnt[u"oneAway"] != u"0":
							evnt[u"oneAway"] = u"0"
							indigo.variable.updateValue(u"oneAway_"+nEvent, u"0")
							self.updatePrefs = True

					if unicode(evnt[u"nAway"]) != indigo.variables[u"nAway_"+nEvent].value:
						indigo.variable.updateValue(u"nAway_"+nEvent, unicode(evnt[u"nAway"]))
					if unicode(evnt[u"nHome"]) != indigo.variables[u"nHome_"+nEvent].value:
						indigo.variable.updateValue(u"nHome_"+nEvent, unicode(evnt[u"nHome"]))



				if self.decideMyLog(u"Events"): self.printEvents(printEvents=nEvent)
	#		if self.decideMyLog(u"Events"): self.indiLOG.log(10,u" leaving checkTriggers   ---->")

			self.checkTriggerInitialized =True
			
			

		except Exception as e:
			self.exceptionHandler(40, e)
		return
	

########################################
	def sortIndigoIndex(self):
		try:
			sortFields =[]
			
			ll=0
			for theMAC in self.indigoIpVariableData:
				kk = self.indigoIpVariableData[theMAC][u"index"]
				ipCompr = int(self.indigoIpVariableData[theMAC][u"ipNumber"].strip().replace(u".",""))  # "  192.168.1.5  " --> "  19216815  "
				sortFields.append([ipCompr,kk])  # [[192168110,1],[19216816,2], ....[....]]
				ll+=1
	#			if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"sort: {}".format(ll) + " " + unicode(kk) +" " + unicode(ipCompr))
			sortedIP = sorted(sortFields, key=lambda tup: tup[0])  # sort ip number: tup([0]) as number,

	#		if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"sort2.0 len: {}".format(len(self.indigoDevicesValues)) )
			for kk in range(ll):
				jj = sortedIP[kk][1]						# old index
	#			if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"sort2: {}".format(kk) + " " + unicode(jj) )
				
				newLine = self.indigoDevicesValues[jj]		# from old ipdevice value
				kk00 = self.int2hexFor2Digit(kk+1)							# make it 01 02 ..09 10 11 ..99
				try:
					indigo.variable.updateValue(u"ipDevice"+kk00, newLine)  # update indigo with new sorted list
				except:
					indigo.variable.create(u"ipDevice"+kk00, newLine,self.indigoVariablesFolderID)  # create new var if it does not exists with new sorted list

			# delete any entry > # of devices
			for kk in range(ll,indigoMaxDevices):
				kk00=self.int2hexFor2Digit(kk+1)						# make it 01 02 ..09 10 11 ..99
				try:
					indigo.variable.delete(u"ipDevice"+kk00)
				except:
					pass
		except Exception as e:
			self.exceptionHandler(40, e)

		return 1





########################################
	def compareToFingIfExpired(self, calledFrom):
		try:
			dateTimeNow = time.strftime(u"%Y-%m-%d %H:%M:%S", time.localtime())
			for theMAC in self.allDeviceInfo:
				if theMAC in self.ignoredMAC: continue
					
				update = False
				devI = self.allDeviceInfo[theMAC]
				try:  ## try to find this indigo mac number in  fingdata
					xxx = self.fingMACNumbers.index(theMAC)
				except:  ## this one is in indigo, but not in the fingdata file, set to exipred if not already done or ignore if better data from wifirouter
					if self.routerType != u"0" and theMAC in self.wifiMacList and self.routerErrorCount==0:
						if self.allDeviceInfo[theMAC][u"setWiFi"] != u"Ethernet":
							if theMAC in self.WiFiChanged:
								if   self.wifiMacList[theMAC][0] == u"Yes":
									if self.allDeviceInfo[theMAC][u"status"] != u"up":
											self.allDeviceInfo[theMAC][u"status"] = u"up"
											update = True
								elif self.allDeviceInfo[theMAC][u"status"] == u"up":
									self.allDeviceInfo[theMAC][u"status"] = u"down"
									update = True
								elif self.allDeviceInfo[theMAC][u"status"] == u"down":
									self.allDeviceInfo[theMAC][u"status"] =  u"expired"
									update = True
				
					else:
							try:
								if (time.time() - self.allDeviceInfo[theMAC][u"lastFingUp"] >  2*self.allDeviceInfo[theMAC][u"expirationTime"] ): 
									if self.allDeviceInfo[theMAC][u"status"] != u"expired":
										update = True
										self.allDeviceInfo[theMAC][u"status"] = u"expired"
								elif (time.time() - self.allDeviceInfo[theMAC][u"lastFingUp"] >  self.allDeviceInfo[theMAC][u"expirationTime"] ): 
									if self.allDeviceInfo[theMAC][u"status"] != u"down":
										update = True
										self.allDeviceInfo[theMAC][u"status"] = u"down"
							except:
								pass
					if update:
						self.allDeviceInfo[theMAC][u"timeOfLastChange"] = dateTimeNow
						self.updateIndigoIpDeviceFromDeviceData(theMAC,[u"status",u"timeOfLastChange"])
						self.updateIndigoIpVariableFromDeviceData(theMAC)
				if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u" fing end..theMAC/wifi/status/: "+theMAC+" -"  + self.allDeviceInfo[theMAC][u"status"] )
				
				
			if self.routerType != "0":
				for theMAC in self.wifiMacList:
					if theMAC not in self.allDeviceInfo:
						if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
						self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
						devI= self.allDeviceInfo[theMAC]
						devI[u"ipNumber"]			= "256.256.256.256"
						devI[u"timeOfLastChange"]	= unicode(dateTimeNow)
						devI[u"status"]				= "up"
						devI[u"nickName"]			= "unidentifiedWiFiDevice"
						devI[u"noOfChanges"]		= 1
						devI[u"deviceInfo"]			= "unidentified"
						if devI[u"setWiFi"] != u"Ethernet":
							devI[u"WiFi"]			= self.wifiMacList[theMAC][9]
						devI[u"usePing"]			= u"usePingUP"
						devI[u"useWakeOnLanSecs "]	= 0
						devI[u"suppressChangeMSG"]	= u"show"
						devI[u"hardwareVendor"]      = self.getVendortName(theMAC)

						newIPDevNumber = unicode(self.indigoEmpty[0])
						if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"new device added ipDevice" +  newIPDevNumber)
						
						self.updateIndigoIpDeviceFromDeviceData(theMAC,[u"all"])
						self.updateIndigoIpVariableFromDeviceData(theMAC)


						## count down empty space
						self.indigoIndexEmpty -= 1  # one less empty slot
						if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list

						## start any triggers if setup
						try:
							indigo.variable.updateValue(u"ipDevsNewDeviceNo", u"ipDevice{}".format(newIPDevNumber)+u";"+devI[u"deviceName"])
						except:
							indigo.variable.create(u"ipDevsNewDeviceNo", u"ipDevice{}".format(newIPDevNumber)+u";"+devI[u"deviceName"],self.indigoVariablesFolderID)
						self.triggerEvent(u"NewDeviceOnNetwork")

						try:
							if self.indigoStoredNoOfDevices != unicode(self.indigoNumberOfdevices):
								indigo.variable.updateValue(u"ipDevsNoOfDevices", unicode(self.indigoNumberOfdevices))
						except:
							indigo.variable.create(u"ipDevsNoOfDevices", unicode(indigoNumberOfdevices))

		except Exception as e:
			self.exceptionHandler(40, e)

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
				if self.fingStatus[kk] != u"up":
					for jj in range(0,self.fingNumberOfdevices):   # sometimes ip numbers are listed twice in fing.data, take the one with "UP"
						if jj == kk: continue
						if self.fingMACNumbers[kk] 	!= self.fingMACNumbers[jj]	: continue  # not the same
						if self.fingStatus[kk] 		== self.fingStatus[jj]		: continue  # same status, should not be, just protecting
						if self.fingStatus[jj] 		== u"up":								# jj is up , kk is not, use jj wait until we are there
							dontUseThisOne = True
							break
						if  theMAC in self.allDeviceInfo:									# and last test if the otehr has the current ip number use jj, not kk
							if self.allDeviceInfo[theMAC][u"ipNumber"] == self.fingIPNumbers[jj]:
								dontUseThisOne = True
							break
				if dontUseThisOne: continue
				

				doIndigoUpdate = 0
				if theMAC in self.allDeviceInfo:
					theAction = u"exist"
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u" theMAC action: "+theMAC+"/"+theAction )
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(10,unicode(self.allDeviceInfo[theMAC]))
				else:
					theAction="new"
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u" theMAC action: "+theMAC+"/"+theAction )
				
				updateStates=[]

				
				if theAction == u"exist" :
					if u"setWiFi" not in self.allDeviceInfo[theMAC]:
						self.allDeviceInfo[theMAC][u"setWiFi"] = copy.deepcopy(emptyAllDeviceInfo[u"setWiFi"])
					devI= self.allDeviceInfo[theMAC]
					
					useFing=True
					if self.allDeviceInfo[theMAC][u"setWiFi"] == u"Wifi":
						useFing=False
						theStatus = u"down"
					else:
						theStatus = self.fingStatus[kk]
						if self.inbetweenPingType!= u"0" and theMAC in self.inbetweenPing:
							if  self.inbetweenPing[theMAC] == u"down": theStatus = u"down"

					#if theMAC =="1C:36:BB:97:C0:85": 
					#    indigo.server.log("exists "+ theStatus+"  {}".format(devI[u"lastFingUp"]))

					if theStatus != u"up":
						if theMAC in self.allDeviceInfo and "useWakeOnLanSecs" in self.allDeviceInfo[theMAC] and  self.allDeviceInfo[theMAC][u"useWakeOnLanSecs"] > 0:
							self.sendWakewOnLanAndPing(theMAC, nBC= 1,waitForPing=10, countPings=1, waitBeforePing = 0., waitAfterPing = 0.0, calledFrom="compareToIndigoDeviceData")

					if theStatus == u"up":
						devI[u"lastFingUp"] = time.time()
					else:
						if devI[u"expirationTime"] != 0 and (time.time() - devI[u"lastFingUp"] < devI[u"expirationTime"]): 
							theStatus = u"up"

					if self.routerType !="0" and self.routerErrorCount ==0:					# check wifi router info if available
						if devI[u"setWiFi"] != u"Ethernet":									# ignore if set to ethernet
							if theMAC in self.wifiMacList:
								associated =self.wifiMacList[theMAC][0]
								if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"before theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI[u"ipNumber"]+" LastUpdateby:"+lastUpdateSource)
								if associated == u"Yes":
									if theStatus != u"up":
										self.fingDate[kk] = unicode(dateTimeNow)
										doIndigoUpdate = 9
									if theStatus != u"changed": theStatus = u"up"
								else:
									if theStatus == u"up" and lastUpdateSource == u"WiFi":
										self.fingDate[kk] = unicode(dateTimeNow)
										theStatus = u"down"
										doIndigoUpdate = 9
		#								if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"wifi theMAC:"+theMAC+" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI[u"ipNumber"]+" LastUpdateby:"+lastUpdateSource)
	
									#### important !!!!
									#fix : add time component > 3 minutes	if theStatus == "up" and lastUpdateSource.find("fing") > -1:
									#	devI[u"WiFi"]=""
									#	doIndigoUpdate = 9
									#	del self.wifiMacList[theMAC]
								if theMAC in self.wifiMacList:
									if devI[u"WiFi"] !=self.wifiMacList[theMAC][9]:
										devI[u"WiFi"] =self.wifiMacList[theMAC][9]
										doIndigoUpdate = 9
								if doIndigoUpdate ==9:
									updateStates.append("WiFi")
								if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"after WiFiF checks theMAC:"+theMAC+u" status:"+theStatus+" wifi:-" +associated +"- IPN:" +devI[u"ipNumber"]+" LastUpdateby:"+lastUpdateSource)


					## found device, check if anything has changed: ip & status, if changed increment # of changes
					if devI[u"status"]!= theStatus:
						updateStates.append("status")
						updateStates.append("noOfChanges")
						doIndigoUpdate = 2
						devI[u"noOfChanges"] +=1
						if theStatus == "up":
							if devI[u"ipNumber"].split("-")[0]!= self.fingIPNumbers[kk]:  # split("-") to remove "-changed" string
								devI[u"ipNumber"] = self.fingIPNumbers[kk]
								updateStates.append(u"ipNumber")
								doIndigoUpdate = 3
						if theStatus == u"down":
							if devI[u"ipNumber"].find(u"changed")>-1 or devI[u"ipNumber"].find(u"double")>-1:
								devI[u"ipNumber"] = self.fingIPNumbers[kk]
								updateStates.append(u"ipNumber")
							self.fingDate[kk] = unicode(dateTimeNow)
							doIndigoUpdate = 5
						if theStatus == u"changed":
							doIndigoUpdate = 6
							updateStates.append(u"ipNumber")
							theStatus = u"up"
					#no status change, check if IP number changed
					else :
						if theStatus == u"up":
							if devI[u"ipNumber"].find(u"changed")>-1 or devI[u"ipNumber"].find(u"double")>-1:
								devI[u"ipNumber"] = self.fingIPNumbers[kk]
								updateStates.append(u"ipNumber")
								doIndigoUpdate = 8
							if devI[u"ipNumber"] != self.fingIPNumbers[kk]:
								doIndigoUpdate = 7
								updateStates.append(u"ipNumber")
								updateStates.append(u"noOfChanges")
								devI[u"noOfChanges"] +=1
					devI[u"status"]	= theStatus
					devI[u"ipNumber"]= self.fingIPNumbers[kk]

					if doIndigoUpdate > 0:
						if doIndigoUpdate== 6:
							if theMAC in self.doubleIPnumbers:
								if len(self.doubleIPnumbers[theMAC]) 	==1: devI[u"ipNumber"]=self.fingIPNumbers[kk]+ u"-changed"
								elif len(self.doubleIPnumbers[theMAC]) 	>1:	 devI[u"ipNumber"]=self.fingIPNumbers[kk]+ u"-double"
						dd = self.fingDate[kk]
						if len(dd) < 5 : dd = unicode(dateTimeNow)
						devI[u"timeOfLastChange"]	=dd
						self.updateDeviceWiFiSignal(theMAC)
						updateStates.append(u"deviceInfo")
						self.updateIndigoIpDeviceFromDeviceData(theMAC,updateStates)
						self.updateIndigoIpVariableFromDeviceData(theMAC)

						if doIndigoUpdate == 3 or doIndigoUpdate == 6 or doIndigoUpdate == 7 :
							try:
								indigo.variable.updateValue(u"ipDevsNewIPNumber", u"ipDevice"+self.indigoIpVariableData[theMAC][u"ipDevice"]+u";"+devI[u"deviceName"])
							except:
								indigo.variable.create(u"ipDevsNewIPNumber",u"ipDevice"+self.indigoIpVariableData[theMAC][u"ipDevice"]+u";"+devI[u"deviceName"],self.indigoVariablesFolderID)
							if theMAC in self.doubleIPnumbers:
								if (len(self.doubleIPnumbers[theMAC])==1 or  (len(self.doubleIPnumbers[theMAC])>1) and  devI[u"suppressChangeMSG"]=="show"):
									self.triggerEvent(u"IPNumberChanged")


				if theAction == u"new" :################################# new device, add device to indigo
					if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
					self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
					devI= self.allDeviceInfo[theMAC]
					devI[u"ipNumber"]			=self.fingIPNumbers[kk]
					dd = self.fingDate[kk]
					if len(dd) < 5 : dd = unicode(dateTimeNow)
					## find a new unique name for device "new-seq#-mac#"
					sqNumber=0
					for dNew in indigo.devices.iter(u"com.karlwachs.fingscan"):
						if dNew.name.find(u"new") ==-1: continue
						xxx= dNew.name.split(u"-")
						if len(xxx)< 3: continue
						try:
							sqn=int(xxx[1])
							sqNumber=sqn+1
						except:
							continue    
					
					devI[u"timeOfLastChange"]	= dd
					devI[u"status"]				= u"up"
					devI[u"nickName"]			= u"new-{}".format(sqNumber)+u"-"+theMAC
					devI[u"noOfChanges"]			=1
					if len(self.fingVendor[kk]) < 4:
						devI[u"hardwareVendor"]      = self.getVendortName(theMAC)
					else:
						devI[u"hardwareVendor"]		=self.fingVendor[kk]

					devI[u"deviceInfo"]			= self.fingDeviceInfo[kk]
					devI[u"WiFi"]				= ""
					devI[u"usePing"]			= u"usePingUP"
					devI[u"useWakeOnLanSecs"]	= 0
					devI[u"suppressChangeMSG"]	= u"show"
					#if theMAC =="1C:36:BB:97:C0:85": 
					#    indigo.server.log("new "+ theStatus+"  {}".format(devI[u"lastFingUp"]))
					devI[u"lastFingUp"]	        = time.time()

					newIPDevNumber = unicode(self.indigoEmpty[0])
					if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"new device added ipDevice" +  newIPDevNumber)
					
					self.updateIndigoIpDeviceFromDeviceData(theMAC,[u"all"])
					self.updateIndigoIpVariableFromDeviceData(theMAC)


					## count down empty space
					self.indigoIndexEmpty -= 1  # one less empty slot
					if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list

					anyUpdate +=1
					## start any triggers if setup
					try:
						indigo.variable.updateValue(u"ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI[u"deviceName"])
					except:
						indigo.variable.create(u"ipDevsNewDeviceNo", "ipDevice{}".format(newIPDevNumber)+";"+devI[u"deviceName"],self.indigoVariablesFolderID)
					self.triggerEvent(u"NewDeviceOnNetwork")



			if self.routerType != u"0" and lastUpdateSource == u"WiFi":
				for theMAC in self.wifiMacList:
					if theMAC in self.allDeviceInfo: continue
					if not self.acceptNewDevices or theMAC in self.ignoredMAC: continue
					self.allDeviceInfo[theMAC]= copy.deepcopy(emptyAllDeviceInfo)
					devI= self.allDeviceInfo[theMAC]
					devI[u"ipNumber"]			= u"254.254.254.254"
					devI[u"timeOfLastChange"]	= unicode(dateTimeNow)
					devI[u"status"]				= "up"
					devI[u"nickName"]			= "unidentified_WiFi_Device"
					devI[u"noOfChanges"]		= 1
					devI[u"hardwareVendor"]     = self.getVendortName(theMAC)
					devI[u"deviceInfo"]			= u"unidentified"
					devI[u"WiFi"]				= self.wifiMacList[theMAC][9]
					devI[u"usePing"]			= ""
					devI[u"useWakeOnLanSecs "]	= 0
					devI[u"suppressChangeMSG"]	= u"show"
					try:
						newIPDevNumber = unicode(self.indigoEmpty[0])
					except:
						newIPDevNumber = u"1"
						self.indiLOG.log(10,u"new device added indigoEmpty not initialized" +  unicode(self.indigoEmpty))
					if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"new device added ipDevice#" +  newIPDevNumber)
					
					self.updateIndigoIpDeviceFromDeviceData(theMAC,[u"all"])
					self.updateIndigoIpVariableFromDeviceData(theMAC)
					## count down empty space
					self.indigoIndexEmpty -= 1  # one less empty slot
					if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list

					try:
						indigo.variable.updateValue(u"ipDevsNewDeviceNo", u"ipDevice{}".format(newIPDevNumber)+u";"+devI[u"deviceName"])
					except:
						indigo.variable.create(u"ipDevsNewDeviceNo", u"ipDevice{}".format(newIPDevNumber)+u";"+devI[u"deviceName"],self.indigoVariablesFolderID)
					self.triggerEvent(u"NewDeviceOnNetwork")

			try:
				if self.indigoStoredNoOfDevices != unicode(self.indigoNumberOfdevices):
					indigo.variable.updateValue(u"ipDevsNoOfDevices", unicode(self.indigoNumberOfdevices))
			except:
				indigo.variable.create(u"ipDevsNoOfDevices", unicode(indigoNumberOfdevices))

		except Exception as e:
			self.exceptionHandler(40, e)


		return 0



########################################
	def getVendortName(self, MAC):
		if self.enableMACtoVENDORlookup == u"0" : return ""
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
					cmd = u"off"
					pri  = ""
				self.timeTrackWaitTime = 20
				return cmd, pri
		except	Exception as e:
			pass

		self.timeTrackWaitTime = 60
		return u"off",""

	####-----------------            ---------
	def printcProfileStats(self,pri=""):
		try:
			if pri !="": pick = pri
			else:		 pick = u'cumtime'
			outFile		= self.indigoPreferencesPluginDir+u"timeStats"
			indigo.server.log(u" print time track stats to: "+outFile+u".dump / txt  with option: "+pick)
			self.pr.dump_stats(outFile+u".dump")
			sys.stdout 	= open(outFile+u".txt", "w")
			stats 		= pstats.Stats(outFile+u".dump")
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
			self.do_cProfile  			= u"x"
			self.timeTrVarName 			= u"enableTimeTracking_"+self.pluginShortName
			indigo.server.log("testing if variable "+self.timeTrVarName+" is == on/off/print-option to enable/end/print time tracking of all functions and methods (option:'',calls,cumtime,pcalls,time)")

		self.lastTimegetcProfileVariable = time.time()

		cmd, pri = self.getcProfileVariable()
		if self.do_cProfile != cmd:
			if cmd == u"on": 
				if  self.cProfileVariableLoaded ==0:
					indigo.server.log(u"======>>>>   loading cProfile & pstats libs for time tracking;  starting w cProfile ")
					self.pr = cProfile.Profile()
					self.pr.enable()
					self.cProfileVariableLoaded = 2
				elif  self.cProfileVariableLoaded >1:
					self.quitNOW = u" restart due to change  ON  requested for print cProfile timers"
			elif cmd == u"off" and self.cProfileVariableLoaded >0:
					self.pr.disable()
					self.quitNOW = u" restart due to  OFF  request for print cProfile timers "
		if cmd == "print"  and self.cProfileVariableLoaded >0:
				self.pr.disable()
				self.printcProfileStats(pri=pri)
				self.pr.enable()
				indigo.variable.updateValue(self.timeTrVarName,u"done")

		self.do_cProfile = cmd
		return 

	####-----------------            ---------
	def checkcProfileEND(self):
		if self.do_cProfile in[u"on",u"print"] and self.cProfileVariableLoaded >0:
			self.printcProfileStats(pri="")
		return
	###########################	   cProfile stuff   ############################ END

	####-----------	------	 ---------
	def setSqlLoggerIgnoreStatesAndVariables(self):
		try:
			if self.indigoVersion <  7.4:                             return 
			if self.indigoVersion == 7.4 and self.indigoRelease == 0: return 
			#tt = [u"beacon",              "rPI","rPI-Sensor","BLEconnect","sensor"]

			outOffD = ""
			outOffV = ""

			for dev in indigo.devices.iter(self.pluginId):
					sp = dev.sharedProps
					if u"sqlLoggerIgnoreStates" not in sp:
						sp[u"sqlLoggerIgnoreStates"] = u"lastfingup"
						dev.replaceSharedPropsOnServer(sp)
						outOffD += dev.name+";"
					elif sp[u"sqlLoggerIgnoreStates"].find(u"lastfingup") == -1:
						sp[u"sqlLoggerIgnoreStates"] += u",lastfingup"
						dev.replaceSharedPropsOnServer(sp)
						outOffD += dev.name+u";"

			varExcludeSQLList = [u"ipDevsLastDevChangedIndigoName",u"ipDevsLastUpdate", u"ipDevsNewDeviceNo",  u"ipDevsNewIPNumber", u"ipDevsOldNewIPNumber"]
			if True:
				for var in indigo.variables.iter():
					if var.name.find(u"ipDevice") >-1:
						varExcludeSQLList.append(var.name)

			for v in varExcludeSQLList:
					var = indigo.variables[v]
					sp = var.sharedProps
					#self.indiLOG.log(30,u"setting /testing off: Var: {} sharedProps:{}".format(var.name.encode("utf8"), sp) )
					if u"sqlLoggerIgnoreChanges" in sp and sp[u"sqlLoggerIgnoreChanges"] == u"true": 
						continue
					#self.indiLOG.log(30,u"====set to off ")
					outOffV += var.name+u"; "
					sp[u"sqlLoggerIgnoreChanges"] = u"true"
					var.replaceSharedPropsOnServer(sp)
					if False: # check if it was written
						var = indigo.variables[v]
						sp = var.sharedProps
						self.indiLOG.log(20,u"switching off SQL logging for variable :{}: sp:{}".format(var.name.encode("utf8"), sp) )
					

			if len(outOffV) > 0: 
				self.indiLOG.log(20,u" \n")
				self.indiLOG.log(20,u"switching off SQL logging for variables\n :{}".format(outOffV.encode("utf8")) )
				self.indiLOG.log(20,u"switching off SQL logging for variables END\n")
			if len(outOffD) > 0: 
				self.indiLOG.log(20,u" \n")
				self.indiLOG.log(20,u"switching off SQL logging for devices/state[lastfingup]\n :{}".format(outOffD.encode("utf8")) )
				self.indiLOG.log(20,u"switching off SQL logging for devices END\n")
		except Exception as e:
			self.exceptionHandler(40, e)

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
			indigo.server.log( u"runConcurrentThread stopping plugin due to:  ::::: " + self.quitNOW + " :::::")
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)


		indigo.server.log( u"killing 2")
		os.system("/bin/kill -9 {}".format(self.myPID) )

		return




####-----------------   main loop          ---------
	def dorunConcurrentThread(self): 

		self.indigoCommand = u"none"
		self.pluginState   = u"run"
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


		self.timeOfStart= time.time()
		try:
			while self.quitNOW == u"no":

				if self.savePrefs > 0: 
					self.savePrefs = 0
					indigo.server.savePluginPrefs() 

				if self.redoAWAY >0:
					self.sleep(1)
					self.redoAWAY -=1
					if self.decideMyLog(u"Ping"): self.indiLOG.log(10,u"redo tests, check if device is back UP: {}".format(self.redoAWAY))
				else:
					xsleep=max(0.5,self.newSleepTime/10)  ## this is to enable a fast reaction to asynchronous events 
					nsleep = int(self.newSleepTime /xsleep)
					tt=time.time()
					for i in range(nsleep):
						if self.newSleepTime == 0: break
						if time.time()-tt > self.newSleepTime: break
						self.sleep( xsleep )
					self.newSleepTime = self.sleepTime
				#self.indiLOG.log(10,u"after sleeploop self.redoAWAY {}".format(self.redoAWAY) +"  nsleep{}".format(nsleep)+"  self.newSleepTime{}".format(self.newSleepTime))    
				#self.printEvents(printEvents="2")              
				if self.triggerFromPlugin:
					self.pluginCalled()
					self.checkTriggers()

				if self.indigoCommand != u"none" and self.indigoCommand != "":
					if self.indigoCommand == u"loadDevices": self.doLoadDevices()
					if self.indigoCommand == u"sort": self.doSortData()
					if self.indigoCommand == u"details": self.doDetails()
					if self.indigoCommand == u"ResetEVENTS": 
						self.resetEvents()
					if self.indigoCommand == u"ResetDEVICES":
						self.resetDevices()
						break
					if self.indigoCommand == u"PrintEVENTS":   self.printEvents()
					if self.indigoCommand == u"PrintWiFi":     self.printWiFi()
					if self.indigoCommand == u"PrintpiBeacon": self.printpiBeaconDevs()
					if self.indigoCommand == u"PrintUnifi":    self.printUnifiDevs()
				self.indigoCommand = u"none"

				checkTime=datetime.datetime.now().strftime(u"%H:%M:%S").split(u":")
				checkTime[0]=int(checkTime[0])
				checkTime[1]=int(checkTime[1])
				checkTime[2]=int(checkTime[2])
				if lastmin !=checkTime[1] and checkTime[2]>10 :
					self.checkcProfile()
					lastmin =checkTime[1]
					self.updateDeviceWiFiSignal()
					self.updateAllIndigoIpDeviceFromDeviceData([u"deviceInfo"])
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
							if dev.deviceTypeId != u"iAppleDeviceAuto": continue
							self.IDretList.append((dev.id,dev.name))
							self.iDevicesEnabled = True
					if self.iDevicesEnabled:
						self.pluginPrefs[u"iDevicesEnabled"] = True
					else:
						self.pluginPrefs[u"iDevicesEnabled"] = False



			
				if lastmin53 !=checkTime[1] and checkTime[1]%53 ==0 and checkTime[1] >0 and checkTime[2]>35 :
					lastmin53 =checkTime[1]
					self.doInbetweenPing(force=True)
					self.totalLoopCounter= 500
					
				if checkTime[0] == 0  and rebootMinute == checkTime[1] and self.totalLoopCounter > 200:
					self.refreshVariables()
					self.quitNOW = u"reboot after midnight"
										


				self.totalLoopCounter +=1
				if self.quitNOW !="no": break
				if self.updatePrefs:
					self.updatePrefs = False
					self.pluginPrefs[u"EVENTS"]	=	json.dumps(self.EVENTS)
					indigo.server.savePluginPrefs() 

				
				if time.time()-lastFingActivity > 280:
					self.indiLOG.log(40, u"seems that FING is not active - no change in data, restarting fing, seconds since last change: {}".format(time.time() - lastFingActivity))
					retCode = self.initFing(1)
					if retCode ==1:
						self.indiLOG.log(20,u"fing restarted successfully")
						fingNotActiveCounter =0
						self.sleep(5) ## give it some time
					else:
						if self.decideMyLog(u"Logic"): self.indiLOG.log(40, u"fing not active, tried to restart fing, did not work, stopping fingscan, may be wrong password \n   in plugins/fingscan/configure:  set password" )
						self.quitNOW = u"yes"
						break

				self.indigoNeedsUpdate=True
				if self.inbetweenPingType != u"0":
					self.throttlePing -=1
					if self.throttlePing <0 :
						if self.doInbetweenPing():
							if self.indigoNeedsUpdate:
								self.getIndigoIpDevicesIntoData()
								self.indigoNeedsUpdate=False
							self.compareToIndigoDeviceData(lastUpdateSource=u"ping")
							self.checkTriggers()


				if time.time() - lastdoWOL > repeatdoWOL:
					lastdoWOL = time.time()
					for theMAC in self.allDeviceInfo:
						devI = self.allDeviceInfo[theMAC]
						if u"useWakeOnLanSecs" in devI and devI[u"useWakeOnLanSecs"] >0:
							if time.time() - devI[u"useWakeOnLanLast"] > devI[u"useWakeOnLanSecs"]:
								devI[u"useWakeOnLanLast"] = time.time()
								self.sendWakewOnLanAndPing(theMAC, nBC= 1, waitForPing=10, countPings=1, waitBeforePing = 0.01, waitAfterPing = 0.0, calledFrom="loop")


				if self.routerType != u"0":
					self.WiFiChanged = {}
					errorMsg = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, rType=self.routerType)
					if errorMsg != u"ok":
						self.routerErrorCount+=1
						if self.routerErrorCount%100 < 3 and self.badWiFiTrigger[u"trigger"]<1:
							if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"WiFi Router does not return valid MAC numbers: "+errorMsg[:200])
							if self.routerErrorCount > 3600:  # about 1 hour
								self.indiLOG.log(20,u"WiFi Router: turning off WiFi Router query, you need to re-enable in configuration after router is back online")
								self.routerType = u"0"

					else:
						if self.routerErrorCount >0:
							if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"WiFi Router back up again")
						self.routerErrorCount = 0
						if 	self.checkIfBadWiFi():
							self.badWiFiTrigger[u"trigger"]=10
							if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"WiFi signal is weak ")#, triggering external python command "+self.indigoPreferencesPluginDir+"pings/doThisWhenWiFiIsBad.py")
							self.printWiFi()
							self.triggerEvent(u"badWiFi")
							self.resetbadWifiTrigger()
							
						if len(self.WiFiChanged)>0 or self.redoAWAY >0:
							if self.indigoNeedsUpdate:
								self.getIndigoIpDevicesIntoData()
								self.indigoNeedsUpdate=False
							self.compareToIndigoDeviceData(lastUpdateSource=u"WiFi")
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
					if self.quitNOW != u"no": break
					if self.indigoNeedsUpdate:
						self.getIndigoIpDevicesIntoData()
						self.indigoNeedsUpdate=False
					if self.quitNOW != u"no": break
					self.compareToIndigoDeviceData(lastUpdateSource=u"fingLog")
					if self.quitNOW != u"no": break
#						retCode = self.getIndigoIpVariablesIntoData()
					self.checkTriggers()
					try:
						if self.debugLevel !=[]: indigo.variable.updateValue(u"ipDevsLastUpdate", time.strftime(u"%H:%M:%S", time.localtime()) )
					except:
						self.quitNOW = u"Indigo variable error 9"#  someting must be wrong, restart
						if self.decideMyLog(u"Ping"): self.indiLOG.log(40,u"can not update variable ipDevsLastUpdate  \n  restarting fingscan" )
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
							indigo.variable.updateValue(u"ipDevsLastUpdate", time.strftime("%H:%M:%S", time.localtime()) )
						except Exception as exc:
							self.quitNOW = u" ipDevsLastUpdate can not be updated"#  something must be wrong, restart
							self.indiLOG.log(40, u"can not update variable ipDevsLastUpdate  \n  restarting fingscan\n exception code: {}".format(exc) )
							break
						if self.indigoNeedsUpdate:
							self.getIndigoIpDevicesIntoData()
							self.indigoNeedsUpdate=False
						if self.quitNOW != u"no": break
						retCode = self.compareToIndigoDeviceData(lastUpdateSource=u"fingData")
						if self.quitNOW != u"no": break
						retCode = self.compareToFingIfExpired(2)
						if self.quitNOW != u"no": break
						if not self.indigoInitialized:
							self.indiLOG.log(20,u"FINGSCAN initialized")
						self.indigoInitialized = True
#						retCode = self.getIndigoIpVariablesIntoData()
						self.checkTriggers()


			self.pluginState  = u"end"
			self.pluginPrefs[u"EVENTS"]	=	json.dumps(self.EVENTS)
			indigo.server.savePluginPrefs() 

			self.killFing(u"all")
			self.killPGM(u"/startfing.py")
		
			try:
				quitNowX = self.quitNow
			except:
				quitNowX = u"please setup config , waiting"
				self.indiLOG.log(40,u"-->  setup config, save, then a manual reload of plugin")

			self.indiLOG.log(20,u"--> while loop break  stopping ...  quitNOW was: {}".format(quitNowX) )
			if quitNowX.find(u"wait") >-1: 
				self.indiLOG.log(40,u"--> you have 2 minutes to fix config, before restart")
				for ii in range(20): 
					if self.passwordOK != u"0": 
						self.indiLOG.log(40,u"--> do a manual reload of plugin")
						break
					time.sleep(10)

			self.quitNOW = u"no"
			self.stopConcurrentCounter = 1
############ if there are PING jobs left  kill them
			self.killPing(u"all")
############ this will tell indigo to stop and restart 
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)
			return

			
		except self.StopThread:
			# do any cleanup here
			self.killPing(u"all")
			self.pluginPrefs[u"EVENTS"]	    =	json.dumps(self.EVENTS)
			self.pluginPrefs[u"piBeacon"]	=	json.dumps(self.piBeaconDevices)
			self.pluginPrefs[u"UNIFI"]	    =	json.dumps(self.unifiDevices)
			indigo.server.savePluginPrefs() 
			try:
				quitNowX = self.quitNow
			except Exception as e:
				self.exceptionHandler(40, e)
				quitNowX = u"please setup config"
				self.indiLOG.log(40,u"-->  exception StopThread triggered ... stopped,  quitNOW was: {}".format(quitNowX))
			self.quitNOW = u"no"
			############ if there are PING jobs left  kill them
		return








	############# main program  -- end ###########
	def	updateDeviceWiFiSignal(self,theMACin=u"all"):
		try:
			if theMACin == u"all":
				for theMAC in self.wifiMacList:
					if theMAC in self.ignoredMAC: continue
					if theMAC in self.allDeviceInfo:
						self.allDeviceInfo[theMAC][u"WiFi"] =  self.wifiMacList[theMAC][9]
						if self.wifiMacList[theMAC][0] ==u"Yes" and self.wifiMacList[theMAC][1] ==u"Yes" :
							self.allDeviceInfo[theMAC][u"WiFiSignal"] =  ("Sig[dBm]:"+("%4.0f"%self.wifiMacList[theMAC][2]  ).strip()
														+u",ave:"+(u"%4.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))).strip()
														#+",cnt:"+("%8.0f"%self.wifiMacList[theMAC][11]).strip()
														)
					if self.wifiMacList[theMAC][11] > 9999999: self.resetbadWifiTrigger() # reset counter if tooo big
			else:
				theMAC=theMACin
				if theMAC not in self.ignoredMAC:
					if theMAC in self.wifiMacList:
						if theMAC in self.allDeviceInfo:
							self.allDeviceInfo[theMAC][u"WiFi"] =  self.wifiMacList[theMAC][9]
							if self.wifiMacList[theMAC][0] == u"Yes" and self.wifiMacList[theMAC][1] == u"Yes" :
								self.allDeviceInfo[theMAC][u"WiFiSignal"] =  ((u"Sig[dBm]:%4.0f"%self.wifiMacList[theMAC][2]  ).strip()
															+ u","+("ave:%4.0f"%(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1))).strip()
															#+","+("cnt:%8.0f"%self.wifiMacList[theMAC][11]).strip()
															)
						if self.wifiMacList[theMAC][11] > 9999999: self.resetbadWifiTrigger() # reset counter if tooo big
		except Exception as e:
			self.exceptionHandler(40, e)

		return


	
##############################################
	def getWifiDevices(self, uid, pwd, ipN, rType="ASUS" ):
		resp =""
		try:
			if uid =="": return u"error no userid given"
			if pwd =="": return u"error no password given"
			if ipN =="": return u"error no ipNumber given"
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
					self.indiLOG.log(20,u" wifi data received not complete(len=0): {}".format(response))
				return u"error bad return from  curl {}".format(response)
			self.wifiErrCounter =0
			if rType==u"MERLIN378_54":
				response2 = response.split("wificlients") # this where the information starts:
				if len(response2) <2:
						self.indiLOG.log(20,u" wifi data received not complete(wificlients): {}".format(response2))
						return "error bad return from  curl {}".format(response2)
				noiseSplit =response.upper().split("\nDATAARRAY")
				if len(noiseSplit) <2:
						self.indiLOG.log(20,u" wifi data received not complete(no nDATAARRAY) {}".format(response2))
						return "error bad return from  curl {}".format(response2)
					
			else:
				response2 = response.split("\n----------------------------------------\n") # this where the information starts:
				if len(response2) < 3: 				return "error bad return from  curl {}".format(response2) # no valid data return, or bad password...
				noiseSplit =response.upper().split("NOISE:")
				if len(noiseSplit) < 2: 			return "error bad return from  curl {}".format(response2) # no valid data return, or bad password...

			fo2 =[u"",u"2GHz",u"5GHz"]
			for i in range(1,3):
				fiveORtwo =fo2[i]
				if rType==u"MERLIN378_54":
					nsplit=  noiseSplit[i].split(u";")[0].split(u"= ")
					if len(nsplit) < 2:
						if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u" wifi data received not complete (nsplit <2): {}".format(noiseSplit))
						continue
					self.wifiMacAv[u"noiseLevel"][fiveORtwo] = json.loads(nsplit[1])[3]
	#				if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u" wifi noiseLevel {}".format(fiveORtwo)+" {}".format(noiseSplit[i]))
				else:
					if len(noiseSplit) > 2:
						self.wifiMacAv[u"noiseLevel"][fiveORtwo] = noiseSplit[i].strip(u" ").split(u" ")[0]
				errorMSG=u" "
				if rType==u"ASUS":			errorMSG =self.parseWIFILogA(response2[i].split("\n\n")[0].split("\n"),fiveORtwo)
				elif rType==u"MERLIN":		errorMSG =self.parseWIFILogM(response2[i].split("\n\n")[0].split("\n"),fiveORtwo)
				elif rType==u"MERLIN378_54":	errorMSG =self.parseWIFILogM378(response2[i],fiveORtwo)
				else: return u"bad wifi defnition"
				if errorMSG !=u"ok": 			return errorMSG
				if self.wifiMacAv[u"numberOfCycles"][fiveORtwo] >3 and self.wifiMacAv[u"curDev"][fiveORtwo]>0. :
					if    abs(self.wifiMacAv[u"curAvSignal"][fiveORtwo] - self.wifiMacAv[u"sumSignal"][fiveORtwo]/self.wifiMacAv[u"numberOfDevices"][fiveORtwo]) > 5.:
						self.signalDelta[u"5"][fiveORtwo] +=1
					elif  abs(self.wifiMacAv[u"curAvSignal"][fiveORtwo] - self.wifiMacAv[u"sumSignal"][fiveORtwo]/self.wifiMacAv[u"numberOfDevices"][fiveORtwo]) > 2.:
						self.signalDelta[u"2"][fiveORtwo] +=1
					elif  abs(self.wifiMacAv[u"curAvSignal"][fiveORtwo] - self.wifiMacAv[u"sumSignal"][fiveORtwo]/self.wifiMacAv[u"numberOfDevices"][fiveORtwo]) > 1:
						self.signalDelta[u"1"][fiveORtwo] +=1
					if    self.totalLoopCounter >99999:
						if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u" wifi signals "+fiveORtwo+": sumSig:%8.0f sumNdev:%8.0f sumNMeas:%8.0f longAv%6.2f longnDevAv%6.2f thisAV:%6.2f thisnMeas:%3.1f del5:%5.0f del2:%5.0f del1:%5.0f"%
							(self.wifiMacAv[u"sumSignal"][fiveORtwo]
							,self.wifiMacAv[u"numberOfDevices"][fiveORtwo]
							,self.wifiMacAv[u"numberOfCycles"][fiveORtwo]
							,self.wifiMacAv[u"sumSignal"][fiveORtwo]/self.wifiMacAv[u"numberOfDevices"][fiveORtwo]
							,self.wifiMacAv[u"numberOfDevices"][fiveORtwo]/self.wifiMacAv[u"numberOfCycles"][fiveORtwo]
							,self.wifiMacAv[u"curAvSignal"][fiveORtwo]
							,self.wifiMacAv[u"curDev"][fiveORtwo]
							,self.signalDelta[u"5"][fiveORtwo]
							,self.signalDelta[u"2"][fiveORtwo]
							,self.signalDelta[u"1"][fiveORtwo]))
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
	
				
					
			#if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u" wifi curl time elapsed: %9.3f " %(time.time()-ticks))
		except Exception as e:
			self.indiLOG.log(40, u"error in  Line '%s' ;  error='%s'" % (sys.exc_info()[2].tb_lineno, e)+" wifi router reponse:{}".format(resp))
			return "error {}".format(resp)

		return "ok"  # [MACno][MACno,Associated,Authorized,RSSI,PSM,SGI,STBC,Tx rate,Rx rate,Connect Time]], "ok"


##############################################
	def resetbadWifiTrigger(self):
		try:
			for theMAC in self.wifiMacList:
				self.wifiMacList[theMAC][10] =0
				self.wifiMacList[theMAC][11] =0
			self.badWiFiTrigger[u"numberOfSecondsBad"] =0
			self.wifiMacAv=copy.deepcopy(emptyWifiMacAv)
		except Exception as e:
			self.exceptionHandler(40, e)
		return

##############################################
	def checkIfBadWiFi(self):
		try:
			if self.badWiFiTrigger[u"minNumberOfSecondsBad"] >998: return False
	#		if self.badWiFiTrigger[u"minNumberOfDevicesBad"] >998: return False
	#		if self.badWiFiTrigger[u"minSignalDrop"] >998: return False
			candidates =0
			for theMAC in self.wifiMacList:
				if self.wifiMacList[theMAC][0]!=u"Yes": continue
				if self.wifiMacList[theMAC][1]!=u"Yes": continue
				if self.wifiMacList[theMAC][9]!=u"2GHz": continue
				if self.wifiMacList[theMAC][11] < 15: continue
				if (
					(	(self.wifiMacList[theMAC][10]/max(self.wifiMacList[theMAC][11],1.)-self.wifiMacList[theMAC][2])  >   self.badWiFiTrigger[u"minSignalDrop"]	) 	or
					(	self.wifiMacList[theMAC][2] <  self.badWiFiTrigger[u"minWiFiSignal"]		)
				   ): candidates +=1

			if candidates < self.badWiFiTrigger[u"minNumberOfDevicesBad"]:
				self.badWiFiTrigger[u"numberOfSecondsBad"] =0
				self.badWiFiTrigger[u"trigger"] -=1
				return False

			if self.badWiFiTrigger[u"numberOfSecondsBad"] >0 : # trigger started?
				nSecBad = time.time() -self.badWiFiTrigger[u"numberOfSecondsBad"]
				if nSecBad%10 == 5:
					if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u" bad wifi signal for %3.0f seconds"%(nSecBad) )
				if (nSecBad) > self.badWiFiTrigger[u"minNumberOfSecondsBad"]:
					# this is the trigger
					self.badWiFiTrigger[u"trigger"] =10
					return True
				else:  # not yet, still waiting
					self.badWiFiTrigger[u"trigger"] -=1
					return False

			# start trigger timer
			self.badWiFiTrigger[u"numberOfSecondsBad"] = time.time()
			self.badWiFiTrigger[u"trigger"] -=1
		except Exception as e:
			self.exceptionHandler(40, e)
		return False


##############################################
	def parseWIFILogM378(self,wifiLog,fiveORtwo):
	# wdataarray24 = ["2","0","0","-92","8","D8:50:E6:CF:B4:E0","AP"];
	#wificlients24 = [["54:9F:13:3F:95:25",u"192.168.1.192","iPhone-20","-62",u"13", "72","  0:24:56"," S AU"],["FC:E9:98:49:BB:B9",u"192.168.1.155", "Kristins-iPhone","-65",u"24", "72","  0:37:11","PS AU"],["6C:AD:F8:26:69:9E",u"192.168.1.242","Chromecast","-50","72", "72","  0:38:00"," STAU"],["F0:7D:68:08:5F:D0",u"192.168.1.74","<not found>","-68","52", u"58","  0:38:02"," STAU"],["28:10:7B:0C:CB:4B",u"192.168.1.77","<not found>","-72","52", "72","  0:38:03"," STAU"],["F0:7D:68:06:F6:87",u"192.168.1.71","<not found>","-51","72", "72","  0:38:03"," STAU"],"-1"];
	#dataarray5 = ["5","0","0","-92",u"149/80","D8:50:E6:CF:B4:E4","AP"];
	#wificlients5 = [["F0:F6:1C:D5:51:16",u"192.168.1.215","<not found>","-69",u"24", "243","  0:36:53","PSTAU"],"-1"];

		try:
			if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"wifiLog:{}".format(wifiLog))
			wl= wifiLog.split(";")[0].split("= ")
			if len(wl) < 2:
				self.indiLOG.log(20,u"parseWIFILogM378 wifilog data not complete (wl=0): {}".format(wifiLog))
				return "error"
			try:
				wlist= json.loads(wl[1])
			except:
				self.indiLOG.log(20,u"parseWIFILogM378: wifilog data not complete( Wl json): {}".format(wifiLog))
				return "error"


			# now parse
			nDevices = len(wlist)-1
			if nDevices <1: return "ok"
			sumSignal =0.
			nDevConnected=0
			for thisDevice1 in wlist:
				if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"thisDevice1:{}".format(thisDevice1))
				thisDevice=[]

				if thisDevice1 =="-1": continue
				
				theMAC =thisDevice1[0]

				if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"thisDevice1>>"+ theMAC+"<<  {}".format(thisDevice1))
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
				self.wifiMacAv[u"sumSignal"][fiveORtwo]+= sumSignal
				self.wifiMacAv[u"numberOfDevices"][fiveORtwo] += nDevConnected
				self.wifiMacAv[u"curAvSignal"][fiveORtwo]= sumSignal/nDevConnected
				self.wifiMacAv[u"curDev"][fiveORtwo]= nDevConnected
				self.wifiMacAv[u"numberOfCycles"][fiveORtwo] +=1

		except Exception as e:
			self.exceptionHandler(40, e)
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
			pointerText = [u"MAC   ",u"IP Address   ",u"Name   ",u"  RSSI",u"   Rx",u"/",u"Tx Rate   ",u"Connected ",u"Flags"]
			thepointers=[]
	#		if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"line:"+ wifiLog[0])
			for pT in range(len(pointerText)):
				p= wifiLog[0].find(pointerText[pT])
				if p ==-1: return "error parsing return string "+pointerText[pT]
				thepointers.append(p)
			thepointers.append(len(wifiLog[0]))
	#		if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"line:{}".format(thepointers))

			# records should be ok..
			
			
			# now parse
			nDevices = len(wifiLog)
			if nDevices <1: return "ok"
			sumSignal =0.
			nDevConnected=0
			for line in range(1,nDevices):
	#			if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"line:"+ wifiLog[line])
				if len(wifiLog[line])< 20: continue

				thisDevice1=[]
				for p in range(1,len(pointerText)):
					thisDevice1.append( wifiLog[line][thepointers[p]: min(thepointers[p+1],len(wifiLog[line]))].strip() )
				
				theMAC = wifiLog[line][:17].strip(" ")

				if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"thisDevice1>>"+ theMAC+"<<  {}".format(thisDevice1))
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
				self.wifiMacAv[u"sumSignal"][fiveORtwo]+= sumSignal
				self.wifiMacAv[u"numberOfDevices"][fiveORtwo] += nDevConnected
				self.wifiMacAv[u"curAvSignal"][fiveORtwo]= sumSignal/nDevConnected
				self.wifiMacAv[u"curDev"][fiveORtwo]= nDevConnected
				self.wifiMacAv[u"numberOfCycles"][fiveORtwo] +=1

		except Exception as e:
			self.exceptionHandler(40, e)
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
			pointerText = [u"MAC",u"Associated",u"Authorized",u"   RSSI",u"PSM",u"SGI",u"STBC",u"Tx rate",u"Rx rate",u"Connect Time"]
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
				self.wifiMacAv[u"sumSignal"][fiveORtwo]+= sumSignal
				self.wifiMacAv[u"numberOfDevices"][fiveORtwo] += nDevConnected
				self.wifiMacAv[u"curAvSignal"][fiveORtwo]= sumSignal/nDevConnected
				self.wifiMacAv[u"curDev"][fiveORtwo]= nDevConnected
				self.wifiMacAv[u"numberOfCycles"][fiveORtwo] +=1
				
		except Exception as e:
			self.exceptionHandler(40, e)

		return  "ok"


##############################################
	def checkWIFIinfo(self):
		try:
			for mac in self.wifiMacList:
				self.wifiMacList[mac]=copy.deepcopy(emptyWiFiMacList)
			if self.routerType !="0":
				errorMSG = self.getWifiDevices(self.routerUID, self.routerPWD, self.routerIPn, rType=self.routerType)
				if errorMSG !="ok":
					if self.decideMyLog(u"WiFi"): self.indiLOG.log(20,u"Router wifi not reachable, userid password or ipnumber wrong?\n{}".format(errorMSG))
					return
				else:
					if self.decideMyLog(u"WiFi"): self.indiLOG.log(10,u"Router wifi data ok")
			else:
				self.routerUID	= ""
				self.routerPWD	= ""
				self.routerIPn	= ""


		except Exception as e:
			self.exceptionHandler(40, e)
		return



##############################################
	def checkDEVICES(self):
	#		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"checking devices")
	#					emptyAllDeviceInfo={"00:00:00:00:00:00":{"ipNumber":"0.0.0.0","timeOfLastChange":"timeOfLastChange","status":"down","nickName":"iphonexyz":"noOfChanges":u"0", "hardwareVendor":"", "deviceInfo":"","WiFi":"","deviceId":0,"deviceName":"","devExists":0}}
		try:
			for theMAC in self.allDeviceInfo:
				self.allDeviceInfo[theMAC][u"devExists"]=0

			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				devID=unicode(dev.id)
				theStates = dev.states.keys()
	#			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"device testing: "+dev.name)
	#			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"device states: MAC-{}".format(theStates))
				
				if "MACNumber" in theStates:
					anyUpdate = False
					theMAC = dev.states[u"MACNumber"]
					if theMAC =="": continue
					if not theMAC in self.allDeviceInfo: continue
					if theMAC in self.ignoredMAC: continue
					devI=self.allDeviceInfo[theMAC]
					devI[u"deviceId"]	=dev.id
					if dev.name != devI[u"deviceName"]:
						devI[u"nickName"] = dev.name
						devI[u"deviceName"]	=dev.name
						
					if theMAC in self.wifiMacList:
						self.updateDeviceWiFiSignal(theMAC)
						dev.description = theMAC+"-"+devI[u"WiFi"]+"-"+devI[u"WiFiSignal"]
						dev.replaceOnServer()
						#dev.updateStateOnServer(u"WiFi",				devI[u"WiFi"])
						self.addToStatesUpdateList(unicode(dev.id),"WiFi",				devI[u"WiFi"])
						try:
							string ="%5.1f"%self.wifiMacList[theMAC][2]
						except:
							string =unicode(self.wifiMacList[theMAC][2])
						
						#dev.updateStateOnServer(u"WiFiSignal",string)
						self.addToStatesUpdateList(unicode(dev.id),"WiFiSignal",string)
					
					if dev.states[u"ipNumber"] != devI[u"ipNumber"]:
						#dev.updateStateOnServer(u"ipNumber",			devI[u"ipNumber"])
						self.addToStatesUpdateList(unicode(dev.id),"ipNumber",			devI[u"ipNumber"])
						anyUpdate=True
					if dev.states[u"status"] != devI[u"status"]:
						#dev.updateStateOnServer(u"status",			devI[u"status"])
						self.addToStatesUpdateList(unicode(dev.id),"status",			devI[u"status"])
						anyUpdate=True
					if dev.states[u"nickName"] != devI[u"nickName"]:
						#dev.updateStateOnServer(u"nickName",			devI[u"nickName"])
						self.addToStatesUpdateList(unicode(dev.id),"nickName",			devI[u"nickName"])
						anyUpdate=True
					if unicode(dev.states[u"noOfChanges"]) != unicode(devI[u"noOfChanges"]):
						#dev.updateStateOnServer(u"noOfChanges",		int(devI[u"noOfChanges"]) )
						self.addToStatesUpdateList(unicode(dev.id),"noOfChanges",		int(devI[u"noOfChanges"]) )
						anyUpdate=True
					if dev.states[u"hardwareVendor"] !=devI[u"hardwareVendor"]:
						#dev.updateStateOnServer(u"hardwareVendor",	devI[u"hardwareVendor"])
						self.addToStatesUpdateList(unicode(dev.id),"hardwareVendor",	devI[u"hardwareVendor"])
						anyUpdate=True
					if dev.states[u"deviceInfo"] !=devI[u"deviceInfo"]:
						#dev.updateStateOnServer(u"deviceInfo",		devI[u"deviceInfo"])
						self.addToStatesUpdateList(unicode(dev.id),"deviceInfo",		devI[u"deviceInfo"])
						anyUpdate=True
					if dev.states[u"WiFi"] !=devI[u"WiFi"]:
						#dev.updateStateOnServer(u"WiFi",				devI[u"WiFi"])
						self.addToStatesUpdateList(unicode(dev.id),"WiFi",				devI[u"WiFi"])
						anyUpdate=True
					if "created" in dev.states and len(dev.states[u"created"]) < 10:
						self.addToStatesUpdateList(unicode(dev.id),"created",		datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
						anyUpdate=True
					usePing = devI[u"usePing"]
					if  unicode(devI[u"useWakeOnLanSecs"]) !="0":
						usePing +="-WOL:{}".format(devI[u"useWakeOnLanSecs"])
					if "usePing-WOL" in dev.states:
						if dev.states[u"usePing-WOL"] !=usePing:
							anyUpdate=True
							#dev.updateStateOnServer(u"usePing",			devI[u"usePing"])
							self.addToStatesUpdateList(unicode(dev.id),"usePing-WOL",			usePing)
					if "suppressChangeMSG" in dev.states:
						if dev.states[u"suppressChangeMSG"] != devI[u"suppressChangeMSG"]:
							anyUpdate=True
							#dev.updateStateOnServer(u"suppressChangeMSG",devI[u"suppressChangeMSG"])
							self.addToStatesUpdateList(unicode(dev.id),"suppressChangeMSG",devI[u"suppressChangeMSG"])
							
					if "lastFingUp" in dev.states:
						if "lastFingUp" not in devI:
							devI[u"lastFingUp"] = 0
						if dev.states[u"lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI[u"lastFingUp"])):
							anyUpdate=True
							#dev.updateStateOnServer(u"suppressChangeMSG",devI[u"suppressChangeMSG"])
							self.addToStatesUpdateList(unicode(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI[u"lastFingUp"])))
							
				

					if anyUpdate:
	#					self.indiLOG.log(20,u"state updates needed")
						#dev.updateStateOnServer(u"timeOfLastChange",	devI[u"timeOfLastChange"])
						self.addToStatesUpdateList(unicode(dev.id),"timeOfLastChange",	devI[u"timeOfLastChange"])
	#				else:
	#					self.indiLOG.log(20,u"state updates NOT  needed")




					pad = self.padStatusForDevListing(devI[u"status"])

					if dev.states[u"statusDisplay"] != (devI[u"status"]).ljust(pad)+devI[u"timeOfLastChange"]:
	#					self.indiLOG.log(20,u"statusDisplay updates needed")
						#dev.updateStateOnServer(u"statusDisplay",	(devI[u"status"]).ljust(pad)+devI[u"timeOfLastChange"])
						self.addToStatesUpdateList(unicode(dev.id),"statusDisplay",	(devI[u"status"]).ljust(pad)+devI[u"timeOfLastChange"])
					self.executeUpdateStatesList()
	#				else:
	#					self.indiLOG.log(20,u"statusDisplay updates NOT  needed")


					try:
						props = dev.pluginProps
						if props[u"address"] != self.formatiPforAddress(devI[u"ipNumber"]):
							if props[u"address"].split("-")[0] != self.formatiPforAddress(devI[u"ipNumber"]).split("-")[0] :
#							if props[u"address"].strip("-changed") != self.formatiPforAddress(devI[u"ipNumber"]).strip("-changed") :
								if "suppressChangeMSG" in dev.states:
									if dev.states[u"suppressChangeMSG"] =="show":
										if theMAC in self.doubleIPnumbers:
											if len(self.doubleIPnumbers[theMAC]) ==1:
												self.indiLOG.log(10,u"IPNumber changed,  old: {}".format(props[u"address"])+ "; new: {}".format(self.formatiPforAddress(devI[u"ipNumber"]))+ " for device MAC#: "+theMAC +" to switch off changed message: edit this device and select no msg")
											else:
												self.indiLOG.log(10,u"Multiple IPNumbers for device MAC#: "+theMAC+" -- {}".format(self.doubleIPnumbers[theMAC])+" to switch off changed message: edit this device and select no msg")
										else:
												self.indiLOG.log(10,u"IPNumber changed,  old: {}".format(props[u"address"])+ "; new: {}".format(self.formatiPforAddress(devI[u"ipNumber"]))+ " for device MAC#: "+theMAC+" to switch off changed message: edit this device and select no msg")
								indigo.variable.updateValue( u"ipDevsOldNewIPNumber", dev.name.strip(" ")+u"/"+theMAC.strip(" ")+"/"+props[u"address"].strip(" ")+"/"+self.formatiPforAddress(devI[u"ipNumber"]).strip(" ") )

							props[u"address"]=self.formatiPforAddress(devI[u"ipNumber"])
							dev.replacePluginPropsOnServer(props)
	#					else:
	#						self.indiLOG.log(10,u"address updates NOT  needed"å)
					except:
						if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"props check did not work")
					devI[u"devExists"]	=1

			for theMAC in self.allDeviceInfo:
				if theMAC =="": continue
				devI = self.allDeviceInfo[theMAC]
				if devI[u"devExists"] == 0 and self.acceptNewDevices and theMAC not in self.ignoredMAC:

	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u" creating device {}".format(devI))
					try:
						if devI[u"nickName"] !="iphone-xyz" and devI[u"nickName"] !="":
							theName=devI[u"nickName"]
							try:
								dev = indigo.devices[theName]
								test= dev.id
								theName = "MAC_"+theMAC
							except:
								theName=devI[u"nickName"]
						else:
							theName = "MAC_"+theMAC
						indigo.device.create(
							protocol=indigo.kProtocol.Plugin,
							address=self.formatiPforAddress(devI[u"ipNumber"]),
							name=theName,
							description=theMAC,
							pluginId="com.karlwachs.fingscan",
							deviceTypeId="IP-Device",
							props = {"setUsePing":"doNotUsePing","setuseWakeOnLan":0,"setExpirationTime":0},
							folder=self.indigoDeviceFolderID
							)
						dev = indigo.devices[theName]
						self.addToStatesUpdateList(unicode(dev.id),"MACNumber",		theMAC)
						self.addToStatesUpdateList(unicode(dev.id),"ipNumber",			devI[u"ipNumber"])
						self.addToStatesUpdateList(unicode(dev.id),"timeOfLastChange",	devI[u"timeOfLastChange"])
						self.addToStatesUpdateList(unicode(dev.id),"status",			devI[u"status"])
						self.addToStatesUpdateList(unicode(dev.id),"nickName",			devI[u"nickName"])
						self.addToStatesUpdateList(unicode(dev.id),"noOfChanges",		int(devI[u"noOfChanges"]) )
						self.addToStatesUpdateList(unicode(dev.id),"hardwareVendor",	devI[u"hardwareVendor"])
						self.addToStatesUpdateList(unicode(dev.id),"deviceInfo",		devI[u"deviceInfo"])
						self.addToStatesUpdateList(unicode(dev.id),"suppressChangeMSG", devI[u"suppressChangeMSG"])
						self.addToStatesUpdateList(unicode(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						self.addToStatesUpdateList(unicode(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						if theMAC in self.wifiMacList:
							self.addToStatesUpdateList(unicode(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])

						self.updateDeviceWiFiSignal(theMAC)
						usePing = devI[u"usePing"]
						if  unicode(devI[u"useWakeOnLanSecs"]) !="0":
							usePing +="-WOL:{}".format(devI[u"useWakeOnLanSecs"])
						if "usePing-WOL" in dev.states: self.addToStatesUpdateList(unicode(dev.id),"usePing-WOL",			usePing)
						self.addToStatesUpdateList(unicode(dev.id),"WiFi",				devI[u"WiFi"])
						pad = self.padStatusForDevListing(devI[u"status"])
						self.addToStatesUpdateList(unicode(dev.id),"statusDisplay",	devI[u"status"].ljust(pad)+devI[u"timeOfLastChange"])
						self.addToStatesUpdateList()
						devI[u"deviceId"]	=dev.id
						devI[u"deviceName"]	=dev.name
						devI[u"devExists"]	=1
						if devI[u"WiFi"] !="":
							dev.description = theMAC+"-"+devI[u"WiFi"]+"-"+devI[u"WiFiSignal"]
							dev.replaceOnServer()
					except:
						pass
						
				try:
					if self.wifiMacAv[u"curAvSignal"][u"2GHz"] !=0.:
						indigo.variable.updateValue(u"averageWiFiSignal_2GHz", "%5.1f"%self.wifiMacAv[u"curAvSignal"][u"2GHz"] )
					if self.wifiMacAv[u"curAvSignal"][u"5GHz"] !=0.:
						indigo.variable.updateValue(u"averageWiFiSignal_5GHz", "%5.1f"%self.wifiMacAv[u"curAvSignal"][u"5GHz"] )
				except:
					pass
			self.executeUpdateStatesList()        
		except Exception as e:
			self.exceptionHandler(40, e)
			
		return

##############################################
	def checkIfDevicesChanged(self):
		try:
	#		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u" check if devices changed..")
			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				#if  dev.pluginId.find("com.karlwachs.fingscan") == -1 :continue
				devID=unicode(dev.id)
				theStates = dev.states.keys()
				update = 0
				if "MACNumber" in theStates:
					theMAC = dev.states[u"MACNumber"]
					if theMAC =="": continue
					if not theMAC in self.allDeviceInfo: continue
					devI=self.allDeviceInfo[theMAC]
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u" checking MAC/values: "+theMAC+":{}".format(devI))
					devI[u"deviceId"]	=dev.id
					if dev.name != devI[u"deviceName"]:
						update = 1
						devI[u"nickName"] 	= dev.name
						devI[u"deviceName"]	= dev.name
						#dev.updateStateOnServer(u"nickName",	devI[u"nickName"])
						self.addToStatesUpdateList(unicode(dev.id),"nickName",	devI[u"nickName"])
					if dev.states[u"hardwareVendor"] != devI[u"hardwareVendor"]:
						devI[u"hardwareVendor"]		=dev.states[u"hardwareVendor"]
						update = 2
					if dev.states[u"deviceInfo"] != devI[u"deviceInfo"]:
						devI[u"deviceInfo"]			=dev.states[u"deviceInfo"]
					if dev.states[u"WiFi"] != devI[u"WiFi"]:
						test 					=dev.states[u"WiFi"]
						if test ==0:devI[u"WiFi"]=""
						else:		devI[u"WiFi"]=dev.states[u"WiFi"]
						update = 3
				if update>0:
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u" updating MAC: "+theMAC)
					self.updateIndigoIpVariableFromDeviceData(theMAC)
		except Exception as e:
			self.exceptionHandler(40, e)
		return

##############################################
	def updateAllIndigoIpDeviceFromDeviceData(self,statesToUdate=[u"all"]):
		devcopy = copy.deepcopy(self.allDeviceInfo)
		for theMAC in devcopy:
			if theMAC in self.ignoredMAC: continue
			self.updateIndigoIpDeviceFromDeviceData(theMAC,statesToUdate)
##############################################
	def updateIndigoIpDeviceFromDeviceData(self,theMAC,statesToUpdate,justStatus=""):
#		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"updating dev and states: "+ theMAC+"/{}".format(statesToUpdate))
		if theMAC in self.ignoredMAC: return
		try:
			try:
				devI=self.allDeviceInfo[theMAC]
			except:
				self.indiLOG.log(40, u"deleteIndigoIpDevicesData: MAC Number: "+ theMAC+" information does not exist in allDeviceInfo")
				return
			try:
				devId =devI[u"deviceId"]
				dev = indigo.devices[devId]
				if justStatus!="": # update only status for quick turn around
					#dev.updateStateOnServer(u"status",justStatus)
					self.addToStatesUpdateList(unicode(dev.id),"status",justStatus)
					pad = self.padStatusForDevListing(justStatus)
					#dev.updateStateOnServer(u"statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", localtime()))
					self.addToStatesUpdateList(unicode(dev.id),"statusDisplay",(justStatus).ljust(pad)+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
					if "lastFingUp" in dev.states:
						if dev.states[u"lastFingUp"] != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI[u"lastFingUp"])):
							self.addToStatesUpdateList(unicode(dev.id),"lastFingUp",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(devI[u"lastFingUp"])))
					self.executeUpdateStatesList()
					self.allDeviceInfo[theMAC][u"status"] =justStatus
					return
			except:
	# create new device
				name="MAC-"+theMAC,
				if "nickName" in devI:
					if devI[u"nickName"] !="": 	name =devI[u"nickName"]
					if True or self.acceptNewDevices:
						try:
							indigo.device.create(
								protocol=indigo.kProtocol.Plugin,
								address=self.formatiPforAddress(devI[u"ipNumber"]),
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
						self.addToStatesUpdateList(unicode(dev.id),"MACNumber",		theMAC)
						self.addToStatesUpdateList(unicode(dev.id),"ipNumber",			devI[u"ipNumber"])
						self.addToStatesUpdateList(unicode(dev.id),"timeOfLastChange",	devI[u"timeOfLastChange"])
						self.addToStatesUpdateList(unicode(dev.id),"status",			devI[u"status"])
						self.addToStatesUpdateList(unicode(dev.id),"nickName",			devI[u"nickName"])
						self.addToStatesUpdateList(unicode(dev.id),"noOfChanges",		int(devI[u"noOfChanges"]) )
						self.addToStatesUpdateList(unicode(dev.id),"hardwareVendor",	devI[u"hardwareVendor"])
						self.addToStatesUpdateList(unicode(dev.id),"deviceInfo",		devI[u"deviceInfo"])
						self.addToStatesUpdateList(unicode(dev.id),"WiFi",				devI[u"WiFi"])
						self.addToStatesUpdateList(unicode(dev.id),"usePing-WOL",		devI[u"usePing"]+"-{}".format(devI[u"useWakeOnLanSecs"]))
						self.addToStatesUpdateList(unicode(dev.id),"suppressChangeMSG", devI[u"suppressChangeMSG"])
						self.addToStatesUpdateList(unicode(dev.id),"lastFingUp",        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						self.addToStatesUpdateList(unicode(dev.id),"created",           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
						if theMAC in self.wifiMacList:
							self.addToStatesUpdateList(unicode(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])
				
						pad = self.padStatusForDevListing(devI[u"status"])
						self.addToStatesUpdateList(unicode(dev.id),"statusDisplay",	(devI[u"status"]).ljust(pad)+devI[u"timeOfLastChange"])
						devI[u"deviceId"]	=dev.id
						devI[u"deviceName"]	=dev.name
						devI[u"devExists"]	=1
						self.executeUpdateStatesList()

				return
			
			if len(statesToUpdate)>0:
				anyUpdate=False
	# update old device
				if "ipNumber" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states[u"ipNumber"] !=devI[u"ipNumber"]:
						self.addToStatesUpdateList(unicode(dev.id),"ipNumber",			devI[u"ipNumber"])
						anyUpdate=True
				if "status" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states[u"status"] !=devI[u"status"]:
						self.addToStatesUpdateList(unicode(dev.id),"status",			devI[u"status"])
						anyUpdate=True

				if "nickName" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states[u"nickName"] !=devI[u"nickName"]:
						self.addToStatesUpdateList(unicode(dev.id),"nickName",			devI[u"nickName"])
						anyUpdate=True
				if "noOfChanges" in statesToUpdate or statesToUpdate[0]=="all":
					if unicode(dev.states[u"noOfChanges"]) != unicode(devI[u"noOfChanges"]):
						self.addToStatesUpdateList(unicode(dev.id),"noOfChanges",		int(devI[u"noOfChanges"]) )
						anyUpdate=True
				if "hardwareVendor" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states[u"hardwareVendor"] !=devI[u"hardwareVendor"]:
						self.addToStatesUpdateList(unicode(dev.id),"hardwareVendor",	devI[u"hardwareVendor"])
						anyUpdate=True
				if "deviceInfo" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states[u"deviceInfo"] !=devI[u"deviceInfo"]:
						self.addToStatesUpdateList(unicode(dev.id),"deviceInfo",		devI[u"deviceInfo"])
						anyUpdate=True
				if "WiFi" in statesToUpdate or statesToUpdate[0]=="all":
					if dev.states[u"WiFi"] !=devI[u"WiFi"]:
						self.addToStatesUpdateList(unicode(dev.id),"WiFi",				devI[u"WiFi"])
						if theMAC in self.wifiMacList:
							self.addToStatesUpdateList(unicode(dev.id),"WiFiSignal",		"%5.1f"%self.wifiMacList[theMAC][2])
						anyUpdate=True

				usePing = devI[u"usePing"]
				if  unicode(devI[u"useWakeOnLanSecs"]) !="0":
					usePing +="-WOL:{}".format(devI[u"useWakeOnLanSecs"])
				if "usePing-WOL" in statesToUpdate or statesToUpdate[0]=="all":
					if "usePing-WOL" in dev.states:
						if dev.states[u"usePing-WOL"] != usePing:
							anyUpdate=True
							self.addToStatesUpdateList(unicode(dev.id),"usePing-WOL",			usePing)
				if "suppressChangeMSG" in statesToUpdate or statesToUpdate[0]=="all":
					if "suppressChangeMSG" in dev.states:
						if dev.states[u"suppressChangeMSG"] !=devI[u"suppressChangeMSG"]:
							anyUpdate=True
							self.addToStatesUpdateList(unicode(dev.id),"suppressChangeMSG",			devI[u"suppressChangeMSG"])

				if anyUpdate:
	#				self.indiLOG.log(20,u"state updates needed")
					self.addToStatesUpdateList(unicode(dev.id),"timeOfLastChange",	devI[u"timeOfLastChange"])
	#			else:
	#				self.indiLOG.log(20,u"state updates NOT  needed")

				if statesToUpdate[0]=="all" or "status" in statesToUpdate or "ipNumber" in statesToUpdate or "WiFi" in statesToUpdate:
					pad = self.padStatusForDevListing(devI[u"status"])
					if (devI[u"status"]).ljust(pad)+devI[u"timeOfLastChange"] !=dev.states[u"statusDisplay"]:
						self.addToStatesUpdateList(unicode(dev.id),"statusDisplay",	(devI[u"status"]).ljust(pad)+devI[u"timeOfLastChange"])
					props = dev.pluginProps
					try:
						if props[u"address"] != self.formatiPforAddress(devI[u"ipNumber"]):
							if "suppressChangeMSG" in dev.states:
								if dev.states[u"suppressChangeMSG"] =="show":
									self.indiLOG.log(10,u"MAC#:"+theMAC  +" -- old IP: {}".format(props[u"address"])+ ";  new IP number: {}".format(self.formatiPforAddress(devI[u"ipNumber"]))+" to switch off changed message: edit this device and select no msg")
							indigo.variable.updateValue( "ipDevsOldNewIPNumber", dev.name.strip(" ")+u"/"+theMAC.strip(" ")+"/"+props[u"address"].strip(" ")+"/"+self.formatiPforAddress(devI[u"ipNumber"]).strip(" ") )
							props[u"address"]=self.formatiPforAddress(devI[u"ipNumber"])
							dev.replacePluginPropsOnServer(props)
					except:
						if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"props check did not work")

				devI[u"deviceId"]		=dev.id
				devI[u"deviceName"]		=dev.name
				devI[u"devExists"]		=1


				self.executeUpdateStatesList()


				if theMAC in self.wifiMacList or "WiFi" in statesToUpdate:
					self.updateDeviceWiFiSignal()
					if devI[u"WiFi"] =="":
						dev.description = theMAC
					else:
						dev.description = theMAC+"-"+devI[u"WiFi"]+"-"+devI[u"WiFiSignal"]
					dev.replaceOnServer()


		except Exception as e:
			self.exceptionHandler(40, e)
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

	#		if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u" list of devices to be deleted: %s"%theList)

			for theMAC in theList:
				try:
					devI=self.allDeviceInfo[theMAC]
					devID =devI[u"deviceId"]
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"deleting device information for theMAC/deviceName "+ theMAC+"/{}".format(self.allDeviceInfo[theMAC][u"deviceName"]))
					indigo.device.delete(devID)
				except:
					if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"deleteIndigoIpDevicesData: theMAC/deviceID/deviceName"+ theMAC+"/{}".format(devID)+"/{}".format(self.allDeviceInfo[theMAC][u"deviceName"])+" device does not exist")
				
				try:
					devV=self.indigoIpVariableData[theMAC]
					indigo.variable.delete(u"ipDevice"+devV[u"ipDevice"])
				except:
					if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"deleteIndigoIpDevicesData: theMAC "+ theMAC+ " information does not exist in indigoIpVariableData")


				try:
					theName= devI[u"deviceName"]
					del self.allDeviceInfo[theMAC]
				except:
					if self.decideMyLog(u"Ping"): self.indiLOG.log(20,u"deleteIndigoIpDevicesData: name/MAC "+ theName+"/"+theMAC+" information does not exist in allDeviceInfo")

	#			if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u"deleted device MAC: "+theMAC)

			self.getIndigoIpVariablesIntoData()
		except Exception as e:
			self.exceptionHandler(40, e)
		return

##############################################
	def getIndigoIpDevicesIntoData(self):  # do this once in the beginning..
	
		try:
			theMAC=""
			for dev in indigo.devices.iter("com.karlwachs.fingscan"):
				if not dev.enabled: continue
				theStates = dev.states.keys()
				if "MACNumber" in theStates:
					theMAC = dev.states[u"MACNumber"]
					if theMAC =="": continue
					update =0
					if not theMAC in self.allDeviceInfo:
						self.allDeviceInfo[theMAC] = copy.deepcopy(emptyAllDeviceInfo)
						update=5
					devI=self.allDeviceInfo[theMAC]
					props = dev.pluginProps
					if dev.name != devI[u"deviceName"]:
						update = 1
						devI[u"nickName"] 	= dev.name
						devI[u"deviceName"]	= dev.name
						#dev.updateStateOnServer(u"nickName",	devI[u"nickName"])
						self.addToStatesUpdateList(unicode(dev.id),"nickName",	devI[u"nickName"])
					if dev.states[u"hardwareVendor"] != devI[u"hardwareVendor"]:
						devI[u"hardwareVendor"]		= dev.states[u"hardwareVendor"]
						update = 2
					if dev.states[u"deviceInfo"] != devI[u"deviceInfo"]:
						devI[u"deviceInfo"]		= dev.states[u"deviceInfo"]
						update = 3
					devI[u"ipNumber"]			= dev.states[u"ipNumber"]
					devI[u"timeOfLastChange"]	= dev.states[u"timeOfLastChange"]
					devI[u"status"]				= dev.states[u"status"]
					devI[u"nickName"]			= dev.states[u"nickName"]
					devI[u"noOfChanges"]		= int(dev.states[u"noOfChanges"])
					devI[u"hardwareVendor"]		= dev.states[u"hardwareVendor"]
					devI[u"deviceInfo"]			= dev.states[u"deviceInfo"]
					try:    devI[u"lastFingUp"]	= devI[u"lastFingUp"]	= time.mktime( datetime.datetime.strptime(dev.states[u"lastFingUp"],"%Y-%m-%d %H:%M:%S").timetuple()  )
					except: devI[u"lastFingUp"]	= time.time()
					if u"setWiFi" not in devI:   devI[u"setWiFi"] =copy.deepcopy(emptyAllDeviceInfo[u"setWiFi"])
					devI[u"WiFi"]				= dev.states[u"WiFi"]
					devI[u"deviceId"]			= dev.id
					devI[u"deviceName"]			= dev.name
					devI[u"devExists"]			= 1

					if "setUsePing"      in props: 
						devI[u"usePing"]           = props[u"setUsePing"]
					else:
						devI[u"usePing"]           = "doNotUsePing"

					if "setuseWakeOnLan" in props: 
						devI[u"useWakeOnLanSecs"]  = int(props[u"setuseWakeOnLan"])
					else:
						devI[u"useWakeOnLanSecs"]  = 0

					if "setExpirationTime" in props: 
						devI[u"expirationTime"]  = float(props[u"setExpirationTime"])
					else:
						devI[u"expirationTime"]  = 90


					if "suppressChangeMSG" in dev.states:
						devI[u"suppressChangeMSG"]			=dev.states[u"suppressChangeMSG"]
					else:
						devI[u"suppressChangeMSG"]			="show"
				if update>0:
	#				if self.decideMyLog(u"Logic"): self.indiLOG.log(20,u" updating MAC: "+theMAC)
					self.updateIndigoIpVariableFromDeviceData(theMAC)
				self.executeUpdateStatesList()    

		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, u"MAC#                           "+ theMAC)
			try:
				self.indiLOG.log(40, u" indigoIpVariableData:     {}".format(self.indigoIpVariableData[theMAC]))
			except:
				self.indiLOG.log(40, u" indigoIpVariableData: all {}".format(self.indigoIpVariableData))
			try:
				self.indiLOG.log(40, u" allDeviceInfo:            {}".format(self.allDeviceInfo[theMAC]))
			except:
				self.indiLOG.log(40, u" allDeviceInfo:  all       {}".format(self.allDeviceInfo))
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
					devV[u"ipDevice"] = unicode(self.indigoEmpty[0])
				except:
					self.indiLOG.log(40,  u"updateIndigoIpVariableFromDeviceData indigoEmpty not initialized" +unicode(self.indigoEmpty))
					self.indiLOG.log(40,  u"updateIndigoIpVariableFromDeviceData theMAC# " +unicode(theMAC))
					self.indiLOG.log(40,  u"updateIndigoIpVariableFromDeviceData indigoIpVariableData" +unicode(self.indigoIpVariableData[theMAC]))
					devV[u"ipDevice"] = u"1"
				self.indigoNumberOfdevices +=1
				devV[u"index"] = self.indigoNumberOfdevices-1
				self.indigoIndexEmpty -= 1  # one less empty slot
				if len(self.indigoEmpty) > 0: self.indigoEmpty.pop(0) ##  remove first empty from list


			devI=self.allDeviceInfo[theMAC]
			updstr  =self.padMAC(theMAC)
			updstr +=u";"+self.padIP(devI[u"ipNumber"])
			updstr +=u";"+self.padDateTime(devI[u"timeOfLastChange"])
			updstr +=u";"+devI[u"status"]
			updstr +=u";"+self.padStatus(devI[u"status"])+self.padNoOfCh(devI[u"noOfChanges"])
			updstr +=u";"+self.padNickName(devI[u"nickName"])
			updstr +=u";"+self.padVendor(devI[u"hardwareVendor"])
			updstr +=u";"+self.padDeviceInfo(devI[u"deviceInfo"])
			updstr +=u";"+devI[u"WiFi"].rjust(5)
			updstr +=u";"+devI[u"WiFiSignal"].rjust(10)
			updstr +=u";"+(devI[u"usePing"]+"-{}".format(devI[u"useWakeOnLanSecs"])).rjust(13)+";"
			theValue = updstr.split(";")

			devV[u"ipNumber"]			= theValue[1].strip()
			devV[u"timeOfLastChange"]	= theValue[2].strip()
			devV[u"status"]				= theValue[3].strip()
			try:
				devV[u"noOfChanges"]	= int(theValue[4].strip())
			except:
				devV[u"noOfChanges"]	= 0
			devV[u"nickName"]			= theValue[5].strip()
			devV[u"hardwareVendor"]		= theValue[6].strip()
			devV[u"deviceInfo"]			= theValue[7].strip()
			devV[u"WiFi"]				= theValue[8].strip()
			devV[u"usePing"]			= theValue[9].strip()


			diff = False
			try:
				curr = indigo.variables[u"ipDevice"+devV[u"ipDevice"]].value.split(";")
			except:
				self.indiLOG.log(40, u" updating ipDevice "+devV[u"ipDevice"]+" does not exist , (re)creating")
				
				curr =[]
			
			old = updstr.split(";")
			if len(old) ==len(curr):
				for i in range(len(curr)):
					if i==2: continue# skip the date field.
					if curr[i] != old[i]:
	#					self.indiLOG.log(20,u" updating ipDevice "+devV[u"ipDevice"]+"  "+curr[i]+"!="+old[i])
						diff= True
						break
			else:
				diff=True
			if diff:
				try:
					indigo.variable.updateValue(u"ipDevice"+devV[u"ipDevice"], updstr)
				except:
					indigo.variable.create(u"ipDevice"+devV[u"ipDevice"], updstr,self.indigoVariablesFolderID)
	#		else:
	#			self.indiLOG.log(20,u"not updating ipDevice"+devV[u"ipDevice"])

		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, u"MAC#                           "+ theMAC)
			try:
				self.indiLOG.log(40, u" indigoIpVariableData:     {}".format(self.indigoIpVariableData[theMAC]))
			except:
				self.indiLOG.log(40, u" indigoIpVariableData: all {}".format(self.indigoIpVariableData))
			try:
				self.indiLOG.log(40, u" allDeviceInfo:            {}".format(self.allDeviceInfo[theMAC]))
			except:
				self.indiLOG.log(40, u" allDeviceInfo:  all       {}".format(self.allDeviceInfo))


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
				devI[u"ipNumber"]			= devV[u"ipNumber"].strip()
				devI[u"timeOfLastChange"]	= devV[u"timeOfLastChange"].strip()
				devI[u"status"]				= devV[u"status"].strip()
				try:
					devI[u"noOfChanges"]	= int(devV[u"noOfChanges"])
				except:
					devI[u"noOfChanges"]	= 0
				devI[u"nickName"]			= devV[u"nickName"].strip()
				devI[u"hardwareVendor"]		= devV[u"hardwareVendor"].strip()
				devI[u"deviceInfo"]			= devV[u"deviceInfo"].strip()
				if "WiFi" not in devV:
					devI[u"WiFi"]			= ""
				else:
					devI[u"WiFi"]			= devV[u"WiFi"].strip()
					
				devI[u"usePing"]			= u"usePing"
				devI[u"usePing"]		    = ""
				devI[u"useWakeOnLanSecs"]	= 0
				if "usePing"  in devV:
					usePing = (devV[u"usePing"].strip()).split("-")
					devI[u"usePing"]			 = usePing[0]
					if len(usePing) == 2:
						devI[u"useWakeOnLanSecs"] = int(usePing[1])
						
				if "deviceId" not in devI: 		devI[u"deviceId"]=""
				if "deviceName" not in devI:	devI[u"deviceName"]=""

		except Exception as e:
			self.exceptionHandler(40, e)
			self.indiLOG.log(40, u"MAC# "+ theMAC+" indigoIpVariableData: {}".format(self.indigoIpVariableData[theMAC]))
			self.indiLOG.log(40, u"MAC# "+ theMAC+" allDeviceInfo:        {}".format(self.allDeviceInfo[theMAC]))

		return 0



	####################  utilities -- start  #######################

########################################
	def padStatusForDevListing(self,status):
		if	 status == u"up": 		return 11
		elif status == u"expired":	return 8
		elif status == u"down":		return 9
		elif status == u"changed":	return 8
		elif status == u"double":	return 8
		else: 						return 10
########################################
	def column(self,matrix, i):
		return [row[i] for row in matrix]
	
########################################
	def padDateTime(self,xxx):
		return u"   "+xxx+u"   "
	
########################################
	def padVendor(self,ddd):
		if ddd == None:
			return " ".ljust(25)
		ddd= ddd.replace("\n","")
		theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
		blanks = " "
		for kk in range(1,theNumberOfBlanks):
			blanks += u" "
		return u"  "+ddd+blanks
	
########################################
	def padDeviceInfo(self,ddd):
		if ddd == None:
			return " ".ljust(25)
		ddd= ddd.replace("\n","")
		theNumberOfBlanks =min(25,max(0,(20-len(ddd))*2))
		blanks = u" "
		for kk in range(1,theNumberOfBlanks):
			blanks += u" "
		return u"  "+ddd+blanks
	
########################################
	def padIP(self,xxx):
		if xxx == None:
			return " ".ljust(25)
		ddd = len(xxx)
		pad = u"   "
		if ddd == 11:	pad = u"       "
		if ddd == 12:	pad = u"     "
		return u"   "+xxx+pad
	
########################################
	def padNickName(self,ddd):
		if ddd == None:
			return " ".ljust(32)
		theNumberOfBlanks =min(32,max(0,(17-len(ddd))*2))
		blanks = u"   "
		for kk in range(1,theNumberOfBlanks):
			blanks += u" "
		return u"   "+ddd+blanks
	
########################################
	def padNoOfCh(self,xxx):
		if xxx == None:
			return " ".ljust(25)
		xxx=int(xxx)
		if xxx < 10:	return u"    {}".format(xxx)+u"               "
		if xxx < 100:	return u"    {}".format(xxx)+u"             "
		if xxx < 1000:	return u"    {}".format(xxx)+u"           "
		if xxx < 10000:	return u"    {}".format(xxx)+u"         "
		return u"    {}".format(xxx)+u"       "
	
	
########################################
	def padStatus(self,xxx):
		if xxx == u"up":		return u"       "
		if xxx == u"down":	 	return u"   "
		if xxx == u"expired":	return u""
		if xxx == u"changed":	return u""
		if xxx == u"double":	return u" "
		return u" "
	
########################################
	def padMAC(self,xxx):
		yyy =unicode(xxx)
		NofA = yyy.count(u"A")
		NofB = yyy.count(u"B")
		NofC = yyy.count(u"C")
		NofD = yyy.count(u"D")
		NofE = yyy.count(u"E")
		NofF = yyy.count(u"F")
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
		if   int(digit) < 10:	last = u"00"
		elif int(digit) < 100:	last = u"0"
		else: last =""
		ips[3] = last+digit
		if u"changed" in ipN:
			ips[3] += u"-changed"
		elif u"double" in ipN:
			ips[3] += u"-double"
		else:
			ips[3] += u"        "
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
			sself.exceptionHandler(40, e)
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
								actualChanged.append({u"key":key,u"value":value})
								if key == u"status": indigo.variable.updateValue(u"ipDevsLastDevChangedIndigoName",dev.name)
						else:            
							if value != newStates[key]:
								newStates[key] = value
						if key == u"status":
							if value in [u"up",u"ON"] :
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							elif value in [u"down",u"off"]:
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
							elif value in [u"expired",u"REC"] :
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
							msg = {u"action":u"event", "id":unicode(dev.id), u"name":dev.name, u"state":"status", u"valueForON":u"up", u"newValue":value.lower()}
							if self.decideMyLog(u"BC"): self.indiLOG.log(10,u"executeUpdateStatesDict  msg added :" + unicode(msg))
							self.sendBroadCastEventsList.append(msg)
							

					if  newStates == "":
						self.updateStatesList[devId]={}           
						if actualChanged !=[]:
							#indigo.server.log("%14.3f"%time.time()+u"  "+dev.name.ljust(25)  + unicode(actualChanged)) 
							dev.updateStatesOnServer(actualChanged)
							
			if len(self.sendBroadCastEventsList) >0: self.sendBroadCastNOW()
			if  newStates != "":  
				return newStates              
		except Exception as e:
			self.exceptionHandler(40, e)


	####----------------- if FINGSCAN is enabled send update signal  ---------
	def sendBroadCastNOW(self):
		try:
			if self.decideMyLog(u"BC"): self.indiLOG.log(10,u"sendBroadCastNOW enter" )
			x = ""
			if  self.enableBroadCastEvents == u"0":
				self.sendBroadCastEventsList = []
				return x
			if self.sendBroadCastEventsList == []:  
				return x
				
			msg = copy.copy(self.sendBroadCastEventsList)
			self.sendBroadCastEventsList = []
			if len(msg) >0:
				msg ={u"pluginId":self.pluginId,u"data":msg}
				try:
					if self.decideMyLog(u"BC"): self.indiLOG.log(10,u"updating BC with " + unicode(msg) )
					indigo.server.broadcastToSubscribers(u"deviceStatusChanged", json.dumps(msg))
				except Exception as e:
					self.exceptionHandler(40, e)

		except Exception as e:
				self.exceptionHandler(40, e)
		return x

####-------------------------------------------------------------------------####
	def isValidIP(self, ip0):
		ipx = ip0.split(u".")
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
		if inPath[-1] !=u"/": inPath +=u"/"
		return inPath


####-----------------	 ---------
	def decideMyLog(self, msgLevel):
		try:
			if msgLevel	 == u"all" or u"all" in self.debugLevel:	 return True
			if msgLevel	 == ""	 and u"all" not in self.debugLevel:	 return False
			if msgLevel in self.debugLevel:							 return True
			return False
		except Exception as e:
				self.exceptionHandler(40, e)
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
			max_range = broadcast
			max_range[-1] -= 1

			return {"netMask":"{}".format(".".join(map(str, mask))),
					"netWorkId":"{}".format(".".join(map(str, network))),
					"broadcast":"{}".format(".".join(map(str, broadcast))),
					"hostRange":"{}".format("{} - {}".format(".".join(map(str, min_range)), ".".join(map(str, max_range)))),
					"maxHosts":(2 ** sum(map(lambda x: sum(c == '1' for c in x), negation_Mask))) - 2}	   
		except Exception as e:
			self.exceptionHandler(40, e)


####-----------------  print to logfile or indigo log  ---------
	def myLog(self,	 text="", mType="", errorType="", showDate=True, destination=""):
		   
	
		try:
				if errorType == u"smallErr":
					self.plugin.errorLog(u"------------------------------------------------------------------------------")
					self.plugin.errorLog(text)
					self.plugin.errorLog(u"------------------------------------------------------------------------------")

				elif errorType == u"bigErr":
					self.plugin.errorLog(u"==================================================================================")
					self.plugin.errorLog(text)
					self.plugin.errorLog(u"==================================================================================")

				elif mType == "":
					indigo.server.log(text)
				else:
					indigo.server.log(text, type=mType)

		except	Exception as e:
			self.exceptionHandler(40, e)
			indigo.server.log(text)


####-------------------------------------------------------------------------####
	def readPopen(self, cmd, pid = False):
		try:
			if type(cmd) == type([]):
				ret, err = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			else:
				ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			return ret.decode('utf_8'), err.decode('utf_8')
		except Exception as e:
			self.exceptionHandler(40, e)


####-------------------------------------------------------------------------####
	def exceptionHandler(self, level, exception_error_message):

		try: 
			if u"{}".format(exception_error_message).find("None") >-1: return 
		except: 
			pass

		filename, line_number, method, statement = traceback.extract_tb(sys.exc_info()[2])[-1]
		#module = filename.split('/')
		log_message = "'{}'".format(exception_error_message )
		log_message +=  "\n{} @line {}: '{}'".format(method, line_number, statement)
		self.indiLOG.log(level, log_message)



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


