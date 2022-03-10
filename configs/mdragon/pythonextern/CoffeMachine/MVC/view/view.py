# coding: utf8
import  time ,os,sys
import PyQt5
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import  QObject ,pyqtSlot,QUrl,Qt, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator
import setting.settings as settings
from memory_profiler import profile
import subprocess
class MyGUI(QtWidgets.QMainWindow):

    def __init__(self, machine, main_controller,server):
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
        
        self.FlaskWeb = server()
        self.FlaskWeb.setDaemon(True)
        self.FlaskWeb.start()


        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.setInterval(10) # in milliseconds, so 5000 = 5 seconds
        self.timer.timeout.connect(self.loopGui)
        self.timer.start()

        continueToBuy = True
        self.initEvent()
        self.initUi()
        self.initPrices()
        #self.numberGui = "0"
        #self.test = 0

            
        self._machine.even_loadPAY.connect(self.on_even_loadPAY)
        self._main_controller.state_robot_error.connect(self.on_state_robot_error)
        self._main_controller.even_changePage.connect(self.on_even_changePage)
        #self.show()
        #self.showFullScreen()

    def loopGui(self):
        timebegin = time.time()
        #print("update",self.test)
        self._main_controller.run()
        """stat = self._main_controller.checkChangeState()
        if int(stat) != 0:
            #print("STATE NEW",flush=True)
            self.updateUi()
            getattr(self, 'stackedWidget').setCurrentIndex(int(stat) - 1)
        """
    def paintEvent(self, event):
        pass


    @pyqtSlot(str)
    def on_even_changePage(self, value):
        self.updateUi()
        getattr(self, 'stackedWidget').setCurrentIndex(int(value) - 1)

    @pyqtSlot(str)
    def on_even_loadPAY(self, value):
        self.webView.load(QUrl(value))

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
        for i in range(1,self._machine.mysql.totalDevice + 1):
            getattr(self, 'totalCoinID' + str(i)).setText(str(self.getPrice(i)))

    
    def updateUi(self):
        
        if self._main_controller.preState == "0":
            pass
            #self.TotalMoney.setText("0")
            #self.nameID.setText("")
            #self.slID.setText("0")
            #self.moneyGet.setText("0")
        elif self._main_controller.preState == "2":
            self.webView.load(QUrl("http://localhost:8081"))
            money = self._machine.item.numBuy * self._machine.item.price

        #x =  {"order":"","sts":"","amount":"","time":""}
        elif self._main_controller.preState == "4": #Success
            self.lbl_orderID.setText(self._machine.vuluePAY["order"])
            self.lbl_orderTime.setText(self._machine.vuluePAY["time"])
            self.lbl_orderGET.setText(self._machine.vuluePAY["amount"])

        elif self._main_controller.preState == "5": #Error
            self.lbl_erID.setText(self._machine.vuluePAY["order"])
            self.lbl_erCode.setText(settings.VNPAY_ERROR_CODE[self._machine.vuluePAY["sts"]])  

        elif self._main_controller.preState == "6":
            self.webView.history().clear()
            money = self._machine.item.numBuy * self._machine.item.price
            self.moneyRefund.setText(str(self._machine.moneyGet))
            self.idRefund.setText(str(self._machine.inforpayment['id']))
            self.dayRefund.setText(str(self._machine.inforpayment['day']))
        
    def initEvent(self):
        self.page_buttonGroup.buttonClicked.connect(self.main_tab_changed)
        self.buy_buttonGroup.buttonClicked.connect(self.haveOrder)
        self.btnReturn.clicked.connect(self.returnOrder)

    def main_tab_changed(self, btn):
        index = btn.property("index")
        if index is None: return
        self.main_tab_widget.setCurrentIndex(int(index))
        self.update()

    def naptien_click(self):
        pass

    def returnOrder(self,value):
        self.webView.history().clear()
        self._machine.returnOrder()

    def getPrice(self,ID):
        return self._machine.getPrice(ID)

    def slOrderChange(self):
        idDevide = self.sender().property('ID')
        price = str(self.getPrice(idDevide))
        sl = 1 #int(self.sender().currentIndex())
        total = int(price)*sl
        #getattr(self, 'totalCoinID' + str(nameStacked)).setText(str(total))
        #print("have slOrderChange",flush=True)

    def haveOrder(self,btn):
        id = btn.property('ID')
        sl = 1 #int(getattr(self, 'numSlID' +str(id) ).currentIndex())
        self._main_controller.setOrder(id,sl)
        print("have order",id,sl,flush=True)

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
#vend()