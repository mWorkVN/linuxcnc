# coding: utf8
import  time ,os
#import logging
#import logging.handlers
import PyQt5
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtCore import  QObject ,pyqtSlot,QUrl,Qt, QTimer
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
        super(MyGUI, self).__init__()
        self.window = QtWidgets.QMainWindow()
        self.widget=uic.loadUi('vendding.ui', self.window )
        self.window.show()
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
        timebegin = time.time()
        #print("update",self.test)
        self._main_controller.run()
        stat = self._main_controller.checkChangeState()
        if int(stat) != 0:
            print("STATE NEW",flush=True)
            self.updateUi()
            getattr(self, 'window.stackedWidget').setCurrentIndex(int(stat) - 1)
        self.window.update()

    #@pyqtSlot(str)
    def on_even_loadPAY(self, value):
        self.window.webView.load(QUrl(value))

    #@pyqtSlot(str)
    def on_state_robot_error(self, value):
        print("ERR")
        """msg = QMessageBox()
        msg.setWindowTitle("Tutorial on PyQt5")
        msg.setText("This is the main text!")
        msg.setInformativeText("informative text, ya!")

        msg.setDetailedText("details")
        msg.exec()"""

    def setImage(self,id):
        nameimage=str(id)+'.jpg'
        mainpath = os.path.dirname(os.path.abspath(__file__))
        goal_dir = os.path.join(mainpath, 'res',nameimage)
        goal_dir = os.path.abspath(goal_dir)
        pixmap = QPixmap(goal_dir)
        pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.FastTransformation)
        getattr(self.window, 'imageID' +str(id) ).setPixmap(pixmap)
        getattr(self.window, 'imageID' +str(id)).resize(pixmap.width(), pixmap.height())        

    def initUi(self):
        self.setImage(1)
        self.setImage(2)
        self.setImage(3)
        self.setImage(4)

    def initPrices(self):
        pass
        #for i in range(1,self._machine.mysql.totalDevice):
        #    getattr(self.window, 'totalCoinID' + str(i)).setText(str(self.getPrice(i)))

    def updateUi(self):
        
        if self._main_controller.preState == "0":
            self.window.TotalMoney.setText("0")
            self.window.nameID.setText("")
            self.window.slID.setText("0")
            self.window.moneyGet.setText("0")
        elif self._main_controller.preState == "2":
            self.window.webView.load(QUrl("http://localhost:8081"))
            money = self._machine.item.numBuy * self._machine.item.price

        #x =  {"order":"","sts":"","amount":"","time":""}
        elif self._main_controller.preState == "4": #Success
            self.window.lbl_orderID.setText(self._machine.vuluePAY["order"])
            self.window.lbl_orderTime.setText(self._machine.vuluePAY["time"])
            self.window.lbl_orderGET.setText(self._machine.vuluePAY["amount"])
        elif self._main_controller.preState == "5": #Error
            self.window.lbl_erID.setText(self._machine.vuluePAY["order"])
            self.window.lbl_erCode.setText(settings.VNPAY_ERROR_CODE[self._machine.vuluePAY["sts"]])  
        elif self._main_controller.preState == "6":
            self.window.webView.history().clear()
            money = self._machine.item.numBuy * self._machine.item.price
            self.window.moneyFrefund.setText(str(self._machine.moneyGet))
        
    def initEvent(self):
        self.window.page_buttonGroup.buttonClicked.connect(self.main_tab_changed)
        self.window.buy_buttonGroup.buttonClicked.connect(self.haveOrder)
        self.window.btnReturn.clicked.connect(self.returnOrder)

    def main_tab_changed(self, btn):
        print("press")
        index = btn.property("index")
        self.window.main_tab_widget.setCurrentIndex(index)

    def naptien_click(self):
        pass

    def returnOrder(self):
        self._machine.returnOrder()

    def getPrice(self,ID):
        return self._machine.getPrice(ID)

    def slOrderChange(self):
        nameStacked = self.window.sender().property('ID')
        sata = str(self.getPrice(nameStacked))
        position = 1 #int(self.sender().currentIndex())
        total = int(sata)*position
        #getattr(self, 'totalCoinID' + str(nameStacked)).setText(str(total))
        print("have slOrderChange",flush=True)

    def haveOrder(self,btn):
        id = btn.property('ID')
        sl = 1 #int(getattr(self, 'numSlID' +str(id) ).currentIndex())
        self._main_controller.setOrder(id,sl)
        print("have order",flush=True)
#vend()