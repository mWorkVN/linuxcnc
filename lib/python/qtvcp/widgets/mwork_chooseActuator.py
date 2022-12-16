#!/usr/bin/env python3

from __future__ import print_function

import os
import sys
import traceback
import time, select
#from PyQt5.QtCore import pyqtSlot, QFile, QRegExp, Qt, QTextStream, QEvent
#from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QMessageBox,
#        QStyleFactory, QWidget, QColorDialog)
from PyQt5 import QtGui, QtCore, QtWidgets, uic 
from PyQt5.QtCore import QProcess, QByteArray
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
import os
from PyQt5.QtGui import QPixmap
from qtvcp.widgets.widget_baseclass import _HalWidgetBase, hal
from subprocess import call as CALL
import json
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
lblPosName  = ["Pick", "Pick2", "Place", "Place2", "PlaceBad", "Home", "CurrentPallet","distance"]


class mwork_chooseActuator(QtWidgets.QWidget,_HalWidgetBase): #
    def __init__(self, parent=None, widgets=None , pathIniFolder = None):
        super(mwork_chooseActuator, self).__init__(parent)
        self._mode = False
        self.w=widgets
        self.iniFolder = pathIniFolder
        #self.prefs = ps_preferences( self.get_preference_file_path() )
        
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
        self.filename = os.path.join(INFO.LIB_PATH,'widgets_ui', 'mwork_chooseActuator.ui')
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
    

    def initvalue(self):
        self.on_combobox_changed()
        self.createHalPin()
        # init value 
        self.grip_open_stacked2.setCurrentIndex(0)
        self.grip_Close_stacked2.setCurrentIndex(0)
        self.va_Close_stacked2.setCurrentIndex(0)
        self.va_open_stacked2.setCurrentIndex(0)

    def createHalPin(self):
        pin = self.HAL_GCOMP_.newpin("actuator.chooseActuator", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.va_close_wait_choose", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.grip_close_wait_choose", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.va_open_wait_choose", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.grip_open_wait_choose", hal.HAL_U32, hal.HAL_IN)
        
        pin = self.HAL_GCOMP_.newpin("actuator.va_open_wait_time", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.grip_open_wait_time", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.va_close_wait_time", hal.HAL_U32, hal.HAL_IN)
        pin = self.HAL_GCOMP_.newpin("actuator.grip_close_wait_time", hal.HAL_U32, hal.HAL_IN)
        axes = ['1','2','3','4']
        for axis in axes: # add each axis position currentIndex
            pin = self.HAL_GCOMP_.newpin('actuator.va_open_control' + axis + '_status', hal.HAL_U32, hal.HAL_IN)
            pin = self.HAL_GCOMP_.newpin('actuator.va_open_control' + axis + '_pin', hal.HAL_U32, hal.HAL_IN)
        for axis in axes: # add each axis position currentIndex
            pin = self.HAL_GCOMP_.newpin('actuator.va_close_control' + axis + '_status', hal.HAL_U32, hal.HAL_IN)
            pin = self.HAL_GCOMP_.newpin('actuator.va_close_control' + axis + '_pin', hal.HAL_U32, hal.HAL_IN)
        for axis in axes: # add each axis position currentIndex
            pin = self.HAL_GCOMP_.newpin('actuator.grip_open_control' + axis + '_status', hal.HAL_U32, hal.HAL_IN)
            pin = self.HAL_GCOMP_.newpin('actuator.grip_open_control' + axis + '_pin', hal.HAL_U32, hal.HAL_IN)
        for axis in axes: # add each axis position currentIndex
            pin = self.HAL_GCOMP_.newpin('actuator.grip_close_control' + axis + '_status', hal.HAL_U32, hal.HAL_IN)
            pin = self.HAL_GCOMP_.newpin('actuator.grip_close_control' + axis + '_pin', hal.HAL_U32, hal.HAL_IN)        

    def _hal_init(self):
        if self.w.PREFS_:
            vari = self.PREFS_.getpref('Nhan Test', 0, int,'CHOOSE_ACTUATOR')
            self.chooseActuator.setCurrentIndex(self.w.PREFS_.getpref('Type Actuator', 0, int, 'CHOOSE_ACTUATOR'))
            self.va_close_wait_choose.setCurrentIndex(self.w.PREFS_.getpref('scum_close_ex2_type', 0, int, 'CHOOSE_ACTUATOR'))
            self.va_open_wait_choose.setCurrentIndex(self.w.PREFS_.getpref('scum_open_ex2_type', 0, int, 'CHOOSE_ACTUATOR'))
            self.grip_open_wait_choose.setCurrentIndex(self.w.PREFS_.getpref('grip_open_ex2_type', 0, int, 'CHOOSE_ACTUATOR'))
            self.grip_close_wait_choose.setCurrentIndex(self.w.PREFS_.getpref('grip_close_ex2_type', 0, int, 'CHOOSE_ACTUATOR'))

            self.va_open_wait_time.setText(str(self.w.PREFS_.getpref('scum_open_ex2_time', 0, int, 'CHOOSE_ACTUATOR')))
            self.grip_open_wait_time.setText(str(self.w.PREFS_.getpref('grip_open_ex2_time', 0, int, 'CHOOSE_ACTUATOR')))
            self.va_close_wait_time.setText(str(self.w.PREFS_.getpref('scum_close_ex2_time', 0, int, 'CHOOSE_ACTUATOR')))
            self.grip_close_wait_time.setText(str(self.w.PREFS_.getpref('grip_close_ex2_time', 0, int, 'CHOOSE_ACTUATOR')))
            axes = ['1','2','3','4']
            for axis in axes: # add each axis position currentIndex
                getattr(self, 'va_open_control' + axis + '_status').setCurrentIndex(self.w.PREFS_.getpref('scum_open_ex' + axis + '_status', 0, int, 'CHOOSE_ACTUATOR'))
                getattr(self, 'va_open_control' + axis + '_pin').setCurrentIndex(self.w.PREFS_.getpref('scum_open_ex' + axis + '_pin', 0, int, 'CHOOSE_ACTUATOR'))
            for axis in axes: # add each axis position currentIndex
                getattr(self, 'va_close_control' + axis + '_status').setCurrentIndex(self.w.PREFS_.getpref('scum_close_ex' + axis + '_status', 0, int, 'CHOOSE_ACTUATOR'))
                getattr(self, 'va_close_control' + axis + '_pin').setCurrentIndex(self.w.PREFS_.getpref('scum_close_ex' + axis + '_pin', 0, int, 'CHOOSE_ACTUATOR'))
            for axis in axes: # add each axis position currentIndex
                getattr(self, 'grip_open_control' + axis + '_status').setCurrentIndex(self.w.PREFS_.getpref('grip_open_ex' + axis + '_status', 0, int, 'CHOOSE_ACTUATOR'))
                getattr(self, 'grip_open_control' + axis + '_pin').setCurrentIndex(self.w.PREFS_.getpref('grip_open_ex' + axis + '_pin', 0, int, 'CHOOSE_ACTUATOR'))
            for axis in axes: # add each axis position currentIndex
                getattr(self, 'grip_close_control' + axis + '_status').setCurrentIndex(self.w.PREFS_.getpref('grip_close_ex' + axis + '_status', 0, int, 'CHOOSE_ACTUATOR'))
                getattr(self, 'grip_close_control' + axis + '_pin').setCurrentIndex(self.w.PREFS_.getpref('grip_close_ex' + axis + '_pin', 0, int, 'CHOOSE_ACTUATOR'))
            self.updateHalPin()
            #self.HAL_GCOMP_.setp ('mdragon.PAP.Pnp_distance' + axis,position)

    def _hal_cleanup(self):
        if self.PREFS_:
            vari = 54
            print(" stop {} hhhhhhhhhhhhhhhhhhhh".format(vari))

    def updateHalPin(self):
        self.HAL_GCOMP_.setp ('mdragon.actuator.chooseActuator', str(self.chooseActuator.currentIndex()))
        self.HAL_GCOMP_.setp ('mdragon.actuator.va_close_wait_choose', str(self.va_close_wait_choose.currentIndex()))
        self.HAL_GCOMP_.setp ('mdragon.actuator.va_open_wait_choose', str(self.va_open_wait_choose.currentIndex()))
        self.HAL_GCOMP_.setp ('mdragon.actuator.grip_open_wait_choose', str(self.grip_open_wait_choose.currentIndex()))
        self.HAL_GCOMP_.setp ('mdragon.actuator.grip_close_wait_choose', str(self.grip_close_wait_choose.currentIndex()))
        self.HAL_GCOMP_.setp ('mdragon.actuator.va_open_wait_time', self.va_open_wait_time.text())
        self.HAL_GCOMP_.setp ('mdragon.actuator.grip_open_wait_time', self.grip_open_wait_time.text())
        self.HAL_GCOMP_.setp ('mdragon.actuator.va_close_wait_time', self.va_close_wait_time.text())
        self.HAL_GCOMP_.setp ('mdragon.actuator.grip_close_wait_time', self.grip_close_wait_time.text())
        axes = ['1','2','3','4']
        for axis in axes: # add each axis position currentIndex
            self.HAL_GCOMP_.setp ('mdragon.actuator.va_open_control' + axis + '_status', str(getattr(self, 'va_open_control' + axis + '_status').currentIndex()))
            self.HAL_GCOMP_.setp ('mdragon.actuator.va_open_control' + axis + '_pin', str(getattr(self, 'va_open_control' + axis + '_pin').currentIndex()))
        for axis in axes: # add each axis position currentIndex
            self.HAL_GCOMP_.setp ('mdragon.actuator.va_close_control' + axis + '_status', str(getattr(self, 'va_close_control' + axis + '_status').currentIndex()))
            self.HAL_GCOMP_.setp ('mdragon.actuator.va_close_control' + axis + '_pin', str(getattr(self, 'va_close_control' + axis + '_pin').currentIndex()))
        for axis in axes: # add each axis position currentIndex
            self.HAL_GCOMP_.setp ('mdragon.actuator.grip_open_control' + axis + '_status', str(getattr(self, 'grip_open_control' + axis + '_status').currentIndex()))
            self.HAL_GCOMP_.setp ('mdragon.actuator.grip_open_control' + axis + '_pin', str(getattr(self, 'grip_open_control' + axis + '_pin').currentIndex()))
        for axis in axes: # add each axis position currentIndex
            self.HAL_GCOMP_.setp ('mdragon.actuator.grip_close_control' + axis + '_status', str(getattr(self, 'grip_close_control' + axis + '_status').currentIndex()))
            self.HAL_GCOMP_.setp ('mdragon.actuator.grip_close_control' + axis + '_pin', str(getattr(self, 'grip_close_control' + axis + '_pin').currentIndex()))

    def savepara_click(self):
        if self.w.PREFS_: #grip_open_wait_choose
            self.w.PREFS_.putpref('Type Actuator', self.chooseActuator.currentIndex(), int, 'CHOOSE_ACTUATOR')

            self.w.PREFS_.putpref('scum_open_ex2_type', self.va_open_wait_choose.currentIndex(), int, 'CHOOSE_ACTUATOR')
            self.w.PREFS_.putpref('scum_close_ex2_type', self.va_close_wait_choose.currentIndex(), int, 'CHOOSE_ACTUATOR')
            self.w.PREFS_.putpref('grip_open_ex2_type', self.grip_open_wait_choose.currentIndex(), int, 'CHOOSE_ACTUATOR')
            self.w.PREFS_.putpref('grip_close_ex2_type', self.grip_close_wait_choose.currentIndex(), int, 'CHOOSE_ACTUATOR')

            self.w.PREFS_.putpref('scum_open_ex2_time',  int(self.va_open_wait_time.text()), int, 'CHOOSE_ACTUATOR')
            self.w.PREFS_.putpref('scum_close_ex2_time', int(self.va_close_wait_time.text()), int, 'CHOOSE_ACTUATOR')
            self.w.PREFS_.putpref('grip_open_ex2_time',  int(self.grip_open_wait_time.text()), int, 'CHOOSE_ACTUATOR')
            self.w.PREFS_.putpref('grip_close_ex2_time', int(self.grip_close_wait_time.text()), int, 'CHOOSE_ACTUATOR')

            axes = ['1','2','3','4']
            for axis in axes: # add each axis position currentIndex
                self.w.PREFS_.putpref('scum_open_ex' + axis + '_status', getattr(self, 'va_open_control' + axis + '_status').currentIndex(), int, 'CHOOSE_ACTUATOR')
                self.w.PREFS_.putpref('scum_open_ex' + axis + '_pin', getattr(self, 'va_open_control' + axis + '_pin').currentIndex(), int, 'CHOOSE_ACTUATOR')
            for axis in axes: # add each axis position currentIndex
                self.w.PREFS_.putpref('scum_close_ex' + axis + '_status', getattr(self, 'va_close_control' + axis + '_status').currentIndex(), int, 'CHOOSE_ACTUATOR')
                self.w.PREFS_.putpref('scum_close_ex' + axis + '_pin', getattr(self, 'va_close_control' + axis + '_pin').currentIndex(), int, 'CHOOSE_ACTUATOR')
            for axis in axes: # add each axis position currentIndex
                self.w.PREFS_.putpref('grip_open_ex' + axis + '_status', getattr(self, 'grip_open_control' + axis + '_status').currentIndex(), int, 'CHOOSE_ACTUATOR')
                self.w.PREFS_.putpref('grip_open_ex' + axis + '_pin',   getattr(self, 'grip_open_control' + axis + '_pin').currentIndex(), int, 'CHOOSE_ACTUATOR')
            for axis in axes: # add each axis position currentIndex
                self.w.PREFS_.putpref('grip_close_ex' + axis + '_status', getattr(self, 'grip_close_control' + axis + '_status').currentIndex(), int, 'CHOOSE_ACTUATOR')
                self.w.PREFS_.putpref('grip_close_ex' + axis + '_pin', getattr(self, 'grip_close_control' + axis + '_pin').currentIndex(), int, 'CHOOSE_ACTUATOR')
        self.updateHalPin()

    def btnRunTest_click(self):
        currenttab = self.tabActuator.currentIndex()
        print(" currentWidget ",currenttab)
        status = 0
        if (currenttab ==0 ):   # grip
            status  = self.tabGrip.currentIndex()
        else:                   # vacuum
            status  = self.tabVacuum.currentIndex()
        if (status == 0):       #M424 OPEN
            ACTION.CALL_MDI("M424")
        else:                   #M425 CLOSE
            ACTION.CALL_MDI("M425")

    def qtvcptest(self):
        pass
        #self.lblColZ_2.setText(str(self.HAL_GCOMP_['qtvcptest']) )
        #self.mbox('scgg')
	
    def all_homed(self, obj):
        self.statusHomeAll = True
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



        
    def settingHalPin(self):
        global lblPosName
        axes = ['X','Y','Z','C']


    def testchange(self):
        pass

    def on_choosetime_changed(self):
        nameStacked = self.sender().property('name')
        value = self.sender().currentIndex()
        print(nameStacked)
        getattr(self, nameStacked).setCurrentIndex(value)
        #self.nameStacked.setCurrentIndex(value)

    def setupConnections(self):
        self.chooseActuator.currentTextChanged.connect(self.on_combobox_changed)
        self.va_close_wait_choose.currentTextChanged.connect(self.on_choosetime_changed)
        self.va_open_wait_choose.currentTextChanged.connect(self.on_choosetime_changed)
        self.grip_open_wait_choose.currentTextChanged.connect(self.on_choosetime_changed)
        self.grip_close_wait_choose.currentTextChanged.connect(self.on_choosetime_changed)
        self.btnSave.clicked.connect(self.savepara_click)
        self.btnRunTest.clicked.connect(self.btnRunTest_click)

    def on_combobox_changed(self):
        position = self.chooseActuator.currentIndex()
        nameimage = ""
        if position ==0:
            nameimage='gripper.png'
        else:
            nameimage='vacuum.png'
        if self.w.PREFS_:
            vari = self.w.PREFS_.getpref('Nhan Test', 0, int,'CHOOSE_ACTUATOR')
            vari = vari + 1
            self.w.PREFS_.putpref('Nhan Test', vari, int, 'CHOOSE_ACTUATOR')
            print ("combobox change {}".format(nameimage))
        path = self.iniFolder
        goal_dir = os.path.join(path, 'chooseActuato',nameimage)
        goal_dir = os.path.abspath(goal_dir)
        pixmap = QPixmap(goal_dir)
        pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.imageAc.setPixmap(pixmap)
        self.imageAc.resize(pixmap.width(), pixmap.height())
        self.tabActuator.setCurrentIndex(position)

    def testhalpin(self):
        if self.HAL_GCOMP_.getvalue ('mdragon.PAP.qtvcpchangevalue') == 1:
            self.HAL_GCOMP_.setp('mdragon.PAP.qtvcpchangevalue',"0")
            self.mbox('hal 0')
        else:
            self.HAL_GCOMP_.setp('mdragon.PAP.qtvcpchangevalue',"1")
            self.mbox('hal 1')
        
    def savaHalToFile(self):
        ACTION.SET_MANUAL_MODE()

    def updatePalletUiToHal(self,status):
        axes = ['X','Y','Z']


        
    def updateHalToUi(self, name, axis):
        pass
    def updatePalletHalToUi(self, name):
        axes = ['X','Y','Z']

    def moveToTeachPoint(self, name):
        pass
            

		
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
        pass
        '''
        tmpl = lambda s: self._current_text_template % s
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
        '''
#MDI Region
    def mdi_call_move(self,gcode):
        ACTION.CALL_MDI(gcode)

    def mdi_savaHalToFile(self):
        ACTION.CALL_MDI_WAIT("M420\n")

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
    