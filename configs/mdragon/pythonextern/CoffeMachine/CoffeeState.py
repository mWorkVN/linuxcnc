
import time ,os
import logging
import logging.handlers
from PyQt5 import uic,QtCore
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator ,QDoubleValidator
#import linuxcnc
from gtts import gTTS
from playsound import playsound
import pyttsx3
import sys
"""
engine = pyttsx3.init()


rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate


volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

engine.say("Xin Chào các bạn")
engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()
engine.stop()
"""
#tts = gTTS(text='Nhìn mặt thằng này biết ế nên khỏi trả 50000 VND', lang='vi')
tts = gTTS(text='Hu Hu', lang='vi')
tts.save('Ninza.mp3')
playsound('Ninza.mp3')

"""
pip install pyttsx3
install espeak ffmpeg libespeak1
"""
LOG_FILENAME = 'mylog.log'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
my_logger.addHandler(handler)

class Item:
    def __init__(self, name, price, stock ,controlfile):
        self.name = name
        self.price = price
        self.stock = stock
        self.controlfile = controlfile
        self.numBuy = 0

    def updateStock(self, stock):
        self.stock = stock

    def buyFromStock(self):
        if self.stock == 0: # if there is no items available
            # raise not item exception
            pass
        self.stock -= self.numBuy # else stock of item decreases by 1

class State:

    def scan(self):
        #self.mprint("Current Name State  " + self.name)
        pass

    def mprint(self,msg):
        if (os.name == 'nt'): print(msg,flush=True) # win
        elif (os.name == 'posix'): print(msg) # linux 

    def logdata(self,level,msg):
        getattr(my_logger,level)(msg)

class RobotControl(State):
    def __init__(self):
        #self.emc = linuxcnc
        #self.emcstat = self.emc.stat() # create a connection to the status channel
        #self.emccommand = self.emc.command()
        self.myRobot=None 
        self.mprint("Init STATE")   

    def moveToPos(self):
        pass
    def controlPin(self):
        pass
    def waitTime(self):
        pass
    def goHome(self):
        pass


class WaitChooseItemState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to WaitChooseItemState")
        selected = input('select item: ')
        sl = 2
        if self.containsItem(selected):
            self.machine.item = self.getItem(selected)
            self.machine.item.numBuy = int(sl)
            if self.machine.item.stock < int(sl):
                self.mprint(self.machine.item.name + ' sold out')
            else: self.machine.state = self.machine.WaitMoneyToBuyState
            self.logdata("info",'***************\nSwitching to WaitChooseItemState')

    def containsItem(self, wanted):
        ret = False
        for item in self.machine.items:
            if item.name == wanted:
                ret = True
                break
        return ret

    def getItem(self, wanted):
        ret = None
        for item in self.machine.items:
            if item.name == wanted:
                ret = item
                break
        return ret

class ShowItemsState(State):
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to showItemsState")
        self.mprint('\nitems available \n***************')
        #remove item,which have stock is 0
        #for item in self.machine.items: # for each item in this vending machine
        #    if item.stock == 0: # if the stock of this item is 0
        #        self.machine.items.remove(item) # remove this item from being displayed
        for item in self.machine.items:
            self.mprint(item.name + " Price: "+ str(item.price) + "(VND) Stock :" + str(item.stock)) # otherwise self.mprint this item and show its price

        self.mprint('***************\n')
        self.machine.state = self.machine.WaitChooseItemState

class WaitMoneyToBuyState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.moneypre = 0

    def checkAndChangeState(self):
        price = self.machine.item.price * self.machine.item.numBuy
        
        if self.machine.moneyGet < price:
            self.machine.moneyGet = self.machine.moneyGet + float(input('Need ' + str(price  - self.machine.moneyGet) + ' (VND) to pay, inser NOW ->'))
            if (self.moneypre != self.machine.moneyGet):
                self.moneypre = self.machine.moneyGet
                self.logdata("info",'oder: ' + str(self.machine.orderNum + 1) + ' Get: ' + str(self.machine.moneyGet))
        else:
            self.machine.state = self.machine.BuyItemState
            self.machine.orderNum += 1 
            self.moneypre = 0
            self.logdata("info",'oder: ' + str(self.machine.orderNum) + ' B: ' +self.machine.item.name + ' Cash: ' + str(self.machine.moneyGet) + " Done")

class BuyItemState(State):
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine

    def checkAndChangeState(self):
        if self.machine.moneyGet < self.machine.item.price:
            self.mprint('You can\'t buy this item. Insert more coins.') # then obvs you cant buy this item
            self.machine.state = self.machine.WaitMoneyToBuyState
        else:
            self.machine.moneyGet -= (self.machine.item.price * self.machine.item.numBuy) # subtract item price from available cash
            self.machine.item.buyFromStock() # call this function to decrease the item inventory by 1
            self.mprint('You got ' +self.machine.item.name)
            self.mprint('Cash remaining: ' + str(self.machine.moneyGet))
            self.machine.state = self.machine.TakeCoffeeState
            self.logdata("info",'oder: ' + str(self.machine.orderNum) + 'Buy: ' +self.machine.item.name + " Success")

class TakeCoffeeState(State):
    def __init__(self, machine,namestate):
        self.name = namestate        
        self.machine = machine
        self.stateRobot = "init"
        self.gcode = []
        self.numLine = 0

    def checkAndChangeState(self):
        if (self.stateRobot == "init"):
            self.mprint('Control Robot to '+str(self.machine.item.controlfile))
            f = open("./gcode/" + self.machine.item.controlfile, "r")
            self.numLine =0
            for line in f.readlines():
                self.gcode.append(line)
                self.numLine += 1
            f.close()
            self.gcode.reverse()
            self.stateRobot = "Control"

        elif (self.stateRobot == "Control"):

            self.numLine = self.numLine - 1
            self.mprint(self.gcode[self.numLine])
            if (self.numLine == 0):
                self.stateRobot = "finish"
                self.mprint("Line End")            
        elif (self.stateRobot == "finish"):
            self.stateRobot = "init"
            self.logdata("info",'Robot take')
            self.machine.state = self.machine.CheckRefundState


class CheckRefundState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to checkRefundState")
        self.logdata("info",'Refunded oder: ' + str(self.machine.orderNum) + 'Buy:' +self.machine.item.name + 'Refund:' + str(self.machine.moneyGet) + " Success")
        if self.machine.moneyGet > 0:
            self.mprint(str(self.machine.moneyGet) + " refunded.")
            self.machine.moneyGet = 0
        self.machine.item.numBuy = 0
        self.logdata("info",'CheckRefundState OK ' )
        self.mprint('Thank you, have a nice day!\n')
        self.machine.state = self.machine.ShowItemsState

class Machine:
 
    def __init__(self,robot):

        self.myrobot= robot
        self.moneyGet = 0
        self.items = [] # all items contained in this list right here
        self.item=None 
        self.timeout = 10 
        self.orderNum = 0

        self.ShowItemsState = ShowItemsState(self,"SHOW STATE")
        self.WaitChooseItemState = WaitChooseItemState(self,"Wait Select State")
        self.WaitMoneyToBuyState = WaitMoneyToBuyState(self,"Wait Money State")
        self.BuyItemState = BuyItemState(self,"Buy Iteam State")
        self.TakeCoffeeState = TakeCoffeeState(self,"Take Coffe State")
        self.CheckRefundState = CheckRefundState(self,"REFUND STATE")
        
        self.state = self.ShowItemsState

    def run(self):
        self.state.checkAndChangeState()

    def scan(self):
        self.state.scan()

    def addItem(self, item):
        self.items.append(item) 


def vend():
    robot=RobotControl()
    machine = Machine(robot)
    #              name     ,        giá,   số lượng,   file
    item1 = Item('caffe d'  ,      15000,    88,  "caffeden.ngc" )
    item2 = Item('caffe s'  ,      20000,    1 ,  "caffesua.ngc")
    item3 = Item('12'       ,      20000,    3 ,  "nuocngot.ngc")
    item4 = Item('23'       ,      10000,    1 ,  "nuocngot.ngc")
    item5 = Item('45'       ,      10000,    3 ,  "nuocngot.ngc")
    item6 = Item('milkshake',      15000,    5 ,  "nuocngot.ngc")

    machine.addItem(item1)
    machine.addItem(item2)
    machine.addItem(item3)
    machine.addItem(item4)
    machine.addItem(item5)
    machine.addItem(item6)
    continueToBuy = True        

    while continueToBuy == True:
        machine.run()
        machine.scan()

class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi('vendding.ui', self)
        self.show()
        robot=RobotControl()
        self.machine = Machine(robot)
        #              name     ,        giá,   số lượng,   file
        item1 = Item('caffe d'  ,      15000,    88,  "caffeden.ngc" )
        item2 = Item('caffe s'  ,      20000,    1 ,  "caffesua.ngc")
        item3 = Item('12'       ,      20000,    3 ,  "nuocngot.ngc")
        item4 = Item('23'       ,      10000,    1 ,  "nuocngot.ngc")
        item5 = Item('45'       ,      10000,    3 ,  "nuocngot.ngc")
        item6 = Item('milkshake',      15000,    5 ,  "nuocngot.ngc")

        self.machine.addItem(item1)
        self.machine.addItem(item2)
        self.machine.addItem(item3)
        self.machine.addItem(item4)
        self.machine.addItem(item5)
        self.machine.addItem(item6)
        continueToBuy = True
    def paintEvent(self, event):
        self.machine.run()
        self.update()
#vend()

class Model:
    def __init__(self):
        self.username = ""
        self.password = ""

    def verify_password(self):
        return self.username == "USER" and self.password == "PASS"


class View(QMainWindow):
    verifySignal = QtCore.pyqtSignal()

    def __init__(self):
        super(View, self).__init__()
        self.username = ""
        self.password = ""
        self.initUi()

    def initUi(self):
        uic.loadUi('vendding.ui', self)
        self.show()
        """
        self.loginButton.clicked.connect(self.verifySignal)
        hoặc để tạo connect
        self.verifySignal.emit(value)
        """

    def clear(self):
        self.usernameInput.clear()
        self.passwordInput.clear()

    def showMessage(self):
        pass
        """messageBox = QtWidgets.QMessageBox(self)
        messageBox.setText("your credentials are valid\n Welcome")
        messageBox.exec_()
        self.close()
        """
    def showError(self):
        pass


class Controller:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._model = Model()
        self._view = View()
        self.init()

    def init(self):
        self._view.verifySignal.connect(self.verify_credentials)

    def verify_credentials(self):
        self._model.username = self._view.username
        self._model.password = self._view.password
        self._view.clear()
        if self._model.verify_password():
            self._view.showMessage()
        else:
            self._view.showError()

    def run(self):
        self._view.show()
        return self._app.exec_()


if __name__ == '__main__':
    c = Controller()
    sys.exit(c.run())








########################################################
"""if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MyGUI()
	#window.show()
	sys.exit(app.exec_())"""