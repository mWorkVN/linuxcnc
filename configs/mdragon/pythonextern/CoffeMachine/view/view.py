from PyQt5 import uic,QtCore
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator ,QDoubleValidator


class View(QMainWindow):
    numberOrderChange = QtCore.pyqtSignal()

    def __init__(self):
        super(View, self).__init__()
        self.username = ""
        self.password = ""
        self.initUi()
        self.initEvent()
    def initUi(self):
        uic.loadUi('vendding.ui', self)
        #self.show()
        """
        self.loginButton.clicked.connect(self.verifySignal)
        hoặc để tạo connect
        self.verifySignal.emit(value)
        """
    def paintEvent(self, event):
        self.update()

    def initEvent(self):
        pass
        self.btnBuyID1.clicked.connect(self.haveOrder)
        self.btnBuyID2.clicked.connect(self.haveOrder)
        self.numSlID1.currentTextChanged.connect(self.slOrderChange)
        self.numSlID2.currentTextChanged.connect(self.slOrderChange)
    def slOrderChange(self):
        print("have slOrderChange",flush=True)

    def haveOrder(self):
        print("have order",flush=True)

    def clear(self):
        self.usernameInput.clear()
        self.passwordInput.clear()

    def showMessage(self):
        pass
        """
        messageBox = QtWidgets.QMessageBox(self)
        messageBox.setText("your credentials are valid\n Welcome")
        messageBox.exec_()
        self.close()
        """
    def showError(self):
        pass
