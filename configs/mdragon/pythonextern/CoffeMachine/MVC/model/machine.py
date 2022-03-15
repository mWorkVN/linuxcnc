# coding: utf8
import sys, time ,os
import linuxcnc
from PyQt5.QtCore import QObject, pyqtSignal
#from until.vnpay import vnpay
from model.state import State
from model.robotControl import RobotControl
from model.controlVal import ControlVal
import setting.settings as settings
from until.sql import mysql
try: 
    import queue
except ImportError: #py2
    import Queue as queue
#import imp
import datetime
import subprocess
from memory_profiler import profile
from until.mylog import getlogger
my_logger=getlogger("__machine___")

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

class WaitChooseItemState(State):

    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.status = 0

    def checkAndChangeState(self,data = [0,0]):
        if (self.status != 0):
            if self.status == 1:
                self.machine.queSpeaker.put("Bạn Sẽ Mua {} số lượng {}".format(self.machine.item.name,self.machine.item.numBuy))
                self.machine.queSpeaker.put("Tổng Tiền Cần thanh toán là {}".format(self.machine.item.price * self.machine.item.numBuy))
                self.machine.queSpeaker.put("END")
                self.status = 2
            elif self.machine.queSpeaker.empty():
                self.status = 0
                self.machine.state = self.machine.WaitMoneyToBuyState
                my_logger.info('***************\nSwitching to WaitChooseItemState')  

    def haveOrder(self,id,sl = 1):
        if sl==0:
            return
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
        pass
        #self.mprint("Switching to showItemsState")
        #self.mprint('\nitems available \n***************')
        #for item in self.machine.items:
        #    pass
            #self.mprint(item.name + " Price: "+ str(item.price) + "(VND) Stock :" + str(item.stock)) # otherwise self.mprint this item and show its price
        #self.mprint('***************\n')
        #self.machine.state = self.machine.WaitChooseItemState


class WaitMoneyToBuyState(State):

    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.moneypre = 0
        self.state= 0
        self.timeLoop = 0

    def checkAndChangeState(self,data = [0,0]):
        price = self.machine.item.price * self.machine.item.numBuy
        if (self.state == 0): # NEED CHECK ROBOT AND VALVE STATE, IF it don't have err then change state
            self.machine.myrobot.checkEMC()
            if self.machine.checkError() == True :
                self.machine.state = self.machine.ErrorMachineState
                my_logger.error("Order : ERROR ROZBOT")
            elif self.machine.checkNLofOrder() == True :
                self.machine.state = self.machine.ErrorMachineState
                my_logger.error("Order : ERROR PLC")
            else:self.state = 1
        if (self.state == 1):
            self.state = 2
            timebegin = datetime.datetime.now()
            self.machine.inforpayment['id']= str(int(round(timebegin.timestamp())))
            self.machine.inforpayment['day'] = timebegin.strftime('%Y%m%d%H%M%S')  
            self.createPayment(price,self.machine.inforpayment['id'],self.machine.inforpayment['day'])
            self.timeLoop = time.time()
            
        elif (self.state == 2):
            if (self.machine.queueWebIN.empty() == False):
                self.machine.msgFromVNPAY = self.machine.queueWebIN.get()
                my_logger.info (self.machine.msgFromVNPAY)
                self.timeLoop = time.time()
                self.state = 3

        elif (self.state == 3):
            if self.machine.msgFromVNPAY["order"] == self.machine.inforpayment['id'] :
                if self.machine.msgFromVNPAY["sts"] == "00":
                    self.machine.moneyGet = price
                    self.machine.state = self.machine.BuyItemState
                else:
                    self.machine.state = self.machine.ErrorState
            else:
                self.machine.state = self.machine.ErrorState
            self.state = 0
            

        """if self.machine.moneyGet < price:
            if (self.moneypre != self.machine.moneyGet):
                self.moneypre = self.machine.moneyGet
                #my_logger.info("info",'oder: ' + str(self.machine.orderNum + 1) + ' Get: ' + str(self.machine.moneyGet))
        elif self.machine.queSpeaker.empty():
            self.state = 0
            self.machine.state = self.machine.BuyItemState
            #self.machine.orderNum += 1 
            self.moneypre = 0
            #my_logger.info("info",'oder: ' + str(self.machine.orderNum) + ' B: ' + str(self.machine.item.id) + ' Cash: ' + str(self.machine.moneyGet) + " Done")
        """

    def increMoney(self, moneyGet):
        if (moneyGet !=0):
            self.machine.moneyGet = self.machine.moneyGet + int(moneyGet)
    def createPayment(self,price,orderID,day):
        url = self.machine.RunVNPAY.payment(price,orderID,day)  
        self.machine.even_loadPAY.emit(url)
    
class ErrorState(State):
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine
        self.timeout = 0
        
    def checkAndChangeState(self,data = [0,0]):
        if self.timeout == 0:
            self.timeout = time.time()
        elif time.time() - self.timeout  > 4:
            self.timeout = 0
            self.machine.state = self.machine.ShowItemsState

class BuyItemState(State):
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine
        self.timeout = 0
    def checkAndChangeState(self,data = [0,0]):

        if self.machine.moneyGet < self.machine.item.price:
            my_logger.info('You can\'t buy this item. Insert more coins.') # then obvs you cant buy this item
            self.machine.state = self.machine.WaitChooseItemState
        else:
            self.machine.item.buyFromStock() # call this function to decrease the item inventory by 1
            self.machine.state = self.machine.TakeCoffeeState
            #my_logger.info("info",'oder: ' + str(self.machine.orderNum) + 'Buy: ' + str(self.machine.item.id) + " Success")

class TakeCoffeeState(State):
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate        
        self.machine = machine
        self.stateRobot = "init"
        #self.dataSQL = None
        self.gcode = []
        self.numLine = 0

    def checkAndChangeState(self,data = [0,0]):
        if (self.stateRobot == "init"):
            self.gcode = []
            #self.dataSQL=self.machine.mysql.getData(str(self.machine.item.id))
            #if self.dataSQL[19] != "END":
            #    self.machine.state = self.machine.CheckRefundState
            self.numLine = 0
            self.stateRobot = "Control"
            self.machine.myrobot.initstate()

        elif (self.stateRobot == "Control"):
            if (self.machine.myrobot.run(self.machine.dataOrder) == 1):
                self.stateRobot = "finish"

        elif (self.stateRobot == "finish"):
            self.stateRobot = "init"
            my_logger.info('Robot take Finish')
            self.machine.moneyGet -= (self.machine.item.price * self.machine.item.numBuy)
            self.machine.state = self.machine.CheckRefundState

class ErrorMachineState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.timeout = 0
    def checkAndChangeState(self,data = [0,0]):
        #DISPLAY ERROR STATE IN 5 seconds
        if self.timeout == 0:
            self.timeout = time.time()
        elif (time.time()- self.timeout ) >3:
            self.timeout = 0
            self.machine.state = self.machine.ShowItemsState


class CheckRefundState(State):
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.state = 0
    def checkAndChangeState(self,data = [0,0]):
        if (self.state == 0):
            self.state = 1
            """
            self.mprint("Switching to checkRefundState")
            
            self.machine.queSpeaker.put("Số Tiền thừa là " + str(self.machine.moneyGet) + "VND")

            if (self.machine.moneyGet == 4000):
                self.machine.queSpeaker.put("Nhìn quý khách là biết ế lâu năm nên\
                                     thôi khỏi thối lại")
            elif (self.machine.moneyGet == 5000):
                self.machine.queSpeaker.put("Quý khách lần này đẹp trai nên thối hẳn \
                                    cho 10000")
            """
            self.machine.queSpeaker.put("Chúc quý khách ngon miệng")
            
        elif self.machine.queSpeaker.empty():
            self.state = 0
            #my_logger.info("info",'Refunded oder: ' + str(self.machine.orderNum)  + 'Refund:' + str(self.machine.moneyGet) + " Success")
            if self.machine.moneyGet > 0:
                #self.mprint(str(self.machine.moneyGet) + " refunded.")
                self.machine.moneyGet = 0
                time.sleep(2)
            self.machine.item.numBuy = 0
            my_logger.info('CheckRefundState OK ' )
            my_logger.info('Thank you, have a nice day!\n')
            time.sleep(2)
            self.machine.inforpayment['id'] = ''
            self.machine.inforpayment['day'] = ''
            self.machine.state = self.machine.ShowItemsState

class Machine(QObject):
    even_loadPAY = pyqtSignal(str)
    even_loads = pyqtSignal(str)
    @profile
    def __init__(self,my_logger,queueWEB,valveModbus, RunVNPAY):
        super().__init__()
        self.RunVNPAY = RunVNPAY 
        self.inforpayment ={'id':'','day':'','moneyGet':0}
        #self.valveModbus = valveModbus
        self.mysql = mysql()
        self.my_logger = my_logger
        self.moneyGet = 0
        self.items = [] # all items contained in this list right here
        self.item=None 
        self.msgFromVNPAY = ''
        self.timeout = 10 
        #self.orderNum = 0

        self.queSpeaker = queue.Queue(5)
        self.queueWebIN = queueWEB

        self.ShowItemsState = ShowItemsState(self,"0")
        self.WaitChooseItemState = WaitChooseItemState(self,"1")
        self.WaitMoneyToBuyState = WaitMoneyToBuyState(self,"2")
        self.BuyItemState = BuyItemState(self,"3")
        self.TakeCoffeeState = TakeCoffeeState(self,"4")
        self.ErrorState = ErrorState(self,"5")
        self.CheckRefundState = CheckRefundState(self,"6")
        self.ErrorMachineState = ErrorMachineState(self,"7")
        self.ErrorNLState = ErrorMachineState(self,"8")
        self.state = self.ShowItemsState

        self.state.speak("S")
        self.plcVal = ControlVal(valveModbus)
        self.myrobot=RobotControl(self.plcVal)
        self.myrobot.initRobot()
        #self.statusMachine = 0 # =1 error Robot, 3error PLC
        self.totalItems = 2
        for i in range(1,self.mysql.totalDevice):
            dataget=self.mysql.getData(str(i))
            self.addItem(Item(i,'caffe sữa'  ,      dataget[4],    8800000000,  "caffeden.ngc" ))

        self.timeLoopGetPLC = 0
        self.timecheckLOOP = 0

        self.mucNguyenLieu = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.dataOrder =  self.mysql.getData(str(1))
        self.msgError = ""

    def returnOrder(self):
        self.state = self.ShowItemsState
        self.WaitMoneyToBuyState.state = 0

    def run(self,data = [0,0]):
        timeNow = time.time()
        self.checkRebootRobot()
        self.state.checkAndChangeState(data)
        if (timeNow - self.timeLoopGetPLC > settings.TIME_CHECK_NGUYENLIEU):
            self.timeLoopGetPLC = timeNow
            mucNuoc = self.plcVal.getData(1,3,28,14)
            my_logger.debug("NL {} ".format(mucNuoc))
            if mucNuoc['s'] == 'ok': self.mucNguyenLieu = mucNuoc['d']
            #self.plcVal.checkError(1) # READ COIN 
        self.timecheckLOOP = timeNow

    def checkRebootRobot(self):
        if self.myrobot.getER() == 'reboot': # linuxcnc mat nguon, can reboot lai
            self.even_loads.emit("c")

    def rebootRobot(self):
        del self.myrobot
        self.myrobot=RobotControl(self.plcVal)

    def initRobot(self):
        self.myrobot.initRobot()


    def checkError(self):
        if self.plcVal.stateModbus == 'er':
            self.msgError = "PLC ERROR"
            return True
        if self.myrobot.statusRobot != 'ok':
            self.msgError = self.myrobot.statusRobot
            return True
        return False

    def checkNLofOrder(self):
        for i in range(0,13):
            if (self.dataOrder[i+5] >0) and self.mucNguyenLieu[i] == 0:
                self.msgError = "Hết Nguyên Liệu Tại Vị Trí {}".format(i)
                return True
        return False

    def scan(self):
        return self.state.scan()

    def addItem(self, item):
        self.items.append(item) 

    def getOrder(self, value,sl):
        self.dataOrder=self.mysql.getData(str(value))
        if self.dataOrder[19] == "END":
            self.state = self.WaitChooseItemState
            self.WaitChooseItemState.haveOrder(value,sl)
            my_logger.info("hve oder")
        else:
            my_logger.error("get Order From Ui sai DATABASE")


    def getPrice(self,ID):
        for item in self.items:
            if item.id == ID:
                return item.price
                break
        return 0

    def SendMoney(self, money):
        self.WaitMoneyToBuyState.increMoney(money)

