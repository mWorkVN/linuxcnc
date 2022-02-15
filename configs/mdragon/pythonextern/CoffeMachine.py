import socket
import atexit
import os,sys, threading, logging
import asyncore
import time
import queue
import json
import linuxcnc
import subprocess
queue  = queue.Queue(10)



class Linuxcnc_cmd(threading.Thread):
    
    def __init__(self):
        #self.emcstat = emcstat
        #self.emccommand = emccommand
        self.state = 0
        threading.Thread.__init__(self)
        self.emc = linuxcnc
        self.emcstat = self.emc.stat() # create a connection to the status channel
        self.emccommand = self.emc.command()
        #self.lcnc_error = self.linuxcncs.error_channel()
        print("LCNC init DONE")
        self.return_to_mode = 0

    def run(self):
        global server_get


if __name__ == '__main__':

    #ar = AsyncoreRunner()
    #ar.daemon = True
    #ar.start()
    li = Linuxcnc_cmd()
    li.daemon = True
    li.start()
    def exit_handler():
        print('My application is ending!')
    atexit.register(exit_handler)
    while(1):
        time.sleep(1)