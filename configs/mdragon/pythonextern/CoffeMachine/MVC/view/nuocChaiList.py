from PyQt5 import QtGui, QtCore, QtWidgets, uic

class ListChai(QtWidgets.QWidget):
    def __init__(self):
        super(ListChai, self).__init__()
        uic.loadUi("view/nuocngot.ui", self)
        self.initEvent()

    def initEvent(self):
        self.buy_buttonGroup.buttonClicked.connect(self.addOrder)


    def addOrder(self,btn):
        id = btn.property('ID')
        if id is None: return
        print("SSSSSSSSSSSSSSSSSSSss")
