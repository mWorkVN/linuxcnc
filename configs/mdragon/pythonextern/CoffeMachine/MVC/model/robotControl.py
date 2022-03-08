# coding: utf8
import sys, time ,os
#import logging
#import logging.handlers
import linuxcnc
from model.state import State
import imp
import posRobot
import subprocess


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
            print("RUN",pos)
            self.exec.robot.sendMDI("G0.1 "+ pos)
            time.sleep(0.05)    
            self.number += 1   

    def moveWToPos(self,pos):
        if (self.exec.robot.checkStatusDoneMDI() != -1):
            pos = getattr(posRobot,str(pos))
            print("RUN",pos)
            self.exec.robot.sendMDI("G0 "+ pos)
            time.sleep(0.05)    
            self.number += 1 

class takeGlassState(until):
    #__slots__ = ['robot', 'state', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.state = "wait"
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
            self.exec.stateRunStep = self.exec.takeNguyenLieu
        return 0

class takeNguyenLieu(until):
    #__slots__ = ['robot', 'runAt', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0
        self.runAt = 0
    def run(self,data):
        if (data[self.runAt+5] == 0):
            self.runAt += 1
        elif self.runAt < 14 :
            self.checkrun(data)
        elif self.runAt == 14 :
            self.runAt = 0
            self.exec.stateRunStep = self.exec.DuaLyThanhPham
        return 0
 #nect state

    def checkrun(self,data):
        if (self.number ==0):
            self.increseStep()
        elif (self.number ==1): #move to Glass 1
            self.moveJoinToPos("TAKE_NL_" + str(self.runAt + 1)) 
        elif (self.number == 2): #wait done
            self.checkFinish()
        elif (self.number == 3): #move to Glass 2
            self.moveJoinToPos("TAKE_NL_END_" + str(self.runAt + 1)) 
        elif (self.number == 4): #Close Glass
            self.checkFinish()
        elif (self.number == 5): #move to Glass 1
            #print("send modbus",(int(self.runAt )*2)+5,timewait)
            self.exec.robot.valveModbus.setData(1,6,int(self.runAt)*2,int( data[(int(self.runAt ))+5]))
            self.increseStep()
        elif (self.number == 6):
            modbusGet = self.exec.robot.valveModbus.getData(1,3,(self.runAt *2) +1,1)
            print(modbusGet)
            if  int(modbusGet['data'][0])!= 1 and int(modbusGet['data'][0])!= 0:
                self.exec.robot.valveModbus.setData(1,16,self.runAt *2 ,[0,0])
                self.increseStep()
        elif (self.number == 7): #move to Glass 1
            self.moveJoinToPos("TAKE_NL_" + str(self.runAt + 1)) 
        elif (self.number == 8): #wait done
            self.checkFinish()
        elif (self.number == 9): #move to Glass 1
            self.number = 0
            self.runAt += 1
        

class DuaLyThanhPham(until):
    #__slots__ = ['robot', 'state', 'number']
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

class goHomeState(until):
    __slots__ = ['robot', 'state', 'number']
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
class finishState(until):
    #__slots__ = ['robot', 'state', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0
    def run(self,data):
        self.exec.stateRunStep = self.exec.waitState 
        return 1 

class waitState(until):
    #__slots__ = ['robot', 'state', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0
    def run(self,data):
        return 0 

class InitStats(until):
    #__slots__ = ['robot', 'number']
    def __init__(self,robot):
        self.exec = robot
        self.number = 0

    def run(self,data):
        self.exec.stateRunStep = self.exec.takeGlassState 
        return 0    

class exec():
    #__slots__ = ['robot', 'state', 'number']
    def __init__(self,robot):
        super().__init__()
        self.robot = robot
        #self.state = "wait"
        self.initStats = InitStats(self)
        self.takeGlassState = takeGlassState(self)
        self.takeNguyenLieu = takeNguyenLieu(self)
        self.DuaLyThanhPham = DuaLyThanhPham(self)
        self.goHomeState = goHomeState(self)
        self.finishState = finishState(self)
        self.waitState = waitState(self)
        self.stateRunStep = self.waitState 
        self.number = 0
        
    def run(self,pos,timewait,data):
        return self.stateRunStep.run(data)

        """if (timewait == "0" or timewait == 0 ):
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
                if (int(pos) == 0) or (int(pos) == 15)or (int(pos) == 16):
                    self.number = 4
                else:
                    print("send modbus",(int(pos)-1)*2,timewait)
                    self.robot.valveModbus.setData(1,6,(int(pos)-1)*2,int(timewait))
                    self.number = 3
            elif (self.number == 3):
                modbusGet = self.robot.valveModbus.getData(1,3,(int(pos)-1)*2 + 1,1)
                print(modbusGet)
                if  int(modbusGet['data'][0])!= 1 and int(modbusGet['data'][0])!= 0:
                    self.robot.valveModbus.setData(1,16,(int(pos)-1)*2 ,[0,0])
                    self.number = 4 
            elif (self.number == 4):
                self.goto(str(pos))
                self.number = 5
            elif (self.number == 5):
                self.state = "wait"
                self.number = 0
                return True
            self.state = "waitdone"
        elif  self.state == "waitdone":  
            if (self.number != 3) and (self.number != 4):
                if (self.robot.checkStatusDoneMDI() != -1):
                    self.state = "move"
            else:
                self.state = "move"
        return False"""

    """def move(self,statep,pos):
        self.goto(str(pos)) # or self.goto("END_" + pos) 
        statep =  statep +1
        self.state = "waitdone"
        if statep == 5:
            self.state = "wait"
            statep = 0
        elif statep == 3:statep = 4

    def goto(self,pos):
        pos = getattr(posRobot,'TAKE_' +str(pos))
        print("RUN",pos)
        self.robot.sendMDI("G0.1 "+ pos)
        time.sleep(0.05)
        #while (self.robot.checkStatusDoneMDI() == -1):
        #    pass
        
    def wait(self):
        pass"""
        

class RobotControl(State):
    def __init__(self,valveModbus):
        self.valveModbus=valveModbus
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
        time.sleep(1)
        #self.myRobot=None 
        print("Init STATE")   
        self.state = 0
        self.isEMCRun = False
        self.exec = exec(self)

    def initstate(self):
        self.exec.stateRunStep = self.exec.initStats 

    def run(self, data):
        return self.exec.run("0",data[3],data)
        """stsDone = False
        datareturn = 0
        if self.state == 0 :
            stsDone = self.exec.run("0",data[3],data)  #TAKE
        elif self.state < 15 :
            stsDone = self.exec.run(self.state,data[self.state+4],data)
            
        elif self.state == 15 :
            stsDone = self.exec.run("15","1",data) #DUA RA
        elif self.state == 16 :
            stsDone = self.exec.run("16","1",data) #HOME
        if stsDone : self.state = self.state + 1
        #print("CHECK",self.state,stsDone)
        if self.state == 17:
            self.state = 0
            datareturn = 1
        return datareturn"""


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
            #self.emcstat = self.emc.stat()
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
        pass
        #self.delInit()
        #self.reload()
        self.checkEMC()

    def checkError(self):
        self.checkEMC()

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
        if self.isEMCRun ==False:
            return 1      
        return self.emccommand.wait_complete(0.001)

    def sendMDI(self,msg):
        if self.isEMCRun ==False:
            return
        self.set_mdi_mode() 
        data  = self.emccommand.mdi(msg)
        #print("MDI returnb",time.time(),data)
        #self.state = 1

    def running(self, do_poll=True):
        '''
        check wether interpreter is running.
        If so, cant switch to MDI mode.
        '''
        if do_poll:
            self.emcstat.poll()
        return (self.emcstat.task_mode == linuxcnc.MODE_AUTO and
                self.emcstat.interp_state != linuxcnc.INTERP_IDLE)

    def axis_home(self, i, c, s):
        c.home(i)
        c.wait_complete(30.0) #This command without argument waits only 1 second.
        while s.homed[i] != 1:
            print("wait H")
            time.sleep(0.1)
            s.poll()

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
        pass
        #res = subprocess.Popen(cmd.split() ) #, stdout = subprocess.PIPE)
        if (self.isRUNLCNC == False):
            cmd = ["/home/mwork/mworkcnc/scripts/linuxcnc","/home/mwork/mworkcnc/configs/mdragon/scara.ini"]
            proc = subprocess.Popen(cmd, stderr=subprocess.STDOUT )
            print("end")

            #Wait 30s at maximum
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
        #subprocess.communicate()
        sproc = subprocess.Popen(killCommand)
        sproc.wait()
        #subprocess.Popen(killCommand, stderr=subprocess.STDOUT )
    def shutdown(self):
        displayname = ""
        #displayname = StatusItem.get_ini_data( only_section='DISPLAY', only_name='DISPLAY' )['data']['parameters'][0]['values']['value']
        p = subprocess.Popen( ['pkill', displayname] , stderr=subprocess.STDOUT )

    # Check presence of LinuxCNC.
    # Returns normally, if LinuxCNC is detected.
    # Raises LinuxCNC_NotRunning, if LinuxCNC is not detected.
    def linuxCNCRun(self):
        # Check whether LinuxCNC is running.
        for lockname in ("/tmp/linuxcnc.lock", "/tmp/emc.lock"):
            if os.path.exists(lockname):
                return True
        #if not opt_watchdog:
            # The check is disabled. Return success.
        #    return True
        return False
        #printError("LinuxCNC doesn't seem to be running. "\"(Use '--watchdog off' to disable this check.)")
        #raise "LINUXCNC NOT RUN"


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