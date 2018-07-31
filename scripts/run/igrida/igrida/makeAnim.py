import glob
import os
import optparse
import subprocess
import time

from cameraMat import *
from extractXml import *

MTS4_EXE = "C:\\Users\\agruson\\Developpement\\Workspace\\mitsuba-future\\dist\\mitsuba.exe"
OPT = " -z -x "
def executeCommand(com):
	print("============================================================")
	print("============================================================")
	print("============================================================")
	print("============================================================")
	print("[INFO] Run command : "+com)
	formatCommand = com.split(" ")
	process = subprocess.Popen(formatCommand,shell=False,stdout=subprocess.PIPE)
	return process.communicate()[0]

def basename(path):
	pos = path.rfind(os.path.sep)
	return path[pos+len(os.path.sep):]
	
def runAnim(nameCam, template, searchPattern, beg, end, dump, output):
	# Try to create the result dir
	if(not os.path.exists(output)):
		os.makedirs(output)
	
	for currentFrame in range(beg, end):
		# Create all variables
		camFile = basename(nameCam) +  str(currentFrame).zfill(5) + ".xml"
		camMat = os.path.dirname(nameCam) +os.path.sep+camFile
		newScenefile = os.path.dirname(template)+os.path.sep+"temp_"+str(currentFrame).zfill(5)+".xml"
		# Create the new temp file
		print camMat,  searchPattern, template, newScenefile
		extractXml(camMat, searchPattern, template, newScenefile)
		# Create the command
		command = MTS4_EXE + OPT + "-o "+output+os.path.sep+str(currentFrame).zfill(5)+" "+newScenefile
		# Execute the command
		res = executeCommand(command)
		if(dump):
			dumpFilename = newScenefile[:-3]+"log"
			print("[INFO] Dump the command result into "+dumpFilename)
			dumpFile = open(dumpFilename,"w")
			dumpFile.write(res)
			
		print res
		
if __name__=="__main__":
	parser = optparse.OptionParser()
	parser.add_option('-b','--begin', default=1)
	parser.add_option('-e','--end', default=100)
	parser.add_option('-c','--camPath', default="camera")
	parser.add_option('-t','--template', default="template.xml")
	parser.add_option('-o','--output')
	parser.add_option('-s','--search', default="search.xml")
	parser.add_option('-d','--dump', action="store_true", default=True)
	parser.add_option('-m','--mitsuba')
	parser.add_option('-p','--proc', default=8)
	
	(options, args) = parser.parse_args()
	
	if( not options.mitsuba == None):
		MTS4_EXE = options.mitsuba
	OPT += "-p"+str(options.proc) + " "
	
	runAnim(options.camPath, options.template, options.search, int(options.begin), int(options.end), options.dump, options.output)