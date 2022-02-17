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
#sudo netstat -ap | grep :8080

"""

sudo lsof -t -i tcp:8080 | xargs kill -9
"""
server_get = {"status":False,"data":""}
handler = None
data=""
class EchoHandler(asyncore.dispatcher_with_send):
    
    def handle_read(self):
        global server_get
        global data
        rev = self.recv(1)
        rev = rev.decode("utf8")
        if rev!='\n':
            data += rev
        else:
            if (len(data)<15):
                data = ''
                return
            print("SERVER",data)
            str_data = data #.decode("utf8")
            data = ''
            server_get["status"] = True
            server_get["data"]=str_data

    def sendData(self,data):
        self.send(data.encode())

    def handle_close(self):
        self.close()
        print("CLOSE")

"""class EchoServer(asyncore.dispatcher):
    
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        #socket.TCPServer.allow_reuse_address = True
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        global handler
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print ('Incoming connection from %s' % repr(addr))
            handler = EchoHandler(sock)"""


class AsyncoreRunner(threading.Thread,asyncore.dispatcher):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stsBind = False
        asyncore.dispatcher.__init__(self)
        #socket.TCPServer.allow_reuse_address = True
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        try:
            self.bind(('0.0.0.0', 8080))
            self.listen(5)
            self.stsBind = True
        except Exception as e:
            print("ERROR - BIND SOCKET",e)
    def ping(self):
        pass

    def run(self):
        print (' thread start')
        while (1):
            if self.stsBind:
                asyncore.loop(timeout=1, count=1)
            else:
                try:
                    #subprocess.call(['sudo netstat -ap | grep :8080'])
                    os.system('sudo netstat -ap | grep :8080')
                    #time.sleep(2)
                    #self.bind(('0.0.0.0', 8080))
                    #self.listen(5)
                    self.stsBind = True
                except Exception as e:
                    self.stsBind = False
                    print("ERROR - BIND SOCKET",e)
        print (' thread stop')

    def handle_accept(self):
        global handler
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print ('Incoming connection from %s' % repr(addr))
            handler = EchoHandler(sock)

    def close(self):
        self.server.close()
        self.join()


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
        timebegin = 0
        timeprint = time.time()
        while (1):
            #self.linuxcncs = linuxcnc
            #self.emcstat = self.linuxcncs.stat() # create a connection to the status channel
            #self.emccommand = self.linuxcncs.command()
            try:
                self.emcstat.poll() # get current values
            except Exception as e:
                if  time.time() - timeprint > 1:
                    timeprint= time.time() 
                    print ("error", e.args)
                

            try:
                lcnc_error = linuxcnc.error_channel()
                error = lcnc_error.poll()
                if error:
                    kind, text = error
                    if kind in (linuxcnc.NML_ERROR, linuxcnc.OPERATOR_ERROR):
                        typus = "error"
                    else:
                        typus = "info"
                        #print (typus, text)
            except Exception as e:
                if "Error buffer invalid" in e.args:
                    if  time.time() - timeprint > 1:
                        timeprint= time.time() 
                        print("Exit")
            
            if (server_get["status"]  == True):
                print("havevari ",server_get["data"] )
                server_get["status"] = False
                try:
                    data = json.loads(server_get["data"])
                except Exception as e:
                    print(e)
                    self.sendBack_server("JsonFail\n")
                    continue
                if "MDI" in data["sts"]:
                    self.call_MDI(data["data"])
                elif "RST" in data["sts"]:
                    self.state = 0
                elif "SET" in data["sts"]:
                    self.call_Set(data["data"],data["arg"])

                elif "GET" in data["sts"]:
                    self.call_Get(data["data"],data["arg"])
                elif "NEWCNC" in data["sts"]:
                    self.initCNC()
                elif "tMDI" in data["sts"]:
                    self.call_tMDI(data["data"])
            
            if (self.state == 1):
                if self.emccommand.wait_complete(0.001) != -1:
                    self.state = 2
            elif (self.state == 2):
                self.sendBack_server("Done\n")
                self.state = 0
            if (time.time()-timebegin > 1):
                timebegin =  time.time()

    def ok_for_mdi(self):
        self.emcstat.poll()
        s = self.emcstat
        return not s.estop and s.enabled and s.homed and \
            (s.interp_state == self.emc.INTERP_IDLE)

    def set_manual_mode(self):
        self.emcstat.poll()
        if self.emcstat.task_mode != self.emc.MODE_MANUAL:
            self.emccommand.mode(self.emc.MODE_MANUAL)
            self.emccommand.wait_complete()

    def set_mdi_mode(self):
        self.emcstat.poll()
        if self.emcstat.task_mode != self.emc.MODE_MDI:
            self.emccommand.mode(self.emc.MODE_MDI)
            self.emccommand.wait_complete()

    def periodic(self):
        # return mode back to preset variable, when idle
        if self.return_to_mode > -1:
            self.emcstat.poll()
            if self.emcstat.interp_state == self.emc.INTERP_IDLE:
                self.emccommand.mode(self.return_to_mode)
                self.return_to_mode = -1

    def set_auto_mode(self):
        self.emcstat.poll()
        if self.emcstat.task_mode != self.emc.MODE_AUTO:
            self.emccommand.mode(self.emc.MODE_AUTO)
            self.emccommand.wait_complete()

    def get_mode(self):
        self.emcstat.poll()
        return self.emcstat.task_mode

    def initCNC(self):
        """self.emc = linuxcnc
        self.emcstat = self.emc.stat() # create a connection to the status channel
        self.emccommand = self.emc.command()
        self.state = 0"""
        self.sendBack_server("Dinit\n")

    def call_MDI(self, cmd):
        if self.state == 0: 
            self.set_mdi_mode() 
            data = self.emccommand.mdi(cmd)
            print("MDI returnb",data)
            self.state = 1
        else:
            print("Wait")   
            self.sendBack_server("Wait\n")
    #{"sts":"SET","data":"mode","arg":["MODE_MDI",1,2.1]}
    #{"sts":"SET","data":"mode","arg":"MODE_MDI"}   ->c.mode(linuxcnc.MODE_MDI)
    #{"sts":"SET","data":"mode","arg":"MODE_AUTO"}  ->c.mode(linuxcnc.MODE_AUTO)
    #{"sts":"SET","data":"mode","arg":"MODE_MANUAL"}->c.mode(linuxcnc.MODE_MANUAL)
    def call_Set(self, cmd,arg):
        try:
            self.emccommand.mode(self.emc.MODE_MANUAL)
            size = len(arg)
            listpara = [None] * size
            for x in range(size):
                if type(arg[x]) is str:
                    listpara[x]=getattr(self.linuxcncs,arg[x])
                else:
                    listpara[x]=arg[x]
            if self.state == 0:
                if (size == 0):
                    getattr(self.emccommand, cmd)
                else:
                    getattr(self.emccommand, cmd)(*listpara)
                self.state = 1
            else:
                print("Wait")   
                self.sendBack_server("Wait\n")       
        except Exception as e:
            print("SER " ,e)
       
    def call_Get(self, cmd,arg):
        valueReturn = ""
        if "Mode" in cmd:
            valueReturn = self.get_mode()
        elif "statusServer" in cmd:
            valueReturn = self.state 
        self.sendBack_server(str(valueReturn) + "\n")      
        

    def call_tMDI(self, cmd):
        print("Call MDI",cmd)

    def sendBack_server(self,cmd):
        global handler
        if handler == None:
            return
        handler.sendData(cmd)

if __name__ == '__main__':

    ar = AsyncoreRunner()
    ar.daemon = True
    ar.start()
    li = Linuxcnc_cmd()
    li.daemon = True
    li.start()
    def exit_handler():
        print('My application is ending!')
    atexit.register(exit_handler)
    while(1):
        time.sleep(1)
