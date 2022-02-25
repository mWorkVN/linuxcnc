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
