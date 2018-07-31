import glob
import os
import optparse
import subprocess
import time
import shutil

# === Perso import
from makeImageIgrida import *
from cameraMat import *
from igrida import *
from extractXml import *

class SequenceScheduler(IgridaScheduler):
	def __init__(self, manager, w, h, cameradir, template, pattern, extension, nameCam, begin, end, step, output, max = 100, subblock = 128, noPattern = False):
		IgridaScheduler.__init__(self, max)
		# Attributs pour la scene
		self.nameCam = nameCam
		self.cameradir = cameradir
		self.template = template
		self.searchPattern = pattern
		self.width = w
		self.height = h
		self.subblock = subblock
		self.extension = extension
		self.output = output
		self.noPattern = noPattern
		# Attributs pour les frames
		self.currentFrame = begin
		self.endFrame = end
		self.step = step
		# Attribut pour le scheduler
		self.max = max
		self.manager = manager


	@staticmethod
	def createOptions(parser):
		parser.add_option('-x','--width', help='width resolution [default: %default]', type="int",default=1920)
		parser.add_option('-y','--height', help='height resolution [default: %default]', type="int",default=1080)
		parser.add_option('-d','--template', help='template file')
		parser.add_option('-z','--pattern', help='search file')
		parser.add_option('-o','--output', help='output dir [default: %default]', default="rendu")
		parser.add_option('-f','--frame', help='nb frames', type="int")
		parser.add_option('-b','--begin', help='begin frame number [default: %default]',  type="int", default=1)
		parser.add_option('-s','--step', help='step at each frame [default: %default]',  type="int", default=1)
		parser.add_option('-c','--camera', help='files input dir')
		parser.add_option('-e','--extension', help='output image extension [default: %default]', default="hdr")
		parser.add_option('-l','--limitjobs', help='set maximum jobs [default: %default]', type="int", default=100)
		parser.add_option('-n','--name', help='Name camera files')
		parser.add_option('-w','--windowsize', help='window sub block size', type="int", default=128)
		parser.add_option('-1','--nopattern', help='use no pattern file behavior',default=False, action="store_true")

	@staticmethod
	def parseOptions(options, parser, manager):
		if(not options.camera):
			parser.error("camera flag need to be specified")
		if(not options.pattern):
			parser.error("pattern flag need to be specified")
		if(not options.frame):
			parser.error("frame flag need to be specified")
		if(not options.name):
			parser.error("name flag need to be specified")

		if(not options.nopattern):
			if(not options.template):
				parser.error("template flag need to be specified")

		return SequenceScheduler(manager,
			options.width, options.height,
			options.camera, options.template, options.pattern, options.extension, options.name,
			options.begin, options.begin+options.frame, options.step,
			options.output, options.limitjobs, options.windowsize, options.nopattern)

	def isFinish(self):
		return (len(self.manager.tasks) == 0) and (self.currentFrame >= self.endFrame)

	def createTasksNextFrame(self):
		camFile = self.nameCam +  str(self.currentFrame).zfill(5) + ".xml"
		camMat = self.cameradir+"/"+camFile
		newScenefile = os.path.dirname(self.template)+"/temp_"+str(self.currentFrame)+".xml"

		if(self.noPattern):
			print camMat, "=>", newScenefile
			shutil.copy(camMat, newScenefile)
		else:
			print camMat,  self.searchPattern, self.template, newScenefile
			extractXml(camMat, self.searchPattern, self.template, newScenefile)


		imageTask = IgridaImage(self.width, self.height, newScenefile, self.output+"/"+str(self.currentFrame), numThreads = self.manager.config.numThreads, subblocks = self.subblock, extension = self.extension)
		imageTask.createTasks(self.manager)

		# Go to next frame
		self.currentFrame += self.step

	def update(self):
		self.manager.updateStatus()
		nbN, nbW, nbR = self.getStats()
		jobsNeedLaunch = self.max - (nbW+nbR)

		# Si on a besoin de remplir la file
		while(self.max > len(self.manager.tasks) and self.currentFrame <= self.endFrame):
			self.createTasksNextFrame()

		if(jobsNeedLaunch > 0): # On en lance plus
			IgridaLogger.get().info("Try to launch " + str(jobsNeedLaunch) + " tasks")
			self.manager.submitTasks(jobsNeedLaunch)

if __name__=="__main__":
	IgridaLogger.create()
	IgridaLogger.logger.setLevel(logging.INFO)
	# Parser d'options pour les differents parametres des jobs
	parser = optparse.OptionParser()
	SequenceScheduler.createOptions(parser)
	IgridaConfig.addOptions(parser)

	# Recupere les valeurs
	# === Create manager
	(options, args) = parser.parse_args()
	typeSched = IgridaTaskManager.OAR
	config = IgridaConfig.parseOptions(options)
	manager = IgridaTaskManager(config, [IgridaOARSubImage], typeSched)

	s = SequenceScheduler.parseOptions(options,parser,manager)
	s.run(10)

	print "FINISH!"
