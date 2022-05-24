#!/usr/bin/ python3

from __future__ import print_function

import os
import sys
import traceback
import time, select
#from PyQt5.QtCore import pyqtSlot, QFile, QRegExp, Qt, QTextStream, QEvent
#from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QMessageBox,
#        QStyleFactory, QWidget, QColorDialog)
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from qtvcp.widgets.dro_widget import DROLabel
from qt5_graphics import Lcnc_3dGraphics
from qtvcp.core import Info, Path, Action, Status
from qtvcp.lib.notify import Notify
from qtvcp import logger
import linuxcnc
from qtvcp.widgets.widget_baseclass import _HalWidgetBase, hal
from linuxcnc import OPERATOR_ERROR, NML_ERROR
#from threading import *
from subprocess import call as CALL
LOG = logger.getLogger(__name__)

if os.path.split(sys.argv[0])[0] == '/usr/bin':
	GUI_PATH = '/usr/lib/python3/dist-packages/libemclog'
	print('Installed')

if os.path.split(sys.argv[0])[0] == '.':
	GUI_PATH = os.path.split(os.path.realpath(sys.argv[0]))[0]
	print('In Development')
STATUS = Status()	
INFO = Info()
PATH = Path()
ACTION = Action()
DATADIR = os.path.abspath( os.path.dirname( __file__ ) )
lblPosName  = ["Pick", "Pick2", "Place", "Place2", "PlaceBad", "Home", "CurrentPallet", "CurrentPalletpick","distance","distancepick"]
#class emclogwitget(QtWidgets.QWidget,QPyDesignerCustomWidgetPlugin):_HalWidgetBase
class threadwait(QtCore.QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def run(self):
        QtCore.QThread.msleep(1000)
        self.finished.emit()


class mwork_pickandplace(QtWidgets.QWidget,_HalWidgetBase): #
    def __init__(self, parent=None, widgets=None , pathIniFolder = None):
        super(mwork_pickandplace, self).__init__(parent)
        self.iniFolder = pathIniFolder
        self._mode = False
        self.w=widgets
        self.statusHomeAll = False
        self._scale = 1.0
        self.reference_type = 0
        self.metric_text_template = '%10.3f'
        self.imperial_text_template = '%9.4f'
        self.angular_text_template = '%9.2f'
        self.lastPosition = []
        self.modescara = "M428"
        self.statuMode = False
        #self.init_preferences()
        #self.setMinimumSize(800, 800)
        self.bluck_update = True	
        self.filename = os.path.join(INFO.LIB_PATH,'widgets_ui', 'mwork_pickandplace.ui')
        try:
            self.instance = uic.loadUi(self.filename, self)
        except AttributeError as e:
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_lines = traceback.format_exc().splitlines()
            print()
            print("Ui loadinr error",formatted_lines[0])
            #traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            print(formatted_lines[-1])
            if 'slotname' in formatted_lines[-2]:
                LOG.critical('Missing slot name {}'.format(e))
            else:
                LOG.critical(e)
        self.qclip = QApplication.clipboard()
        self._joint_type = 1
        self._joint_type  = INFO.JOINT_TYPE_INT[0]
        if self._joint_type == linuxcnc.ANGULAR:
            self._current_text_template =  self.angular_text_template
        elif self.display_units_mm:
            self._current_text_template = self.metric_text_template
        else:
            self._current_text_template = self.imperial_text_template
        self.stackedWidget.setCurrentIndex(1)
        STATUS.connect('current-position', self.update)
        STATUS.connect('motion-mode-changed',self.motion_mode)
        STATUS.connect('metric-mode-changed', self._switch_units)
        STATUS.connect('dro-reference-change-request', self._status_reference_change)
        STATUS.connect('all-homed', self.all_homed)
        STATUS.connect('not-all-homed', self.not_all_homed)
        self.settingHalPin()
        #self.callLoadSettingFile()
        self.dro_label_2 = DROLabel()
        self.setupConnections()
        self.initvalue()

    def _hal_init(self):
        if self.w.PREFS_:
            print("init hal value")
            axes = ['X','Y','Z','C']
            for lblPos in lblPosName: # add each axis position       
                for axis in axes: # add each axis position
                    value = str(self.w.PREFS_.getpref('Pnp_' + lblPos +  axis, 0, float, 'PICK_AND_PLACE'))
                    self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_' + lblPos +  axis, value) 
            for axis in axes: # add each axis position
                value = str(self.w.PREFS_.getpref('Pnp_numpallet' +  axis, 0, int, 'PICK_AND_PLACE'))             
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_numpallet' +  axis, value)
                value = str(self.w.PREFS_.getpref('Pnp_numpalletpick' +  axis, 0, int, 'PICK_AND_PLACE'))             
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_numpalletpick' +  axis, value)
            self.HAL_GCOMP_.setp ('mdragon.pap.pnp-speed',  str(self.w.PREFS_.getpref('Pnp_Speed', 0, int, 'PICK_AND_PLACE')))
            self.HAL_GCOMP_.setp ('mdragon.pap.pnp-speed-zu',  str(self.w.PREFS_.getpref('Pnp_SpeedZU', 0, int, 'PICK_AND_PLACE')))
            self.HAL_GCOMP_.setp ('mdragon.pap.pnp-speed-zd',  str(self.w.PREFS_.getpref('Pnp_SpeedZD', 0, int, 'PICK_AND_PLACE')))
            self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_InputBad',  str(self.w.PREFS_.getpref('Pnp_InputBad', 0, int, 'PICK_AND_PLACE')))
            CALL(['halcmd', 'net','pinIn' + str(self.w.PREFS_.getpref('Pnp_InputBad', 0, int, 'PICK_AND_PLACE')), 'mdragon.pap.pnp-inputpadpinstatus'])
    def _hal_cleanup(self):
        if self.PREFS_:
            pass

    def savepara_click(self):
        if self.w.PREFS_:
            axes = ['X','Y','Z','C']
            for lblPos in lblPosName: # add each axis position       
                for axis in axes: # add each axis position
                    self.w.PREFS_.putpref('Pnp_' + lblPos +  axis, self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_' +lblPos + axis), float, 'PICK_AND_PLACE')	
            for axis in axes: # add each axis position
                self.w.PREFS_.putpref('Pnp_numpallet'  +  axis, self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_numpallet' + axis), int, 'PICK_AND_PLACE')
                self.w.PREFS_.putpref('Pnp_numpalletpick'  +  axis, self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_numpalletpick' + axis), int, 'PICK_AND_PLACE')		
            self.w.PREFS_.putpref('Pnp_Speed', self.HAL_GCOMP_.getvalue ('mdragon.pap.pnp-speed'), int, 'PICK_AND_PLACE')	
            self.w.PREFS_.putpref('Pnp_SpeedZU', self.HAL_GCOMP_.getvalue ('mdragon.pap.pnp-speed-zu'), int, 'PICK_AND_PLACE')	
            self.w.PREFS_.putpref('Pnp_SpeedZD', self.HAL_GCOMP_.getvalue ('mdragon.pap.pnp-speed-zd'), int, 'PICK_AND_PLACE')	
            self.w.PREFS_.putpref('Pnp_InputBad', self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_InputBad'), int, 'PICK_AND_PLACE')	

    def qtvcptest(self):
        self.lblColZ_2.setText(str(self.HAL_GCOMP_['qtvcptest']) )
        #self.mbox('scgg')
	
    def all_homed(self, obj):
        self.statusHomeAll = True
        self.mdi_savaHalToFile()
        self.stackedWidget.setCurrentIndex(1)
		
    def not_all_homed(self, obj, list):
        self.statusHomeAll = False
        self.stackedWidget.setCurrentIndex(2)
		
    def changescarachange(self):
        self.mbox('sc')
        self.statuMode = True
        if self.HAL_GCOMP_.getvalue('motion.switchkins-type') == 0:
            self.modescara = "M439"
        elif self.HAL_GCOMP_.getvalue('motion.switchkins-type') == 1:
            self.modescara = "M438"
        else:
            self.modescara = "M440"		

    def initvalue(self):
        self.tabWidget.setCurrentIndex(0)

    def settingHalPin(self):
        global lblPosName
        axes = ['X','Y','Z','C']
        pin = self.HAL_GCOMP_.newpin("changescaraFFF", hal.HAL_FLOAT, hal.HAL_IN)
        CALL(['halcmd', 'net', ':kinstype-select', 'mdragon.changescaraFFF'])
        pin = self.HAL_GCOMP_.newpin("qtvcpchangevalue", hal.HAL_U32, hal.HAL_IN)
        for lblPos in lblPosName: # add each axis position       
            for axis in axes: # add each axis position
                pin = self.HAL_GCOMP_.newpin("pap.Pnp_" + lblPos +  axis, hal.HAL_FLOAT, hal.HAL_IN)
                pin.value_changed.connect(lambda data,lblPos=lblPos,axis=axis: self.updateHalToUi(lblPos,axis))    
        for axis in axes: # add each axis position
            pin = self.HAL_GCOMP_.newpin("pap.Pnp_numpallet" +  axis, hal.HAL_U32, hal.HAL_IN)
            pin.value_changed.connect(lambda data,axis=axis,type="": self.updatePalletHalToUi(axis,type))
            pin = self.HAL_GCOMP_.newpin("pap.Pnp_numpalletpick" +  axis, hal.HAL_U32, hal.HAL_IN)
            pin.value_changed.connect(lambda data,axis=axis,type="pick": self.updatePalletHalToUi(axis,type))
        pin = self.HAL_GCOMP_.newpin("pap.pnp-speed", hal.HAL_U32, hal.HAL_IN)
        pin.value_changed.connect(lambda data,lblPos="Speed",axis="": self.updateHalToUi(lblPos,axis))   
        pin = self.HAL_GCOMP_.newpin("pap.pnp-speed-zu", hal.HAL_U32, hal.HAL_IN)
        pin.value_changed.connect(lambda data,lblPos="SpeedZU",axis="": self.updateHalToUi(lblPos,axis))  
        pin = self.HAL_GCOMP_.newpin("pap.pnp-speed-zd", hal.HAL_U32, hal.HAL_IN)
        pin.value_changed.connect(lambda data,lblPos="SpeedZD",axis="": self.updateHalToUi(lblPos,axis))  
        pin = self.HAL_GCOMP_.newpin("pap.Pnp_InputBad", hal.HAL_U32, hal.HAL_IN)
        pin.value_changed.connect(lambda data,lblPos="InputBad",axis="": self.updateHalToUi(lblPos,axis)) 
        pin = self.HAL_GCOMP_.newpin("pap.pnp-inputpadpinstatus", hal.HAL_BIT, hal.HAL_IN)
        pin.value_changed.connect(lambda data: self.pinBadChange(data)) 

    def pinBadChange(self,data):
        print("Pin change ", data)
        self.led.change_state(data)
        self.StatusIN.setText(str(data))
        
    def setupConnections(self):
        lblupdate = ["Pick", "Pick2", "Place", "Place2", "PlaceBad", "Home"]
        
        for lblPos in lblupdate: # add each axis position
            getattr(self, 'btnUpdate'  + lblPos).clicked.connect(lambda data, label = lblPos: self.updateUiToHal(label))
            getattr(self, 'btnGoto'  + lblPos).clicked.connect(lambda data, label = lblPos: self.moveToTeachPoint(label))
        
        self.btnSave.clicked.connect(self.savaHalToFile)
        self.btnUpdatePallet.clicked.connect(lambda data,status=0: self.updatePalletUiToHal(status))
        self.btnUpdatePalletpick.clicked.connect(lambda data,status=0: self.updatePalletUiToHal(status))
        self.btnUpdatePalletRun.clicked.connect(lambda data,status=1: self.updatePalletUiToHal(status))
        self.btnUpdatePalletPickRun.clicked.connect(lambda data,status=2: self.updatePalletUiToHal(status))
        self.btnLoadToGcode.clicked.connect(self.loadAndRunGcode)
        self.btnUpdatespeed.clicked.connect(self.btnUpdatespeed_click)
        self.btnUpdatePinBad.clicked.connect(self.btnUpdatePinBad_click)

    def loadAndRunGcode(self):
        try:
            path = self.iniFolder
            goal_dir = os.path.join(path,'../', 'gcode',"pickandplace.ngc")
            goal_dir = os.path.abspath(goal_dir)
            ACTION.OPEN_PROGRAM(goal_dir)
            STATUS.emit('update-machine-log', 'Loaded: ' + goal_dir, 'TIME')
            ACTION.SET_AUTO_MODE()
        except Exception as e:
            LOG.error("Load file error: {}".format(e))
            STATUS.emit('error', NML_ERROR, "Load file error: {}".format(e))
        
    def savaHalToFile(self):
        self.savepara_click()
        self.mdi_savaHalToFile()

    def updatePalletUiToHal(self,status):
        axes = ['X','Y','Z']
        if status ==0:
            for axis in axes: # add each axis position currentIndex
                position = str(getattr(self, 'lblPosdistance' + axis).text())
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_distance' + axis,position)
                position = str(getattr(self, 'lblPosdistancepick' + axis).text())
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_distancepick' + axis,position)
            for axis in axes: # add each axis position currentIndex
                position = str(getattr(self, 'lblPosnumpallet' + axis).currentIndex())
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_numpallet' + axis,position)
                position = str(getattr(self, 'lblPosnumpalletpick' + axis).currentIndex())
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_numpalletpick' + axis,position)
        elif status ==1:
            for axis in axes: # add each axis position currentIndex
                position = str(getattr(self, 'lblPosUpdatePallet' + axis).text())
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_CurrentPallet' + axis,position)
            self.mdi_updatePalletToNewCol()
        elif status ==2:
            for axis in axes: # add each axis position currentIndex
                position = str(getattr(self, 'lblPosUpdatePalletpick' + axis).text())
                self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_CurrentPalletpick' + axis,position)
            self.mdi_updatePalletToNewCol()
        
    def updateHalToUi(self, name, axis):
        if name =="Place2" or name =="Pick2":
            if axis == "X" or axis == "Y":
                return
        if name == "SpeedZU" or name == "SpeedZD" or name == "Speed":
            namehal = ""
            if name=="SpeedZU":
                namehal = "speed-zu"    
            elif name=="SpeedZD":
                namehal = "speed-zd"  
            elif name=="Speed":
                namehal = "speed" 
            getattr(self, 'lblPos' +name + axis).setText(str(self.HAL_GCOMP_.getvalue ('mdragon.pap.pnp-' +namehal + axis))) 
            return
        if name =="CurrentPallet" and axis == "C":
            return
        if name =="CurrentPalletpick" and axis == "C":
            return
        if name =="distance" and axis == "C":
            return
        if name =="distancepick" and axis == "C":
            return
        if name=="InputBad":
            self.Pnp_InputPinBad.setCurrentIndex(self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_InputBad'))
            return
        getattr(self, 'lblPos' +name + axis).setText(str(self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_' +name + axis))) 

    def updatePalletHalToUi(self, name,type):
        axes = ['X','Y','Z']
        for axis in axes: # add each axis position
            getattr(self, 'lblPosnumpallet'+type+ axis).setCurrentIndex(self.HAL_GCOMP_.getvalue ('mdragon.pap.Pnp_numpallet' +type+ axis))
    
    def moveToTeachPoint(self, name):
        if self.HAL_GCOMP_.getvalue('motion.switchkins-type') ==0:
            self.mdi_callloadJoinMode()
            time.sleep(0.3)	
        axes = ['X','Y','Z','C']
        if name =="Place2" or name =="Pick2":
            axes = ['Z','C']
        gcodetext = "G0.1 "
        for axis in axes: # add each axis position
            position = str(getattr(self, 'lblPos' + name + axis).text())
            gcodetext = gcodetext + axis + position + " "
        self.mdi_call_move(gcodetext)
        self.mbox(gcodetext)
            
    def btnUpdatespeed_click(self):
        self.HAL_GCOMP_.setp ('mdragon.pap.pnp-speed',self.lblPosSpeed.text())
        self.HAL_GCOMP_.setp ('mdragon.pap.pnp-spee-zu',self.lblPosSpeedZU.text())
        self.HAL_GCOMP_.setp ('mdragon.pap.pnp-speed-zd',self.lblPosSpeedZD.text())

    def btnUpdatePinBad_click(self):
        self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_InputBad',str(self.Pnp_InputPinBad.currentIndex()))

    def updateUiToHal_Thread(self,status,name):
        #time.sleep(2)
        axes = ['X','Y','Z','C']
        if name =="Place2" or name =="Pick2":
            axes = ['Z','C']
        if name =="CurrentPallet":
            axes = ['X','Y','Z']
        for axis in axes: # add each axis position
            position = str(getattr(self, 'position_' + axis).text())
            self.HAL_GCOMP_.setp ('mdragon.pap.Pnp_' +name + axis,position)
        if status:
            self.mdi_callloadJoinMode()    
  

    def finishThread(self):
        pass
        #self.mdi_callloadJoinMode()
    def updateUiToHal(self, name): #motion.switchkins-type = changescara
        statusScara = False
        if self.HAL_GCOMP_.getvalue('motion.switchkins-type')==1:
            self.mdi_callloadWorldMode()	
            statusScara = True
        if (statusScara):
            self.thread = QThread()
            self.threadwait = threadwait()
            self.threadwait.moveToThread(self.thread)
            self.thread.started.connect(self.threadwait.run)
            self.threadwait.finished.connect(self.thread.quit)
            self.threadwait.finished.connect(lambda status=statusScara,name=name: self.updateUiToHal_Thread(status,name))
            self.threadwait.finished.connect(self.threadwait.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
        else:
            self.updateUiToHal_Thread(statusScara,name)
		
    def mbox(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        

    def _switch_units(self, widget, data):
        self.display_units_mm = data
        self.update_units()

    def update_units(self):
        if self._joint_type == linuxcnc.ANGULAR:
            self._current_text_template =  self.angular_text_template
        elif self.display_units_mm:
            self._current_text_template = self.metric_text_template
        else:
            self._current_text_template = self.imperial_text_template

    def motion_mode(self, w, mode):
        if mode == linuxcnc.TRAJ_MODE_COORD:
            pass
        # Joint mode
        elif mode == linuxcnc.TRAJ_MODE_FREE:
            self._mode = False
        # axis 
        elif mode == linuxcnc.TRAJ_MODE_TELEOP:
            self._mode = True
    
    def _status_reference_change(self,w ,value):
        self.reference_type = value
	
    def update(self, widget, absolute, relative, dtg, joint):
        #absolute = INFO.convert_units_9(absolute)
        #relative = INFO.convert_units_9(relative)
        tmpl = lambda s: self._current_text_template % s
        self.position_X.setText(tmpl(absolute[0]*self._scale))
        self.position_Y.setText(tmpl(absolute[1]*self._scale))
        self.position_Z.setText(tmpl(absolute[2]*self._scale))
        self.position_C.setText(tmpl(absolute[5]*self._scale))
        """
        if self.reference_type == 0:
            if not self._mode and STATUS.stat.kinematics_type != linuxcnc.KINEMATICS_IDENTITY:
                self.position_X.setText(tmpl(joint[0]))
                self.position_Y.setText(tmpl(joint[1]))
                self.position_Z.setText(tmpl(joint[2]))
                self.position_C.setText(tmpl(joint[3]))
            else:
                self.position_X.setText(tmpl(absolute[0]*self._scale))
                self.position_Y.setText(tmpl(absolute[1]*self._scale))
                self.position_Z.setText(tmpl(absolute[2]*self._scale))
                self.position_C.setText(tmpl(absolute[5]*self._scale))
        elif self.reference_type == 1:
            self.position_X.setText(tmpl(relative[0]*self._scale))
        elif self.reference_type == 2:
            self.position_X.setText(tmpl(dtg[0]*self._scale))
		"""	
#MDI Region
    def mdi_call_move(self,gcode):
        ACTION.CALL_MDI(gcode)

    def mdi_savaHalToFile(self):
        ACTION.CALL_MDI_WAIT("M420")
    def mdi_callLoadSettingFromPara(self):
        pass
    def mdi_updatePalletToNewCol(self):
        ACTION.CALL_MDI_WAIT("M423")
    def mdi_callloadWorldMode(self):
        ACTION.CALL_MDI("M438")
    def mdi_callloadJoinMode(self):
        ACTION.CALL_MDI("M439")
    def mdi_onspindle(self):
        ACTION.CALL_MDI_WAIT("M3")
    def mdi_offspindle(self):
        ACTION.CALL_MDI_WAIT("M5")
    