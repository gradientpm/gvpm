import glob
import os
import optparse
import subprocess
from igrida import *
from shutil import *
import getpass

################
## CONSTANTES
################
NAME_USER = getpass.getuser()
MTS_ROOT = "/temp_dd/igrida-fs1/"+NAME_USER+"/mtsbin"
MTS_EXE = MTS_ROOT+"/mitsuba.sh"

################
## CLASSES
################
	
class MtsCommand:
	def __init__(self, other = {}):
		self.definitions = other
	
	def __str__(self):
		command = MTS_EXE + " -z"
		for (k,v) in self.definitions.iteritems():
			command += " -D"+k+"="+str(v)
		return command

class MtsSubCommand(MtsCommand):
	def __init__(self, width, height, cropWidth, cropHeight, cropX, cropY, other = {}):
		MtsCommand.__init__(self,other)
		self.definitions.update({"width" : width,
			"height" : height,
			"cropWidth" : cropWidth,
			"cropHeight" : cropHeight,
			"cropX" : cropX,
			"cropY" : cropY})

class IgridaOARSubImage(IgridaOARTask):
	def __init__(self, config, others):
		IgridaOARTask.__init__(self, config, others)
	
	def preprocess(self):
		if(os.path.isfile(self.others["image"])):
			IgridaLogger.get().debug("Image found... Skip !")
			return False
		return True
	
	def postprocess(self):
		if not os.path.isfile(self.others["image"]):
			IgridaLogger.get().warning("Pas d'image : " + self.others["image"])
		else:
			IgridaLogger.get().debug("Image OK :" + self.others["image"])
			
class IgridaImage:
	def __init__(self, width, height, inputFile, outputDir, numThreads = 1, subblocks = 128, others = {}, extension = "png"):
		self.width = width
		self.height = height
		self.inputFile = inputFile
		self.outputPath = outputDir
		self.subblocks = subblocks
		self.numThreads = numThreads
		self.others = others
		self.extension = extension
		
		# Compute subblocks
		subBlocks = self.subblocks / int(self.numThreads)
		self.mtsSubBlocks = 1
		while(subBlocks > self.mtsSubBlocks*2):
			self.mtsSubBlocks = self.mtsSubBlocks*2
		
		self.makeOutputDir()
	
	def makeOutputDir(self):
		if not os.path.isdir(self.outputPath):
			os.makedirs(self.outputPath)
	
	def __createtask(self, manager, cropX, cropY, cropW, cropH) :
		# Compute ...
		nameJob = ""+str(cropX)+"_"+str(cropY)
		imagePath = self.outputPath + "/" + nameJob
		
		# Create mitsuba strategy
		mtsCom = MtsSubCommand(self.width, self.height, cropW, cropH, cropX, cropY, self.others)
		mtsCom = str(mtsCom) + " -p " + str(self.numThreads) + " -b " + str(self.mtsSubBlocks) + " -o " + imagePath + " " + self.inputFile
		
		# Create task
		manager.createTask(mtsCom,
			self.outputPath + "/" + nameJob + ".out",
			self.outputPath + "/" + nameJob + ".err",
			{"image" : imagePath+"."+self.extension})
	
	def createTasks(self, manager):
		for x in range(self.width/self.subblocks):
			for y in range(self.height/self.subblocks):
				self.__createtask(manager, x*self.subblocks,y*self.subblocks, self.subblocks, self.subblocks)
		
		# Gestion des bord
		newW = self.width % self.subblocks
		newH = self.height % self.subblocks
		
		if(newH != 0):
			for x in range(self.width/self.subblocks):
				self.__createtask(manager, x*self.subblocks,(self.height/self.subblocks)*self.subblocks, self.subblocks, newH)
		
		if(newW != 0):
			for y in range(self.height/self.subblocks):
				self.__createtask(manager,(self.width/self.subblocks)*self.subblocks,y*self.subblocks, newW, self.subblocks)
		
		if(newW != 0 and newH != 0):
			self.__createtask(manager,(self.width/self.subblocks)*self.subblocks,(self.height/self.subblocks)*self.subblocks, newW, newH)
	

if __name__=="__main__":
	IgridaLogger.create()
	IgridaLogger.logger.setLevel(logging.DEBUG)
	# Parser d'options pour les differents parametres des jobs
	parser = optparse.OptionParser()
	parser.add_option('-z', '--mitsuba', help="overwrite MTS default placement", default=MTS_EXE)
	parser.add_option('-x','--width', help='width resolution', default=1920)
	parser.add_option('-y','--height', help='height resolution', default=1080)
	parser.add_option('-i','--input', help='input file')
	parser.add_option('-o','--output', help='output dir', default="rendu")
	parser.add_option('-s','--subblocks', help='sub-blocks dim', default=128)
	parser.add_option('-e','--extension', help='output image extension')
	IgridaConfig.addOptions(parser)
	
	# Recupere les valeurs
	(options, args) = parser.parse_args()
	width = int(options.width)
	height = int(options.height)
	inputFile = options.input
	subblocks = int(options.subblocks)
	if(not options.extension):
		print "Must specify extension"
		exit()
	if(not inputFile):
		print "Must specify a input file"
		exit()
	outputDir = options.output
	
	config = IgridaConfig.parseOptions(options)
	
	typeSched = IgridaTaskManager.OAR
	
	# === Check MTS
	MTS_EXE = options.mitsuba
	if(not os.path.exists(MTS_EXE)):
		print("WARN: MITSUBA not found: "+MTS_EXE)
		print("Veuillez appeler igrida-install.sh et copier mitsuba.sh dans "+MTS_ROOT)
		exit()
	else:
		print("MITSUBA found: "+MTS_EXE)
	
	# Create ...
	manager = IgridaTaskManager(config, [IgridaOARSubImage], typeSched)
	jobs = IgridaImage(width, height, inputFile, outputDir, config.numThreads, subblocks, extension = options.extension)
	jobs.createTasks(manager)
	
	# Run
	s = IgridaSchedulerMaxJobs(manager,300)
	while not s.isFinish():
		s.printStats()
		s.update()
		time.sleep(3)
	print "Finish !"
