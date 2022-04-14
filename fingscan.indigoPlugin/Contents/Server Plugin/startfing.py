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
	global fingEXEpath, theNetwork, yourPassword,  netwType
		
	try:
	## first check which versio we are running
	## get opsys
	## get fing version
		opsys, fingVersion = checkVer()

		if  opsys < 10.15 and fingVersion < 5:
			formatFING = u" -o table,csv,fing.data log,csv,fing.log "
			if theNetwork !="":
				cmd =u"cd '"+indigoPreferencesPluginDir+u"';echo '" +yourPassword +u"' | sudo -S '"+fingEXEpath+"' "+theNetwork+"/"+netwType+"  "+formatFING+" > /dev/null 2>&1 &"
			else:
				cmd =u"cd '"+indigoPreferencesPluginDir+u"';echo '" +yourPassword +u"' | sudo -S '"+fingEXEpath+"' "+formatFING+" > /dev/null 2>&1 &"
			os.system(cmd)
			if logLevel > 0: logger.log(20,u"fing.bin launched, version: {},  opsys: {}, with command:\n{}".format(fingVersion, opsys, cmd))
			time.sleep(0.5)
			# kill mnother processes only leave '/usr/local/lib/fing/fing.bin' running
			stopPGM(u'/bin/sh /usr/local/bin/fing')
			stopPGM('sudo -S /usr/local/bin/fing')
			return 

		elif fingVersion >= 5:
			doFingV5(fingVersion, opsys)

		elif opsys >= 10.15 and fingVersion < 5:
			logger.log(40,u"miss match version of opsys:{} and fing:{} you need to upgrade FING to 64 bits".format(opsys,fingversion))
		else:
			logger.log(40,u"miss match version of opsys:{} and fing:{}  please upgrade".format(opsys,fingversion))


	except  Exception as e:
		exceptionHandler(40,e)
	

def checkVer():
	global fingEXEpath
	try:
		opsys	=  platform.mac_ver()[0].split(".")
		opsys	= float(opsys[0]+"."+opsys[1])
		cmd 	= u"echo '"+yourPassword+ u"' | sudo -S "+fingEXEpath+u" -v"
		ret, err= readPopen(cmd)
		ret = ret.strip("\n").split(".")
		fingVersion	= float(ret[0]+"."+ret[1])
		if logLevel > 0: logger.log(20,"chk versions.opsys: {};   fingVersion:{} from cmd:{};   ".format(opsys, fingVersion, cmd))
		return opsys, fingVersion
	except  Exception as e:
		exceptionHandler(40,e)
	return 0,0

def doFingV5(fingVersion, opsys):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType
	global startCommand

	buffer 		= 32000
	yearTag		= datetime.datetime.now().strftime(u"%Y/%m")
	netTag		= theNetwork.split(u".")[0]+"."

	if logLevel > 0: logger.log(20,u"into doFingV5 with yearTag: {}, netTag: {}, version: {};  opsys: {}".format(yearTag, netTag, fingVersion, opsys) )
	try:
			fingFormat= u" -o table,csv,  log,csv "
			if theNetwork !="":
				cmd =u"cd '"+indigoPreferencesPluginDir+u"';echo '" +yourPassword + u"' | sudo -S '"+fingEXEpath+u"' "+theNetwork+u"/"+netwType+u"  "+fingFormat+u" &"
			else:
				cmd =u"cd '"+indigoPreferencesPluginDir+u"';echo '" +yourPassword + u"' | sudo -S '"+fingEXEpath+u"' "+fingFormat+u" &"

			if logLevel > 0:logger.log(20,u"fing start command: {}".format(cmd)) 
			ListenProcessFileHandle = ""
			for ii in range(5):
				ListenProcessFileHandle = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				##pid = ListenProcessFileHandle.pid
				err = str(ListenProcessFileHandle.stderr)
				msg = str(ListenProcessFileHandle.stdout)
				logger.log(40,u"try# {}; msg  {} -- err: {}, ListenProcessFileHandle:{}".format(ii+1, msg, err, str(ListenProcessFileHandle)) )
				if msg.find(u"open file") == -1 and msg.find("io.BufferedReader name=") == -1 :	# try this again
					logger.log(40,u"error connecting , try again to read file")
					if ii < 1:	time.sleep(10)
					else:		time.sleep(5)
					continue
				break
			time.sleep(2)
			stopPGM('sudo -S /usr/local/bin/fing')
			stopPGM('/bin/sh /usr/local/bin/fing')

			if str(ListenProcessFileHandle) == "": return 
			logger.log(20,u"fing.bin launched")

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
					if unicode(e).find(u"[Errno 35]") > -1:	 # "Errno 35" is the normal response if no data, if other error stop and restart
						msgSleep = 0.4 # nothing new, can wait
					else:
						if len(unicode(e)) > 5:
							out = u"os.read(ListenProcessFileHandle.stdout.fileno(),{})  in Line {} has error={}\n ip:{}  type: {}".format(buffer, sys.exc_info()[2].tb_lineno, e, ipNumber,uType)
							try: out+= u"  fileNo: {}".format(ListenProcessFileHandle.stdout.fileno() )
							except: pass
							if unicode(e).find(u"[Errno 22]") > -1:  # "Errno 22" is  general read error "wrong parameter"
								out+= u" ..      try lowering read buffer parameter" 
								logger.log(30,out)
							else:
								logger.log(40,out)
						lastForcedRestartTimeStamp = 1 # this forces a restart of the listener
					continue

				if lines.find(u"Discovery stopped") >-1:
					logger.log(40,u"restart of startfing due to discovery stoppped message from fing.bin")
					os.system(startCommand)
					
					

				if len(lines) > 10:  
					for line in lines.split(u"\n"): 
						if line.find(netTag) == 0:
							dataLines.append(line)
						if line.find(yearTag) == 0:
							logLines.append(line)

					#logger.log(20,"lines {}".format(lines) )
					#logger.log(20,"data {}".format(dataLines) )
					#logger.log(20,"log  {}".format(logLines) )

				if lines.find(u"Discovery round completed") > -1:
					##logger.log(20,"Discovery round completed {}".format(dataLines) )
					dataOut = u""
					for line in dataLines:
						dataOut += line+u"\n"
					if dataOut !=u"":
						f=open(indigoPreferencesPluginDir+fingDataFileName,u"w")
						f.write(dataOut)
						f.close()
						dataOut = u""
						dataLines = []
				else:
					logOut = u""
					for line in logLines:
						if lastLogLine != line:
							logOut += line+u"\n"
							lastLogLine = line
					if logOut !=u"":
						f=open(indigoPreferencesPluginDir+fingLogFileName,u"a")
						f.write(logOut)
						f.close()
						logOut = u""
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
			if u"{}".format(exception_error_message).find("None") >-1: return 
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
	global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType
	stopPGM(u'Plugin/startfing.py', mypid = str(os.getpid()) )
	stopPGM(u'/usr/local/lib/fing/fing.bin')
	stopPGM(u'/usr/local/bin/fing')

#################################
def stopPGM(pgm, mypid =""):
	global indigoPreferencesPluginDir
	global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
	global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType

	cmd = u"ps -ef | grep '{}' | grep -v grep | awk '{{print $2}}'".format(pgm)
	if logLevel > 0: logger.log(20,u" get pids of old processes w cmd:{}".format(cmd))
	ret, err= readPopen(cmd)
	pids = ret.split(u"\n")
	for pid in pids:
		if len(pid) < 3: continue # 100
		if pid == mypid: continue # dont kill myself
		cmd = u"echo '{}' | sudo -S /bin/kill -9 {} > /dev/null 2>&1 &".format(yourPassword, pid)
		if logLevel > 0: logger.log(20,u"  FING kill cmd:{}".format(cmd))
		ret= subprocess.Popen(cmd,shell=True) # kill fing

####### main pgm / loop ############
global indigoPreferencesPluginDir
global logfileName, logLevel, logger,  fingDataFileName, fingLogFileName, fingErrorFileName
global fingEXEpath, theNetwork, yourPassword, theNetwork, netwType
global startCommand


pluginDir					= sys.argv[0].split(u"startFing.py")[0]
indigoDir					= pluginDir.split("Plugins/")[0]
indigoPreferencesPluginDir 	= indigoDir+u"Preferences/Plugins/com.karlwachs.fingscan/"
logfileName 				= indigoDir+u"Logs/com.karlwachs.fingscan/plugin.log"
fingDataFileName			= u"fing.data"
fingLogFileName				= u"fing.log"


f 							= open(sys.argv[1],u"r")
params 						= json.loads(f.read())
f.close()


pythonPath					= params[u"pythonPath"]
fingEXEpath					= params[u"fingEXEpath"]
logLevel 					= params[u"logLevel"]
yourPassword 				= params[u"ppp"][3:-3][::-1] 
theNetwork 					= params[u"theNetwork"]
netwType 					= params[u"netwType"]
macUser 					= params[u"macUser"]
startCommand 				=  "{} '{}' '{}'".format(pythonPath, sys.argv[0], sys.argv[1])


logging.basicConfig(level=logging.DEBUG, filename= logfileName,format=u'%(module)-10s %(asctime)s L:%(lineno)3d Lv:%(levelno)s %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


#
logger.setLevel(logging.DEBUG)
logger.log(20,u"========= start   @ {}   ===========;  loglevel:{}".format(datetime.datetime.now(), logLevel))



stopOldPGMs()

#cmd = "cd '"+"'; echo '"+yourPassword+ "' | sudo /usr/sbin/chown "+macUser+" *"
#os.system(cmd) 
#cmd = "echo '"+yourPassword+ "' | sudo /bin/chmod -R 777 '"+indigoPreferencesPluginDir+"'"
#os.system(cmd) 

if logLevel > 0: logger.log(20,u"params: {}".format(params))

cmd = u"echo '" +yourPassword + u"' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingDataFileName+u"'"
if logLevel > 0:  logger.log(20,cmd)
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

cmd = u"echo '" +yourPassword + u"' | sudo -S /bin/rm '"+indigoPreferencesPluginDir+fingLogFileName+u"'"
if logLevel > 0:  logger.log(20,cmd)
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

cmd = u"echo 0 > '"+indigoPreferencesPluginDir+fingLogFileName+"'"
if logLevel > 0: logger.log(20,cmd)
subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	
startFing()
if logLevel > 0: logger.log(20,u"========= stopped @ {}   =========== ".format(datetime.datetime.now()))

sys.exit(0)		
