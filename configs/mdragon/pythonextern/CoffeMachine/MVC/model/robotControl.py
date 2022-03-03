# coding: utf8
import sys, time ,os
#import logging
#import logging.handlers
import linuxcnc
from model.state import State
import imp
import posRobot



class exec10():
    def __init__(self,robot):
        self.robot = robot
        self.state = "wait"
        self.number = 0
        pass
    def run(self,pos,time):
        if (time == "0" or time == 0 ):
            return True
        if self.state == "wait":
            self.state = "move"
        elif self.state == "move":
            #move to pos
            if (self.number ==0):
                self.goto(str(pos)) # or self.goto("END_" + pos) 
                self.number = 1
            elif (self.number ==1):
                self.goto("END_" + str(pos)) 
                self.number = 2
            elif (self.number ==2):
                self.wait() 
                self.number = 3
            elif (self.number == 3):
                self.goto("END_" + str(pos)) 
                self.number = 4
            elif (self.number == 5):
                self.goto(str(pos))
                self.number = 6
            elif (self.number == 6):
                self.number = 0
                return True
            self.state = "waitdone"
        elif  self.state == "waitdone":  
            if (self.number != 3):
                if (self.robot.checkStatusDoneMDI() != -1):
                    self.state = "move"
            else:
                time.sleep(time)
        return False

    def goto(self,pos):
        pos = getattr(posRobot,'TAKE_' +str(pos))
        self.robot.sendMDI("G0.1 "+ pos)
        while (self.robot.checkStatusDoneMDI() == -1):
            pass
        
    def wait(self):
        pass
        

class RobotControl(State):
    def __init__(self):
        self.emc = linuxcnc
        self.emcstat = self.emc.stat() # create a connection to the status channel
        self.emccommand = self.emc.command()
        self.myRobot=None 
        self.mprint("Init STATE")   
        self.state = 0
        self.isEMCRun = False
        self.exec = exec10(self)
        """for x in range(0, 12):
            getattr(self, 'exec' +str(x)) = exec11() #getattr('exec' +str(x))()"""

    def run(self, data):
        stsDone = False
        if self.state == 0 :
            stsDone = self.exec.run("0","1")
        else:
            stsDone = self.exec.run(self.state,data[self.state+4])
        if stsDone : self.state = self.state + 1
        if self.state ==10:
            self.state = 0
            data = 1
        return data


    def moveToPos(self):
        pass
    def controlPin(self):
        pass
    def waitTime(self):
        pass
    def goHome(self):
        pass
    def delInit(self):
        return
        del self.emc
        del self.emcstat
        del self.emccommand 

    def checkEMC(self):
        try:
            self.emcstat = self.emc.stat()
            self.emcstat.poll()
            self.isEMCRun = True
        except linuxcnc.error as e:
            print('Unable to poll linuxcnc, is it running?')
            #self.error('Error message: {}'.format(e))
            self.isEMCRun = False
        return self.isEMCRun 

    def reload(self):
        imp.reload(linuxcnc)  
        self.emc = linuxcnc
        self.emccommand = self.emc.command()
        

    def init(self):
        self.delInit()
        self.reload()
        self.checkEMC()

    def set_mdi_mode(self):
        if self.isEMCRun ==False:
            return
        self.emcstat.poll()
        if self.emcstat.task_mode != self.emc.MODE_MDI:
            self.emccommand.mode(self.emc.MODE_MDI)
            self.emccommand.wait_complete()

    def checkStatusDoneMDI(self):
        if self.isEMCRun ==False:
            return 1      
        return self.emccommand.wait_complete(0.001)

    def sendMDI(self,msg):
        if self.isEMCRun ==False:
            return
        self.set_mdi_mode() 
        data  = self.emccommand.mdi(msg)
        print("MDI returnb",time.time(),data)
        self.state = 1

    def running(self, do_poll=True):
        '''
        check wether interpreter is running.
        If so, cant switch to MDI mode.
        '''
        if do_poll:
            self.emcstat.poll()
        return (self.emcstat.task_mode == linuxcnc.MODE_AUTO and
                self.emcstat.interp_state != linuxcnc.INTERP_IDLE)




















class myLinuxcnc:
	def __init__(self):
		startCmd = "/usr/bin/linuxcnc /home/machinekit/machinekit/configs/my_mill/my_mill.ini"
		self.cleanLinuxcnc()
		self.startLinuxcnc(startCmd)
		self.initLinuxcnc()
		self.c.mode(linuxcnc.MODE_MANUAL)
		time.sleep(10)
		for i in range(4):
			self.axis_home(i, self.c, self.s)
		self.c.mode(linuxcnc.MODE_MDI)
		time.sleep(1)

	def axis_home(self, i, c, s):
		c.home(i)
		c.wait_complete(30.0)	#This command without argument waits only 1 second.
		while s.homed[i] != 1:
			time.sleep(1)
			s.poll()

	def initLinuxcnc(self):
		self.s = linuxcnc.stat()
		self.c = linuxcnc.command()
		self.s.poll()
		
		while self.s.task_state == linuxcnc.STATE_ESTOP:
			print("WAITING INITIALIZATION")
			time.sleep(3)
			self.s.poll()

		self.c.state(linuxcnc.STATE_ESTOP_RESET)
		time.sleep(1)
		print("ESTOP RELEASED")
		self.s.poll()
		
		if self.s.task_state == linuxcnc.STATE_ESTOP_RESET:
			self.c.state(linuxcnc.STATE_ON)
			time.sleep(1)
			print("ESTOP RESET")
		else:
			print("ESTOP RESET ERROR")
		self.s.poll()

		if self.s.task_state == linuxcnc.STATE_ON:
			print("MACHINE IS READY")
		else:
			print("FAIL TO INITIALIZE THE MACHINE")	
	
	def startLinuxcnc(self, cmd):
		res = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
		
		#Wait 30s at maximum
		for i in range(30):
			time.sleep(1)
			if self.checkProcess("axis") != False:
				break

	def getProcesses(self, str):
		processCommand = ["ps", "-A"]
		checkProcess = ["grep", "-e", str]
		
		processExec = subprocess.Popen(processCommand, stdout = subprocess.PIPE)
		checkExec = subprocess.Popen(checkProcess, stdin = processExec.stdout, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
		
		processesOut, processesErr = checkExec.communicate()
		processSplit = processesOut.split()
	
		return processSplit
	
	def checkIo(self):
		ioGrep = self.getProcesses("io")
		for i in range(len(ioGrep) / 4):
			if len(ioGrep[4*i + 3]) == 2:
				return ioGrep[4*i + 3], ioGrep[4*i]
	
		return False

	def checkProcess(self, str):
		retVal = []
	
		strGrep = self.getProcesses(str)
		for i in range(len(strGrep) / 4):
			retVal.append([strGrep[4*i + 3], strGrep[4*i]])

		return retVal

	def killProcess(self, processId):
		killCommand = ["kill", processId]
	
		subprocess.Popen(killCommand)
	
	def cleanLinuxcnc(self):
		if len(self.checkProcess("axis")) > 0:
			for p in self.checkProcess("axis"):
				self.killProcess(p[1])
			time.sleep(20)

		if len(self.checkProcess("linuxcnc")) > 0:
			if len(self.checkProcess("milltask")) > 0:
				for p in self.checkProcess("milltask"):
					self.killProcess(p[1])
			
			if len(self.checkIo()) != False:
				self.killProcess(self.checkIo()[1])

			if len(self.checkProcess("rtapi")) > 0:
				for p in self.checkProcess("rtapi"):
					self.killProcess(p[1])

			if len(self.checkProcess("linuxcnc")) > 0:
				for p in self.checkProcess("linuxcnc"):
					self.killProcess(p[1])