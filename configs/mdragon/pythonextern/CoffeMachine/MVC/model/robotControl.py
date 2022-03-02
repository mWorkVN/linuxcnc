# coding: utf8
import sys, time ,os
#import logging
#import logging.handlers
import linuxcnc
from model.state import State

import imp


class RobotControl(State):
    def __init__(self):
        self.emc = linuxcnc
        self.emcstat = self.emc.stat() # create a connection to the status channel
        self.emccommand = self.emc.command()
        self.myRobot=None 
        self.mprint("Init STATE")   
        self.state = 0
        self.isEMCRun = False

    """def is_homed():
        '''Returns TRUE if all joints are homed.'''
        stat.poll()
        for joint in range(num_joints):
            if not stat.joint[joint]['homed']:
                return False
        return True"""

    """def checkReady(self):
        self.emcstat.poll()
        if self.emcstat.estop:
            log.error("Can't issue MDI when estoped")
        elif not self.emcstat.enabled:
            log.error("Can't issue MDI when not enabled")
        elif not no_force_homing if no_force_homing else not is_homed():
            log.error("Can't issue MDI when not homed")
        elif not self.emcstat.interp_state == linuxcnc.INTERP_IDLE:
            log.error("Can't issue MDI when interpreter is not idle")
        else:"""



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