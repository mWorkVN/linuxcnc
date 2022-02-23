# coding: utf8
import sys, time ,os
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QObject
from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator
from model.machine import Machine
from controller.control import MainController
from view.view import MyGUI
import logging
import logging.handlers
#import linuxcnc
from gtts import gTTS
from playsound import playsound
import pyttsx3
from threading import Thread
try: 
    import queue
except ImportError: #py2
    import Queue as queue
LOG_FILENAME = 'mylog.log'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
my_logger.addHandler(handler)

 
class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        self.Machine = Machine(my_logger)
        self.main_controller = MainController(self.Machine)
        self.main_view = MyGUI(self.Machine, self.main_controller)
        self.main_view.show()
 
 
if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())