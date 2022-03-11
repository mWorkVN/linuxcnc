#!/usr/bin/ python3
# coding: utf8
import  time ,os,sys
import PyQt5
from PyQt5 import QtWidgets, uic,QtCore
from PyQt5.QtCore import  QObject ,pyqtSlot,QUrl,Qt, QTimer ,QRect
from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator , QTransform , QPainter
import setting.settings as settings
from memory_profiler import profile
import subprocess

class MyGUI(QtWidgets.QMainWindow):

    def __init__(self, machine, main_controller):
        super(MyGUI, self).__init__()
        #self.window = QtWidgets.QMainWindow()
        self.load_resources()
        uic.loadUi('ui/vendding.ui', self )
        
        mainpath = os.path.dirname(os.path.abspath(__file__))
        goal_dir = os.path.join(mainpath, 'res','coofee.qss')
        goal_dir = os.path.abspath(goal_dir)
        qss_file = open(goal_dir).read()
        self.setStyleSheet(qss_file)

        self._machine = machine
        self._main_controller = main_controller
    
        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.setInterval(1) # in milliseconds, so 5000 = 5 seconds
        self.timer.timeout.connect(self.loopGui)
        self.timer.start()
        
        self.initUi()
        self.initPrices()
        self.initEvent()
            
        self._machine.even_loadPAY.connect(self.on_even_loadPAY)
        self._main_controller.state_robot_error.connect(self.on_state_robot_error)
        self._main_controller.even_changePage.connect(self.on_even_changePage)

        self.main_tab_widget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)

        self.videoslider.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        """from view.nuocChaiList import ListNuocChai
        self.CHOOSEACTUATOR = ListNuocChai()
        self.CHOOSEACTUATOR.setObjectName('CHOOSEACTUATOR')
        self.actuator.addWidget(self.CHOOSEACTUATOR)"""

        self.sttImage = 1
        self.timeDisplaySlider = 0
        #self.show()
        #self.showFullScreen()

    def mouseReleaseEvent(self, e):
        if self.stackedWidget.currentIndex() == 0 :
            self._main_controller.beginOrder()
            print("MOUSE")


    def loopGui(self):
        self._main_controller.run()

    def paintEvent(self, event):
        if (time.time() - self.timeDisplaySlider > 2): 
            self.timeDisplaySlider = time.time()
            if self.stackedWidget.currentIndex() == 0 :
                mainpath = os.path.dirname(os.path.abspath(__file__))
                goal_dir = os.path.join(mainpath, 'pic',str(self.sttImage) + '.jpg')
                goal_dir = os.path.abspath(goal_dir)
                pixmap = QPixmap(goal_dir)
                self.videoslider.setPixmap(pixmap)
                self.sttImage += 1
                xform = QTransform()
                xform.rotate(12)
                xformed_pixmap = pixmap.transformed(xform, Qt.SmoothTransformation)
                self.videoslider.setPixmap(xformed_pixmap)
                painter = QPainter(self)
                rect = QRect(10, 60, 8888, 8888)
                painter.drawPixmap(rect, pixmap)
                if (self.sttImage == 18):self.sttImage = 1
                del pixmap,goal_dir,mainpath
                
        self.update()


    @pyqtSlot(str)
    def on_even_changePage(self, value):
        self.updateUi()
        numpage = int(value) 
        if numpage<0: return
        self.stackedWidget.setCurrentIndex(numpage)

    @pyqtSlot(str)
    def on_even_loadPAY(self, value):
        print("begin load",time.time())
        self.webView.load(QUrl(value))
        print("end load",time.time())

    @pyqtSlot(str)
    def on_state_robot_error(self, value):
        print("ERR")
        """msg = QMessageBox()
        msg.setWindowTitle("Tutorial on PyQt5")
        msg.setText("This is the main text!")
        msg.setInformativeText("informative text, ya!")

        msg.setDetailedText("details")
        msg.exec()"""

    def setImage(self,id):
        pass
        """nameimage=str(id)+'.jpg'
        mainpath = os.path.dirname(os.path.abspath(__file__))
        goal_dir = os.path.join(mainpath, 'res',nameimage)
        goal_dir = os.path.abspath(goal_dir)
        pixmap = QPixmap(goal_dir)
        pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.FastTransformation)
        getattr(self, 'imageID' +str(id) ).setPixmap(pixmap)
        getattr(self, 'imageID' +str(id)).resize(pixmap.width(), pixmap.height())     
        del pixmap
        del goal_dir"""
    
    def initUi(self):
        pass
        #self.setImage(1)
        #self.setImage(2)
        #self.setImage(3)
        #self.setImage(4)
    
    def initPrices(self):
        #for i in range(1,self._machine.mysql.totalDevice + 1):
        for i in range(1,12):
            getattr(self, 'totalCoinID' + str(i)).setText(str(self.getPrice(i)))

    
    def updateUi(self):
        
        if self._main_controller.preState == "0":
            pass
        elif self._main_controller.preState == "2":
            self.webView.load(QUrl("http://localhost:8081"))
            money = self._machine.item.numBuy * self._machine.item.price

        #x =  {"order":"","sts":"","amount":"","time":""}
        elif self._main_controller.preState == "4": #Success
            self.lbl_orderID.setText(self._machine.msgFromVNPAY["order"])
            self.lbl_orderTime.setText(self._machine.msgFromVNPAY["time"])
            self.lbl_orderGET.setText(self._machine.msgFromVNPAY["amount"])

        elif self._main_controller.preState == "5": #Error
            self.lbl_erID.setText(self._machine.msgFromVNPAY["order"])
            self.lbl_erCode.setText(settings.VNPAY_ERROR_CODE[self._machine.msgFromVNPAY["sts"]])  

        elif self._main_controller.preState == "6":
            self.webView.history().clear()
            money = self._machine.item.numBuy * self._machine.item.price
            self.moneyRefund.setText(str(self._machine.moneyGet))
            self.idRefund.setText(str(self._machine.inforpayment['id']))
            self.dayRefund.setText(str(self._machine.inforpayment['day']))

        elif self._main_controller.preState == "7":
            self.msgError.setText(str(self._machine.msgError))
            

    def initialized__(self):        

        print("sssssssssssssssssss")

    def initEvent(self):
        self.page_buttonGroup.buttonClicked.connect(self.main_tab_changed)
        self.buy_buttonGroup.buttonClicked.connect(self.haveOrder)
        self.btnReturn.clicked.connect(self.returnOrder)

    def main_tab_changed(self, btn):
        index = btn.property("index")
        if index is None: return
        self.main_tab_widget.setCurrentIndex(int(index))
        self.update()

    def haveOrder(self,btn):
        id = btn.property('ID')
        if id is None: return
        sl = 1 #int(getattr(self, 'numSlID' +str(id) ).currentIndex())
        self._main_controller.setOrder(id,sl)
        print("have order",id,sl)

    def naptien_click(self):
        pass

    def returnOrder(self,value):
        self.webView.history().clear()
        self.webView.load(QUrl("http://localhost:8081"))
        self._machine.returnOrder()

    def getPrice(self,ID):
        return self._machine.getPrice(ID)

    def slOrderChange(self):
        idDevide = self.sender().property('ID')
        price = str(self.getPrice(idDevide))
        sl = 1 #int(self.sender().currentIndex())
        total = int(price)*sl

    def load_resources(self):
        def qrccompile(qrcname, qrcpy):
            try:
                subprocess.call(["pyrcc5", "-o", "{}".format(qrcpy), "{}".format(qrcname)])
            except OSError as e:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("QTvcp qrc compiling ERROR! ")
                msg.setInformativeText(
                    'Qrc Compile error, try: "sudo apt install pyqt5-dev-tools" to install dev tools')
                msg.setWindowTitle("Error")
                msg.setDetailedText('You can continue but some images may be missing')
                msg.setStandardButtons(QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Abort)
                msg.show()
                retval = msg.exec_()
                if retval == QtWidgets.QMessageBox.Abort:  # cancel button
                    raise SystemError('pyrcc5 compiling error: try: "sudo apt install pyqt5-dev-tools"')
        mainpath = os.path.dirname(os.path.abspath(__file__))
        goal_dir = os.path.join(mainpath, 'res','coofee.qrc')
        goal_dir = os.path.abspath(goal_dir)
        resources_dir = os.path.join(mainpath, 'res','resources.py')
        resources_dir = os.path.abspath(resources_dir)
        qrcname = goal_dir
        qrcpy = resources_dir

        # Is there a qrc file in directory?
        if qrcname is not None:
            qrcTime = os.stat(qrcname).st_mtime
            if qrcpy is not None and os.path.isfile(qrcpy):
                pyTime = os.stat(qrcpy).st_mtime
                # is py older then qrc file?
                if pyTime < qrcTime:
                    qrccompile(qrcname, qrcpy)
            # there is a qrc file but no resources.py file...compile it
            else:
                if not os.path.isfile(qrcpy):
                    # make the missing directory
                    try:
                        os.makedirs(os.path.split(qrcpy)[0])
                    except Exception as e:
                        print('could not make directory {} resource file: {}'.format(os.path.split(qrcpy)[0], e))
                qrccompile(qrcname, qrcpy)

        # is there a resource.py in the directory?
        # if so add a path to it so we can import it.
        if qrcpy is not None and os.path.isfile(qrcpy):
            try:
                sys.path.insert(0, os.path.split(qrcpy)[0])
                import importlib
                importlib.import_module('resources', os.path.split(qrcpy)[0])
            except Exception as e:
                print('could not load {} resource file: {}'.format(qrcpy, e))
        else:
            print('No resource file to load: {}'.format(qrcpy))
    ##############################
    # required class boiler code #
    ##############################
    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)
#vend()