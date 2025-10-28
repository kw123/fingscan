#

import sys, os, subprocess
import time
import datetime
import json
import logging
import logging.handlers
global logging, logger
import platform
import copy
import fcntl
try:
	str("x")
except:
	str = str
import traceback


#  /usr/bin/python2.7 '/Library/Application Support/Perceptive Automation/Indigo 7.4/Plugins/fingscan.indigoPlugin/Contents/Server Plugin/startfing.py' '/Library/Application Support/Perceptive Automation/Indigo 7.4/Preferences/Plugins/com.karlwachs.fingscan/paramsForStart' & 
####### main pgm / loop ############
#################################
def initPGM():
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword,  netwType
	global pluginPID
		
	try:
		# kill old pgms
		stopOldPGMs()
		
		# init output files 
		dopgmLaunch("echo '" +yourPassword + "' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingDataFileName+"'")
		dopgmLaunch("echo '" +yourPassword + "' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingLogFileName+"'")
		dopgmLaunch("echo 0 > '"+indigoPreferencesPluginDir+fingLogFileName+"'")

		## first check which versions we are running
		## get opsys
		## get fing version
		
		opsys, fingVersion = checkVer()

		if  opsys < 10.15 and fingVersion < 5:
			formatFING = " -o table,csv,fing.data log,csv,fing.log "
			if theNetwork !="":
				cmd = "cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword +"' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+formatFING+" > /dev/null 2>&1 &"
				if showPassword:
					cmdSHOW = cmd
				else:
					cmdSHOW = "cd '"+indigoPreferencesPluginDir+"';echo 'xxxxx' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+formatFING+" > /dev/null 2>&1 &"

			else:
				cmd = "cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword +"' | sudo -S '"+fingEXEpath+"' "+formatFING+" > /dev/null 2>&1 &"
				if showPassword:
					cmdSHOW = cmd
				else:
					cmdSHOW = "cd '"+indigoPreferencesPluginDir+"';echo 'xxxx' | sudo -S '"+fingEXEpath+"' "+formatFING+" > /dev/null 2>&1 &"

			os.system(cmd)
			if logLevel > 0: logger.log(20, pluginPID+"> initPGM; fing.bin launched, version: {},  opsys: {}, with command:\n{}".format(fingVersion, opsys, cmdSHOW))
			time.sleep(0.5)
			# kill mnother processes only leave '/usr/local/lib/fing/fing.bin' running
			stopPGM('/bin/sh /usr/local/bin/fing')
			stopPGM('sudo -S /usr/local/bin/fing')
			return 

		elif fingVersion >= 5:
			doFingV5(fingVersion, opsys)

		elif opsys >= 10.15 and fingVersion < 5:
			logger.log(40,"initPGM; miss match version of opsys:{} and fing:{} you need to upgrade FING to 64 bits".format(opsys,fingversion))
		else:
			logger.log(40,"initPGM; miss match version of opsys:{} and fing:{}  please upgrade".format(opsys,fingversion))


	except  Exception as e:
		exceptionHandler(40,e)
	

#################################
def checkVer():
	global fingEXEpath
	global pluginPID
	try:
		opsys	=  platform.mac_ver()[0].split(".")
		opsys	= float(opsys[0]+"."+opsys[1])
		cmd 	= "echo '"+yourPassword+ "' | sudo -S "+fingEXEpath+" -v"
		if showPassword:
			cmdSHOW = cmd
		else:
			cmdSHOW = "echo 'xxxxx' | sudo -S "+fingEXEpath+" -v"
		ret, err = readPopen(cmd)
		ret = ret.strip("\n").split(".")
		if len(ret) > 1:
			fingVersion	= float(ret[0]+"."+ret[1])
			if logLevel > 0: logger.log(20, pluginPID+"> checkVer; opsys: {};   fingVersion:{} from cmd:{};   ".format(opsys, fingVersion, cmdSHOW))
			return opsys, fingVersion
		else:
			logger.log(20, pluginPID+"> checkVer; bad return for cmd:{} \nret:{}\err:{}  ".format(cmdSHOW, ret, err))
			return 0,0

	except  Exception as e:
		exceptionHandler(40,e)
	return 0,0

#################################
def doFingV5(fingVersion, opsys):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
	global startCommand
	global pluginPID
	firstFile = True
	buffer 		= 32000
	yearTag		= datetime.datetime.now().strftime("%Y/%m")
	netTag		= theNetwork.split(".")[0]+"."

	if logLevel > 0: logger.log(20, pluginPID+"> doFingV5; start with yearTag: {}, netTag: {}, version: {};  opsys: {}".format(yearTag, netTag, fingVersion, opsys) )
	try:
			fingFormat= " -o table,csv,  log,csv "
			if theNetwork !="":
				cmd = "cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword + "' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+fingFormat+" &"
				if showPassword:
					cmdSHOW = cmd
				else:
					cmdSHOW =  "cd '"+indigoPreferencesPluginDir+"';echo 'xxxxx' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+fingFormat+" &"
			else:
				cmd = "cd '"+indigoPreferencesPluginDir+"';echo '" +yourPassword + "' | sudo -S '"+fingEXEpath+"' "+fingFormat+" &"
				if showPassword:
					cmdSHOW = cmd
				else:
					cmdSHOW = "cd '"+indigoPreferencesPluginDir+"';echo 'xxxxx' | sudo -S '"+fingEXEpath+"' "+fingFormat+" &"

			if logLevel > 0: logger.log(20, pluginPID+"> doFingV5; fing start command: {}".format(cmdSHOW)) 
			ListenProcessFileHandle = ""
			for ii in range(5):
				ListenProcessFileHandle = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				##pid = ListenProcessFileHandle.pid
				err = str(ListenProcessFileHandle.stderr)
				msg = str(ListenProcessFileHandle.stdout)
				if logLevel > 0: logger.log(20, pluginPID+"> doFingV5; try# {}; msg  {} -- err: {}, ListenProcessFileHandle:{}".format(ii+1, msg, err, str(ListenProcessFileHandle)) )
				if msg.find("open file") == -1 and msg.find("io.BufferedReader name=") == -1 :	# try this again
					logger.log(40,"doFingV5; error connecting , try again to read file")
					if ii < 1:	time.sleep(10)
					else:		time.sleep(5)
					continue
				break
			time.sleep(2)
			stopPGM('sudo -S /usr/local/bin/fing')
			stopPGM('/bin/sh /usr/local/bin/fing')

			if str(ListenProcessFileHandle) == "": 
				logger.log(40, luginPID+"> doFingV5; could not start fing exiting; ListenProcessFileHandle empty " )
				return 
				
			time.sleep(2)
			listOfFingPids = isFingRunning()
			if logLevel > 0: logger.log(20, pluginPID+"> doFingV5; fing.bin launched with pids:{}".format(listOfFingPids))

			flags = fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_GETFL)  # get current p.stdout flags
			fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

			dataLines = []
			logLines  = []
			lastLogLine = ""
			lastDataReceived = time.time() - 10
			while True:
				try:
					time.sleep(0.1)
					lines = ""
					try:
						lines = os.read(ListenProcessFileHandle.stdout.fileno(), buffer).decode('utf_8') ## = 32k
					except	Exception as e:
						time.sleep(0.2)
						if str(e).find("[Errno 35]") > -1:	 # "Errno 35" is the normal response if no data, if other error stop and restart
							msgSleep = 0.4 # nothing new, can wait
						else:
							if len(str(e)) > 5:
								out = "os.read(ListenProcessFileHandle.stdout.fileno(),{})  in Line {} has error={}\n ip:{}  type: {}".format(buffer, sys.exc_info()[2].tb_lineno, e, ipNumber,uType)
								try: out+= "  fileNo: {}".format(ListenProcessFileHandle.stdout.fileno() )
								except: pass
								if str(e).find("[Errno 22]") > -1:  # "Errno 22" is  general read error "wrong parameter"
									out+= " ..      try lowering read buffer parameter" 
									logger.log(30, pluginPID+"> doFingV5; "+out)
								else:
									logger.log(40, pluginPID+"> doFingV5; "+out)
							lastForcedRestartTimeStamp = 1 # this forces a restart of the listener
						continue
	
					if lines.find("Discovery stopped") > -1:
						logger.log(40, pluginPID+"> doFingV5; restart of startfing due to 'discovery stoppped' message from fing.bin")
						os.system(startCommand)
						
						
	
					dataComplete = False
					if firstFile and logLevel > 0: logger.log(20, pluginPID+"> doFingV5; nchar:{},  raw data:{} ...".format(len(lines), lines[:200]))
					if len(lines) > 10:  
						linesSplit = lines.split("\n")
						lastDataReceived = time.time()
						for line in linesSplit: 
							if line.find(netTag) == 0:
								dataLines.append(line)
							if line.find(yearTag) == 0:
								logLines.append(line)
	
						#logger.log(20, pluginPID+"> lines {}".format(lines) )
						#logger.log(20, pluginPID+"> data {}".format(dataLines) )
						#logger.log(20, pluginPID+"> log  {}".format(logLines) )
	
						if lines.find("Discovery round completed") > -1:
							dataComplete = True
							
						if firstFile and logLevel > 0: logger.log(20, pluginPID+"> doFingV5; #of lines received: {:4d} dataComplete:{:1}, line0: {}".format(len(lines), dataComplete,  linesSplit[0]))
		
						##logger.log(20, pluginPID+"> Discovery round completed {}".format(dataLines) )
						if dataComplete:
							dataOut = ""
							nLines = 0
							for line in dataLines:
								nLines +=1
								dataOut += line+"\n"
							if firstFile and logLevel > 0: logger.log(20, pluginPID+"> doFingV5; compiling data for first file: # of bytes:{}, lines:{}, fname:{}".format(len(dataOut), nLines, indigoPreferencesPluginDir+fingDataFileName))
							if dataOut != "":
								f = open(indigoPreferencesPluginDir+fingDataFileName,"w")
								f.write(dataOut)
								f.close()
								dataOut = ""
								dataLines = []
								if firstFile and logLevel > 0: logger.log(20, pluginPID+"> doFingV5; written datafile: {}".format(indigoPreferencesPluginDir+fingDataFileName))
								firstFile = False
							else:
								if firstFile and logLevel > 0: logger.log(20, pluginPID+"> doFingV5; no datafile written , no data ")
						else:
							logOut = ""
							for line in logLines:
								if lastLogLine != line:
									logOut += line+"\n"
									lastLogLine = line
							if logOut != "":
								if firstFile and logLevel > 0: logger.log(20, pluginPID+"> doFingV5; new log line: {}".format(lastLogLine))
								f = open(indigoPreferencesPluginDir+fingLogFileName,"a")
								f.write(logOut)
								f.close()
								logOut = ""
							logLines = []
						
					if time.time() - lastDataReceived > 30:
						if firstFile and logLevel > 0: logger.log(30, pluginPID+"> doFingV5; no data received for {} secs".format(time.time() - lastDataReceived))
						lastDataReceived = time.time()
				except  Exception as e:
					exceptionHandler(40,e)
	

	
	except  Exception as e:
		exceptionHandler(40,e)
	return 


####-------------------------------------------------------------------------####
def readPopen(cmd):
	global pluginPID
	try:
		if type(cmd) == type([]):
			ret, err = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		else:
			ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		return ret.decode('utf_8'), err.decode('utf_8')
	except Exception as e:
		exceptionHandler(40,e)

####-----------------  exception logging ---------
def exceptionHandler(level, exception_error_message):
	global pluginPID

	try: 
		if "{}".format(exception_error_message).find("None") >-1: return 
	except: 
		pass

	filename, line_number, method, statement = traceback.extract_tb(sys.exc_info()[2])[-1]
	#module = filename.split('/')
	log_message = pluginPID+"> '{}'".format(exception_error_message )
	log_message +=  "\n{} @line {}: '{}'".format(method, line_number, statement)
	logger.log(level, log_message)


########################################
def isFingRunning():
	global pluginPID
	#if self.decideMyLog("Logic", Second="StartFi"): self.indiLOG.log(10, "testFing; testing if FING is running ")


	#ret, err = self.readPopen("ps -ef | grep fing.bin | grep -v grep | grep -v fingscan| grep -v Indigo | awk '{print$2,$3}'")
	ret, err = readPopen("ps -ef | grep /fing | grep -v grep | grep -v fingscan| grep -v Indigo ")
	pids = ret.strip("\n")
	pidLines = pids.split("\n")
	fingPids = []
	parentPids = []
	if logLevel > 0: logger.log(20, pluginPID+ "> isFingRunning; running pids found = {}".format(pidLines))
	
	for kk in range(len(pidLines)):
		p = pidLines[kk].split()
		if logLevel > 0: logger.log(20, pluginPID+ "> isFingRunning; p:{}".format(p))
		if len(p) < 3: continue
		fingPids.append(p[1])
		if p[2] == "1": continue
		if p[2] == "0": continue
		if p[2] == " ": continue
		parentPids.append(p[2])
		# pids has the process ids #  of fing and parent shell as simple string have removed PID # 1 = the root
	return fingPids, parentPids

#################################
def stopOldPGMs():
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
	global pluginPID
	stopPGM('Plugin/startfing.py', mypid = str(os.getpid()) )
	stopPGM('/usr/local/lib/fing/fing.bin')
	stopPGM('/usr/local/bin/fing')

#################################
def stopPGM(pgm, mypid=""):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
	global pluginPID
	#cmd = "ps -ef | grep '{}' | grep -v grep | awk '{{print $2}}'".format(pgm)
	cmd = "ps -ef | grep '{}' | grep -v grep".format(pgm)
	if logLevel > 0: logger.log(20, pluginPID+"> stopPGM; get pids of old FING processes ignornig PID={};  w cmd:{}".format(mypid , cmd))
	ret, err = readPopen(cmd)
	pidLines = ret.split("\n")
	if logLevel > 0: logger.log(20, pluginPID+"> stopPGM; pgm:{} pids found:{}".format(pgm, pidLines))
	for ppp in pidLines:
		ppp = ppp.split()
		if len(ppp) < 3: continue # 100
		pid = ppp[1]
		if pid == mypid: 
				if logLevel > 0: logger.log(20, pluginPID+"> stopPGM; not killing myself: PID={}".format(mypid))
				continue # dont kill myself
		cmd = "echo '{}' | sudo -S /bin/kill -9 {} > /dev/null 2>&1 &".format(yourPassword, pid)
		if showPassword:
			cmdSHOW = cmd
		else:
			cmdSHOW = "echo '{}' | sudo -S /bin/kill -9 {} > /dev/null 2>&1 &".format("XXXXX", pid)

		if logLevel > 0: logger.log(20, pluginPID+"> stopPGM; kill cmd:{}".format(cmdSHOW))
		ret = str(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)) # kill fing
		#if not showPassword: ret = ret.replace(yourPassword,"xxxxxx")
		#if logLevel > 0: logger.log(20, pluginPID+"> {}".format(ret))

#################################
def dopgmLaunch(cmd):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
	global startCommand
	global pluginPID

	if showPassword:
		cmdSHOW = cmd
	else:
		cmdSHOW = cmd.replace(yourPassword, "xxxxx")
	if logLevel > 0:  logger.log(20, pluginPID+"> dopgmLaunch:"+ cmdSHOW)
	ret = str(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
	if not showPassword: ret = ret.replace(yourPassword,"xxxxxx")
	#if logLevel > 0:  logger.log(20, pluginPID+"> "+ ret)
	return 



####### main pgm / loop ############
global indigoPreferencesPluginDir
global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
global pluginPID
global startCommand


pluginDir					= sys.argv[0].split("startFing.py")[0]
indigoDir					= pluginDir.split("Plugins/")[0]
indigoPreferencesPluginDir 	= indigoDir+"Preferences/Plugins/com.karlwachs.fingscan/"
logfileName 				= indigoDir+"Logs/com.karlwachs.fingscan/plugin.log"
fingDataFileName			= "fing.data"
fingLogFileName				= "fing.log"


f 							= open(sys.argv[1],"r")
params 						= json.loads(f.read())
f.close()


pythonPath					= params["pythonPath"]
fingEXEpath					= params["fingEXEpath"]
logLevel 					= params["logLevel"]
yourPassword 				= params["ppp"][3:-3][::-1] 
showPassword				= params["showPassword"]
theNetwork 					= params["theNetwork"]
netwType 					= params["netwType"]
macUser 					= params["macUser"]
pluginPID 					= str(params["pluginPID"])
startCommand 				=  "{} '{}' '{}'".format(pythonPath, sys.argv[0], sys.argv[1])


logging.basicConfig(level=logging.DEBUG, filename= logfileName,format='%(module)-10s %(asctime)s L:%(lineno)3d: %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


#
logger.setLevel(logging.DEBUG)
xxx = copy.copy(params)
if not showPassword:
	xxx["ppp"]	= "xxxxx"
logger.log(20, pluginPID+"> Main; ========= start   @ {}   ===========;  params:{}".format(datetime.datetime.now(), xxx))


	
initPGM()
if logLevel > 0: logger.log(20, pluginPID+"> Main; ========= stopped @ {}   =========== ".format(datetime.datetime.now()))

sys.exit(0)		
