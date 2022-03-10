# coding: utf8
import sys, time ,os
import linuxcnc
from PyQt5.QtCore import QObject, pyqtSignal
from until.vnpay import vnpay
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

    @profile
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.status = 0

    def checkAndChangeState(self,data = [0,0]):
        if (self.status != 0):
            """print("Cho HÀN")
            if self.machine.item.stock < int(self.machine.item.numBuy):
                print("HET HaN")"""
            if self.status == 1:
                self.machine.Que.put("Bạn Sẽ Mua {} số lượng {}".format(self.machine.item.name,self.machine.item.numBuy))
                self.machine.Que.put("Tổng Tiền Cần thanh toán là {}".format(self.machine.item.price * self.machine.item.numBuy))
                self.machine.Que.put("END")
                self.status = 2
            elif self.machine.Que.empty():
                self.status = 0
                self.machine.state = self.machine.WaitMoneyToBuyState
                self.logdata("info",'***************\nSwitching to WaitChooseItemState')  

    def haveOrder(self,id,sl = 1):
        if sl==0:
            return
        if self.containsItem(id):
            self.machine.item = self.getItem(id)
            self.machine.item.numBuy = sl
            self.status = 1
            print("DSD",self.status)

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
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate      
        self.machine = machine

    def checkAndChangeState(self,data = [0,0]):
        self.mprint("Switching to showItemsState")
        self.mprint('\nitems available \n***************')
        #for item in self.machine.items:
        #    pass
            #self.mprint(item.name + " Price: "+ str(item.price) + "(VND) Stock :" + str(item.stock)) # otherwise self.mprint this item and show its price
        self.mprint('***************\n')
        self.machine.state = self.machine.WaitChooseItemState


class WaitMoneyToBuyState(State,vnpay):
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
        self.moneypre = 0
        self.state= 0
        self.timeLoop = 0

    def checkAndChangeState(self,data = [0,0]):
        price = self.machine.item.price * self.machine.item.numBuy
        if (self.state == 0):
            self.state = 1
            timebegin = datetime.datetime.now()
            self.machine.orderNum = str(int(round(timebegin.timestamp())))
            self.payment(price,self.machine.orderNum)
            self.timeLoop = time.time()
            
        elif (self.state == 1):
            if (self.machine.queueWebIN.empty() == False):
                self.machine.vuluePAY = self.machine.queueWebIN.get()
                print (self.machine.vuluePAY)
                self.timeLoop = time.time()
                self.state = 2

        elif (self.state == 2):
            if self.machine.vuluePAY["order"] == self.machine.orderNum :
                if self.machine.vuluePAY["sts"] == "00":
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
                #self.logdata("info",'oder: ' + str(self.machine.orderNum + 1) + ' Get: ' + str(self.machine.moneyGet))
        elif self.machine.Que.empty():
            self.state = 0
            self.machine.state = self.machine.BuyItemState
            #self.machine.orderNum += 1 
            self.moneypre = 0
            #self.logdata("info",'oder: ' + str(self.machine.orderNum) + ' B: ' + str(self.machine.item.id) + ' Cash: ' + str(self.machine.moneyGet) + " Done")
        """

    def increMoney(self, moneyGet):
        if (moneyGet !=0):
            self.machine.moneyGet = self.machine.moneyGet + int(moneyGet)
            #self.machine.Que.put("B?n V?a N?p" + str(moneyGet) + " T?ng Ti?n là" + str(self.machine.moneyGet))
            #self.machine.Que.put("END")
            #self.speak(" ")

    def payment(self,price,orderID):
        order_type ='1'
        amount = price
        order_desc = 'Testr'
        bank_code = ''
        language = 'vn'
        ipaddr = '127.0.0.1'
        # Build URL Payment
        
        timebegin = datetime.datetime.now()
        time_change = datetime.timedelta(minutes=1)
        timeend = timebegin + time_change
        order_id = orderID
        self.machine.inforpayment['id'] = order_id
        self.machine.inforpayment['day'] = timebegin.strftime('%Y%m%d%H%M%S')
        #self.idCheck = order_id
        #self.dateCheck=timebegin.strftime('%Y%m%d%H%M%S')
        vnp = vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = 'AGM2PN7X'
        vnp.requestData['vnp_Amount'] = amount * 100
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = self.machine.inforpayment['id']
        vnp.requestData['vnp_OrderInfo'] = order_desc
        vnp.requestData['vnp_OrderType'] = order_type
        # Check language, default: vn
        if language and language != '':
            vnp.requestData['vnp_Locale'] = language
        else:
            vnp.requestData['vnp_Locale'] = 'vn'
            # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
        if bank_code and bank_code != "":
            vnp.requestData['vnp_BankCode'] = bank_code
        
        vnp.requestData['vnp_CreateDate'] = self.machine.inforpayment['day']  # 20150410063022
        vnp.requestData['vnp_ExpireDate'] = timeend.strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = ipaddr
        vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
        #pzrint(vnpay_payment_url)
        del vnp
        self.machine.even_loadPAY.emit(vnpay_payment_url)
        
    def query(self):
        vnp = vnpay()
        vnp.requestData = {}
        vnp.requestData['vnp_Command'] = 'querydr'
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
        vnp.requestData['vnp_TxnRef'] = self.idCheck
        vnp.requestData['vnp_OrderInfo'] = 'Kiem tra ket qua GD OrderId:{}'.format(self.idCheck)
        vnp.requestData['vnp_TransDate'] = self.dateCheck  # 20150410063022
        vnp.requestData['vnp_CreateDate'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
        vnp.requestData['vnp_IpAddr'] = '127.0.0.1'
        requestUrl = vnp.get_payment_url(settings.VNPAY_API_URL, settings.VNPAY_HASH_SECRET_KEY)
        responseData = urllib.request.urlopen(requestUrl).read().decode()
        #print('RequestURL:' + requestUrl)
        #print('VNPAY Response:' + responseData)
        if 'Request_is_duplicate' in responseData:
            del vnp
            return
        data = responseData.split('&')
        for x in data:
            tmp = x.split('=')
            if len(tmp) == 2:
                vnp.responseData[tmp[0]] = urllib.parse.unquote(tmp[1]).replace('+', ' ')
        del vnp
        #print('Validate data from VNPAY:' + str(vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY))  )

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
            self.mprint('You can\'t buy this item. Insert more coins.') # then obvs you cant buy this item
            self.machine.state = self.machine.WaitChooseItemState
        else:
            # subtract item price from available cash
            self.machine.item.buyFromStock() # call this function to decrease the item inventory by 1
            #self.mprint('You got ' +self.machine.item.name)
            #self.mprint('Cash remaining: ' + str(self.machine.moneyGet))
            self.machine.state = self.machine.TakeCoffeeState
            #self.logdata("info",'oder: ' + str(self.machine.orderNum) + 'Buy: ' + str(self.machine.item.id) + " Success")

class TakeCoffeeState(State):
    @profile
    def __init__(self, machine,namestate):
        self.name = namestate        
        self.machine = machine
        self.stateRobot = "init"
        self.dataSQL = None
        self.gcode = []
        self.numLine = 0

    def checkAndChangeState(self,data = [0,0]):
        if (self.stateRobot == "init"):
            self.gcode = []
            self.dataSQL=self.machine.mysql.getData(str(self.machine.item.id))
            if self.dataSQL[19] != "END":
                print("Sai Data")
                self.machine.state = self.machine.CheckRefundState
            self.numLine = 0
            self.stateRobot = "Control"
            self.machine.myrobot.initstate()

        elif (self.stateRobot == "Control"):
            if (self.machine.myrobot.run(self.dataSQL) == 1):
                self.stateRobot = "finish"
                self.mprint("Line End") 

        elif (self.stateRobot == "finish"):
            self.stateRobot = "init"
            self.logdata("info",'Robot take')
            self.machine.moneyGet -= (self.machine.item.price * self.machine.item.numBuy)
            self.machine.state = self.machine.CheckRefundState

class ErrorMachineState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine
    def checkAndChangeState(self,data = [0,0]):
        pass

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
            
            self.machine.Que.put("Số Tiền thừa là " + str(self.machine.moneyGet) + "VND")

            if (self.machine.moneyGet == 4000):
                self.machine.Que.put("Nhìn quý khách là biết ế lâu năm nên\
                                     thôi khỏi thối lại")
            elif (self.machine.moneyGet == 5000):
                self.machine.Que.put("Quý khách lần này đẹp trai nên thối hẳn \
                                    cho 10000")
            """
            self.machine.Que.put("Chúc quý khách ngon miệng")
            
        elif self.machine.Que.empty():
            self.state = 0
            #self.logdata("info",'Refunded oder: ' + str(self.machine.orderNum)  + 'Refund:' + str(self.machine.moneyGet) + " Success")
            if self.machine.moneyGet > 0:
                #self.mprint(str(self.machine.moneyGet) + " refunded.")
                self.machine.moneyGet = 0
                time.sleep(2)
            self.machine.item.numBuy = 0
            self.logdata("info",'CheckRefundState OK ' )
            self.mprint('Thank you, have a nice day!\n')
            time.sleep(2)
            self.machine.inforpayment['id'] = ''
            self.machine.inforpayment['day'] = ''
            self.machine.state = self.machine.ShowItemsState

class Machine(QObject):
    even_loadPAY = pyqtSignal(str)
    
    @profile
    def __init__(self,my_logger,queueWEB,valveModbus):
        super().__init__()
        self.inforpayment ={'id':'','day':''}
        self.valveModbus = valveModbus
        self.mysql = mysql()
        self.my_logger = my_logger
        self.moneyGet = 0
        self.items = [] # all items contained in this list right here
        self.item=None 
        self.vuluePAY = ''
        self.timeout = 10 
        self.orderNum = 0
        self.Que = queue.Queue(5)

        self.queueWebIN = queueWEB
        self.ShowItemsState = ShowItemsState(self,"0")
        self.WaitChooseItemState = WaitChooseItemState(self,"1")
        self.WaitMoneyToBuyState = WaitMoneyToBuyState(self,"2")
        self.BuyItemState = BuyItemState(self,"3")
        self.TakeCoffeeState = TakeCoffeeState(self,"4")
        self.ErrorState = ErrorState(self,"5")
        self.CheckRefundState = CheckRefundState(self,"6")
        self.ErrorMachineState = ErrorMachineState(self,"7")
        self.state = self.ShowItemsState
        self.state.speak("S")
        self.plcVal = ControlVal(valveModbus)
        self.myrobot=RobotControl(self.plcVal)
        self.statusMachine = 0 # =1 error Robot, 3error PLC
        self.totalItems = 2
        for i in range(1,self.mysql.totalDevice):
            dataget=self.mysql.getData(str(i))
            self.addItem(Item(i,'caffe sữa'  ,      dataget[4],    8800000000,  "caffeden.ngc" ))

        self.timeLoopGetPLC = 0

    def returnOrder(self):
        self.state = self.ShowItemsState
        self.WaitMoneyToBuyState.state = 0

    def run(self,data = [0,0]):
        self.state.checkAndChangeState(data)
        if (time.time() - self.timeLoopGetPLC > 60):
            self.timeLoopGetPLC = time.time()
            mucNuoc = self.plcVal.getData(1,3,28,14)
            print("mucNuoc",mucNuoc)
        if self.plcVal.stateModbus == 'er' or self.myrobot.statusRobot == 'er':
            pass
        elif self.state.scan() == "7":
            self.state = self.ShowItemsState
            print("error")

    def scan(self):
        return self.state.scan()

    def addItem(self, item):
        self.items.append(item) 

    def getOrder(self, value,sl):
        self.WaitChooseItemState.haveOrder(value,sl)
        print("get Order From Ui",value,sl,flush=True)

    def getPrice(self,ID):
        for item in self.items:
            if item.id == ID:
                return item.price
                break
        return 0

    def SendMoney(self, money):
        self.WaitMoneyToBuyState.increMoney(money)

