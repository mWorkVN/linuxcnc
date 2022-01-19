#!/usr/bin/ python3

from __future__ import print_function

import os
import sys
import traceback
#from PyQt5.QtCore import pyqtSlot, QFile, QRegExp, Qt, QTextStream, QEvent
#from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QMessageBox,
#        QStyleFactory, QWidget, QColorDialog)
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from qtvcp.widgets.dro_widget import DROLabel
from qt5_graphics import Lcnc_3dGraphics
from qtvcp.core import Info, Path, Action, Status
from qtvcp.lib.notify import Notify
from qtvcp import logger
import linuxcnc
from qtvcp.widgets.widget_baseclass import _HalWidgetBase, hal
LOG = logger.getLogger(__name__)

if os.path.split(sys.argv[0])[0] == '/usr/bin':
	GUI_PATH = '/usr/lib/python3/dist-packages/libemclog'
	#self.printDebug('Installed')

if os.path.split(sys.argv[0])[0] == '.':
	GUI_PATH = os.path.split(os.path.realpath(sys.argv[0]))[0]
	#self.printDebug('In Development')
STATUS = Status()	
INFO = Info()
PATH = Path()
ACTION = Action()
DATADIR = os.path.abspath( os.path.dirname( __file__ ) )
#class emclogwitget(QtWidgets.QWidget,QPyDesignerCustomWidgetPlugin):_HalWidgetBase

class threadwait(QtCore.QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def run(self):
        QtCore.QThread.msleep(1000)
        self.finished.emit()

class mwork_emclogwitget(QtWidgets.QWidget,_HalWidgetBase):
    def __init__(self, parent=None, path=None):
        super(mwork_emclogwitget, self).__init__(parent)
        self.iniFolder = path
        self._mode = False
        self.statusHomeAll = False
        self._scale = 1.0
        self.reference_type = 0
        self.metric_text_template = '%10.3f'
        self.imperial_text_template = '%9.4f'
        self.angular_text_template = '%9.2f'
        self.lastPosition = []
        self.modescara = "M428"
        self.statuMode = False
        #self.setMinimumSize(800, 800)
        self.bluck_update = True	
        self.filename = os.path.join(INFO.LIB_PATH,'widgets_ui', 'mwork_mEmclog.ui')
        try:
            self.instance = uic.loadUi(self.filename, self)
        except AttributeError as e:
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_lines = traceback.format_exc().splitlines()
            self.printDebug("Ui loadinr error" + formatted_lines[0])
            #traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            self.printDebug(formatted_lines[-1])
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
		#ACTION.CALL_MDI(self.command_text)
		#self.stackedWidget_dro.setCurrentIndex(0)  #lenh set page cho stackwwidget
        pin = self.HAL_GCOMP_.newpin("changescara", hal.HAL_FLOAT, hal.HAL_IN)
        pin.value_changed.connect(self.changescarachange)
        self.dro_label_2 = DROLabel()
        self.setupConnections()
        self.initvalue()

    def printDebug(self, nd):
        print("TEACHING MODE",nd)

    def all_homed(self, obj):
        self.statusHomeAll = True
        self.stackedWidget.setCurrentIndex(0)
		
    def not_all_homed(self, obj, list):
        self.statusHomeAll = False
        self.stackedWidget.setCurrentIndex(1)
		
    def changescarachange(self):
        self.statuMode = True
        if self.HAL_GCOMP_['changescara'] == 0:
            self.modescara = "M439"
        elif self.HAL_GCOMP_['changescara'] == 1:
            self.modescara = "M438"
        else:
            self.modescara = "M440"		
            		
    def initvalue(self):
        self.feedLE.setText("300")
        self.speedmoveJoint.setText("300")
        self.tabControl.setCurrentIndex(1)

    def setupConnections(self):
        self.actionOpen.triggered.connect(self.OpenFile)
        self.actionSave.triggered.connect(self.SaveFile)
        self.actionSave_As.triggered.connect(self.SaveFileAs)
        self.actionSavePreferences.triggered.connect(self.SavePreferences)
        self.btnNewProgram.clicked.connect(self.btnNewProgram_click)
        self.btnOpen.clicked.connect(self.OpenFile)
        self.btnSaveAs.clicked.connect(self.SaveFileAs)
        self.addExtraPB.clicked.connect(self.addExtra)
        self.actionCopy.triggered.connect(self.copy)
        self.btn_spindle_on.clicked.connect(self.addControl_click)
        self.btn_spindle_off.clicked.connect(self.addControl_click)
        self.btn_grip_on.clicked.connect(self.addControl_click)
        self.btn_grip_off.clicked.connect(self.addControl_click)
        self.btn_addWaitPin.clicked.connect(self.addWaitPin)
        self.btn_addControlPin.clicked.connect(self.addControlPin)
        self.logPB.clicked.connect(lambda data,status="world" :self.log(status))
        self.logmovejoint.clicked.connect(lambda data,status="joint" :self.log(status))
        self.btn_addtimePause.clicked.connect(self.btn_addtimePause_click)
        self.btnDeleleLine.clicked.connect(lambda data,status="delete" : self.btnEditline_click(status))
        self.btntestLine.clicked.connect(lambda data,status="run" :self.btnEditline_click(status))
        self.btnNextLine.clicked.connect(lambda data,status="next" : self.btnEditline_click(status))
        self.btnPreLine.clicked.connect(lambda data,status="pre" : self.btnEditline_click(status))
        self.btnLoadToGcode.clicked.connect(self.loadgcode_click)
        self.gcodeLW.currentRowChanged.connect(self.gcoderawchange)
        self.btn_update_gcode.clicked.connect(self.updateChangeGcode)

    def gcoderawchange(self):
        try:
            self.lblgcodeEdit.setText(self.gcodeLW.currentItem().text())
        except Exception as e:
            pass
            #self.printDebug("gcoderawchange : " + e)

    def updateChangeGcode(self):
        sel_items = self.gcodeLW.selectedItems()
        for item in sel_items:
            item.setText(self.lblgcodeEdit.text())

    def btnEditline_click(self,status):
        listItems=self.gcodeLW.selectedItems()
        if not listItems: return 
        if (status == "delete"):       
            for item in listItems:
                self.gcodeLW.takeItem(self.gcodeLW.row(item))
        elif (status == "run"):
            ACTION.CALL_MDI(self.gcodeLW.currentItem().text())
            printDebug("Run line " + str(self.gcodeLW.currentItem().text()))
        elif (status == "next"):
            self.gcodeLW.setCurrentRow(self.gcodeLW.currentRow() + 1)  
        elif (status == "pre"):
            self.gcodeLW.setCurrentRow(self.gcodeLW.currentRow() - 1)

    def loadgcode_click(self):
        items = self.gcodeLW.findItems('M30', Qt.MatchContains)
        items = items + self.gcodeLW.findItems('M2', Qt.MatchContains)
        if len(items) == 0:
            self.gcodeLW.addItem('M30')
            self.printDebug("ADD END GCODE")
        path = self.iniFolder
        goal_dir = os.path.join(path,'../', 'gcode/teachingMode',"teaching.ngc")
        goal_dir = os.path.abspath(goal_dir)
        self.savetoFile(goal_dir)
        ACTION.OPEN_PROGRAM(goal_dir)
        STATUS.emit('update-machine-log', 'Loaded: ' + goal_dir, 'TIME')
        ACTION.SET_AUTO_MODE()



    def btn_addtimePause_click(self):
        if self.gcodeLW.count() == 0:
            self.mbox('Add Move POS')
            return   
        timewait = int(self.lbltimePause.text())
        self.gcodeLW.addItem('M180 P{}'.format(timewait / 1000))
        ACTION.CALL_MDI('M180 P{}'.format( timewait / 1000))


    def addControl_click(self): 
        nameStacked = self.sender().property('name')
        MDI_CMD = ""
        fspintdle = self.lblfspindle.text()
        self.printDebug("fspintdle "+ fspintdle )
        if (nameStacked == "OnSpindle"):
            MDI_CMD = "M3"
        elif (nameStacked == "OffSpindle"):
            MDI_CMD = "M5"
        elif (nameStacked == "OpenGrip"):
            MDI_CMD = "M424"
        elif (nameStacked == "CloseGrip"):
            MDI_CMD = "M425"
        ACTION.CALL_MDI(MDI_CMD)
        self.gcodeLW.addItem(MDI_CMD)

    def addControlPin(self):
        if self.gcodeLW.count()== 0:
            self.mbox('Add Move POS')
            return 
        statusCtr = ''
        numPinCtr = ''
        mode = ''
        numPinCtr = self.nCtrPin.currentText()
        if self.statusCtrPin.currentText() == 'ON':
            mode = 'M64'
        elif  self.statusCtrPin.currentText() == 'OFF':
            mode = 'M65'
        self.gcodeLW.addItem('{} {}'.format(mode,numPinCtr))	
        ACTION.CALL_MDI('{} {}'.format(mode,numPinCtr))
		
    def addWaitPin(self):
        if self.gcodeLW.count() == 0:
            self.mbox('Add Move POS')
            return   
        statusWait = ''
        pinNumber = ''
        mode = 'L4'
        pinNumber = self.numberPin.currentText()
        if self.statusWaitPin.currentText() == 'ON':
            mode = 'L3'
        timewait = int(self.lbltimewaitInput.text())
        self.gcodeLW.addItem('M66 {} {} Q{}'.format(pinNumber,mode , timewait / 1000))
        ACTION.CALL_MDI('M66 {} {} Q{}'.format( pinNumber, mode, timewait / 1000))
		
    def mbox(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def updateUiToHal_Thread(self,status,cmdgcode):
        axes = ['X','Y','Z','C']
        gcode = []
        gcode.append(cmdgcode)
        for axis in axes: # add each axis position
            axisLetter = str(getattr(self, 'axisCB_' + axis).property('axis'))
            position = str(getattr(self, 'position_' + axis).text())
            gcode.append(axisLetter + position.strip() + ' ')
        if (cmdgcode == "G0.1 "):
            gcode.append(' F{}'.format(str(self.speedmoveJoint.text())))
        elif (cmdgcode == "M438 G53 G1 "):
            gcode.append(' F{}'.format(str(self.feedLE.text())))
        self.gcodeLW.addItem(''.join(gcode))
        if status:
            self.mdi_callloadJoinMode()  

    def logmovejoint_click(self,type,moveType):
        statusScara = False
        cmdgcode = "G0.1 "
        if (type == "world"): 
            cmdgcode = "M438 G53 " + moveType + " "
        if self.HAL_GCOMP_.getvalue('motion.switchkins-type')==1:
            self.mdi_callloadWorldMode()	
            statusScara = True
        if (statusScara):
            self.thread = QThread()
            self.threadwait = threadwait()
            self.threadwait.moveToThread(self.thread)
            self.thread.started.connect(self.threadwait.run)
            self.threadwait.finished.connect(self.thread.quit)
            self.threadwait.finished.connect(lambda status=statusScara,moveType=cmdgcode: self.updateUiToHal_Thread(status,moveType))
            self.threadwait.finished.connect(self.threadwait.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
        else:
            self.updateUiToHal_Thread(statusScara,cmdgcode)

    def log(self,status): 
        firstrun = False
        print("Sssssssssssssssss") 
        if self.gcodeLW.count() == 0:
		    # init parameter gcode 
            self.gcodeLW.addItem(';Begin')
            self.gcodeLW.addItem('G21')
            self.statuMode = False
            firstrun = True
        #if status=="joint":
        for radio in self.moveGB.findChildren(QRadioButton):
            if radio.isChecked(): # add the move type
                moveType = str(radio.property('gcode'))
        self.logmovejoint_click(status,moveType)
        #    return
        """
        if firstrun:
            if self.HAL_GCOMP_['changescara'] == 0:
                self.modescara = "M439"
            elif self.HAL_GCOMP_['changescara'] == 1:
                self.modescara = "M438"
            else:
                self.modescara = "M440"	
            self.gcodeLW.addItem(self.modescara)
        if (self.statuMode == True):
            self.statuMode = False
            self.gcodeLW.addItem(self.modescara)
        axes = ['X','Y','Z','C']
        gcode = []
        currentPosition = []

        if moveType in ['G1', 'G0']:
            gcode.append("G53 " + moveType + ' ')
        for axis in axes: # add each axis position
            axisLetter = str(getattr(self, 'axisCB_' + axis).property('axis'))
            position = str(getattr(self, 'position_' + axis).text())
            currentPosition.append(float(position))
            gcode.append(axisLetter + position.strip() + ' ')
        if moveType in ['G2', 'G3']:
            if self.arcRadiusLE.text() == '':
                self.mbox('{} moves require an arc radius'.format(moveType))
                return
            if len(self.lastPosition) == 0:
                self.mbox('A G0 or G1 move must be done before a {} move'
				.format(moveType))
            x1 = self.lastPosition[0]
            x2 = currentPosition[0]
            y1 = self.lastPosition[1]
            y2 = currentPosition[1]
            if x1 == x2 and y1 == y2:
                self.mbox('{} move needs a different end point'.format(moveType))
                return
            xMid = (x1 + x2) / 2
            yMid = (y1 + y2) / 2
            slope = (y2 - y1) / (x2 - x1)
            distance = math.sqrt(pow((x1 - x2),2) + pow((y1 - y2),2))
            radius = float(self.arcRadiusLE.text())
            if radius < (distance / 2):
                self.mbox('Radius can not be smaller than {0:0.4f}'.format(distance/2))
                return
            c = 1/math.sqrt(1+((slope * -1)*(slope * -1)))
			#sine
            s = (slope * -1)/math.sqrt(1+((slope * -1)*(slope * -1)))
        if moveType == 'G2':
            i = xMid + radius * (c)
            j = yMid + radius * (s)
            gcode.append(' I{0:.{2}f} J{1:.{2}f}'.format(i, j, self.precisionSB.value()))
        elif moveType == 'G3':
            i = xMid + (-radius) * (c)
            j = yMid + (-radius) * (s)
            gcode.append(' I{0:.{2}f} J{1:.{2}f}'.format(i, j, self.precisionSB.value()))
        if moveType in ['G1', 'G2', 'G3']: # check for a feed rate
            feedMatch = self.gcodeLW.findItems('F', Qt.MatchContains)
            if len(feedMatch) > 0: # check last feed rate to see if it is different
                lastMatch =  str(feedMatch[-1].text()).split()
                if lastMatch[-1][1:] != self.feedLE.text():
                    gcode.append(' F{}'.format(str(self.feedLE.text())))
            if not self.gcodeLW.findItems('F', Qt.MatchContains):
                if self.feedLE.text():
                    gcode.append(' F{}'.format(str(self.feedLE.text())))
                else:
                    self.mbox('A feed rate must be entered for a {} move'.format(moveType))
                    return
        self.gcodeLW.addItem(''.join(gcode))
        self.lastPosition = []
        for axis in axes:
            self.lastPosition.append(float(getattr(self, 'position_' + axis).text()))
        """
    def OpenFile(self):
        if os.path.isdir(os.path.expanduser('~/linuxcnc/nc_files')):
            configsDir = os.path.expanduser('~/linuxcnc/nc_files')
        else:
            configsDir = os.path.expanduser('~/')
        fileName = QFileDialog.getOpenFileName(self,
        caption="Select a G code File",
        directory=configsDir,
        filter='*.ngc',
        options=QFileDialog.DontUseNativeDialog,)
        if fileName:
            try:
                self.gcodeLW.clear()
                with open(fileName[0], 'r') as f:
                    for line in f:
                        self.gcodeLW.addItem(line.strip('\n'))
            except BaseException:
                pass
            """
            iniFile = (fileName[0])
            print(fileName[0])
            with open(fileName[0]) as f:
				text = f.read()
				self.gCodeViewer.insertPlainText(text)
			"""

    def savetoFile(self, fileName):
        items = self.gcodeLW.findItems('M30', Qt.MatchContains)
        items = items + self.gcodeLW.findItems('M2', Qt.MatchContains)
        if len(items) == 0:
            self.gcodeLW.addItem('M30')
            self.printDebug("ADD END GCODE")
        if fileName:
            gcode = '\n'.join(self.gcodeLW.item(i).text() for i in range(self.gcodeLW.count()))
            with open(fileName, 'w') as f:
                f.write(gcode)
        
    def btnNewProgram_click(self):
        self.gcodeLW.clear()

    def SaveFile(self):
        if os.path.isdir(os.path.expanduser('~/linuxcnc/nc_files')):
            configsDir = os.path.expanduser('~/linuxcnc/nc_files')
        else:
            configsDir = os.path.expanduser('~/')
        fileName, _ = QFileDialog.getSaveFileName(self,
        caption="Save G Code",
        directory=configsDir,
        options=QFileDialog.DontUseNativeDialog)
        self.savetoFile(fileName)

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
    def SaveFileAs(self):
        self.SaveFile()

    def SavePreferences(self):
        if not os.path.exists(self.pref_path):
            self.config.add_section('MAIN')
        self.config.set('MAIN','dio', str(self.dioSB.value()))
        with open(self.pref_path, 'w') as cfgfile:
            self.config.write(cfgfile)
		#	f.write(str(self.dioSB.value()))

    def copy(self):
        items = []
        gcode = [str(self.gcodeLW.item(i).text()) for i in range(self.gcodeLW.count())]
        self.qclip.setText('\n'.join(gcode))

    def addExtra(self):
        if (len(self.extraLE.text()) == 0):
            return
        self.gcodeLW.addItem(self.extraLE.text())

    def exit(self):
        exit()

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