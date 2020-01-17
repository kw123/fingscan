#

import sys, os, subprocess
import time
import datetime
import json
import logging
import logging.handlers
global logging, logger
import platform
import fcntl

#  /usr/bin/python2.7 '/Library/Application Support/Perceptive Automation/Indigo 7.4/Plugins/fingscan.indigoPlugin/Contents/Server Plugin/startfing.py' '/Library/Application Support/Perceptive Automation/Indigo 7.4/Preferences/Plugins/com.karlwachs.fingscan/paramsForStart' & 
####### main pgm / loop ############
#################################
def startFing():
	global indigoPreferencesPluginDir
	global logfileName, logLevel,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword,  netwType
		
	try:
	## first check which versio we are running
	## get opsys
	## get fing version
		opsys, fingVersion = checkVersion()

		if  opsys < 10.15 and fingVersion < 5:
			formatFING = " -o table,csv,fing.data log,csv,fing.log "
			if theNetwork !="":
				cmd ="cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword + "' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+formatFING+" > /dev/null 2>&1 &"
			else:
				cmd ="cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword + "' | sudo -S '"+fingEXEpath+"' "+formatFING+" > /dev/null 2>&1 &"
			os.system(cmd)
			logger.log(20,"fing.bin launched, version: {},  opsys: {}".format(fingVersion, opsys))
			time.sleep(0.5)
			stopPGM('/bin/sh /usr/local/bin/fing')
			return 

		elif fingVersion >= 5:
			doFingV5(fingVersion, opsys)

		elif opsys >= 10.15 and fingVersion < 5:
			logger.log(40,"miss match version of opsys:{} and fing:{} you need to upgrade FING to 64 bits".format(opsys,fingversion))

	except  Exception, e:
		logger.log(40,"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
	

def checkVersion():
	global fingEXEpath
	try:
		opsys	=  platform.mac_ver()[0].split(".")
		opsys	= float(opsys[0]+"."+opsys[1])
		#logger.log(20,"{}".format(opsys))
		cmd 	= "echo '"+yourPassword+ "' | sudo -S "+fingEXEpath+" -v"
		ret 	= subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0].strip("\n").split(".")
		fingVersion	= float(ret[0]+"."+ret[1])
		#logger.log(20,"{}  {}".format(ret, fingVersion))
		return opsys, fingVersion
	except  Exception, e:
		logger.log(40,"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
	return 0,0

def doFingV5(fingVersion, opsys):
	global indigoPreferencesPluginDir
	global logfileName, logLevel,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType
	global startCommand

	buffer 		= 32000
	yearTag		= datetime.datetime.now().strftime("%Y/%m")
	netTag		= theNetwork.split(".")[0]+"."

	logger.log(20,"into doFingV5 with yearTag: {}, netTag: {}, version: {};  opsys: {}".format(yearTag, netTag, fingVersion, opsys) )
	try:
			fingFormat= " -o table,csv,  log,csv "
			if theNetwork !="":
				cmd ="cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword + "' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+fingFormat+" &"
			else:
				cmd ="cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword + "' | sudo -S '"+fingEXEpath+"' "+fingFormat+" &"

			ListenProcessFileHandle =""
			for ii in range(3):
				ListenProcessFileHandle = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				##pid = ListenProcessFileHandle.pid
				##self.myLog( text=u" pid= " + unicode(pid) )
				msg = unicode(ListenProcessFileHandle.stderr)
				if msg.find("open file") == -1:	# try this again
					self.indiLOG.log(40,"uType {}; IP#: {}; error connecting {}".formaat(uType, ipNumber, msg) )
					self.sleep(20)
					continue
				break
			time.sleep(2)
			#stopPGM('sudo -S /usr/local/bin/fing')
			#stopPGM('/bin/sh /usr/local/bin/fing')

			if ListenProcessFileHandle =="": return 
			logger.log(20,"fing.bin launched")

			flags = fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_GETFL)  # get current p.stdout flags
			fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

			dataLines =[]
			logLines  = []
			lastLogLine = ""
			while True:
				time.sleep(0.1)
				try:
					lines = os.read(ListenProcessFileHandle.stdout.fileno(), buffer) ## = 32k
				except	Exception, e:
					time.sleep(0.2)
					if unicode(e).find("[Errno 35]") > -1:	 # "Errno 35" is the normal response if no data, if other error stop and restart
						msgSleep = 0.4 # nothing new, can wait
					else:
						if len(unicode(e)) > 5:
							out = "os.read(ListenProcessFileHandle.stdout.fileno(),{})  in Line {} has error={}\n ip:{}  type: {}".format(buffer, sys.exc_traceback.tb_lineno, e, ipNumber,uType)
							try: out+= "  fileNo: {}".format(ListenProcessFileHandle.stdout.fileno() )
							except: pass
							if unicode(e).find("[Errno 22]") > -1:  # "Errno 22" is  general read error "wrong parameter"
								out+= " ..      try lowering read buffer parameter" 
								logger.log(30,out)
							else:
								logger.log(40,out)
						lastForcedRestartTimeStamp = 1 # this forces a restart of the listener
					continue

				if lines.find("Discovery stopped") >-1:
					logger.log(40,"restart of startfing due to discovery stppped message from fing.bin")
	 				os.system(startCommand)
					
					

				if len(lines) > 10:  
					for line in lines.split("\n"): 
						if line.find(netTag) == 0:
							dataLines.append(line)
						if line.find(yearTag) == 0:
							logLines.append(line)

					#logger.log(20,"lines {}".format(lines) )
					#logger.log(20,"data {}".format(dataLines) )
					#logger.log(20,"log  {}".format(logLines) )

				if lines.find("Discovery round completed") > -1:
					##logger.log(20,"Discovery round completed {}".format(dataLines) )
					dataOut = ""
					for line in dataLines:
						dataOut += line+"\n"
					if dataOut !="":
						f=open(indigoPreferencesPluginDir+fingDataFileName,"w")
						f.write(dataOut)
						f.close()
						dataOut = ""
						dataLines = []
				else:
					logOut = ""
					for line in logLines:
						if lastLogLine != line:
							logOut += line+"\n"
							lastLogLine = line
					if logOut !="":
						f=open(indigoPreferencesPluginDir+fingLogFileName,"a")
						f.write(logOut)
						f.close()
						logOut = ""
					logLines = []
	

	
	except  Exception, e:
		logger.log(40,"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
	return 


#################################
def stopOldPGMs():
	global indigoPreferencesPluginDir
	global logfileName, logLevel,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType
	stopPGM('Plugin/startfing.py', mypid = str(os.getpid()) )
	stopPGM('/usr/local/lib/fing/fing.bin')
	stopPGM('/usr/local/bin/fing')

#################################
def stopPGM(pgm, mypid =""):
	global indigoPreferencesPluginDir
	global logfileName, logLevel,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType

	pids = subprocess.Popen("ps -ef | grep '"+pgm+"' | grep -v grep | awk '{print $2}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0]
	pids = pids.split("\n")
	for pid in pids:
		if len(pid) < 3: continue # 100
		if pid == mypid: continue # dont kill myself
		cmd = "echo '" + yourPassword + "' | sudo -S /bin/kill -9 " + str(pid) +" > /dev/null 2>&1 &"
		#logger.log(20,u"  FING kill cmd:" + cmd)
		ret= subprocess.Popen(cmd,shell=True) # kill fing

####### main pgm / loop ############
global indigoPreferencesPluginDir
global logfileName, logLevel,  fingDataFileName, fingLogFileName, fingErrorFileName
global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType
global startCommand

startCommand 				= "/usr/bin/python2.7 '"+sys.argv[0] +"' '" +sys.argv[1]+"'"
pluginDir					= sys.argv[0].split("startFing.py")[0]
indigoDir					= pluginDir.split("Plugins/")[0]
indigoPreferencesPluginDir 	= indigoDir+"Preferences/Plugins/com.karlwachs.fingscan/"
logfileName 				= indigoDir+"Logs/com.karlwachs.fingscan/plugin.log"
fingDataFileName			= "fing.data"
fingLogFileName				= "fing.log"

f 							= open(sys.argv[1],"r")
params 						= json.loads(f.read())
f.close()


fingEXEpath					= params["fingEXEpath"]
logLevel 					= params["logLevel"]
yourPassword 				= params["yourPassword"][3:-3][::-1] 
theNetwork 					= params["theNetwork"]
netwType 					= params["netwType"]
macUser 					= params["macUser"]




logging.basicConfig(level=logging.DEBUG, filename= logfileName,format='%(module)-23s L:%(lineno)3d Lv:%(levelno)s %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


#
if logLevel > 20:
	logger.setLevel(logging.ERROR)
else:
	logger.setLevel(logging.DEBUG)
logger.log(20,"========= start   @ {}   =========== ".format(datetime.datetime.now()))



stopOldPGMs()

#cmd = "cd '"++"'; echo '"+yourPassword+ "' | sudo /usr/sbin/chown "+macUser+" *"
#os.system(cmd) 
#cmd = "echo '"+yourPassword+ "' | sudo /bin/chmod -R 777 '"+indigoPreferencesPluginDir+"'"
#os.system(cmd) 


cmd ="echo '" +yourPassword + "' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingDataFileName+"'"
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#logger.log(40,cmd)
cmd ="echo '" +yourPassword + "' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingLogFileName+"'"
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#logger.log(40,cmd)
cmd ="echo 0 > '"+indigoPreferencesPluginDir+fingLogFileName+"'"

	
startFing()
logger.log(20,"========= stopped @ {}   =========== ".format(datetime.datetime.now()))
sys.exit(0)		
