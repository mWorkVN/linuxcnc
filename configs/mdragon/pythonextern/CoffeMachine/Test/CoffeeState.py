# coding: utf8
import sys, time ,os
import logging
import logging.handlers
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QObject
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

"""
tts = gTTS(text='Hu Hu', lang='vi')
tts.save('Ninza.mp3')
playsound('Ninza.mp3')
os.remove('Ninza.mp3')
"""

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
    def __init__(self,id, name, price, stock ,controlfile):
        self.id = id
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
        return self.name
        pass

    def mprint(self,msg):
        if (os.name == 'nt'): print(msg,flush=True) # win
        elif (os.name == 'posix'): print(msg) # linux 

    def logdata(self,level,msg):
        getattr(my_logger,level)(msg)
    

    def speak1(self,msg):
        while(1):
            if (self.machine.Que.empty() == False):
                filename = "talk"+str(int(time.time()))+".mp3"
                msg = self.machine.Que.get() 
                if (msg == "END"):continue
                print("Play ",str(filename),flush=True)
                tts = gTTS(text=msg, lang='vi')
                tts.save(filename)
                audio_file =filename
                playsound(audio_file)
                os.remove(audio_file)

    def speak(self,msg):
        t = Thread(target=self.speak1, args=(msg,))
        t.setDaemon(True); 
        t.start()


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
        self.status = 0

    def checkAndChangeState(self,data = [0,0]):
        if (self.status != 0):
            if self.machine.item.stock < int(self.machine.item.numBuy):
                pass
            elif self.status == 1:
                self.machine.Que.put("Bạn Sẽ Mua " + str(self.machine.item.name) + " số lượng " + str(self.machine.item.numBuy))
                self.machine.Que.put("Tổng Tiền Cần thanh toán là" + str(self.machine.item.price * self.machine.item.numBuy))
                self.machine.Que.put("END")
                self.status = 2
            elif self.machine.Que.empty():
                self.status = 0
                self.machine.state = self.machine.WaitMoneyToBuyState
                self.logdata("info",'***************\nSwitching to WaitChooseItemState')  

    def haveOrder(self,id,sl = 1):
        if self.containsItem(id):
            self.machine.item = self.getItem(id)
            self.machine.item.numBuy = sl
            self.status = 1

    def containsItem(self, wanted):
        ret = False
        wanted = int(wanted)
        for item in self.machine.items:
            if item.id == wanted:
                ret = True
                break
        return ret

    def checkID(self, wanted):
        ret = False
        wanted = int(wanted)
        for item in self.machine.items:
            if item.id == wanted:
                ret = True
                break
        return ret

    def getItem(self, wanted):
        ret = None
        for item in self.machine.items:
            if item.id == wanted:
                ret = item
                break
        return ret

class ShowItemsState(State):
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine

    def checkAndChangeState(self,data = [0,0]):
        self.mprint("Switching to showItemsState")
        self.mprint('\nitems available \n***************')
        for item in self.machine.items:
            pass
            #self.mprint(item.name + " Price: "+ str(item.price) + "(VND) Stock :" + str(item.stock)) # otherwise self.mprint this item and show its price
        self.mprint('***************\n')
        self.machine.state = self.machine.WaitChooseItemState


class WaitMoneyToBuyState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.moneypre = 0

    def checkAndChangeState(self,data = [0,0]):
        price = self.machine.item.price * self.machine.item.numBuy
        
        if self.machine.moneyGet < price:
            if (self.moneypre != self.machine.moneyGet):
                self.moneypre = self.machine.moneyGet
                self.logdata("info",'oder: ' + str(self.machine.orderNum + 1) + ' Get: ' + str(self.machine.moneyGet))
        elif self.machine.Que.empty():
            self.machine.state = self.machine.BuyItemState
            self.machine.orderNum += 1 
            self.moneypre = 0
            self.logdata("info",'oder: ' + str(self.machine.orderNum) + ' B: ' + str(self.machine.item.id) + ' Cash: ' + str(self.machine.moneyGet) + " Done")

    def increMoney(self, moneyGet):
        if (moneyGet !=0):
            self.machine.moneyGet = self.machine.moneyGet + int(moneyGet)
            self.machine.Que.put("Bạn Vừa Nạp" + str(moneyGet) + " Tổng Tiền là" + str(self.machine.moneyGet))
            self.machine.Que.put("END")
            #self.speak(" ")

class BuyItemState(State):
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine

    def checkAndChangeState(self,data = [0,0]):
        if self.machine.moneyGet < self.machine.item.price:
            self.mprint('You can\'t buy this item. Insert more coins.') # then obvs you cant buy this item
            self.machine.state = self.machine.WaitMoneyToBuyState
        else:
            self.machine.moneyGet -= (self.machine.item.price * self.machine.item.numBuy) # subtract item price from available cash
            self.machine.item.buyFromStock() # call this function to decrease the item inventory by 1
            #self.mprint('You got ' +self.machine.item.name)
            self.mprint('Cash remaining: ' + str(self.machine.moneyGet))
            self.machine.state = self.machine.TakeCoffeeState
            self.logdata("info",'oder: ' + str(self.machine.orderNum) + 'Buy: ' + str(self.machine.item.id) + " Success")

class TakeCoffeeState(State):
    def __init__(self, machine,namestate):
        self.name = namestate        
        self.machine = machine
        self.stateRobot = "init"
        self.gcode = []
        self.numLine = 0

    def checkAndChangeState(self,data = [0,0]):
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
            time.sleep(1)
            if (self.numLine == 0):
                self.stateRobot = "finish"
                self.mprint("Line End")            
        elif (self.stateRobot == "finish"):
            self.stateRobot = "init"
            self.logdata("info",'Robot take')
            self.machine.state = self.machine.CheckRefundState

class textToSpeed(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
    def checkAndChangeState(self,data = [0,0]):
        pass

class CheckRefundState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.state = 0
    def checkAndChangeState(self,data = [0,0]):
        if (self.state == 0):
            self.state = 1
            self.mprint("Switching to checkRefundState")
            
            self.machine.Que.put("Số Tiền thừa là " + str(self.machine.moneyGet) + "VND")

            if (self.machine.moneyGet == 4000):
                self.machine.Que.put("Nhìn quý khách là biết ế lâu năm nên thôi khỏi thối lại")
            elif (self.machine.moneyGet == 5000):
                self.machine.Que.put("Quý khách lần này đẹp trai nên thối hẳn cho 10000")
            self.machine.Que.put("Chúc quý khách ngon miệng")
        elif self.machine.Que.empty():
            self.state = 0
            self.logdata("info",'Refunded oder: ' + str(self.machine.orderNum)  + 'Refund:' + str(self.machine.moneyGet) + " Success")
            if self.machine.moneyGet > 0:
                self.mprint(str(self.machine.moneyGet) + " refunded.")
                self.machine.moneyGet = 0
            self.machine.item.numBuy = 0
            self.logdata("info",'CheckRefundState OK ' )
            self.mprint('Thank you, have a nice day!\n')
            time.sleep(2)
            self.machine.state = self.machine.ShowItemsState

class Machine:
 
    def __init__(self,robot):
        super().__init__()
        self.myrobot= robot
        self.moneyGet = 0
        self.items = [] # all items contained in this list right here
        self.item=None 
        self.timeout = 10 
        self.orderNum = 0
        self.Que = queue.Queue(5)
        self.ShowItemsState = ShowItemsState(self,"0")
        self.WaitChooseItemState = WaitChooseItemState(self,"1")
        self.WaitMoneyToBuyState = WaitMoneyToBuyState(self,"2")
        self.BuyItemState = BuyItemState(self,"3")
        self.TakeCoffeeState = TakeCoffeeState(self,"4")
        self.CheckRefundState = CheckRefundState(self,"5")
        
        self.state = self.ShowItemsState
        self.state.speak("S")

    def run(self,data = [0,0]):
        self.state.checkAndChangeState(data)

    def scan(self):
        return self.state.scan()

    def addItem(self, item):
        self.items.append(item) 
    # Takes Signal from UI
    @pyqtSlot(int)
    def getOrder(self, value,sl):
        self.WaitChooseItemState.haveOrder(value,sl)
        print("get Order From Ui",flush=True)

    def getPrice(self,ID):
        for item in self.items:
            if item.id == ID:
                return item.price
                break
        return 0

    def SendMoney(self, money):
        self.WaitMoneyToBuyState.increMoney(money)


class MyGUI(QMainWindow):
    
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi('vendding.ui', self)
        self.show()
        robot=RobotControl()
        self.machine = Machine(robot)
        #              name     ,        giá,   số lượng,   file
        item1 = Item(1,'caffe sữa'  ,      15000,    88,  "caffeden.ngc" )
        item2 = Item(2,'caffe đen'  ,      20000,    1 ,  "caffesua.ngc")
        item3 = Item(3,'caffe Kem'  ,      25000,    88,  "caffeden.ngc" )
        item4 = Item(4,'Nước Suối'  ,      10000,    1 ,  "caffesua.ngc")
        self.machine.addItem(item1)
        self.machine.addItem(item2)
        self.machine.addItem(item3)
        self.machine.addItem(item4)
        continueToBuy = True
        self.initEvent()
        self.initUi()
        self.preState = "0"

    def paintEvent(self, event):
        self.machine.run()
        if (self.preState != self.machine.scan()):
            self.preState = self.machine.scan()
            print("STATE NEW",self.preState,flush=True)
            getattr(self, 'stackedWidget').setCurrentIndex(int(self.preState) - 1)
            self.updateUi()
        self.update()

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
        if self.preState == "0":
            self.TotalMoney.setText("0")
            self.nameID.setText("")
            self.slID.setText("0")
            self.moneyGet.setText("0")
        elif self.preState == "2":
            money = self.machine.item.numBuy * self.machine.item.price
            self.TotalMoney.setText(str(money))
            self.nameID.setText(self.machine.item.name)
            self.slID.setText(str(self.machine.item.numBuy))
            self.moneyGet.setText(str(self.machine.moneyGet))
        elif self.preState == "5":
            money = self.machine.item.numBuy * self.machine.item.price
            self.moneyFrefund.setText(str(self.machine.moneyGet))

    def initEvent(self):

        self.btnBuyID1.clicked.connect(self.haveOrder)
        self.btnBuyID2.clicked.connect(self.haveOrder)
        self.numSlID1.currentTextChanged.connect(self.slOrderChange)
        self.numSlID2.currentTextChanged.connect(self.slOrderChange)
        self.btn_naptien.clicked.connect(self.naptien_click)

    def naptien_click(self):
        money = int(self.lblmoneyNap.text())
        self.machine.SendMoney(money)
        self.moneyGet.setText(str(self.machine.moneyGet))

    def getPrice(self,ID):
        return self.machine.getPrice(ID)

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
        self.machine.getOrder(id,sl)
        print("have order",flush=True)
#vend()


"""

if __name__ == '__main__':
    c = Controller()
    sys.exit(c.run())

"""






########################################################
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MyGUI()
	#window.show()
	sys.exit(app.exec_())