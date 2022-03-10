from PyQt5 import QtGui, QtCore, QtWidgets, uic

class ListNuocChai(QtWidgets.QWidget):
    def __init__(self):
        super(ListNuocChai, self).__init__()
        uic.loadUi("view/nuocngot.ui", self)

    