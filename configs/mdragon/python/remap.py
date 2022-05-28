#!/usr/bin/env python3

import os
import sys
import time, select , math, traceback
import hal
from util import lineno, call_pydevd
from interpreter import *
from stdglue import *
from emccanon import MESSAGE, SET_MOTION_OUTPUT_BIT, CLEAR_MOTION_OUTPUT_BIT,SET_AUX_OUTPUT_BIT,CLEAR_AUX_OUTPUT_BIT
from mWork_Gcode_PickandPlace import *
from mWork_actuator import *

import inspect
import numpy as np

xold = 0
xyol = 0
throw_exceptions = 1
offsetPosi = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
AxisJoint = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
TestPARA = 0
CoordinateNumber = 0
CoordinateGcode  = ["G54", "G55", "G56", "G57", "G58", "G59", "G59.1", "G59.2","G59.3"]
lenghtArm = [0,0,0,0,0,0]

_sticky_params = dict()

def m432remap(self):
    global TestPARA
    #hal.component_exists("TestPARA")
    debug = hal.get_value("joint.0.free-pos-cmd")
    return INTERP_OK

def m435remap(self):
    global lenghtArm
    for x in range(0, 5):
        lenghtArm[x] = hal.get_value("scarakins.D%d" %(x+1))
    #print("lenghtArm %d-%d-%d-%d-%d-%d" %(lenghtArm[0],lenghtArm[1],lenghtArm[2],lenghtArm[3],lenghtArm[4],lenghtArm[5]))
    return INTERP_OK  

def m462OutAnDelay(self, **words):
    """ remap function which does the equivalent of M62, but via Python """
    print("begin",time.time())
    p = int(words['p']) #pin OUT
    q = float(words['q']) #delay time
    #SET_MOTION_OUTPUT_BIT(p)
    self.execute("M64 P{}".format(p))
    self.execute("M180 P{}".format(q))
    self.execute("M65 P{}".format(p))
    yield INTERP_EXECUTE_FINISH
    #CLEAR_MOTION_OUTPUT_BIT(p)
    print("end",time.time())
    return INTERP_OK

def m463OutRCAnDelay(self, **words):
    p = float(words['p']) # goc
    q = float(words['q']) #delay time
    hal.set_p("hm2_7i80.0.rcpwmgen.00.width",str(p))
    self.execute("M180 P{}".format(q))
    yield INTERP_EXECUTE_FINISH
    return INTERP_OK




def convertJoinMode(self):
    global offsetPosi
    global AxisJoint
    global CoordinateNumber
    global CoordinateGcode
    try:
        value = hal.get_value("motion.switchkins-type")
        if (value == 1):
            self.execute("M66 E0 L0")
        else:
            SWITCHKINS_PIN = 3
            kinstype = 1  
            CoordinateNumber = self.params[5220]
            self.execute("M129")  
            self.execute("M68 E%d Q%d"%(SWITCHKINS_PIN,kinstype))
            self.execute("M66 E0 L0")
        return True
    except Exception as e:
        return False   

def m439remap(self, **words): #convert to joint mode
    if convertJoinMode(self):return INTERP_OK
    return INTERP_ERROR

def convertWorldMode(self):   
    global offsetPosi
    global AxisJoint
    global CoordinateNumber
    global CoordinateGcode
    try:
        value = hal.get_value("motion.switchkins-type")

        if (value == 0):
            self.execute("M66 E0 L0")
        else:
            #numberCoor = int(CoordinateNumber-1)
            #if (numberCoor > 8):
            #    pass
            #else:
            #    self.execute(CoordinateGcode[numberCoor]) # return CoordinateGcode
            SWITCHKINS_PIN = 3
            kinstype = 0
            self.execute("M128")
            self.execute("M68 E%d Q%d"%(SWITCHKINS_PIN,kinstype))
            self.execute("M66 E0 L0")
        return True
    except Exception as e:
        print("REMAP - Error M428 Exception:{}".format(e.error_message))
        return False

def m438remap(self, **words): # convert to world mode
    if convertWorldMode(self):return INTERP_OK
    return INTERP_ERROR

def g01testskins(self, **words):
    global lenghtArm
    global xold, yold
    pos={'x':0,'y':0,'z':0,'c':0}
    fcmd =""
    hasF = False
    try:
        cmd = {'x':"",'y':"",'z':"",'c':"",'f':""}
        typeGcode = "g0"
        for name in cmd:
            if name == "f":
                if name in words:
                    typeGcode = "g1"
                    cmd[name] = "F{} ".format(words[name])     
            elif name in words:
                pos[name] = float(words[name])
                cmd[name] = "{}{} ".format(name,words[name])
                statusKin = 1
            else: 
                pos[name]  = float(hal.get_value('axis.{}.pos-commanded'.format(name)))   
        gcodecmd="G53 %s X%.4fY%.4fZ%.4f C %.4f %s "%(typeGcode, pos['x'] ,pos['y'] ,pos['z'] ,pos['c'], cmd["f"])
        self.execute(gcodecmd )
        yield INTERP_EXECUTE_FINISH
    except Exception as e:
        self.set_errormsg(e)
        return INTERP_ERROR
    return INTERP_OK



def check_coords(self, axis, wanted):
    actual = getattr(self, "current_%s" % axis)
    wanted = float(wanted)
    if abs(actual - wanted) > 0.000001:
        #print("(ERROR  %s:  %0.1f != %0.1f)" % (axis, actual, wanted))
        self.execute("(ERROR  %s:  %0.1f != %0.1f)" % (axis, actual, wanted))
    else:
        self.execute("(%s: %0.1f = %0.1f)" % (axis, actual, wanted))
        #print("(%s: %0.1f = %0.1f)" % (axis, actual, wanted))
#
# Move Joint in world mode
# ex: Move to X50 Y50 in world mode
# my code will caculater invert kinematic to get joint pos
# After conver mode to joint mode, move and return world mode
#
def g01_move_joint_by_world(self, **words):
    global lenghtArm
    global xold
    global yold
    pos={'x':0,'y':0,'z':0,'c':0}
    fcmd =""
    hasF = False
    try:
        value = hal.get_value("motion.switchkins-type")
        if (value == 0):
            convertJoinMode(self)
        self.execute("M66 E0 L0")
        yield INTERP_EXECUTE_FINISH
        cmd = {'x':"",'y':"",'z':"",'c':"",'f':""}
        typeGcode = "g0"
        for name in cmd:
            if name == "f":
                if name in words:
                    typeGcode = "g1"
                    cmd[name] = "F{} ".format(words[name])     
            elif name in words:
                pos[name] = float(words[name])
                cmd[name] = "{}{} ".format(name,words[name])
            else: 
                pos[name]  = float(hal.get_value('axis.{}.pos-cmd'.format(name)))   
        anglepos = scarakinematicInver(pos)
        xcmd = ""
        if (xold != anglepos[0]) or (yold != anglepos[1]):
            xcmd = "X%.4f Y%.4f"%(anglepos[0],anglepos[1])
            xold= anglepos[0]
            yold= anglepos[1]
        gcodecmd="G53 %s X%f Y%f Z %f C %f %s "%(typeGcode, anglepos[0] ,anglepos[1] ,anglepos[2] ,anglepos[3], cmd["f"])
        self.execute(gcodecmd )
        check_coords(self, 'z', anglepos[2])
        if (value==0):
            convertWorldMode(self)
        self.execute("M66 E0 L0")
        yield INTERP_EXECUTE_FINISH
    except Exception as e:
        self.set_errormsg(e)
        return INTERP_ERROR
    return INTERP_OK

def g11remapskins(self, **words):
    global lenghtArm
    pos={'x':0,'y':0,'z':0,'c':0}
    try:
        value = hal.get_value("motion.switchkins-type") 
        xposvalue = 0
        yposvalue = 0
        statusKin = 0
        cmd = {'x':"",'y':"",'z':"",'c':"",'f':""}
        for name in cmd:
            if name == "f":
                if name in words:
                    cmd[name] = "F{} ".format(words[name])     
            elif name in words:
                pos[name] = float(words[name])
                cmd[name] = "{}{} ".format(name,words[name])
                statusKin = 1
            else: 
                pos[name]  = float(hal.get_value('axis.{}.pos-commanded'.format(name)))     
        cmdgcode = ""
        if (value==1):
            anglepos = scarakinematicInver(pos)
            gcodecmd="G53 G01 X%.4f Y%.4f Z%.4f C%.4f %s"%(anglepos[0] ,anglepos[1] ,anglepos[2] ,anglepos[3], cmd["f"])
            self.execute(gcodecmd)
        elif (value==0): 
            print("REMAP - G1.1 {} {} {} {} {}".format(cmd["x"],cmd["y"],cmd["z"],cmd["c"],cmd["f"])) 
    except Exception as e:
        return INTERP_ERROR
    return INTERP_OK
#
# Move Joint. If world mode, my code will convert to joint mode to move and back to world mode
# Ex: G0.2 X20 Y30 
# Or with F: G0.2 X20 Y30 F1000
#
def g02_move_joint(self, **words):
    global lenghtArm
    global xold
    global yold
    pos={'x':0,'y':0,'z':0,'c':0}
    try:
        value = hal.get_value("motion.switchkins-type")
        if (value == 0):
            convertJoinMode(self)
        self.execute("M66 E0 L0")
        yield INTERP_EXECUTE_FINISH
        cmd = {'x':"",'y':"",'z':"",'c':"",'f':""}
        typeGcode = "G0"
        gcodestr=""
        for name in cmd:
            if name == "f":
                if name in words:
                    typeGcode = "G1"
                    gcodestr="{} F{}".format(gcodestr,words[name])
                    cmd[name] = "F{} ".format(words[name])     
            elif name in words:
                pos[name] = float(words[name])
                cmd[name] = "{}{} ".format(name,words[name])
                gcodestr="{} {}{}".format(gcodestr,name,pos[name])
        gcodecmd="{} {}".format(typeGcode, gcodestr)
        self.execute(gcodecmd ) 
        if (value==0):
            convertWorldMode(self)
        self.execute("M66 E0 L0")
        yield INTERP_EXECUTE_FINISH
    except Exception as e:
        self.set_errormsg(e)
        return INTERP_ERROR
    return INTERP_OK