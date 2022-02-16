
import time



class Item:
    def __init__(self, name, price, stock ,controlfile):
        self.name = name
        self.price = price
        self.stock = stock
        self.controlfile = controlfile

    def updateStock(self, stock):
        self.stock = stock

    def buyFromStock(self):
        if self.stock == 0: # if there is no items available
            # raise not item exception
            pass
        self.stock -= 1 # else stock of item decreases by 1

class State:
    def __init__(self):
        self.myRobot=None 
        self.text = "Ss" 
        self.mprint("Init STATE")

    def scan(self):
        pass

    def mprint(self,msg):
        print(msg,flush=True)

    def moveRobot(self,msg):
        pass

class RobotControl(State):
    def __init__(self):
        self.myRobot=None 
        self.text = "Ss" 
        self.mprint("Init STATE")   

class WaitChooseItemState(State):

    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to WaitChooseItemState")
        selected = input('select item: ')
        if self.containsItem(selected):
            self.machine.item = self.getItem(selected)
            self.machine.state = self.machine.waitMoneyToBuyState

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

class showItemsState(State):
    def __init__(self, machine):  
        State.__init__(self)    
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to showItemsState")
        self.mprint('\nitems available \n***************')
        #remove item,which have stock is 0
        #for item in self.machine.items: # for each item in this vending machine
        #    if item.stock == 0: # if the stock of this item is 0
        #        self.machine.items.remove(item) # remove this item from being displayed
        for item in self.machine.items:
            self.mprint(item.name + " Gia: "+ str(item.price) + " + SL :" + str(item.stock)) # otherwise self.mprint this item and show its price

        self.mprint('***************\n')
        self.machine.state = self.machine.WaitChooseItemState


class waitMoneyToBuyState(State):
  
    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        price = self.machine.item.price
        if self.machine.moneyGet < price:
            self.machine.moneyGet = self.machine.moneyGet + float(input('insert ' + str(price - self.machine.moneyGet) + ': '))
        else:
            self.machine.state = self.machine.buyItemState

class buyItemState(State):
    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        if self.machine.moneyGet < self.machine.item.price:
            self.mprint('You can\'t buy this item. Insert more coins.') # then obvs you cant buy this item
            self.machine.state = self.machine.waitMoneyToBuyState
        else:
            self.machine.moneyGet -= self.machine.item.price # subtract item price from available cash
            self.machine.item.buyFromStock() # call this function to decrease the item inventory by 1
            # (what if we buy more than one?)
            self.mprint('You got ' +self.machine.item.name)
            self.mprint('Cash remaining: ' + str(self.machine.moneyGet))
            self.machine.state = self.machine.takeCoffeeState

class takeCoffeeState(State):
    def __init__(self, machine):      
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
        self.machine.state = self.machine.checkRefundState

class checkRefundState(State):
    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to checkRefundState")
        if self.machine.moneyGet > 0:
            self.mprint(str(self.machine.moneyGet) + " refunded.")
            self.machine.moneyGet = 0
        self.mprint('Thank you, have a nice day!\n')
        self.machine.state = self.machine.showItemsState

class Machine:
 
    def __init__(self,robot):
        self.myrobot= robot
        self.moneyGet = 0
        self.items = [] # all items contained in this list right here
        self.item=None 
        self.timeout = 10        
        self.showItemsState = showItemsState(self)
        self.WaitChooseItemState = WaitChooseItemState(self)
        self.waitMoneyToBuyState = waitMoneyToBuyState(self)
        self.buyItemState = buyItemState(self)
        self.takeCoffeeState = takeCoffeeState(self)
        self.checkRefundState = checkRefundState(self)
        
        self.state = self.showItemsState

    def run(self):
        self.state.checkAndChangeState()

    def scan(self):
        self.state.scan()

    def addItem(self, item):
        self.items.append(item) 


def vend():
    robot=RobotControl()
    machine = Machine(robot)
    #              name,giá,số lượng
    item1 = Item('caffe d',      1.5,    88, "caffeden.ngc" )
    item2 = Item('caffe s',      1.75,   1, "caffesua.ngc")
    item3 = Item('12'    ,       2.0,    3, "nuocngot.ngc")
    item4 = Item('23'    ,       0.50,   1,  "nuocngot.ngc")
    item5 = Item('45'    ,       0.75,   3,  "nuocngot.ngc")
    item6 = Item('milkshake',    1.2,    5, "nuocngot.ngc")
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