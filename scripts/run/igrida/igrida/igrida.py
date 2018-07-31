import subprocess
import time
import logging
import sys
import os
import optparse
import threading
import stat

class Command(threading.Thread):
	def __init__(self, cmd):
		threading.Thread.__init__(self)
		self.cmd = cmd
		self.output = None
		self.finished = False
		
	def run(self):
		self.process = subprocess.Popen(self.cmd,shell=False,stdout=subprocess.PIPE,
									stdin=subprocess.PIPE)
		self.output = self.process.communicate()[0]

	def runSecure(self, timeout):
		self.start()
		self.join(timeout)
		if self.is_alive():
			try:
				print('ERROR: Try to terminating process')
				self.process.stdin.write('\n')
			except:
				print('ERROR: Impossible to write ENTER proc')
				print('INFO: Try to join process ... ')
				
			self.finished = False
			self.join()
		else:
			self.finished = True
		return (self.finished,self.output)

class IgridaLogger:
	logger = None
	hdlrs = []
	
	@staticmethod
	def addHandler(h):
		IgridaLogger.hdlrs.append(h)
		formatter = logging.Formatter('%(asctime)s | %(levelname)s : %(message)s')
		h.setFormatter(formatter)
		IgridaLogger.logger.addHandler(h) 
	
	@staticmethod
	def create():
		IgridaLogger.logger = logging.getLogger('igrida')
		IgridaLogger.addHandler(logging.FileHandler('out.log'))
		IgridaLogger.addHandler(logging.StreamHandler())
		
		IgridaLogger.logger.setLevel(logging.INFO)
	
	@staticmethod
	def get():
		return IgridaLogger.logger
	
	@staticmethod
	def flush():
		for h in IgridaLogger.hdlrs:
			pass
			#h.flush()

			
class IgridaConfig:
	'''Configure the jobs (ressources limits, commands ... etc.)'''
	def __init__(self,command=None, out=None, err=None, memory="1G", time="00:00:10", numThreads = 1,queue = None, options = ""):
		self.command = command
		self.out = out
		self.err = err
		self.memory = memory
		self.time = time
		self.numThreads = numThreads
		self.queue = queue
		self.options = options

	def clone(self):
		return IgridaConfig(self.command, self.out, self.err, self.memory, self.time, self.numThreads, self.queue, self.options)

	@staticmethod
	def addOptions(parser):
		parser.add_option('-m','--memory', help='memory Need', default=None)
		parser.add_option('-t','--time', help='time Need', default=None)
		parser.add_option('-q','--queue', help='specify queue to launch on igrida', default=None)
		parser.add_option('-j','--jobs', help='nb jobs per nodes', default=1)
		parser.add_option('-a','--options', help="add optional option to the JOB: (OAR: 'BEST')", default="")
		
	@staticmethod
	def parseOptions(options):
		return IgridaConfig(memory=options.memory, time=options.time, numThreads=options.jobs, queue=options.queue, options=options.options)
	
		
class IgridaTaskStatus:
	NOSUBIMITTED = 0
	WAITING = 1
	RUNNING = 2
	FINISHED = 3
	SKIPPED = 4
	
class IgridaTask:
	'''Abstract igrida task'''
	def __init__(self, config, others):
		self.config = config
		self.idTask = None
		self.status = IgridaTaskStatus.NOSUBIMITTED
		self.others = others
		
	def cloneConfig(self):
		return self.config.clone()
	
	def isRunning(self):
		return self.status == IgridaTaskStatus.RUNNING
	
	def isFinished(self):
		return self.status == IgridaTaskStatus.FINISHED
		
	def isSkipped(self):
		return self.status == IgridaTaskStatus.SKIPPED
	
	def isWaiting(self):
		return self.status == IgridaTaskStatus.WAITING
	
	def isNotSubmitted(self):
		return self.status == IgridaTaskStatus.NOSUBIMITTED

	def postprocess(self):
		pass
	
	def preprocess(self):
		return True
	
	def getOutputFile(self):
		Cs = self.config.command.split()
		for i in range(len(Cs)):
			if(Cs[i] == "-o"):
				return Cs[i+1]
		raise Exception("Not possible to find output file ... ")
		return ""
	
class IgridaOARTask(IgridaTask):
	def __init__(self, config, others):
		IgridaTask.__init__(self, config, others)

	def postprocess(self):
		IgridaTask.postprocess(self)
	
	def preprocess(self):
		return IgridaTask.preprocess(self)
	
	def updateStatus(self, output):
		if((not self.isWaiting()) and (not self.isRunning())):
			return True
			
		if(self.idTask in output):
			if self.isWaiting():
				posQsub = output.find(self.idTask)
				ligne = output[posQsub:]
				state = ligne.split("\n")[0].split()[5]
				if(state == "R"):
					self.status = IgridaTaskStatus.RUNNING
			return True
		else:
			IgridaLogger.get().info(self.idTask+" is finished")
			IgridaLogger.flush()
			self.postprocess()
			self.status = IgridaTaskStatus.FINISHED
			return False
	
	def submit(self):
		if(not self.isNotSubmitted()):
			return False
	
		if(not self.preprocess()):
			self.status = IgridaTaskStatus.SKIPPED
			IgridaLogger.get().debug("Task is skipped")
			return False
		
		# === Get output file
		fileArgsname = self.getOutputFile() + "_args.sh"
		IgridaLogger.get().debug("Write arg file: "+fileArgsname)
		IgridaLogger.flush()
		
		# === Open file
		fileArgs = open(fileArgsname, "w")
		fileArgs.write("#!/bin/sh\n")
		
		# === Write Out/Err files
		if(self.config.out):
			fileArgs.write("#OAR -O "+self.config.out+"\n")
		if(self.config.err):
			fileArgs.write("#OAR -E "+self.config.err+"\n")
		
		# === Write ressources
		fileArgs.write("#OAR -l /nodes=1/core=" + str(self.config.numThreads))
		if self.config.queue == None:
			fileArgs.write(",walltime="+self.config.time)
		fileArgs.write("\n")
		
		# === Write special options
		if(self.config.options != ""):
			if("BEST" in self.config.options):
				fileArgs.write("#OAR -t besteffort\n") 
				fileArgs.write("#OAR -t idempotent\n")
		# === Write header needed
		fileArgs.write("EXECUTABLE=/temp_dd/igrida-fs1/agruson/mtsbin/mitsuba\n") # TODO: Add config
		fileArgs.write("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/temp_dd/igrida-fs1/agruson/mtsbin\n") #TODO: Make it auto
		fileArgs.write("export OMP_NUM_THREADS=1\n")
		
		# === Write MTS command and options
		fileArgs.write("$EXECUTABLE ")
		commandSplit = self.config.command.split()
		for i in range(len(commandSplit)-1):
			fileArgs.write(commandSplit[i+1]+" ")
		fileArgs.write("\n")
		fileArgs.close()
		
		# === Change mod file
		st = os.stat(fileArgsname)
		os.chmod(fileArgsname, st.st_mode | stat.S_IEXEC)
		
		# === Write OAR command
		formatCommand = ["oarsub", "-S", fileArgsname]
		secProc = Command(formatCommand)
		terminate, programOutput = secProc.runSecure(20)
		
		# === Get output
		IgridaLogger.get().debug(programOutput)
		IgridaLogger.get().debug(programOutput.split('\n')[-2])
		IgridaLogger.get().debug(' '.join(formatCommand))
		IgridaLogger.flush()
		
		# === Error management
		if(terminate):
			try:
				self.idTask = programOutput.split('\n')[-2].split('=')[1]
			except:
				IgridaLogger.get().info("Error Parsing ID Task ")
				IgridaLogger.flush()
				self.status = IgridaTaskStatus.NOSUBIMITTED
				self.idTask = -1
				
				return False
				
			idTaskInt = int(self.idTask)
			if(idTaskInt < 0):
				IgridaLogger.get().info("Error id task: " + self.idTask)
				IgridaLogger.flush()
				self.status = IgridaTaskStatus.NOSUBIMITTED
			
				return False
			else:
				IgridaLogger.get().info("Submit task: " + self.idTask)
				IgridaLogger.flush()
				self.status = IgridaTaskStatus.WAITING
				
				return True
		else:
			self.idTask = "-1"
			IgridaLogger.get().info("Error submit task: " + self.idTask)
			IgridaLogger.flush()
			self.status = IgridaTaskStatus.NOSUBIMITTED
			
			return False
		
class IgridaTaskManager:
	OAR = 0
	
	def __init__(self, config, classType = [IgridaOARTask], type = OAR):
		self.type = type
		self.tasks = []
		self.config = config
		self.classType = classType
	
	def createTask(self, command = None, out = None, err = None, others = {}):
		newConfig = self.config.clone()
		if(command):
			newConfig.command = command
		if(out):
			newConfig.out = out
		if(err):
			newConfig.err = err
		self.tasks.append(self.createTaskObj(newConfig, others))
	
	def submitTasks(self, nbMax):
		nbSub = 0
		for task in self.tasks:
			if(task.submit()):
				nbSub += 1
			if(nbSub>=nbMax):
				break
		return nbSub
	
	def updateStatus(self):
		process = subprocess.Popen(["oarstat"],shell=False,stdout=subprocess.PIPE)
		output = process.communicate()[0]
		newTasks = []
		nbDel = 0
		for task in self.tasks:
				task.updateStatus(output)
				if((not task.isFinished()) and (not task.isSkipped())):
					newTasks.append(task)
				else:
					nbDel += 1
		self.tasks = newTasks
		return nbDel
		
	# ==== Virtual function
	def createTaskObj(self, config, others):
		return self.classType[self.type](config,others)

class IgridaScheduler:
	def __init__(self, manager):
		self.manager = manager
		
	def isFinish(self):
		return len(self.manager.tasks) == 0
	
	def getStats(self):
		nbWaiting = 0
		nbRunning = 0
		nbNotSub = 0
		for task in self.manager.tasks:
			if(task.isRunning()):
				nbRunning += 1
			elif(task.isWaiting()):
				nbWaiting += 1
			elif(task.isNotSubmitted()):
				nbNotSub += 1
		return (nbNotSub, nbWaiting, nbRunning)
	
	def printStats(self):
		nbN, nbW, nbR = self.getStats()
		IgridaLogger.get().info("Stats : [N: " + str(nbN) +", W: "+ str(nbW) +", R: "+ str(nbR)+"]")
		
	def update(self):
		raise Exception("Not implemented update")
	
	def run(self, updateTime):
		while not self.isFinish():
			self.printStats()
			self.update()
			time.sleep(updateTime)

class IgridaSchedulerMaxJobs(IgridaScheduler):
	def __init__(self, manager, max):
		IgridaScheduler.__init__(self, manager)
		self.max = max
	
	def update(self):
		self.manager.updateStatus()
		nbN, nbW, nbR = self.getStats()
		jobsNeedLaunch = self.max - (nbW+nbR)
		if(jobsNeedLaunch > 0):
			IgridaLogger.get().info("Try to launch " + str(jobsNeedLaunch) + " tasks")
			self.manager.submitTasks(jobsNeedLaunch)
		
if __name__=="__main__":

	IgridaLogger.create()
	IgridaLogger.logger.setLevel(logging.DEBUG)
	c = IgridaConfig("", 
		os.getcwd()+"/out.out", 
		os.getcwd()+"/out.err")
	t = IgridaTaskManager(c,type=IgridaTaskManager.OAR)
	for i in range(100):
		t.createTask(os.getcwd()+"/task.sh "+str(i))
	s = IgridaSchedulerMaxJobs(t,10)
	s.run(3)
	print "Finish !"
