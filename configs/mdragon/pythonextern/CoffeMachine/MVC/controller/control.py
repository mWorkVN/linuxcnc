from PyQt5.QtCore import QObject, pyqtSlot ,pyqtSignal

 
class MainController(QObject):
    state_robot_error = pyqtSignal(str)
    def __init__(self, Machine):
        super().__init__()
        self.preState = "0"
        self._machine = Machine

    #Call From GUI
    def run(self):
        self._machine.run()

    def checkChangeState(self):
        if (self.preState != self._machine.scan()):
            self.preState = self._machine.scan()
            return self.preState
        return "0"

    def setOrder(self,id,sl):
        self._machine.myrobot.checkError()
        if self._machine.myrobot.checkEMC() == True:
            self._machine.getOrder(id,sl)
        else:
            self.state_robot_error.emit("ERR")
        pass

    def setMoneyGet(self,money):
        self._machine.SendMoney(money)

    def getCurrentState(self):
        return self.preState
       