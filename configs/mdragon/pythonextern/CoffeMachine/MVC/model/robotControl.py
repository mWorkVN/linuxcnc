# coding: utf8
import sys, time ,os
#import logging
#import logging.handlers
import linuxcnc
from model.state import State
import imp
import setting.posRobot as posRobot
import subprocess
from memory_profiler import profile

class until:
    def increseStep(self):
        self.number += 1
        
    def openGrib(self):
        self.number += 1
        pass
    def closeGrib(self):
        self.number += 1
        pass
    def checkFinish(self):
        if (self.exec.robot.checkStatusDoneMDI() != -1):
            self.number += 1 
        return False

    def moveJoinToPos(self,pos):
        if (self.exec.robot.checkStatusDoneMDI() != -1):
            pos = getattr(posRobot,str(pos))
            self.exec.robot.sendMDI("G0.1 "+ pos)
            time.sleep(0.05)    
            self.number += 1   

    def moveWToPos(self,pos):
        if (self.exec.robot.checkStatusDoneMDI() != -1):
            pos = getattr(posRobot,str(pos))
            self.exec.robot.sendMDI("G0 "+ pos)
            time.sleep(0.05)    
            self.number += 1 

class TakeGlassState(until):
    __slots__ = ['robot', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0

    def run(self,data):
        if (self.number ==0):
            self.openGrib()
        elif (self.number ==1): #move to Glass 1
            self.moveJoinToPos("TAKE_GLASS_" + str(data[3])) 
        elif (self.number == 2): #wait done
            self.checkFinish()
        elif (self.number == 3): #move to Glass 2
            self.moveJoinToPos("TAKE_GLASS_END_" + str(data[3])) 
        elif (self.number == 4): #Close Glass
            self.checkFinish()
        elif (self.number == 5): #move to Glass 1
            self.closeGrib() 
        elif (self.number == 6): #move to Glass 1
            self.moveJoinToPos("TAKE_GLASS_" + str(data[3])) 
        elif (self.number == 7): #move to Glass 1
            self.checkFinish()
        elif (self.number == 8): #move to Glass 1
            self.number = 0
            self.exec.stateRunStep = self.exec.takeNguyenLieuState
        return 0

class TakeNguyenLieuState(until):
    __slots__ = ['robot', 'runAt', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0
        self.runAt = 0
    def run(self,data):
        if (data[self.runAt+5] == 0):
            self.runAt += 1
        elif self.runAt < 14 :
            self.__checkrun(data)
        elif self.runAt == 14 :
            self.runAt = 0
            self.exec.stateRunStep = self.exec.duaLyThanhPhamState
        return 0
 #nect state

    def __checkrun(self,data):
        if (self.number ==0):
            self.increseStep()
        elif (self.number ==1): 
            self.moveJoinToPos("TAKE_NL_" + str(self.runAt + 1)) 
        elif (self.number == 2): #wait done
            self.checkFinish()
        elif (self.number == 3): 
            self.moveJoinToPos("TAKE_NL_END_" + str(self.runAt + 1)) 
        elif (self.number == 4): 
            self.checkFinish()
        elif (self.number == 5): 
            modbusReturn = self.exec.robot.PLCModbus.setData(1,6,int(self.runAt)*2,int( data[(int(self.runAt ))+5]))
            if (modbusReturn == True):
                self.increseStep()
        elif (self.number == 6):
            modbusGet = self.exec.robot.PLCModbus.getData(1,3,(self.runAt *2) +1,1)
            #print(modbusGet)
            if (modbusGet['status'] == 'er'):
                self.increseStep()
            elif  int(modbusGet['data'][0])!= 1 and int(modbusGet['data'][0])!= 0:
                self.exec.robot.PLCModbus.setData(1,16,self.runAt *2 ,[0,0])
                self.increseStep()
        elif (self.number == 7): #move to Glass 1
            self.moveJoinToPos("TAKE_NL_" + str(self.runAt + 1)) 
        elif (self.number == 8): #wait done
            self.checkFinish()
        elif (self.number == 9): #move to Glass 1
            self.number = 0
            self.runAt += 1
        

class DuaLyThanhPhamState(until):
    __slots__ = ['robot', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0
    def run(self,data):
        if (self.number ==0):
            self.increseStep()
        elif (self.number ==1): #move to Glass 1
            self.moveJoinToPos("MOVE_END_FIRST") 
        elif (self.number == 2): #wait done
            self.checkFinish()
        elif (self.number == 3): #move to Glass 2
            self.moveJoinToPos("MOVE_END_END") 
        elif (self.number == 4): #Close Glass
            self.checkFinish()
        elif (self.number == 5): #move to Glass 1
            self.openGrib() 
        elif (self.number == 6): #move to Glass 1
            self.moveJoinToPos("MOVE_END_FIRST") 
        elif (self.number == 7): #move to Glass 1
            self.checkFinish()
        elif (self.number == 8): #move to Glass 1
            self.number = 0
            self.exec.stateRunStep = self.exec.goHomeState 
        return 0

class GoHomeState(until):
    __slots__ = ['robot', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0
    def run(self,data):
        if (self.number ==0):
            self.increseStep()
        elif (self.number ==1): #move to Glass 1
            self.moveJoinToPos("MOVE_HOME") 
        elif (self.number == 2): #wait done
            self.checkFinish()
        elif (self.number == 3): #move to Glass 1
            self.number = 0
            self.exec.stateRunStep = self.exec.finishState 
        return 0

class FinishState(until):
    __slots__ = ['exec']
    def __init__(self,robot):
        self.exec = robot
    def run(self,data):
        self.exec.stateRunStep = self.exec.waitState 
        return 1 

class WaitState(until):
    __slots__ = ['exec']
    def __init__(self,robot):
        self.exec = robot
    def run(self,data):
        return 0 

class InitStats(until):
    __slots__ = ['exec']
    def __init__(self,robot):
        self.exec = robot

    def run(self,data):
        self.exec.stateRunStep = self.exec.takeGlassState 
        return 0    

class exec():
    __slots__ = ['robot', 'initStats', 'takeGlassState', 'takeNguyenLieuState',\
                   'duaLyThanhPhamState',  'goHomeState','finishState','waitState','stateRunStep']
    def __init__(self,robot):
        super().__init__()
        self.robot = robot
        self.initStats = InitStats(self)
        self.takeGlassState = TakeGlassState(self)
        self.takeNguyenLieuState = TakeNguyenLieuState(self)
        self.duaLyThanhPhamState = DuaLyThanhPhamState(self)
        self.goHomeState = GoHomeState(self)
        self.finishState = FinishState(self)
        self.waitState = WaitState(self)
        self.stateRunStep = self.waitState 
        #self.number = 0
        
    def run(self,data):
        return self.stateRunStep.run(data)
        

class RobotControl(State):
    __slots__ = ['PLCModbus','exec','emc','emccommand','emcstat']
    def __init__(self,PLCModbus):
        self.PLCModbus=PLCModbus
        self.statusRobot = 'ok'
        self.isRUNLCNC = False
        startCmd = "/home/mwork/mworkcnc/scripts/linuxcnc /home/mwork/mworkcnc/configs/mdragon/scara.ini"
        self.cleanLinuxcnc()
        self.startLinuxcnc(startCmd)
        self.isEMCRun = True
        self.emc = linuxcnc
        self.emcstat = self.emc.stat() # create a connection to the status channel
        self.emccommand = self.emc.command()
        self.initLinuxcnc()
        self.set_manual_mode()
        for i in range(4):
            self.axis_home(i, self.emccommand, self.emcstat)
        self.set_mdi_mode()
        self.isEMCRun = False
        self.exec = exec(self)

    def initstate(self):
        self.exec.stateRunStep = self.exec.initStats 


    def run(self, data):
        return self.exec.run(data)

    def delInit(self):
        return
        del self.emc
        del self.emcstat
        del self.emccommand 

    def checkEMC(self):
        self.checkReady()
        try:  
            self.emcstat.poll()
            self.isEMCRun = True
            self.statusRobot = 'ok'
        except linuxcnc.error as e:
            self.statusRobot = 'er'
            self.isEMCRun = False
        return self.isEMCRun 

    def reload(self):
        pass
        #imp.reload(linuxcnc) 
        #self.emc = linuxcnc
        #self.emccommand = self.emc.command()
        

    def init(self):
        pass
        #self.delInit()
        #self.reload()
        self.checkEMC()

    """def checkError(self):
        self.checkEMC()"""

    def set_mdi_mode(self):
        if self.isEMCRun ==False:
            return
        self.emcstat.poll()
        if self.emcstat.task_mode != self.emc.MODE_MDI:
            self.emccommand.mode(self.emc.MODE_MDI)
            self.emccommand.wait_complete()

    def set_manual_mode(self):
        if self.isEMCRun ==False:
            return
        self.emcstat.poll()
        if self.emcstat.task_mode != self.emc.MODE_MANUAL:
            self.emccommand.mode(self.emc.MODE_MANUAL)
            self.emccommand.wait_complete()

    def checkStatusDoneMDI(self):
        if self.isEMCRun == False:
            return 1      
        return self.emccommand.wait_complete(0.001)

    def sendMDI(self,msg):
        if self.isEMCRun ==False:
            return
        self.set_mdi_mode() 
        data  = self.emccommand.mdi(msg)


    def axis_home(self, i, c, s):
        c.home(i)
        c.wait_complete(30.0) #This command without argument waits only 1 second.
        while s.homed[i] != 1:
            print("wait H")
            time.sleep(0.1)
            s.poll()

    def checkReady(self):
        self.emcstat.poll()
        if self.emcstat.task_state == self.emc.STATE_ESTOP:
            print("ESP ON")
        if self.emcstat.task_state != linuxcnc.STATE_ON:
            print("NOT ON MACHINE")
        for i in range(0,4):
            if self.emcstat.homed[i] != 1:
                print("Axis ", i , "not Home")


    def initLinuxcnc(self):
        time.sleep(2)
        self.emcstat.poll()
        
        while self.emcstat.task_state == self.emc.STATE_ESTOP:
            print("WAITING INITIALIZATION")
            time.sleep(1)
            self.emcstat.poll()

        self.emccommand.state(linuxcnc.STATE_ESTOP_RESET)
        time.sleep(1)
        print("ESTOP RELEASED")
        self.emcstat.poll()
        
        if self.emcstat.task_state == linuxcnc.STATE_ESTOP_RESET:
            self.emccommand.state(linuxcnc.STATE_ON)
            time.sleep(2)
            print("ESTOP RESET")
        else:
            print("ESTOP RESET ERROR")
        self.emcstat.poll()
        if self.emcstat.task_state == linuxcnc.STATE_ON:
            print("MACHINE IS READY")
        else:
            print("FAIL TO INITIALIZE THE MACHINE")	
    
    def startLinuxcnc(self, cmd):
        #res = subprocess.Popen(cmd.split() ) #, stdout = subprocess.PIPE)
        if (self.isRUNLCNC == False):
            cmd = ["/home/mwork/mworkcnc/scripts/linuxcnc","/home/mwork/mworkcnc/configs/mdragon/scara.ini"]

            cmd = ["/home/mwork/mworkcnc/scripts/linuxcnc","/home/mwork/mworkcnc/configs/mdragon/noGui.ini"]
            proc = subprocess.Popen(cmd, stderr=subprocess.STDOUT )
            for i in range(30):
                time.sleep(1)
                if (self.checkProcess("axis") != False) and (self.checkProcess("linuxcnc") != False):
                    print("check")
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
        for i in range(len(ioGrep) // 4):
            if len(ioGrep[4*i + 3]) == 2:
                return ioGrep[4*i + 3], ioGrep[4*i]
    
        return False

    def checkProcess(self, str):
        retVal = []
        strGrep = self.getProcesses(str)
        for i in range(len(strGrep) // 4):
            retVal.append([strGrep[4*i + 3], strGrep[4*i]])
        print("CHECK", retVal)
        return retVal

    def killProcess(self, processId):
        killCommand = ["kill", processId]
        sproc = subprocess.Popen(killCommand)
        sproc.wait()

        

    def linuxCNCRun(self):
        for lockname in ("/tmp/linuxcnc.lock", "/tmp/emc.lock"):
            if os.path.exists(lockname):
                return True
        return False


    def cleanLinuxcnc(self):
        if self.linuxCNCRun():
            self.isRUNLCNC = True
        #displayname = StatusItem.get_ini_data( only_section='DISPLAY', only_name='DISPLAY' )['data']['parameters'][0]['values']['value']
        #p = subprocess.Popen( ['pkill', displayname] , stderr=subprocess.STDOUT )
        """if len(self.checkProcess("axis")) > 0:
            for p in self.checkProcess("axis"):
                self.killProcess(p[1])
            time.sleep(20)
        if len(self.checkProcess("linuxcnc")) > 0:
            if len(self.checkProcess("linuxcncsvr")) > 0:
                self.isRUNLCNC = True
                for p in self.checkProcess("linuxcncsvr"):
                    self.killProcess(p[1])             
            if len(self.checkProcess("milltask")) > 0:
                for p in self.checkProcess("milltask"):
                    self.killProcess(p[1])
            if self.checkIo() != False:
                self.killProcess(self.checkIo()[1])

            if len(self.checkProcess("rtapi_app")) > 0:
                for p in self.checkProcess("rtapi_app"):
                    self.killProcess(p[1])

            if len(self.checkProcess("linuxcnc")) > 0:
                for p in self.checkProcess("linuxcnc"):
                    self.killProcess(p[1])"""
       
"""


CHECK []
CHECK [[b'linuxcnc', b'5363'], [b'linuxcncsvr', b'5415']]
CHECK [[b'milltask', b'5465']]
CHECK [[b'milltask', b'5465']]
CHECK [[b'rtapi_app', b'5425']]
CHECK [[b'rtapi_app', b'5425']]
CHECK [[b'linuxcnc', b'5363'], [b'linuxcncsvr', b'5415']]
CHECK [[b'linuxcnc', b'5363'], [b'linuxcncsvr', b'5415']]

"""