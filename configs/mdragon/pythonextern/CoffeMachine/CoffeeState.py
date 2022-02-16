
import time


class Item:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def updateStock(self, stock):
        self.stock = stock

    def buyFromStock(self):
        if self.stock == 0: # if there is no items available
            # raise not item exception
            pass
        self.stock -= 1 # else stock of item decreases by 1

class State:
    def scan(self):
        pass
    def mprint(self,msg):

        print(msg,flush=True)

class WaitChooseItemState(State):
  
    """constructor for AM state class"""
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
        self.machine = machine

    def checkAndChangeState(self):
        self.mprint("Switching to showItemsState")
        self.mprint('\nitems available \n***************')

        for item in self.machine.items: # for each item in this vending machine
            if item.stock == 0: # if the stock of this item is 0
                self.machine.items.remove(item) # remove this item from being displayed
        for item in self.machine.items:
            self.mprint(item.name + " Gia: "+ str(item.price) + " + SL :" + str(item.stock)) # otherwise self.mprint this item and show its price

        self.mprint('***************\n')
        self.machine.state = self.machine.WaitChooseItemState


class waitMoneyToBuyState(State):
  
    """constructor for AM state class"""
    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        price = self.machine.item.price
        if self.machine.amount < price:
            self.machine.amount = self.machine.amount + float(input('insert ' + str(price - self.machine.amount) + ': '))
        else:
            self.machine.state = self.machine.buyItemState

class buyItemState(State):
  
    """constructor for AM state class"""
    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        if self.machine.amount < self.machine.item.price:
            self.mprint('You can\'t buy this item. Insert more coins.') # then obvs you cant buy this item
        else:
            self.machine.amount -= self.machine.item.price # subtract item price from available cash
            self.machine.item.buyFromStock() # call this function to decrease the item inventory by 1
            # (what if we buy more than one?)
            self.mprint('You got ' +self.machine.item.name)
            self.mprint('Cash remaining: ' + str(self.machine.amount))
        self.machine.state = self.machine.checkRefundState

class checkRefundState(State):
  
    """constructor for AM state class"""
    def __init__(self, machine):      
        self.machine = machine

    def checkAndChangeState(self):
        if self.machine.amount > 0:
            self.mprint(str(self.machine.amount) + " refunded.")
            self.machine.amount = 0
        self.mprint('Thank you, have a nice day!\n')

        self.mprint("Switching to checkRefundState")
        self.machine.state = self.machine.showItemsState

class Machine:
 
    def __init__(self):
        self.amount = 0
        self.items = [] # all items contained in this list right here
        self.item=None         
        self.showItemsState = showItemsState(self)
        self.WaitChooseItemState = WaitChooseItemState(self)
        self.waitMoneyToBuyState = waitMoneyToBuyState(self)
        self.checkRefundState = checkRefundState(self)
        self.buyItemState = buyItemState(self)
        self.state = self.showItemsState

    def run(self):
        self.state.checkAndChangeState()

    def scan(self):
        self.state.scan()

    def addItem(self, item):
        self.items.append(item) # method to add item to vending machine


def vend():

    machine = Machine()
    item1 = Item('choc',  1.5,  0)
    item2 = Item('pop', 1.75,  1)
    item3 = Item('chips',  2.0,  3)
    item4 = Item('gum',  0.50, 1)
    item5 = Item('mints',0.75,  3)
    item6 = Item('milkshake',1.2, 5 )
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