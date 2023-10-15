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
	unicode("x")
except:
	unicode = str
import traceback


#  /usr/bin/python2.7 '/Library/Application Support/Perceptive Automation/Indigo 7.4/Plugins/fingscan.indigoPlugin/Contents/Server Plugin/startfing.py' '/Library/Application Support/Perceptive Automation/Indigo 7.4/Preferences/Plugins/com.karlwachs.fingscan/paramsForStart' & 
####### main pgm / loop ############
#################################
def startFing():
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword,  netwType
		
	try:
	## first check which versio we are running
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
			if logLevel > 0: logger.log(20,"fing.bin launched, version: {},  opsys: {}, with command:\n{}".format(fingVersion, opsys, cmdSHOW))
			time.sleep(0.5)
			# kill mnother processes only leave '/usr/local/lib/fing/fing.bin' running
			stopPGM(u'/bin/sh /usr/local/bin/fing')
			stopPGM('sudo -S /usr/local/bin/fing')
			return 

		elif fingVersion >= 5:
			doFingV5(fingVersion, opsys)

		elif opsys >= 10.15 and fingVersion < 5:
			logger.log(40,"miss match version of opsys:{} and fing:{} you need to upgrade FING to 64 bits".format(opsys,fingversion))
		else:
			logger.log(40,"miss match version of opsys:{} and fing:{}  please upgrade".format(opsys,fingversion))


	except  Exception as e:
		exceptionHandler(40,e)
	

def checkVer():
	global fingEXEpath
	try:
		opsys	=  platform.mac_ver()[0].split(".")
		opsys	= float(opsys[0]+"."+opsys[1])
		cmd 	= "echo '"+yourPassword+ "' | sudo -S "+fingEXEpath+" -v"
		if showPassword:
			cmdSHOW = cmd
		else:
			cmdSHOW = "echo 'xxxxx' | sudo -S "+fingEXEpath+" -v"
		ret, err= readPopen(cmd)
		ret = ret.strip("\n").split(".")
		if len(ret) > 1:
			fingVersion	= float(ret[0]+"."+ret[1])
			if logLevel > 0: logger.log(20,"chk versions.opsys: {};   fingVersion:{} from cmd:{};   ".format(opsys, fingVersion, cmdSHOW))
			return opsys, fingVersion
		else:
			logger.log(20,"bad return for cmd:{} \nret:{}\err:{}  ".format(cmdSHOW, ret, err))
			return 0,0

	except  Exception as e:
		exceptionHandler(40,e)
	return 0,0

def doFingV5(fingVersion, opsys):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
	global startCommand

	buffer 		= 32000
	yearTag		= datetime.datetime.now().strftime("%Y/%m")
	netTag		= theNetwork.split(".")[0]+"."

	if logLevel > 0: logger.log(20,"into doFingV5 with yearTag: {}, netTag: {}, version: {};  opsys: {}".format(yearTag, netTag, fingVersion, opsys) )
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

			if logLevel > 0: logger.log(20,"fing start command: {}".format(cmdSHOW)) 
			ListenProcessFileHandle = ""
			for ii in range(5):
				ListenProcessFileHandle = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				##pid = ListenProcessFileHandle.pid
				err = str(ListenProcessFileHandle.stderr)
				msg = str(ListenProcessFileHandle.stdout)
				logger.log(40,"try# {}; msg  {} -- err: {}, ListenProcessFileHandle:{}".format(ii+1, msg, err, str(ListenProcessFileHandle)) )
				if msg.find("open file") == -1 and msg.find("io.BufferedReader name=") == -1 :	# try this again
					logger.log(40,"error connecting , try again to read file")
					if ii < 1:	time.sleep(10)
					else:		time.sleep(5)
					continue
				break
			time.sleep(2)
			stopPGM('sudo -S /usr/local/bin/fing')
			stopPGM('/bin/sh /usr/local/bin/fing')

			if str(ListenProcessFileHandle) == "": return 
			logger.log(20,"fing.bin launched")

			flags = fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_GETFL)  # get current p.stdout flags
			fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

			dataLines =[]
			logLines  = []
			lastLogLine = ""
			while True:
				time.sleep(0.1)
				try:
					lines = os.read(ListenProcessFileHandle.stdout.fileno(), buffer).decode('utf_8') ## = 32k
				except	Exception as e:
					time.sleep(0.2)
					if unicode(e).find("[Errno 35]") > -1:	 # "Errno 35" is the normal response if no data, if other error stop and restart
						msgSleep = 0.4 # nothing new, can wait
					else:
						if len(unicode(e)) > 5:
							out = "os.read(ListenProcessFileHandle.stdout.fileno(),{})  in Line {} has error={}\n ip:{}  type: {}".format(buffer, sys.exc_info()[2].tb_lineno, e, ipNumber,uType)
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
					logger.log(40,"restart of startfing due to discovery stoppped message from fing.bin")
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
	

	
	except  Exception as e:
		exceptionHandler(40,e)
	return 


####-------------------------------------------------------------------------####
def readPopen(cmd):
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

		try: 
			if "{}".format(exception_error_message).find("None") >-1: return 
		except: 
			pass

		filename, line_number, method, statement = traceback.extract_tb(sys.exc_info()[2])[-1]
		#module = filename.split('/')
		log_message = "'{}'".format(exception_error_message )
		log_message +=  "\n{} @line {}: '{}'".format(method, line_number, statement)
		logger.log(level, log_message)

#################################
def stopOldPGMs():
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
	stopPGM(u'Plugin/startfing.py', mypid = str(os.getpid()) )
	stopPGM(u'/usr/local/lib/fing/fing.bin')
	stopPGM(u'/usr/local/bin/fing')

#################################
def stopPGM(pgm, mypid =""):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType

	cmd = "ps -ef | grep '{}' | grep -v grep | awk '{{print $2}}'".format(pgm)
	if logLevel > 0: logger.log(20," get pids of old processes w cmd:{}".format(cmd))
	ret, err= readPopen(cmd)
	pids = ret.split("\n")
	for pid in pids:
		if len(pid) < 3: continue # 100
		if pid == mypid: continue # dont kill myself
		cmd = "echo '{}' | sudo -S /bin/kill -9 {} > /dev/null 2>&1 &".format(yourPassword, pid)
		if showPassword:
			cmdSHOW = cmd
		else:
			cmdSHOW = "echo '{}' | sudo -S /bin/kill -9 {} > /dev/null 2>&1 &".format("XXXXX", pid)

		if logLevel > 0: logger.log(20,"  FING kill cmd:{}".format(cmdSHOW))
		ret= subprocess.Popen(cmd,shell=True) # kill fing

####### main pgm / loop ############
global indigoPreferencesPluginDir
global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
global fingEXEpath, theNetwork, yourPassword, showPassword, theNetwork, netwType
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
startCommand 				=  "{} '{}' '{}'".format(pythonPath, sys.argv[0], sys.argv[1])


logging.basicConfig(level=logging.DEBUG, filename= logfileName,format='%(module)-10s %(asctime)s L:%(lineno)3d Lv:%(levelno)s %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


#
logger.setLevel(logging.DEBUG)
xxx = copy.copy(params)
if not showPassword:
	xxx["ppp"]	= "xxxxx"
logger.log(20,"========= start   @ {}   ===========;  params:{}".format(datetime.datetime.now(), xxx))



stopOldPGMs()

#cmd = "cd '"+"'; echo '"+yourPassword+ "' | sudo /usr/sbin/chown "+macUser+" *"
#os.system(cmd) 
#cmd = "echo '"+yourPassword+ "' | sudo /bin/chmod -R 777 '"+indigoPreferencesPluginDir+"'"
#os.system(cmd) 

if logLevel > 0: logger.log(20,"params: {}".format(params))

cmd = "echo '" +yourPassword + "' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingDataFileName+"'"
if showPassword:
	cmdSHOW = cmd
else:
	cmdSHOW = "echo 'xxxxx' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingDataFileName+"'"
if logLevel > 0:  logger.log(20,cmdSHOW)
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

cmd = "echo '" +yourPassword + "' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingLogFileName+"'"
if showPassword:
	cmdSHOW = cmd
else:
	cmdSHOW = "echo 'xxxxx' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingLogFileName+"'"
if logLevel > 0:  logger.log(20,cmdSHOW)
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

cmd = "echo 0 > '"+indigoPreferencesPluginDir+fingLogFileName+"'"
cmdSHOW = cmd

if logLevel > 0: logger.log(20,cmdSHOW)
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	
startFing()
if logLevel > 0: logger.log(20,"========= stopped @ {}   =========== ".format(datetime.datetime.now()))

sys.exit(0)		
