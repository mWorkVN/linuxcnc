
import time ,os
import logging
import logging.handlers
#import linuxcnc
#https://stackoverflow.com/questions/39442558/logging-rewrite-if-size-gets-too-big

"""
logging.basicConfig(level=logging.DEBUG, filename="newfile.log",format='%(asctime)s - %(levelname)s -%(message)s', filemode='w')
"""

LOG_FILENAME = 'mylog.log'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
#formatter = logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME,format='%(asctime)s - %(levelname)s -%(message)s', filemode='w')
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)
my_logger.addHandler(handler)
for i in range(2000):
    my_logger.debug('ihhhhhhhhhhhhhhhhhhhhhhhh = %d' % i)

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
        self.mprint("Current Name State  " + self.name)
        pass

    def mprint(self,msg):
        #'nt'  # for Linux and Mac it prints 'posix'
        if (os.name == 'nt'): print(msg,flush=True)
        else: print(msg)

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
            my_logger.info('***************\n')
            my_logger.info('Switching to WaitChooseItemState')

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

    def checkAndChangeState(self):
        price = self.machine.item.price * self.machine.item.numBuy
        if self.machine.moneyGet < price:
            self.machine.moneyGet = self.machine.moneyGet + float(input('Need ' + str(price  - self.machine.moneyGet) + ' (VND) to pay, inser NOW ->'))
        else:
            self.machine.state = self.machine.BuyItemState
            my_logger.info('Get Money: ' + str(self.machine.moneyGet))

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
            # (what if we buy more than one?)
            self.mprint('You got ' +self.machine.item.name)
            self.mprint('Cash remaining: ' + str(self.machine.moneyGet))
            self.machine.state = self.machine.TakeCoffeeState
            my_logger.info('BuyItemState ')
class TakeCoffeeState(State):
    def __init__(self, machine,namestate):
        self.name = namestate        
        self.machine = machine

    def checkAndChangeState(self):
        gcode = []
        self.mprint('Control Robot to '+str(self.machine.item.controlfile))
        f = open("./gcode/" + self.machine.item.controlfile, "r")
        for line in f.readlines():
            gcode.append(line)
        self.mprint(gcode)
        f.close()
        #for x in gcode:
        #    self.mprint(x)
        my_logger.info('Robot take ')
        self.machine.state = self.machine.CheckRefundState

class CheckRefundState(State):
    def __init__(self, machine,namestate):
        self.name = namestate     
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to checkRefundState")
        my_logger.info('CheckRefundState '+ str(self.machine.moneyGet)  )
        if self.machine.moneyGet > 0:
            self.mprint(str(self.machine.moneyGet) + " refunded.")
            self.machine.moneyGet = 0
        self.machine.item.numBuy = 0
        my_logger.info('CheckRefundState OK ' )
        self.mprint('Thank you, have a nice day!\n')
        self.machine.state = self.machine.ShowItemsState

class Machine:
 
    def __init__(self,robot):

        self.myrobot= robot
        self.moneyGet = 0
        self.items = [] # all items contained in this list right here
        self.item=None 
        self.timeout = 10 

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

vend()