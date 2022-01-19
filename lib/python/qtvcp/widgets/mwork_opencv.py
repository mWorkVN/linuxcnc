#!/usr/bin/env python3
# Qtvcp camview
#
# Copyright (c) 2017  Chris Morley <chrisinnanaimo@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# use open cv to do camera alignment

import _thread as Thread

import hal
import os
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QImage
from qtvcp.core import Info, Path, Action, Status
from qtvcp.widgets.widget_baseclass import _HalWidgetBase
from qtvcp import logger
import struct
import redis
# Instiniate the libraries with global reference
# STATUS gives us status messages from linuxcnc
# LOG is for running code logging
if __name__ != '__main__':  # This avoids segfault when testing directly in python
    from qtvcp.core import Status
    STATUS = Status()
LOG = logger.getLogger(__name__)
INFO = Info()
# If the library is missing don't crash the GUI
# send an error and just make a blank widget.
LIB_GOOD = True
try:
    import cv2 as CV
except:
    LOG.error('Qtvcp Error with camview - is python3-opencv installed?')
    LIB_GOOD = False

import numpy as np


class mwork_opencv(QtWidgets.QWidget, _HalWidgetBase):

    testemit = pyqtSignal()

    def __init__(self, parent=None):
        super(mwork_opencv, self).__init__(parent)
        self._qImageFormat=QImage.Format_RGB888
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.video = None
        self.grabbed = None
        self.frame = None
        self._camNum = 0
        self.diameter = 20
        self.rotation = 0
        self.rotationIncrement = .5
        self.scale = 1
        self.gap = 5
        self._noRotate = False
        self.setWindowTitle('Cam View')
        self.setGeometry(100, 100, 200, 200)
        self.text_color = QColor(255, 255, 255)
        self.circle_color = QtCore.Qt.red
        self.cross_color = QtCore.Qt.yellow
        self.cross_pointer_color = QtCore.Qt.white
        self.font = QFont("arial,helvetica", 40)
        self.filename = os.path.join(INFO.LIB_PATH,'widgets_ui', 'mwork_opencv.ui')
        try:
            self.instance = uic.loadUi(self.filename, self)
        except AttributeError as e:
            pass
        if LIB_GOOD:
            self.text = 'No Image'
        else:
            self.text = 'Missing\npython-opencv\nLibrary'
        self.pix = None
        self.stopped = False
        self.degree = str("\N{DEGREE SIGN}")

        from qtvcp.widgets.mwork_camview import mwork_camview
        self.MWORKCAMVIEW = mwork_camview()
        self.MWORKCAMVIEW.setObjectName('MWORKCAMVIEW')
        self.camview.addWidget(self.MWORKCAMVIEW)
        self.MWORKCAMVIEW.hal_init()
        
        self.init_connect()
        self.init_default()
        #self.blobInit()

    def _hal_init(self):
        pass
        #self.pin_ = self.HAL_GCOMP_.newpin('cam-rotation',hal.HAL_FLOAT, hal.HAL_OUT)
        #if LIB_GOOD:
            #STATUS.connect('periodic', self.nextFrameSlot)

    def init_connect(self):
        self.btn_viewcam.clicked.connect(self.changewindown_click)
        self.btn_setting.clicked.connect(self.changewindown_click)
        self.btnzoom.valueChanged.connect(lambda value,status = 1:self.btncamvew_click(value,status))
        self.btndia.valueChanged.connect(lambda value,status = 2:self.btncamvew_click(value,status))
        self.btnrot.valueChanged.connect(lambda value,status = 3:self.btncamvew_click(value,status))

    def init_default(self):
        self.pageSetting.setCurrentIndex(0) 

    def btncamvew_click(self,value,status):
        if (status ==1):
            self.MWORKCAMVIEW.scale = float(value) / 10
        elif (status ==2):
            self.MWORKCAMVIEW.diameter = value
        else:
            self.MWORKCAMVIEW.rotation = float(value) / 10        

    def changewindown_click(self):
        numWin = self.sender().property('index')
        self.pageSetting.setCurrentIndex(numWin) 
        self.testemit.emit()
        pass
        #self.verticalFrame_2.show()


if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    capture = mwork_camview()
    capture.show()

    def jump():
        capture.nextFrameSlot(None)
    timer = QtCore.QTimer()
    timer.timeout.connect(jump)
    timer.start(10)
    sys.exit(app.exec_())
