# coding: utf8
import sys
from model.machine import Machine
from controller.control import MainController
from view.view import MyGUI
import logging
import logging.handlers
from until.web import server    
import until.variThreading as variThreading
from until.modbus import ModbusPull
from PyQt5.QtWidgets import QApplication
from memory_profiler import profile
from until.vnpay import runVNPAY

LOG_FILENAME = 'mylog.log'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
my_logger.addHandler(handler)



class App(QApplication):

    __slots__ = ['FlaskWeb', 'Machine', 'main_controller', 'main_view','RunVNPAY','valveModbus']
    @profile
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.queueWEB = variThreading.init()
        self.RunVNPAY = runVNPAY()
        self.FlaskWeb = server(self.RunVNPAY)
        self.FlaskWeb.setDaemon(True)
        self.FlaskWeb.start()
        self.valveModbus = ModbusPull()
        self.Machine = Machine(my_logger,variThreading.queueVNPAY,self.valveModbus,self.RunVNPAY)
        self.main_controller = MainController(self.Machine)
        self.main_view = MyGUI(self.Machine, self.main_controller)
        self.main_view.show()
        self.main_view.initialized__()
        #self.main_view.showFullScreen()
 
if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())