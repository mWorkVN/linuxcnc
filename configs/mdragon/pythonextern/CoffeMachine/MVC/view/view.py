# coding: utf8
import  time ,os
#import logging
#import logging.handlers
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot,  QObject ,pyqtSlot,QUrl,Qt, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator
#import linuxcnc
from gtts import gTTS
from playsound import playsound
import pyttsx3
#from threading import Thread
try: 
    import queue
except ImportError: #py2
    import Queue as queue
import variThreading
import settings

class MyGUI(QMainWindow):
    
    def __init__(self, machine, main_controller,server):
        super(MyGUI, self).__init__( )
        uic.loadUi('vendding.ui', self)
        #self.show()
        self._machine = machine
        self._main_controller = main_controller
        
        self.FlaskWeb = server()
        self.FlaskWeb.setDaemon(True); 
        self.FlaskWeb.start()
        self._machine.even_loadPAY.connect(self.on_even_loadPAY)
        self._main_controller.state_robot_error.connect(self.on_state_robot_error)

        continueToBuy = True
        self.initEvent()
        self.initUi()
        self.initPrices()
        self.numberGui = "0"
        self.test = 0
        #self.showFullScreen()
        
    def paintEvent(self, event):
        self.test += 1
        #print("update",self.test)
        self._main_controller.run()
        stat = self._main_controller.checkChangeState()
        if int(stat) != 0:
            print("STATE NEW",flush=True)
            self.updateUi()
            getattr(self, 'stackedWidget').setCurrentIndex(int(stat) - 1)
            
        #time.sleep(0.005)
        self.update()

    @pyqtSlot(str)
    def on_even_loadPAY(self, value):
        self.webView.load(QUrl(value))

    @pyqtSlot(str)
    def on_state_robot_error(self, value):
        print("ERR")
        msg = QMessageBox()
        msg.setWindowTitle("Tutorial on PyQt5")
        msg.setText("This is the main text!")
        msg.setInformativeText("informative text, ya!")

        msg.setDetailedText("details")
        msg.exec()

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

    def initPrices(self):
        pass
        for i in range(1,self._machine.mysql.totalDevice):
            getattr(self, 'totalCoinID' + str(i)).setText(str(self.getPrice(i)))

    def updateUi(self):
        if self._main_controller.preState == "0":
            self.TotalMoney.setText("0")
            self.nameID.setText("")
            self.slID.setText("0")
            self.moneyGet.setText("0")
        elif self._main_controller.preState == "2":
            #self.webView.setHTML('')
            self.webView.load(QUrl("http://localhost:8081"))
            money = self._machine.item.numBuy * self._machine.item.price
            #self.TotalMoney.setText(str(money))
            #self.nameID.setText(self._machine.item.name)
            #self.slID.setText(str(self._machine.item.numBuy))
            #self.moneyGet.setText(str(self._machine.moneyGet))
        #x =  {"order":"","sts":"","amount":"","time":""}
        elif self._main_controller.preState == "4": #Success
            self.lbl_orderID.setText(self._machine.vuluePAY["order"])
            self.lbl_orderTime.setText(self._machine.vuluePAY["time"])
            self.lbl_orderGET.setText(self._machine.vuluePAY["amount"])
        elif self._main_controller.preState == "5": #Error
            self.lbl_erID.setText(self._machine.vuluePAY["order"])
            self.lbl_erCode.setText(settings.VNPAY_ERROR_CODE[self._machine.vuluePAY["sts"]])  
        elif self._main_controller.preState == "6":
            #self.webView.setHTML('')
            self.webView.history().clear()
            money = self._machine.item.numBuy * self._machine.item.price
            self.moneyFrefund.setText(str(self._machine.moneyGet))

    def initEvent(self):
        self.btnReturn.clicked.connect(self.returnOrder)
        self.btnBuyID1.clicked.connect(self.haveOrder)
        self.btnBuyID2.clicked.connect(self.haveOrder)
        #self.numSlID1.currentTextChanged.connect(self.slOrderChange)
        #self.numSlID2.currentTextChanged.connect(self.slOrderChange)

    def naptien_click(self):
        pass

    def returnOrder(self):
        self._machine.returnOrder()

    def getPrice(self,ID):
        return self._machine.getPrice(ID)

    def slOrderChange(self):
        nameStacked = self.sender().property('ID')
        sata = str(self.getPrice(nameStacked))
        position = 1 #int(self.sender().currentIndex())
        total = int(sata)*position
        #getattr(self, 'totalCoinID' + str(nameStacked)).setText(str(total))
        print("have slOrderChange",flush=True)

    def haveOrder(self):
        id = self.sender().property('ID')
        sl = 1 #int(getattr(self, 'numSlID' +str(id) ).currentIndex())
        self._main_controller.setOrder(id,sl)
        print("have order",flush=True)
#vend()