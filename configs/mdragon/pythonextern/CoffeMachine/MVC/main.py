# coding: utf8
import sys, time ,os
from model.machine import Machine
from controller.control import MainController
from view.view import MyGUI
import logging
import logging.handlers
from web import server    
import variThreading

from PyQt5.QtWidgets import QApplication
#from PyQt5.QtCore import pyqtSlot,  QObject ,pyqtSlot,QUrl,Qt, QTimer
#from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator
from modbus import ModbusPull


LOG_FILENAME = 'mylog.log'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
my_logger.addHandler(handler)
from memory_profiler import profile

class App(QApplication):
    @profile
    def __init__(self, sys_argv,server):
        super(App, self).__init__(sys_argv)
        queueWEB = variThreading.init()
        valveModbus = ModbusPull()
        self.Machine = Machine(my_logger,variThreading.queueVNPAY,valveModbus)
        self.main_controller = MainController(self.Machine)
        self.main_view = MyGUI(self.Machine, self.main_controller,server)
        #self.main_controller.loop()
        #self.main_view.show()

 
if __name__ == '__main__':
    app = App(sys.argv,server)
    sys.exit(app.exec_())