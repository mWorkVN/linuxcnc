# coding: utf8
import sys, time ,os
import logging
import logging.handlers
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QObject ,pyqtSlot,QUrl
from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator
#import linuxcnc
from gtts import gTTS
from playsound import playsound
import pyttsx3
from threading import Thread
try: 
    import queue
except ImportError: #py2
    import Queue as queue

import variThreading

class MyGUI(QMainWindow):
    
    def __init__(self, machine, main_controller,server):
        super(MyGUI, self).__init__()

        self._machine = machine
        self._main_controller = main_controller
        self.FlaskWeb = server()
        self.FlaskWeb.setDaemon(True); 
        self.FlaskWeb.start()
        self._machine.even_odd_changed.connect(self.on_even_odd_changed)
        uic.loadUi('vendding.ui', self)
        self.show()
        continueToBuy = True
        self.initEvent()
        self.initUi()
        self.numberGui = "0"

    def paintEvent(self, event):
        self._main_controller.run()
        stat = self._main_controller.checkChangeState()
        if int(stat) != 0:
            print("STATE NEW",flush=True)
            getattr(self, 'stackedWidget').setCurrentIndex(int(stat) - 1)
            self.updateUi()
        
        self.update()

    @pyqtSlot(str)
    def on_even_odd_changed(self, value):
        self.webView.load(QUrl(value))


    def setImage(self,id):
        nameimage=str(id)+'.jpg'
        mainpath = os.path.dirname(os.path.abspath(__file__))
        goal_dir = os.path.join(mainpath, 'res',nameimage)
        goal_dir = os.path.abspath(goal_dir)
        pixmap = QPixmap(goal_dir)
        pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.FastTransformation)
        getattr(self, 'imageID' +str(id) ).setPixmap(pixmap)
        getattr(self, 'imageID' +str(id)).resize(pixmap.width(), pixmap.height())        

    def initUi(self):
        self.setImage(1)
        self.setImage(2)
        self.setImage(3)
        self.setImage(4)

    def updateUi(self):
        if self._main_controller.preState == "0":
            self.TotalMoney.setText("0")
            self.nameID.setText("")
            self.slID.setText("0")
            self.moneyGet.setText("0")
        elif self._main_controller.preState == "2":
            money = self._machine.item.numBuy * self._machine.item.price
            self.TotalMoney.setText(str(money))
            self.nameID.setText(self._machine.item.name)
            self.slID.setText(str(self._machine.item.numBuy))
            self.moneyGet.setText(str(self._machine.moneyGet))
        elif self._main_controller.preState == "5":
            money = self._machine.item.numBuy * self._machine.item.price
            self.moneyFrefund.setText(str(self._machine.moneyGet))

    def initEvent(self):

        self.btnBuyID1.clicked.connect(self.haveOrder)
        self.btnBuyID2.clicked.connect(self.haveOrder)
        self.numSlID1.currentTextChanged.connect(self.slOrderChange)
        self.numSlID2.currentTextChanged.connect(self.slOrderChange)
        self.btn_naptien.clicked.connect(self.naptien_click)

    def naptien_click(self):
        money = int(self.lblmoneyNap.text())
        self._main_controller.setMoneyGet(money)
        self.moneyGet.setText(str(self._machine.moneyGet))

    def getPrice(self,ID):
        return self._machine.getPrice(ID)

    def slOrderChange(self):
        nameStacked = self.sender().property('ID')
        sata = str(self.getPrice(nameStacked))
        position = int(self.sender().currentIndex())
        total = int(sata)*position
        getattr(self, 'totalCoinID' + str(nameStacked)).setText(str(total))
        print("have slOrderChange",flush=True)

    def haveOrder(self):
        id = self.sender().property('ID')
        sl = int(getattr(self, 'numSlID' +str(id) ).currentIndex())
        self._main_controller.setOrder(id,sl)
        print("have order",flush=True)
#vend()