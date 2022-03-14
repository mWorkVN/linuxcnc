from PyQt5.QtCore import QObject, pyqtSlot ,pyqtSignal
from manage.checkSys import checkSys
import time
from until.mylog import getlogger
my_logger=getlogger("__Control___")
class MainController(QObject):
    even_changePage = pyqtSignal(str)
    state_robot_error = pyqtSignal(str)
    def __init__(self, Machine):
        super().__init__()
        self.preState = "0"
        self._machine = Machine
        self._manageSysTem = checkSys()
        self.timeLOOPCheckSYS = 0
        self.timeBeginOrder = 0
    #Call From GUI
    def run(self):
        self._machine.run()
        self.checkChangeState()
        self.checkMemory()
        self.checkTimeOutDisplay()

    def checkChangeState(self):
        if (self.preState != self._machine.scan()):
            self.preState = self._machine.scan()
            self.even_changePage.emit(self.preState)
            
    def checkMemory(self):
        if (time.time()- self.timeLOOPCheckSYS > 10):
            self.timeLOOPCheckSYS = time.time()
            my_logger.debug("Mempry {} ".format(self._manageSysTem.run()))

    def setOrder(self,id,sl):
        self.timeBeginOrder = 0
        my_logger.info("have order {} {}".format(id,sl))
        self._machine.getOrder(id,sl)
        """if self._machine.myrobot.checkEMC() == True:
            my_logger.info("have order {} {}".format(id,sl))
            self._machine.getOrder(id,sl)
        else:
            self.state_robot_error.emit("ERR")
        """
    def setMoneyGet(self,money):
        self._machine.SendMoney(money)

    def getCurrentState(self):
        return self.preState

    def checkTimeOutDisplay(self):
        if self.timeBeginOrder == 0: return
        elif time.time() -self.timeBeginOrder >30:
            self.timeBeginOrder =0
            self._machine.state = self._machine.ShowItemsState

    def beginOrder(self):
        self.timeBeginOrder = time.time()
        self._machine.state = self._machine.WaitChooseItemState
       