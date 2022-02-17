#!/usr/bin/env python3

from stdglue import *
import os
import sys
import traceback
import math
from interpreter import *
from emccanon import MESSAGE
import hal, time, select
import inspect
import numpy as np


throw_exceptions = 1
#                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
actuatorValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0]
actuatorOpenValue =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0]

def gethalvalue(status):
    print(" Get Value " , status)
    try:
        statusControl = "_close"
        if (status==1):
            statusControl = "_open"
        actuatorValue[0] = hal.get_value("mdragon.actuator.chooseActuator")
        name = 'grip'
        if (actuatorValue[0] == 1):
            name = 'va'
        actuatorValue[1]  = hal.get_value("mdragon.actuator." + name + statusControl + "_wait_choose")
        actuatorValue[2]  = hal.get_value("mdragon.actuator." + name + statusControl + "_wait_time")
        actuatorValue[3]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control1_pin") # pin input danh tư 0-4 cho system
        actuatorValue[4]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control1_status")
        actuatorValue[5]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control2_pin")
        actuatorValue[6]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control2_status")
        actuatorValue[7]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control3_pin")
        actuatorValue[8]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control3_status")
        actuatorValue[9]  = hal.get_value("mdragon.actuator." + name + statusControl + "_control4_pin")
        actuatorValue[10] = hal.get_value("mdragon.actuator." + name + statusControl + "_control4_status")
    except Exception as e:
        print(e)

def controlPin(pin, value):
    mode = 'M65' # OFF
    if value == 1:
        mode = 'M64'
    #print('{} P{}'.format(mode,pin))
    return '{} P{}'.format(mode,pin)

def waitPin(pin, value):
    mode = 'L4' #OFF
    if value == 1:
        mode = 'L3'
    #print('M66 P{} {} Q10'.format(pin,mode))
    return 'M66 P{} {} Q10'.format(pin,mode)

def waitTime(value):
    return 'M180 P{}'.format(value/1000)

def actuatorClose(self):
    try:
        gethalvalue(0)
        #print(" Close Value ", actuatorValue[0],actuatorValue[1],actuatorValue[2],actuatorValue[3],actuatorValue[4],actuatorValue[5],actuatorValue[6],actuatorValue[7],actuatorValue[8],actuatorValue[9],actuatorValue[10])
        if (actuatorValue[0] == 0): # grip control
            self.execute(controlPin(actuatorValue[3],actuatorValue[4]))
            if (actuatorValue[1] == 0): 
                self.execute(waitTime(actuatorValue[2]))
            else:
                self.execute(waitPin(actuatorValue[5],actuatorValue[6]))
            self.execute(controlPin(actuatorValue[7],actuatorValue[8]))
            self.execute(controlPin(actuatorValue[9],actuatorValue[10]))
        else: #vacum control
            self.execute(controlPin(actuatorValue[3],actuatorValue[4]))
            if (actuatorValue[1] == 0): 
                self.execute(waitTime(actuatorValue[2]))
            else:
                self.execute(waitPin(actuatorValue[5],actuatorValue[6]))
            self.execute(controlPin(actuatorValue[7],actuatorValue[8]))
            self.execute(controlPin(actuatorValue[9],actuatorValue[10]))
        yield INTERP_EXECUTE_FINISH
        return INTERP_OK
    except Exception as e:
        print(e)
        return INTERP_ERROR   

def actuatorOpen(self):
    try:
        gethalvalue(1)
        #print(" open Value ", actuatorValue[0],actuatorValue[1],actuatorValue[2],actuatorValue[3],actuatorValue[4],actuatorValue[5],actuatorValue[6],actuatorValue[7],actuatorValue[8],actuatorValue[9],actuatorValue[10])
        gcode = ""
        if (actuatorValue[0] == 0): # grip control
            self.execute(controlPin(actuatorValue[3],actuatorValue[4]))
            if (actuatorValue[1] == 0): 
                self.execute(waitTime(actuatorValue[2]))
            else:
                self.execute(waitPin(actuatorValue[5],actuatorValue[6]))
            self.execute(controlPin(actuatorValue[7],actuatorValue[8]))
            self.execute(controlPin(actuatorValue[9],actuatorValue[10]))
        else: #vacum control
            self.execute(controlPin(actuatorValue[3],actuatorValue[4]))
            if (actuatorValue[1] == 0): 
                self.execute(waitTime(actuatorValue[2]))
            else:
                self.execute(waitPin(actuatorValue[5],actuatorValue[6]))
            self.execute(controlPin(actuatorValue[7],actuatorValue[8]))
            self.execute(controlPin(actuatorValue[9],actuatorValue[10]))
        yield INTERP_EXECUTE_FINISH
        return INTERP_OK
    except Exception as e:
        print(e)
        return INTERP_ERROR   
