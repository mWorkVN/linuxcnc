#!/usr/bin/env python3

from stdglue import *
import sys
import traceback
import math
from interpreter import *
from emccanon import MESSAGE
import hal, time
from qtvcp.core import Status, Action, Info, Path
import inspect
import numpy as np
throw_exceptions = 1
offsetPosi = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
AxisJoint = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
TestPARA = 0
CoordinateNumber = 0
CoordinateGcode  = ["G54", "G55", "G56", "G57", "G58", "G59", "G59.1", "G59.2","G59.3"]
lenghtArm = [0,0,0,0,0,0]
ACTION = Action()
def getlenghArm():
    global lenghtArm
    for x in range(0, 5):
        lenghtArm[x] = hal.get_value("scarakins.D%d" %(x+1))
    #MESSAGE("X%.4f Y %s Z%.4f C%.4f C%.4f C%.4f"%(lenghtArm[0] ,lenghtArm[1] ,lenghtArm[2] ,lenghtArm[3],lenghtArm[4],lenghtArm[5]))
       
def scarakinematicInver(pos):
    global lenghtArm
    anglepos = [0,0,0,0]
    getlenghArm()
    try:
        x = pos['x']
        y = pos['y']
        z = pos['z']
        c = pos['c']
        q0 = q1 = 0
        a3 = c * ( math.pi / 180 )
        xt = x - lenghtArm[5]*math.cos(a3)
        yt = y - lenghtArm[5]*math.sin(a3)
        rsq = xt*xt + yt*yt
        cc = (rsq - lenghtArm[1]*lenghtArm[1] - lenghtArm[3]*lenghtArm[3]) / (2*lenghtArm[1]*lenghtArm[3])
        if(cc < -1):
            cc = -1
        if(cc > 1): 
            cc = 1
        q1 = math.acos(cc)
        iflags = 1
        joint1= float(hal.get_value("joint.1.motor-pos-cmd"))
        if (joint1 > 0):iflags = 0
        if (iflags==1):
            q1 = -q1
        q0 = math.atan2(yt, xt)
        xt = lenghtArm[1] + lenghtArm[3]*math.cos(q1)
        yt = lenghtArm[3]*math.sin(q1)
        q0 = q0 - math.atan2(yt, xt)
        q0 = q0 * (180 / math.pi)
        q1 = q1 * (180 / math.pi)
        if (q0 > 180):
            q0 = q0-360
        elif q0 < -180:
            q0 = 360 + q0
        anglepos[0] = q0
        anglepos[1] = q1
        anglepos[2] = z
        anglepos[3] = c - ( q0 + q1)
        """
        if (anglepos[3] > 180):
            anglepos[3] =  anglepos[3] - 360
        elif (anglepos[3] < -180):
            anglepos[3] =   360 - anglepos[3]
        """
    except Exception as e:
        print(" - %s" % ( e.error_message))
    return anglepos


def PAP_callLoadSettingFile(self):
    try:
        print("PAP LOAD SETTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    except Exception as e:
        self.params["_CounterNumber"]= 0
        print("Error  : {}".format(e))
    return INTERP_OK

def PAP_saveparaM580(self):
    try:
        lblPosName  = ["Pick", "Pick2", "Place", "Place2", "PlaceBad", "Home", "CurrentPallet"]
        self.params[4000] = hal.get_value("mdragon.pap.Pnp_PickX")
        self.params[4001] = hal.get_value("mdragon.pap.Pnp_PickY")
        self.params[4002] = hal.get_value("mdragon.pap.Pnp_PickZ")
        self.params[4003] = hal.get_value("mdragon.pap.Pnp_PickC")
        self.params[4004] = hal.get_value("mdragon.pap.Pnp_Pick2Z")
        self.params[4005] = hal.get_value("mdragon.pap.Pnp_Pick2C")
        self.params[4007] = hal.get_value("mdragon.pap.Pnp_HomeX")
        self.params[4008] = hal.get_value("mdragon.pap.Pnp_HomeY")
        self.params[4009] = hal.get_value("mdragon.pap.Pnp_HomeZ")
        self.params[4010] = hal.get_value("mdragon.pap.Pnp_HomeC")
        self.params[4011] = hal.get_value("mdragon.pap.Pnp_PlaceBadX")
        self.params[4012] = hal.get_value("mdragon.pap.Pnp_PlaceBadY")
        self.params[4013] = hal.get_value("mdragon.pap.Pnp_PlaceBadZ")
        self.params[4014] = hal.get_value("mdragon.pap.Pnp_PlaceBadC")
        self.params[4015] = hal.get_value("mdragon.pap.Pnp_numpalletX")
        self.params[4016] = hal.get_value("mdragon.pap.Pnp_numpalletY")
        self.params[4017] = hal.get_value("mdragon.pap.Pnp_numpalletZ")
        self.params[4018] = hal.get_value("mdragon.pap.Pnp_distanceX")
        self.params[4019] = hal.get_value("mdragon.pap.Pnp_distanceY")
        self.params[4020] = hal.get_value("mdragon.pap.Pnp_distanceZ")
        self.params[4021] = hal.get_value("mdragon.pap.Pnp_PlaceX")
        self.params[4022] = hal.get_value("mdragon.pap.Pnp_PlaceY")
        self.params[4023] = hal.get_value("mdragon.pap.Pnp_PlaceZ")
        self.params[4024] = hal.get_value("mdragon.pap.Pnp_PlaceC")
        self.params[4025] = hal.get_value("mdragon.pap.Pnp_Place2Z")
        self.params[4026] = hal.get_value("mdragon.pap.Pnp_Place2C")
        self.params[4027] = hal.get_value("mdragon.pap.pnp-speed-zu")
        self.params[4028] = hal.get_value("mdragon.pap.pnp-speed-zd")
        self.params[4029] = hal.get_value("mdragon.pap.pnp-speed")
        self.params[4006] = self.params[4029]
        self.params[4030] = hal.get_value("mdragon.pap.Pnp_numpalletpickX")
        self.params[4031] = hal.get_value("mdragon.pap.Pnp_numpalletpickY")
        self.params[4032] = hal.get_value("mdragon.pap.Pnp_numpalletpickZ")
        self.params[4033] = hal.get_value("mdragon.pap.Pnp_distancepickX")
        self.params[4034] = hal.get_value("mdragon.pap.Pnp_distancepickY")
        self.params[4035] = hal.get_value("mdragon.pap.Pnp_distancepickZ")
    except Exception as e:
        self.params["_CounterNumber"]= 0
    return INTERP_OK

def PAP_updatePalletToNewCol(self):
    try:
        self.params[5381] = hal.get_value("mdragon.pap.Pnp_CurrentPalletX")
        self.params[5382] = hal.get_value("mdragon.pap.Pnp_CurrentPalletY")
        self.params[5383] = hal.get_value("mdragon.pap.Pnp_CurrentPalletZ")
        self.params[5384] = hal.get_value("mdragon.pap.Pnp_CurrentPalletpickX")
        self.params[5385] = hal.get_value("mdragon.pap.Pnp_CurrentPalletpickY")
        self.params[5386] = hal.get_value("mdragon.pap.Pnp_CurrentPalletpickZ")
    except Exception as e:
        self.params["_CounterNumber"]= 0
    return INTERP_OK

def PAP_updateCurrentPallet(self):
    try:
        hal.set_p("mdragon.pap.Pnp_CurrentPalletX",str(self.params[5381]))
        hal.set_p("mdragon.pap.Pnp_CurrentPalletY",str(self.params[5382]))
        hal.set_p("mdragon.pap.Pnp_CurrentPalletZ",str(self.params[5383]))
        hal.set_p("mdragon.pap.Pnp_CurrentPalletpickX",str(self.params[5384]))
        hal.set_p("mdragon.pap.Pnp_CurrentPalletpickY",str(self.params[5385]))
        hal.set_p("mdragon.pap.Pnp_CurrentPalletpickZ",str(self.params[5386]))
    except Exception as e:
        self.params["_CounterNumber"]= 0
    return INTERP_OK